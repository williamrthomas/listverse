#!/usr/bin/env python3
"""Assemble the static directory site from site/ plus data/lists.json."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DIST = ROOT / "dist"
LISTS = ROOT / "data" / "lists.json"
META = ROOT / "data" / "catalog_meta.json"


def catalog_generated_at() -> str | None:
    if META.is_file():
        try:
            payload = json.loads(META.read_text(encoding="utf-8"))
            value = payload.get("generated_at")
            if isinstance(value, str) and value.strip():
                return value.strip()
        except json.JSONDecodeError:
            pass

    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", "data/lists.json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        date = result.stdout.strip()
        if result.returncode == 0 and len(date) == 10:
            return date
    except OSError:
        pass
    return None


def main() -> None:
    if not SITE.is_dir():
        raise SystemExit(f"Missing site directory: {SITE}")
    if not LISTS.is_file():
        raise SystemExit(f"Missing catalog data: {LISTS}")

    lists_data = json.loads(LISTS.read_text(encoding="utf-8"))
    if not isinstance(lists_data, list):
        raise SystemExit("data/lists.json must be an array of lists")

    payload: dict = {"lists": lists_data}
    generated_at = catalog_generated_at()
    if generated_at:
        payload["generated_at"] = generated_at

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SITE, DIST, ignore=shutil.ignore_patterns(".DS_Store"))

    data_dir = DIST / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "lists.json").write_text(
        json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    extra = f", generated_at {generated_at}" if generated_at else ""
    print(f"Built {DIST} ({LISTS.stat().st_size} bytes of catalog data{extra})")


if __name__ == "__main__":
    main()
