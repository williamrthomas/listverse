#!/usr/bin/env python3
"""Assemble the static directory site from site/ plus data/lists.json."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DIST = ROOT / "dist"
LISTS = ROOT / "data" / "lists.json"
HIGHLIGHTS = ROOT / "HIGHLIGHTS.md"


def main() -> None:
    if not SITE.is_dir():
        raise SystemExit(f"Missing site directory: {SITE}")
    if not LISTS.is_file():
        raise SystemExit(f"Missing catalog data: {LISTS}")
    if not HIGHLIGHTS.is_file():
        raise SystemExit(f"Missing highlights: {HIGHLIGHTS}")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SITE, DIST, ignore=shutil.ignore_patterns(".DS_Store"))

    data_dir = DIST / "data"
    data_dir.mkdir(exist_ok=True)
    shutil.copy2(LISTS, data_dir / "lists.json")
    shutil.copy2(HIGHLIGHTS, DIST / "HIGHLIGHTS.md")

    catalog = json.loads(LISTS.read_text())
    if not isinstance(catalog, list):
        raise SystemExit("Catalog data is not a list")
    template = (SITE / "list.html").read_text()
    lists_dir = DIST / "lists"
    lists_dir.mkdir(exist_ok=True)
    for entry in catalog:
        list_id = entry.get("id")
        if not list_id:
            continue
        dest = lists_dir / str(list_id)
        dest.mkdir(exist_ok=True)
        (dest / "index.html").write_text(template)
    template_copy = DIST / "list.html"
    if template_copy.exists():
        template_copy.unlink()

    def emit_static(content: str, dest_dir: Path, dest_file: Path) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "index.html").write_text(content)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(content)

    about = (SITE / "about.html").read_text()
    emit_static(about, DIST / "about", DIST / "about.html")

    browse = (SITE / "browse.html").read_text()
    emit_static(browse, DIST / "browse", DIST / "browse.html")

    journey = (SITE / "journey.html").read_text()
    emit_static(journey, DIST / "journeys" / "agents", DIST / "journeys" / "agents.html")
    emit_static(journey, DIST / "journeys" / "learn", DIST / "journeys" / "learn.html")
    journey_template = DIST / "journey.html"
    if journey_template.exists():
        journey_template.unlink()

    print(
        f"Built {DIST} ({LISTS.stat().st_size} bytes of catalog data, {len(catalog)} interiors, about + 2 journeys)"
    )


if __name__ == "__main__":
    main()
