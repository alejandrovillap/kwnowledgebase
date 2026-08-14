#!/usr/bin/env python3
"""
repair_all_notes.py — Batch Mermaid repair for all existing notes.

Scans every .md file under the KnowledgeBase folders, repairs Mermaid blocks,
and reports what changed.

Usage:
    python repair_all_notes.py                  # repair in place
    python repair_all_notes.py --dry-run        # preview only, no writes
    python repair_all_notes.py --no-claude      # regex rules only (no API)
    python repair_all_notes.py --folder 10-Work # limit to one folder
"""

import os
import sys
import argparse
from pathlib import Path

BASE = Path(__file__).parent

# Folders to scan (skip assets, __pycache__, etc.)
NOTE_FOLDERS = [
    "10-Work",
    "20-Learning",
    "30-Personal",
    "40-Projects",
    "50-Resources",
    "60-Archive",
    "Journal",
    "Inbox",
]


def find_notes(base: Path, folder_filter: str | None) -> list[Path]:
    notes = []
    if folder_filter:
        search_roots = [base / folder_filter]
    else:
        search_roots = [base / f for f in NOTE_FOLDERS if (base / f).is_dir()]
        # Also pick up .md files directly under base (like daily notes)
        search_roots.append(base)

    for root in search_roots:
        if not root.exists():
            continue
        pattern = "*.md" if root == base else "**/*.md"
        notes.extend(root.glob(pattern))

    return sorted(set(notes))


def main():
    ap = argparse.ArgumentParser(description="Batch-repair Mermaid blocks in all KB notes.")
    ap.add_argument("--dry-run",   action="store_true", help="Preview changes without writing")
    ap.add_argument("--no-claude", action="store_true", help="Regex rules only, no API calls")
    ap.add_argument("--folder",    default=None,        help="Limit to one folder (e.g. 10-Work)")
    args = ap.parse_args()

    from dotenv import load_dotenv
    import anthropic
    from mermaid_repair import repair_all_in_text

    load_dotenv(BASE / ".env")
    client = None if args.no_claude else anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    notes = find_notes(BASE, args.folder)
    if not notes:
        print("No .md files found.")
        return

    print(f"Scanning {len(notes)} notes{'  [dry-run]' if args.dry_run else ''}...\n")

    total_files  = 0
    total_blocks = 0

    for path in notes:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  [ERROR] {path.relative_to(BASE)}: {e}")
            continue

        fixed, n = repair_all_in_text(text, client=client)

        if n == 0:
            continue

        total_files  += 1
        total_blocks += n
        rel = path.relative_to(BASE)

        if args.dry_run:
            print(f"  ⚠️  {rel}  — {n} bloque(s) a reparar")
        else:
            path.write_text(fixed, encoding="utf-8")
            print(f"  ✅  {rel}  — {n} bloque(s) reparado(s)")

    print()
    if total_files == 0:
        print("✅  Todas las notas están limpias — sin cambios necesarios.")
    elif args.dry_run:
        print(f"⚠️   {total_files} archivo(s), {total_blocks} bloque(s) necesitan reparación.")
        print("    Corre sin --dry-run para aplicar los cambios.")
    else:
        print(f"✅  {total_files} archivo(s) actualizados, {total_blocks} bloque(s) reparados.")


if __name__ == "__main__":
    main()
