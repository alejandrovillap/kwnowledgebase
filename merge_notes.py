#!/usr/bin/env python3
"""
merge_notes.py — Merge two or more notes into one using Claude API.

Claude reads all source bodies + frontmatters and produces a single,
well-structured merged note. Originals are moved to 50-Archive.

Usage:
    python merge_notes.py note_a.md note_b.md [note_c.md ...]
    python merge_notes.py note_a.md note_b.md --dry-run   (print merged, don't write)
"""

import re
import sys
import json
import shutil
import argparse
import os
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    raise ImportError("pip install PyYAML")

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE           = Path(__file__).parent
ARCHIVE_DIR    = BASE / "50-Archive"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

FOLDER_MAP = {
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    for ch in r'/\:*?"<>|':
        text = text.replace(ch, "-")
    return text.strip().replace(" ", "_")[:80]


def _read_note(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_str)."""
    content = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(content)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        body = content[m.end():].strip()
    else:
        fm = {}
        body = content.strip()
    return fm, body


def _write_frontmatter(meta: dict) -> str:
    for key in ("tags", "keywords"):
        if not isinstance(meta.get(key), list):
            meta[key] = []
    ordered = {k: meta.get(k) for k in [
        "title", "date", "updated", "type", "status", "technology",
        "tags", "keywords", "project", "certification",
        "target_folder", "confidence", "source",
    ]}
    return "---\n" + yaml.dump(ordered, allow_unicode=True, default_flow_style=False) + "---\n"


# ── Merge logic ───────────────────────────────────────────────────────────────

def _merge_frontmatters(fms: list[dict]) -> dict:
    """Combine frontmatters: union tags/keywords, earliest date, best title."""
    merged = {}

    # Title: longest / most descriptive
    titles = [fm.get("title", "") for fm in fms if fm.get("title")]
    merged["title"] = max(titles, key=len) if titles else "Merged Note"

    # Date: earliest
    dates = [str(fm.get("date", "")) for fm in fms if fm.get("date")]
    merged["date"] = min(dates) if dates else date.today().isoformat()

    merged["updated"] = date.today().isoformat()

    # Type: most specific (lesson-learned > concept > resume > reference)
    type_rank = {"lesson-learned": 5, "case": 4, "concept": 3,
                 "idea": 3, "resume": 2, "reference": 1, "journal": 0}
    types = [fm.get("type", "") for fm in fms if fm.get("type")]
    merged["type"] = max(types, key=lambda t: type_rank.get(t, 0)) if types else ""

    # Status: most advanced (active > to-review > archived)
    status_rank = {"active": 2, "to-review": 1, "archived": 0}
    statuses = [fm.get("status", "") for fm in fms if fm.get("status")]
    merged["status"] = max(statuses, key=lambda s: status_rank.get(s, 0)) if statuses else "active"

    # Union of tags and keywords
    all_tags = []
    for fm in fms:
        all_tags.extend(fm.get("tags") or [])
    merged["tags"] = sorted(set(all_tags))

    all_kw = []
    for fm in fms:
        all_kw.extend(fm.get("keywords") or [])
    merged["keywords"] = sorted(set(all_kw))

    # Take first non-empty for these
    for key in ("technology", "project", "certification", "target_folder", "confidence"):
        merged[key] = next((fm.get(key) for fm in fms if fm.get(key)), None)

    # Source: list all merged sources
    sources = [fm.get("source", "") for fm in fms if fm.get("source")]
    merged["source"] = ", ".join(sources) if sources else None

    return merged


def _call_claude_merge(notes_data: list[dict]) -> str:
    """Ask Claude to merge N note bodies into one cohesive document."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    notes_xml = ""
    for i, n in enumerate(notes_data, 1):
        notes_xml += f"\n<note_{i}>\n<title>{n['title']}</title>\n<body>\n{n['body']}\n</body>\n</note_{i}>\n"

    prompt = f"""You are merging {len(notes_data)} knowledge base notes that cover the same topic into one single, comprehensive note.

{notes_xml}

Rules:
- Write in the same language as the source notes (Spanish or English as appropriate)
- Keep ALL unique information from every note — do not lose content
- Eliminate exact duplications of facts/sentences
- Organize with clear Markdown headers (##, ###)
- Start with a brief one-paragraph summary of the topic
- Merge related sections together logically
- Keep code blocks, tables, and lists intact
- Do NOT add a title heading at the top (it's in the frontmatter)
- Output only the merged Markdown body, no preamble"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ── Main merge ────────────────────────────────────────────────────────────────

def merge(paths: list[Path], dry_run: bool = False) -> dict:
    """
    Merge notes at given paths into one. Archive originals.
    Returns {"dest": str, "archived": [str], "title": str}
    """
    paths = [Path(p).resolve() for p in paths]
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Not found: {p}")

    print(f"\nFusionando {len(paths)} notas:")
    for p in paths:
        print(f"  - {p.relative_to(BASE)}")

    # Read all notes
    notes_data = []
    fms = []
    for p in paths:
        fm, body = _read_note(p)
        fms.append(fm)
        notes_data.append({"title": fm.get("title", p.stem), "body": body})

    # Merge frontmatters
    merged_fm = _merge_frontmatters(fms)
    folder_key = merged_fm.get("target_folder") or _infer_folder(paths[0])
    merged_fm["target_folder"] = folder_key

    print(f"  -> Titulo: {merged_fm['title']}")
    print(f"  -> Carpeta: {folder_key}")
    print(f"  -> Llamando Claude API para fusionar contenido...")

    # Merge bodies via Claude
    merged_body = _call_claude_merge(notes_data)

    if dry_run:
        print("\n--- MERGED FRONTMATTER ---")
        print(yaml.dump(merged_fm, allow_unicode=True))
        print("--- MERGED BODY (primeros 1000c) ---")
        print(merged_body[:1000])
        print("--- (dry-run, no se escribio nada) ---")
        return {"dest": None, "archived": [], "title": merged_fm["title"]}

    # Write merged note
    dest_dir = FOLDER_MAP.get(folder_key, FOLDER_MAP["40-Reference"])
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(merged_fm["title"])
    dest_path = dest_dir / f"{merged_fm['date']}_{slug}_merged.md"
    content = _write_frontmatter(merged_fm) + "\n" + merged_body + "\n"
    dest_path.write_text(content, encoding="utf-8")
    print(f"  [OK] Nota fusionada -> {dest_path.relative_to(BASE)}")

    # Archive originals
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archived = []
    for p in paths:
        archive_dest = ARCHIVE_DIR / p.name
        # avoid collision
        if archive_dest.exists():
            archive_dest = ARCHIVE_DIR / (p.stem + "_archived" + p.suffix)
        shutil.move(str(p), archive_dest)
        archived.append(str(archive_dest.relative_to(BASE)))
        print(f"  [ARCHIVE] {p.relative_to(BASE)} -> {archive_dest.relative_to(BASE)}")

    # Rebuild indexes + dashboard
    print("  Reconstruyendo indice y dashboard...")
    from build_index import build_all
    build_all()
    from build_dashboard import build_dashboard
    build_dashboard()
    print("  [OK] Indice y dashboard actualizados")

    return {"dest": str(dest_path.relative_to(BASE)), "archived": archived, "title": merged_fm["title"]}


def _infer_folder(path: Path) -> str:
    """Infer target_folder from file path."""
    try:
        rel = path.relative_to(BASE)
        parts = rel.parts
        if len(parts) >= 3:
            return "/".join(parts[:-1])
        elif len(parts) == 2:
            return parts[0]
    except Exception:
        pass
    return "40-Reference"


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Merge knowledge base notes using Claude.")
    ap.add_argument("notes", nargs="+", help="Paths to .md files to merge")
    ap.add_argument("--dry-run", action="store_true", help="Preview merge without writing")
    args = ap.parse_args()

    paths = [BASE / p if not Path(p).is_absolute() else Path(p) for p in args.notes]
    result = merge(paths, dry_run=args.dry_run)

    if result["dest"]:
        print(f"\nFusion completada: {result['title']}")
        print(f"  Nota nueva: {result['dest']}")
        print(f"  Archivadas: {len(result['archived'])} notas originales")


if __name__ == "__main__":
    main()
