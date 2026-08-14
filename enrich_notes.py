#!/usr/bin/env python3
"""
enrich_notes.py — Fix mojibake encoding AND reformat notes with rich Markdown.

Usage:
    python enrich_notes.py                   # auto-selects notes with source: gmail-draft-*
    python enrich_notes.py path/to/note.md   # single file
    python enrich_notes.py --all-ocr         # also include OCR-sourced notes
    python enrich_notes.py --dry-run         # preview without writing

Steps per note:
    1. Read file (UTF-8)
    2. Fix mojibake (Windows-1252 bytes misread as UTF-8 code points)
    3. Call Claude to reformat body with markdown structure
    4. Write back
"""

import re, os, sys, argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("pip install PyYAML")

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

BASE = Path(__file__).parent
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# ── Encoding fix ──────────────────────────────────────────────────────────────

def fix_mojibake(text: str) -> str:
    """
    Attempt to fix Windows-1252 bytes that were decoded as Latin-1 then stored
    as if they were UTF-8 code points (classic mojibake pattern).
    Falls back to original if the round-trip fails.
    """
    try:
        fixed = text.encode("latin-1").decode("utf-8")
        if fixed != text:
            return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Also try cp1252 → utf-8 for Windows smart-quotes edge cases
    try:
        fixed = text.encode("cp1252").decode("utf-8")
        if fixed != text:
            return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    return text


def fix_file_encoding(text: str) -> str:
    """Fix mojibake in both frontmatter title and body."""
    m = FM_RE.match(text)
    if m:
        fm_raw = m.group(0)
        body   = text[m.end():]
        return fix_mojibake(fm_raw) + fix_mojibake(body)
    return fix_mojibake(text)


# ── Format ────────────────────────────────────────────────────────────────────

FORMAT_SYSTEM = """You are a knowledge management editor. Reformat the raw text into rich, well-structured Markdown.

Rules:
- PRESERVE 100% of the original content — never remove, summarize, or invent information
- Write in the SAME LANGUAGE as the source (Spanish or English)
- Use ## for main sections, ### for subsections — infer logical structure from content
- **Bold** key terms, concepts, acronyms, and important facts on first meaningful use
- Use bullet lists (- item) or numbered lists for enumerations, steps, phases
- Use tables (| col | col |) for comparisons or structured multi-attribute data
- Use `inline code` for commands, flags, field names, config values
- Use > blockquote for definitions, warnings, or key takeaways
- Use *italics* for examples, analogies, or secondary context
- Remove duplicate blank lines; clean up stray artifact characters (â€™ → ', â†' → →)
- Do NOT add a title heading (it's already in frontmatter)
- Do NOT output introductory phrases — output ONLY the formatted Markdown body"""


def format_body(raw_text: str, title: str = "", note_type: str = "") -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    ctx = ""
    if title:
        ctx += f"Note title: {title}\n"
    if note_type:
        ctx += f"Note type: {note_type}\n"
    if ctx:
        ctx = f"<context>\n{ctx}</context>\n\n"

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=FORMAT_SYSTEM,
        messages=[{"role": "user", "content": f"{ctx}<raw_text>\n{raw_text}\n</raw_text>"}],
    )
    return msg.content[0].text.strip()


# ── Per-file pipeline ─────────────────────────────────────────────────────────

def enrich_file(path: Path, dry_run: bool = False) -> bool:
    raw = path.read_text(encoding="utf-8-sig")  # strips BOM

    # Step 1: fix encoding
    fixed = fix_file_encoding(raw)
    encoding_changed = fixed != raw

    m = FM_RE.match(fixed)
    if m:
        fm_raw  = m.group(0)
        fm      = yaml.safe_load(m.group(1)) or {}
        body    = fixed[m.end():].strip()
    else:
        fm_raw  = ""
        fm      = {}
        body    = fixed.strip()

    if not body:
        print(f"  [SKIP] {path.name} — empty body")
        return False

    title     = fm.get("title", path.stem)
    note_type = fm.get("type", "")

    print(f"\n  [{path.parent.name}] {title[:60]}")
    print(f"    Encoding fix: {'yes' if encoding_changed else 'no'}  |  body: {len(body)} chars")

    # Step 2: reformat
    rich = format_body(body, title=title, note_type=note_type)
    print(f"    Formatted: {len(rich)} chars")

    if dry_run:
        print("    --- PREVIEW (first 500 chars) ---")
        print(rich[:500])
        print("    --- (dry-run, not written) ---")
        return False

    new_content = fm_raw + "\n" + rich + "\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"    OK — written")
    return True


# ── File discovery ────────────────────────────────────────────────────────────

def discover_notes(also_ocr: bool = False) -> list[Path]:
    targets = []
    for md in BASE.rglob("*.md"):
        if md.name == "_index.md":
            continue
        if "50-Archive" in md.parts:
            continue

        try:
            text = md.read_text(encoding="utf-8-sig")  # strips BOM if present
        except Exception:
            continue

        m = FM_RE.match(text)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        source = str(fm.get("source") or "")

        if "gmail-draft" in source:
            targets.append(md)
        elif also_ocr and source.endswith(".pdf"):
            targets.append(md)

    return sorted(targets)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Enrich KB notes: fix encoding + add markdown formatting.")
    ap.add_argument("files", nargs="*", help="Specific .md files to process")
    ap.add_argument("--all-ocr",  action="store_true", help="Also process PDF-OCR sourced notes")
    ap.add_argument("--dry-run",  action="store_true", help="Preview without writing")
    args = ap.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = discover_notes(also_ocr=args.all_ocr)

    if not paths:
        print("No notes found to process.")
        return

    print(f"Enriching {len(paths)} note(s)...")
    ok = 0
    for p in paths:
        if enrich_file(p, dry_run=args.dry_run):
            ok += 1

    if not args.dry_run:
        print(f"\nDone — {ok}/{len(paths)} notes enriched.")

        # Rebuild index + dashboard
        print("Rebuilding index and dashboard...")
        sys.path.insert(0, str(BASE))
        from build_index import build_all
        build_all()
        from build_dashboard import build_dashboard
        build_dashboard()
        print("Done.")


if __name__ == "__main__":
    main()
