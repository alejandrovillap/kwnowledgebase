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
    "10-Work":                      BASE / "10-Work",
    "20-Learning":                  BASE / "20-Learning",
    "20-Learning/CCA-F":            BASE / "20-Learning" / "CCA-F",
    "20-Learning/Certifications":   BASE / "20-Learning" / "Certifications",
    "20-Learning/Cognitive-PM-AI":  BASE / "20-Learning" / "Cognitive-PM-AI",
    "20-Learning/Antigravity":      BASE / "20-Learning" / "Antigravity",
    "20-Learning/Gemini-Enterprise":BASE / "20-Learning" / "Gemini-Enterprise",
    "40-Reference":                 BASE / "40-Reference",
    "50-Archive":                   BASE / "50-Archive",
    "Journal":                      BASE / "Journal",
}

# Number of path components below BASE for each folder (used for ../assets/ depth)
FOLDER_DEPTH: dict[str, int] = {
    "10-Work": 1, "20-Learning": 1, "40-Reference": 1,
    "50-Archive": 1, "Journal": 1,
    "20-Learning/Antigravity": 2, "20-Learning/Gemini-Enterprise": 2,
    "20-Learning/CCA-F": 2, "20-Learning/Certifications": 2,
    "20-Learning/Cognitive-PM-AI": 2,
}


def _resolve_folder(folder_key: str) -> tuple[Path, int]:
    """Return (dest_path, depth) for a folder key.
    Supports dynamically created subfolders under 20-Learning.
    """
    if folder_key in FOLDER_MAP:
        depth = FOLDER_DEPTH.get(folder_key, 1)
        return FOLDER_MAP[folder_key], depth

    # Allow new one-level subfolders under 20-Learning (e.g. "20-Learning/PMI-ACP")
    if folder_key.startswith("20-Learning/"):
        parts = folder_key.split("/")
        if len(parts) == 2 and parts[1]:
            subfolder = parts[1].replace(" ", "-")
            path = BASE / "20-Learning" / subfolder
            return path, 2

    # Fallback to 40-Reference
    print(f"[WARN] Unknown folder '{folder_key}', using 40-Reference")
    return FOLDER_MAP["40-Reference"], 1


def _slug(text: str) -> str:
    for ch in r'/\:*?"<>|':
        text = text.replace(ch, "-")
    return text.strip().replace(" ", "_")[:80]


SKIP_DIRS = {"00-Inbox", ".git", "assets", "__pycache__"}

FRONTMATTER_RE = __import__("re").compile(r"^---\s*\n(.*?)\n---\s*\n", __import__("re").DOTALL)


def _frontmatter(meta: dict) -> str:
    for key in ("tags", "keywords"):
        if not isinstance(meta.get(key), list):
            meta[key] = []
    ordered = {k: meta.get(k) for k in [
        "title", "date", "updated", "type", "status", "technology",
        "tags", "keywords", "project", "certification",
        "target_folder", "confidence", "source",
    ]}
    return "---\n" + yaml.dump(ordered, allow_unicode=True, default_flow_style=False) + "---\n"


def _normalize_stem(filename: str) -> str:
    """Strip extension and trailing OneDrive collision suffix (_1, _2, …)."""
    import re
    stem = Path(filename).stem
    return re.sub(r"_\d+$", "", stem).strip()


def find_existing(source_filename: str) -> Path | None:
    """Search all .md files for one whose frontmatter source: matches source_filename.
    Ignores file extension and trailing numeric suffixes (_1, _2 …) added by OneDrive.
    Returns the Path if found, None otherwise."""
    incoming = _normalize_stem(source_filename)
    for md in BASE.rglob("*.md"):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        try:
            content = md.read_text(encoding="utf-8")
            m = FRONTMATTER_RE.match(content)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1)) or {}
            existing_source = fm.get("source", "")
            if existing_source and _normalize_stem(existing_source) == incoming:
                return md
        except Exception:
            continue
    return None


def update_note(
    existing_md: Path,
    markdown_body: str,
    source_path: str | Path | None = None,
) -> dict:
    """Update body of an existing note, preserve frontmatter, add updated: date."""
    content = existing_md.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(content)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
    else:
        fm = {}

    fm["updated"] = _date.today().isoformat()

    new_content = _frontmatter(fm) + "\n" + markdown_body + "\n"
    existing_md.write_text(new_content, encoding="utf-8")

    if source_path:
        PROCESSED.mkdir(parents=True, exist_ok=True)
        src = Path(source_path)
        shutil.move(str(src), PROCESSED / src.name)

    folder_key = fm.get("target_folder", "40-Reference")
    title      = fm.get("title", existing_md.stem)
    print(f"[UPDATE] -> {existing_md.relative_to(BASE)}")
    print(f"     folder: {folder_key} | updated: {fm['updated']}")

    return {"dest_md": str(existing_md), "folder": folder_key, "title": title,
            "date": fm.get("date", ""), "updated": True}


def file_note(
    text: str,
    markdown_body: str | None = None,
    meta: dict | None = None,
    source_path: str | Path | None = None,
) -> dict:
    """
    Classify text (or use supplied meta) and write a .md file into the right folder.
    Stores source filename in frontmatter so future exports can be matched for update.

    Returns:
        {"dest_md": str, "folder": str, "title": str, "date": str, "updated": bool}
    """
    if meta is None:
        meta = classify(text.strip())

    # Embed source filename so find_existing() can match it later
    if source_path:
        meta["source"] = Path(source_path).name

    folder_key = meta.get("target_folder") or "40-Reference"
    dest_dir, _ = _resolve_folder(folder_key)
    dest_dir.mkdir(parents=True, exist_ok=True)

    title     = meta.get("title") or "untitled"
    note_date = meta.get("date")  or _date.today().isoformat()
    slug      = _slug(title)
    dest_md   = dest_dir / (slug + ".md")
    # Avoid collision if title already exists
    counter = 1
    while dest_md.exists():
        dest_md = dest_dir / (f"{slug}_{counter}.md")
        counter += 1

    body = markdown_body if markdown_body is not None else text
    content = _frontmatter(meta) + "\n" + body + "\n"
    dest_md.write_text(content, encoding="utf-8")

    if source_path:
        PROCESSED.mkdir(parents=True, exist_ok=True)
        src = Path(source_path)
        shutil.move(str(src), PROCESSED / src.name)

    print(f"[CREATE] -> {dest_md.relative_to(BASE)}")
    print(f"     folder: {folder_key} | confidence: {meta.get('confidence')} | type: {meta.get('type')}")

    return {"dest_md": str(dest_md), "folder": folder_key, "title": title,
            "date": note_date, "updated": False}


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
