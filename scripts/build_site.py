#!/usr/bin/env python3
"""Assemble the static directory site from site/ plus data/lists.json."""

from __future__ import annotations

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
    print(f"Built {DIST} ({LISTS.stat().st_size} bytes of catalog data)")


if __name__ == "__main__":
    main()
