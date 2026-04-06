#!/usr/bin/env python3
"""Refresh live GitHub stats for all entries in data/lists.json.

Usage:
    python scripts/refresh_stats.py

Requires:
    - GITHUB_TOKEN environment variable (or gh CLI authenticated)
    - Python 3.8+
    - requests (pip install requests) OR gh CLI installed

The script:
1. Reads data/lists.json
2. Fetches live stats from GitHub API for each entry
3. Updates the JSON in place
4. Regenerates data/lists.csv
5. Prints a summary of changes
"""

import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LISTS_JSON = REPO_ROOT / "data" / "lists.json"
LISTS_CSV = REPO_ROOT / "data" / "lists.csv"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

STAT_FIELDS = [
    "stars_count", "forks_count", "last_commit_date",
    "open_issues_count", "is_archived", "watchers_count"
]

# Array fields that need pipe-delimited encoding in CSV
ARRAY_FIELDS = ["tags", "use_cases", "overlaps_with", "best_sections", "related_lists"]
BOOL_FIELDS = ["has_contributions_guide", "has_website", "is_awesome_verified", "is_archived"]


def fetch_with_requests(owner, repo):
    """Fetch repo stats using the requests library."""
    import requests

    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code == 403:
        # Rate limited
        reset = resp.headers.get("X-RateLimit-Reset")
        if reset:
            wait = max(int(reset) - int(time.time()), 1)
            print(f"  Rate limited. Waiting {wait}s...")
            time.sleep(min(wait, 60))
            resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code != 200:
        return None

    data = resp.json()
    return {
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "pushed": data.get("pushed_at", ""),
        "issues": data["open_issues_count"],
        "archived": data["archived"],
        "watchers": data["watchers_count"],
    }


def fetch_with_gh(owner, repo):
    """Fetch repo stats using the gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}", "--jq",
             '{stars: .stargazers_count, forks: .forks_count, pushed: .pushed_at, '
             'issues: .open_issues_count, archived: .archived, watchers: .watchers_count}'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def fetch_repo_stats(owner, repo):
    """Fetch stats, preferring requests if available, falling back to gh CLI."""
    try:
        import requests  # noqa: F401
        return fetch_with_requests(owner, repo)
    except ImportError:
        return fetch_with_gh(owner, repo)


def extract_owner_repo(github_url):
    """Extract owner/repo from a GitHub URL."""
    parts = github_url.rstrip("/").split("/")
    return parts[-2], parts[-1]


def regenerate_csv(data):
    """Regenerate lists.csv from the JSON data."""
    if not data:
        return

    fieldnames = list(data[0].keys())

    with open(LISTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for entry in data:
            row = {}
            for key, value in entry.items():
                if isinstance(value, list):
                    row[key] = "|".join(str(v) for v in value)
                elif isinstance(value, bool):
                    row[key] = "TRUE" if value else "FALSE"
                elif value is None:
                    row[key] = ""
                else:
                    row[key] = value
            writer.writerow(row)


def main():
    print(f"Loading {LISTS_JSON}...")
    with open(LISTS_JSON) as f:
        data = json.load(f)

    total = len(data)
    print(f"Found {total} entries. Fetching live stats...\n")

    changes = []
    errors = []

    for i, entry in enumerate(data):
        owner, repo = extract_owner_repo(entry["github_url"])
        print(f"[{i + 1}/{total}] {owner}/{repo}...", end=" ", flush=True)

        stats = fetch_repo_stats(owner, repo)
        if not stats:
            errors.append(f"{owner}/{repo}")
            print("ERROR")
            continue

        old_stars = entry.get("stars_count", 0)
        new_stars = stats["stars"]

        entry["stars_count"] = stats["stars"]
        entry["forks_count"] = stats["forks"]
        entry["last_commit_date"] = stats["pushed"][:10] if stats["pushed"] else entry.get("last_commit_date")
        entry["open_issues_count"] = stats["issues"]
        entry["is_archived"] = stats["archived"]
        entry["watchers_count"] = stats["watchers"]

        star_diff = new_stars - old_stars
        if abs(star_diff) > 100:
            changes.append((entry["name"], old_stars, new_stars, star_diff))

        print(f"OK ({new_stars:,} stars)")

        # Rate limit: pause every 30 requests
        if (i + 1) % 30 == 0:
            time.sleep(2)

    # Save updated JSON
    with open(LISTS_JSON, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"\nUpdated {LISTS_JSON}")

    # Regenerate CSV
    regenerate_csv(data)
    print(f"Regenerated {LISTS_CSV}")

    # Print summary
    print("\n" + "=" * 60)
    print("REFRESH SUMMARY")
    print("=" * 60)
    print(f"Total entries: {total}")
    print(f"Successful: {total - len(errors)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print(f"\nFailed repos: {', '.join(errors)}")

    if changes:
        print(f"\nSignificant star changes (>100):")
        for name, old, new, diff in sorted(changes, key=lambda x: -abs(x[3])):
            sign = "+" if diff > 0 else ""
            print(f"  {name}: {old:,} -> {new:,} ({sign}{diff:,})")

    archived = [e["name"] for e in data if e.get("is_archived")]
    if archived:
        print(f"\nArchived repos: {', '.join(archived)}")

    print("\nDone!")


if __name__ == "__main__":
    main()
