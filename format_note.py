#!/usr/bin/env python3
"""
format_note.py — Reformat a flat note body into rich Markdown using Claude.

Takes raw text (OCR or plain import) and produces a structured document with
headers, bold key terms, bullet lists, tables, and code blocks where appropriate.
Content is preserved 100% — only structure and formatting are added.

Usage:
    from format_note import format_body
    rich_md = format_body(raw_text, title="Note title", note_type="concept")

    python format_note.py path/to/note.md          # rewrites in place
    python format_note.py path/to/note.md --dry-run
"""

import os, sys, re, argparse
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

SYSTEM = """You are a knowledge management editor. Your job is to reformat raw text into rich, well-structured Markdown.

Rules:
- PRESERVE 100% of the original content — never remove or summarize information
- Write in the SAME LANGUAGE as the source text (Spanish or English)
- Use ## for main sections, ### for subsections — infer logical structure from content
- **Bold** key terms, concepts, and important facts
- Use bullet lists (- item) or numbered lists for enumerations and steps
- Use tables (| col | col |) for comparisons, options, or structured data with 2+ attributes
- Use `inline code` for commands, flags, field names, config values, code snippets
- Use > blockquotes for definitions, important notes, or warnings
- Use *italics* for examples, clarifications, or secondary context
- Do NOT add a title heading (it's already in frontmatter)
- Do NOT add introductory phrases like "Here is the formatted note:"
- Output ONLY the formatted Markdown body

Diagram and Mermaid rules (CRITICAL):
- If the text contains ```mermaid ... ``` blocks, preserve them VERBATIM — do not alter a single character inside the fence
- If the text contains nested bullet lists that represent mind maps or hierarchies, preserve the indentation exactly
- If the text contains markdown tables, preserve their column structure; you may align | separators for readability but never add or remove columns
- Do NOT convert Mermaid blocks into plain text descriptions — they must stay as code fences
- Do NOT "clean up" or "simplify" diagram-originated content — it was machine-generated from a visual and must be kept intact
- If diagram content appears mid-paragraph mixed with prose, keep the mermaid block as its own fenced section and surround it with appropriate prose context"""


def format_body(raw_text: str, title: str = "", note_type: str = "") -> str:
    """Return richly formatted Markdown for the given raw text."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    context = ""
    if title:
        context += f"Note title: {title}\n"
    if note_type:
        context += f"Note type: {note_type}\n"
    if context:
        context = f"<context>\n{context}</context>\n\n"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"{context}<raw_text>\n{raw_text}\n</raw_text>"
        }],
    )
    return message.content[0].text.strip()


def reformat_file(md_path: Path, dry_run: bool = False) -> bool:
    """Read a .md file, reformat its body, write back (or print if dry_run)."""
    import yaml
    FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    text = md_path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if m:
        fm_raw = m.group(0)
        fm = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():].strip()
    else:
        fm_raw = ""
        fm = {}
        body = text.strip()

    if not body:
        print(f"[SKIP] {md_path.name} — empty body")
        return False

    title = fm.get("title", md_path.stem)
    note_type = fm.get("type", "")

    print(f"Formatting: {title[:60]} ({len(body)} chars)...")
    rich = format_body(body, title=title, note_type=note_type)

    if dry_run:
        print("\n--- FORMATTED BODY (preview) ---")
        print(rich[:1000])
        print("--- (dry-run, not written) ---")
        return False

    new_content = fm_raw + "\n" + rich + "\n"
    md_path.write_text(new_content, encoding="utf-8")
    print(f"  OK — {len(rich)} chars written")
    return True


def main():
    ap = argparse.ArgumentParser(description="Reformat a KB note body into rich Markdown.")
    ap.add_argument("files", nargs="+", help=".md files to reformat")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = ap.parse_args()

    for f in args.files:
        reformat_file(Path(f), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
