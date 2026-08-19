#!/usr/bin/env python3
"""
build_index.py — Generate _index.md files at global and per-folder level.

Indexes are chronological (by date field in frontmatter, fallback to file mtime).
Run automatically by agent.py after each note is filed.

Usage:
    python build_index.py          # rebuild all indexes
    python build_index.py --dry-run
"""

import re
import argparse
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install PyYAML")

BASE = Path(__file__).parent

SKIP_DIRS  = {"00-Inbox", ".git", "assets", "__pycache__", "_trash"}
SKIP_FILES = {"_index.md"}

_STATIC_FOLDERS = {
    "10-Work":                    "Work & Projects",
    "40-Reference":               "Reference",
    "50-Archive":                 "Archive",
    "Journal":                    "Journal",
}

def _discover_folders() -> dict[str, str]:
    """Return all note folders: static ones + auto-discovered subdirs of 20-Learning."""
    base = Path(__file__).parent
    folders = dict(_STATIC_FOLDERS)
    learning = base / "20-Learning"
    if learning.exists():
        folders["20-Learning"] = "Learning"
        for sub in sorted(learning.iterdir()):
            if sub.is_dir() and not sub.name.startswith("."):
                key = f"20-Learning/{sub.name}"
                folders[key] = sub.name.replace("-", " ")
    return folders

INDEXED_FOLDERS = _discover_folders()

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


# ── Data loading ──────────────────────────────────────────────────────────────

def _parse_date(val) -> date | None:
    if not val:
        return None
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def load_notes() -> list[dict]:
    """Return list of note dicts with metadata for all .md files in KB."""
    notes = []
    for md in BASE.rglob("*.md"):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        if md.name in SKIP_FILES:
            continue
        try:
            content = md.read_text(encoding="utf-8")
            m = FRONTMATTER_RE.match(content)
            fm = yaml.safe_load(m.group(1)) if m else {}
            fm = fm or {}
        except Exception:
            fm = {}

        note_date = _parse_date(fm.get("date")) or date.fromtimestamp(md.stat().st_mtime)
        updated   = _parse_date(fm.get("updated"))

        # Determine folder key from path
        rel = md.relative_to(BASE)
        parts = rel.parts
        if len(parts) == 1:
            folder_key = ""
        elif len(parts) == 2:
            folder_key = parts[0]
        else:
            folder_key = "/".join(parts[:-1])

        notes.append({
            "path":       md,
            "rel":        rel,
            "folder_key": folder_key,
            "date":       note_date,
            "updated":    updated,
            "title":      fm.get("title") or md.stem,
            "type":       fm.get("type", ""),
            "status":     fm.get("status", ""),
            "project":    fm.get("project", ""),
            "tags":       fm.get("tags") or [],
        })

    return sorted(notes, key=lambda n: n["date"], reverse=True)


# ── Rendering ─────────────────────────────────────────────────────────────────

def _month_label(d: date) -> str:
    return d.strftime("%Y-%m — %B %Y")


def _note_row(note: dict, rel_to: Path) -> str:
    try:
        link_path = note["path"].relative_to(rel_to)
    except ValueError:
        link_path = note["rel"]

    title   = note["title"]
    ndate   = note["date"].isoformat()
    ntype   = f"`{note['type']}`" if note["type"] else ""
    updated = f" *(updated {note['updated']})*" if note["updated"] else ""
    folder  = f" · `{note['folder_key']}`" if note["folder_key"] else ""

    return f"| {ndate} | [{title}]({link_path}){updated} | {ntype}{folder} |"


def _build_section(notes: list[dict], rel_to: Path) -> str:
    by_month: dict[str, list] = defaultdict(list)
    for n in notes:
        by_month[_month_label(n["date"])].append(n)

    lines = []
    for month, mnotes in by_month.items():
        lines.append(f"\n## {month}\n")
        lines.append("| Date | Note | Type |")
        lines.append("|------|------|------|")
        for n in mnotes:
            lines.append(_note_row(n, rel_to))

    return "\n".join(lines)


# ── Index writers ─────────────────────────────────────────────────────────────

def build_global_index(notes: list[dict], dry_run: bool = False) -> int:
    today = date.today().isoformat()
    total = len(notes)

    # Summary by folder
    by_folder: dict[str, int] = defaultdict(int)
    for n in notes:
        by_folder[n["folder_key"]] += 1

    folder_summary = " | ".join(
        f"**{INDEXED_FOLDERS.get(k, k)}** {v}"
        for k, v in sorted(by_folder.items()) if k
    )

    header = (
        f"# KnowledgeBase — Global Index\n\n"
        f"{total} notes | Last updated: {today}\n\n"
        f"{folder_summary}\n"
    )

    body   = _build_section(notes, BASE)
    output = header + body + "\n"

    dest = BASE / "_index.md"
    if not dry_run:
        dest.write_text(output, encoding="utf-8")
    return total


def build_folder_index(folder_key: str, label: str, notes: list[dict], dry_run: bool = False) -> int:
    folder_path = BASE / Path(folder_key.replace("/", "\\"))
    if not folder_path.exists():
        return 0

    folder_notes = [n for n in notes if n["folder_key"].startswith(folder_key)]
    if not folder_notes:
        return 0

    today = date.today().isoformat()
    total = len(folder_notes)

    header = (
        f"# {label}\n\n"
        f"{total} notes | Last updated: {today}\n"
    )

    body   = _build_section(folder_notes, folder_path)
    output = header + body + "\n"

    dest = folder_path / "_index.md"
    if not dry_run:
        dest.write_text(output, encoding="utf-8")
    return total


# ── Public API ────────────────────────────────────────────────────────────────

def build_all(dry_run: bool = False) -> dict[str, int]:
    notes   = load_notes()
    results = {}

    results["_global"] = build_global_index(notes, dry_run)

    for folder_key, label in INDEXED_FOLDERS.items():
        count = build_folder_index(folder_key, label, notes, dry_run)
        if count:
            results[folder_key] = count

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Rebuild all KnowledgeBase index files.")
    ap.add_argument("--dry-run", action="store_true", help="Print counts without writing files")
    args = ap.parse_args()

    results = build_all(dry_run=args.dry_run)
    mode    = "DRY-RUN" if args.dry_run else "BUILT"

    print(f"[{mode}] Global index: {results.get('_global', 0)} notes")
    for k, v in results.items():
        if k != "_global":
            print(f"[{mode}] {k}: {v} notes")


if __name__ == "__main__":
    main()
