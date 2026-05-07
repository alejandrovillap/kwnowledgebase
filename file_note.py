#!/usr/bin/env python3
"""
file_note.py — Classify a note and file it into the correct KnowledgeBase folder as .md.

Usage (CLI):
    python file_note.py note.txt
    python file_note.py note.txt --markdown-body "text with ![diagram](...) refs"

Usage (module):
    from file_note import file_note
    result = file_note(text="raw text", markdown_body="...", meta={...})
    # returns {"dest_md": str, "folder": str, "title": str, "date": str}
"""

import sys
import json
import argparse
import shutil
from datetime import date as _date
from pathlib import Path

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install PyYAML")

from classify_note import classify

BASE      = Path(__file__).parent
PROCESSED = BASE / "00-Inbox" / "processed"

FOLDER_MAP: dict[str, Path] = {
    "10-Work":                    BASE / "10-Work",
    "20-Learning":                BASE / "20-Learning",
    "20-Learning/CCA-F":          BASE / "20-Learning" / "CCA-F",
    "20-Learning/Certifications": BASE / "20-Learning" / "Certifications",
    "40-Reference":               BASE / "40-Reference",
    "50-Archive":                 BASE / "50-Archive",
    "Journal":                    BASE / "Journal",
}

# Number of path components below BASE for each folder (used for ../assets/ depth)
FOLDER_DEPTH: dict[str, int] = {
    "10-Work": 1, "20-Learning": 1, "40-Reference": 1,
    "50-Archive": 1, "Journal": 1,
    "20-Learning/CCA-F": 2, "20-Learning/Certifications": 2,
}


def _slug(text: str) -> str:
    return text.strip().replace(" ", "_").replace("/", "-")[:80]


def _frontmatter(meta: dict) -> str:
    # Ensure lists are real lists, not None
    for key in ("tags", "keywords"):
        if not isinstance(meta.get(key), list):
            meta[key] = []
    ordered = {k: meta.get(k) for k in [
        "title", "date", "type", "status", "technology",
        "tags", "keywords", "project", "certification",
        "target_folder", "confidence",
    ]}
    return "---\n" + yaml.dump(ordered, allow_unicode=True, default_flow_style=False) + "---\n"


def file_note(
    text: str,
    markdown_body: str | None = None,
    meta: dict | None = None,
    source_path: str | Path | None = None,
) -> dict:
    """
    Classify text (or use supplied meta) and write a .md file into the right folder.

    Args:
        text:          Raw OCR text (used for classification if meta is None).
        markdown_body: Markdown body with diagram refs. Falls back to text.
        meta:          Pre-computed classification dict. If None, classify(text) is called.
        source_path:   Original file to move to 00-Inbox/processed/ after filing.

    Returns:
        {"dest_md": str, "folder": str, "title": str, "date": str}
    """
    if meta is None:
        meta = classify(text.strip())

    folder_key = meta.get("target_folder") or "40-Reference"
    dest_dir   = FOLDER_MAP.get(folder_key, FOLDER_MAP["40-Reference"])
    dest_dir.mkdir(parents=True, exist_ok=True)

    title     = meta.get("title") or "untitled"
    note_date = meta.get("date")  or _date.today().isoformat()
    slug      = _slug(title)
    stem      = f"{note_date}_{slug}"
    dest_md   = dest_dir / (stem + ".md")

    body = markdown_body if markdown_body is not None else text
    content = _frontmatter(meta) + "\n" + body + "\n"
    dest_md.write_text(content, encoding="utf-8")

    # Move source to processed/
    if source_path:
        PROCESSED.mkdir(parents=True, exist_ok=True)
        src = Path(source_path)
        shutil.move(str(src), PROCESSED / src.name)

    print(f"[OK] → {dest_md.relative_to(BASE)}")
    print(f"     folder: {folder_key} | confidence: {meta.get('confidence')} | type: {meta.get('type')}")

    return {"dest_md": str(dest_md), "folder": folder_key, "title": title, "date": note_date}


def main():
    ap = argparse.ArgumentParser(description="Classify and file a note into KnowledgeBase.")
    ap.add_argument("file", help="Text file with OCR content")
    ap.add_argument("--markdown-body", default=None,
                    help="Markdown body to use instead of raw text (optional)")
    args = ap.parse_args()

    src = Path(args.file)
    text = src.read_text(encoding="utf-8")
    file_note(text=text, markdown_body=args.markdown_body, source_path=src)


if __name__ == "__main__":
    main()
