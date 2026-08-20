#!/usr/bin/env python3
"""
migrate_rename_notes.py — Strip date prefix from existing note filenames.

Renames YYYY-MM-DD_Title.md  →  Title.md
Skips files that don't match the date pattern.
Handles collisions by appending _1, _2, ...

Usage:
    python migrate_rename_notes.py --dry-run   # preview only
    python migrate_rename_notes.py             # apply
"""

import re
import argparse
from pathlib import Path

BASE      = Path(__file__).parent
SKIP_DIRS = {"00-Inbox", ".git", "assets", "__pycache__", "_trash"}
DATE_RE   = re.compile(r"^\d{4}-\d{2}-\d{2}_(.+)$")


def strip_date(stem: str) -> str | None:
    m = DATE_RE.match(stem)
    return m.group(1) if m else None


def migrate(dry_run: bool = False):
    renamed = 0
    skipped = 0
    collisions = 0

    for md in sorted(BASE.rglob("*.md")):
        if any(p in SKIP_DIRS for p in md.parts):
            continue
        if md.name.startswith("_"):
            continue

        new_stem = strip_date(md.stem)
        if not new_stem:
            skipped += 1
            continue

        dest = md.parent / (new_stem + ".md")

        # Handle collision
        counter = 1
        while dest.exists() and dest != md:
            dest = md.parent / (f"{new_stem}_{counter}.md")
            counter += 1
            collisions += 1

        if dest == md:
            skipped += 1
            continue

        print(f"{'[DRY]' if dry_run else '[RENAME]'} {md.relative_to(BASE)}  →  {dest.name}")
        if not dry_run:
            md.rename(dest)
        renamed += 1

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Done: {renamed} renamed, {skipped} skipped, {collisions} collision(s) resolved.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    migrate(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
