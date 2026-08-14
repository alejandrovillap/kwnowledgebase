#!/usr/bin/env python3
"""
reocr_note.py — Re-process a source image/PDF and update an existing note.

Replaces the note body with a fresh OCR result (pre-processing + specialized
prompt + Mermaid repair + confidence banner) while keeping the frontmatter intact.

Usage:
    python reocr_note.py scan.jpg 10-Work/mi-nota.md
    python reocr_note.py scan.pdf 10-Work/mi-nota.md --dry-run
    python reocr_note.py scan.jpg 10-Work/mi-nota.md --depth 2
"""

import re
import sys
import argparse
from pathlib import Path

BASE = Path(__file__).parent
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def main():
    ap = argparse.ArgumentParser(description="Re-OCR a source file and update an existing note.")
    ap.add_argument("source", help="Image or PDF source file")
    ap.add_argument("note",   help="Existing .md note to update")
    ap.add_argument("--dry-run", action="store_true", help="Print result without writing")
    ap.add_argument("--depth",   type=int, default=1,
                    help="Folder depth for asset paths (default 1)")
    args = ap.parse_args()

    source = Path(args.source)
    note   = Path(args.note)

    if not source.exists():
        sys.exit(f"Source not found: {source}")
    if not note.exists():
        sys.exit(f"Note not found: {note}")

    print(f"Re-processing: {source.name}")
    from ocr import ocr
    result = ocr(source, folder_depth=args.depth)

    conf  = result["confidence"]
    ctype = result["content_type"]
    emoji = {"high": "✅", "medium": "⚠️", "low": "🔴"}.get(conf, "?")
    print(f"{emoji}  Confianza: {conf.upper()}  |  Tipo: {ctype}")
    if result["uncertain_regions"]:
        for r in result["uncertain_regions"]:
            print(f"   • {r}")

    # Preserve existing frontmatter
    existing = note.read_text(encoding="utf-8")
    m = FM_RE.match(existing)
    frontmatter = m.group(0) if m else ""

    new_content = frontmatter + "\n" + result["markdown_body"] + "\n"

    if args.dry_run:
        print("\n── PREVIEW (primeros 1000 chars del body) ──")
        print(result["markdown_body"][:1000])
        print("\n── (dry-run, sin escribir) ──")
    else:
        note.write_text(new_content, encoding="utf-8")
        print(f"✅  Nota actualizada: {note}")


if __name__ == "__main__":
    main()
