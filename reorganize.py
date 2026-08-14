#!/usr/bin/env python3
"""
reorganize.py — Analyze notes in a folder and move misclassified ones intelligently.

Claude reads all note titles + excerpts, proposes a new folder taxonomy,
and moves the files (updating frontmatter's target_folder field).

Usage:
    python reorganize.py                        # analyze 10-Work, preview only
    python reorganize.py --execute              # actually move files
    python reorganize.py --folder 50-Archive    # analyze a different folder
    python reorganize.py --all                  # analyze all top-level folders
"""

import json
import argparse
import shutil
from pathlib import Path
from datetime import date

import yaml
import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE           = Path(__file__).parent
FRONTMATTER_RE = __import__("re").compile(r"^---\s*\n(.*?)\n---\s*\n", __import__("re").DOTALL)
SKIP_NAMES     = {"_index.md"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def read_notes(folder_path: Path) -> list[dict]:
    notes = []
    for md in sorted(folder_path.glob("*.md")):
        if md.name in SKIP_NAMES or md.name.startswith("_"):
            continue
        try:
            text = md.read_text(encoding="utf-8-sig")
            m    = FRONTMATTER_RE.match(text)
            fm   = yaml.safe_load(m.group(1)) if m else {}
            fm   = fm or {}
            body = text[m.end():].strip() if m else text.strip()
            notes.append({
                "file":           md.name,
                "path":           md,
                "title":          fm.get("title") or md.stem,
                "tags":           fm.get("tags") or [],
                "type":           fm.get("type") or "",
                "current_folder": fm.get("target_folder") or "",
                "excerpt":        body[:250],
                "fm":             fm,
            })
        except Exception as e:
            print(f"[WARN] Skipping {md.name}: {e}")
    return notes


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        end   = -1 if lines[-1].strip() == "```" else len(lines)
        text  = "\n".join(lines[1:end]).strip()
    return text


def propose_folders(notes: list[dict]) -> dict[str, str]:
    """Ask Claude to classify all notes and return {filename: new_folder}."""
    lines = []
    for n in notes:
        tags = ", ".join(n["tags"]) if n["tags"] else "—"
        lines.append(
            f'  "{n["file"]}"\n'
            f'    title: {n["title"]}\n'
            f'    tags: {tags}  type: {n["type"]}\n'
            f'    excerpt: {n["excerpt"][:180]}'
        )
    notes_block = "\n\n".join(lines)

    system = """You are a knowledge management expert organizing a personal learning vault.

FOLDER RULES:
- "10-Work": ONLY active work outputs — client projects, deliverables, meeting notes with real clients, proposals, consulting engagements. NOT studying, NOT learning content.
- "20-Learning/CCA-F": Anthropic CCA-F / Claude Code / MCP / agentic architecture certification.
- "20-Learning/Cognitive-PM-AI": Cognitive PM AI course — cognition + AI in project management.
- "20-Learning/Antigravity": Antigravity Platform — agentic editor, soul framework.
- "20-Learning/Gemini-Enterprise": Google Gemini Enterprise certification.
- "20-Learning/Certifications": other certifications without a dedicated subfolder.
- "20-Learning": general learning without a dedicated subfolder.
- "40-Reference": reference material, glossaries, lookup tables.
- "50-Archive": outdated or superseded content.
- "Journal": personal reflections, emotions, personal development diary.

DYNAMIC SUBFOLDER RULE: You MAY create NEW subfolders under 20-Learning when 3+ notes share a clear, specific topic. Examples: "20-Learning/PMI-ACP" for PMI-ACP agile exam prep, "20-Learning/AI-SDLC" for AI in software development lifecycle, "20-Learning/Coaching" for coaching methodology, "20-Learning/RPA" for robotic process automation study.

Return ONLY valid JSON: {"filename.md": "target_folder", ...}
Include every file. No preamble, no explanation."""

    user = f"""Classify each note below into the correct folder. Create new subfolders where warranted.

Notes to classify:
{notes_block}

Return JSON mapping each filename to its target folder."""

    client = anthropic.Anthropic()
    msg    = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = _strip_fences(msg.content[0].text)
    return json.loads(raw)


# ── Execution ─────────────────────────────────────────────────────────────────

def _resolve_dest(folder_key: str) -> Path:
    """Return the absolute path for a folder key, creating subfolders as needed."""
    top_level = {
        "10-Work", "20-Learning", "40-Reference", "50-Archive", "Journal",
    }
    if folder_key in top_level:
        return BASE / folder_key
    if folder_key.startswith("20-Learning/"):
        parts = folder_key.split("/")
        if len(parts) == 2 and parts[1]:
            return BASE / "20-Learning" / parts[1]
    print(f"[WARN] Unknown folder '{folder_key}', using 40-Reference")
    return BASE / "40-Reference"


def _update_frontmatter_folder(md_path: Path, new_folder: str) -> None:
    text = md_path.read_text(encoding="utf-8-sig")
    m    = FRONTMATTER_RE.match(text)
    if not m:
        return
    fm   = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    fm["target_folder"] = new_folder
    fm["updated"]       = date.today().isoformat()
    # Preserve key order for readability
    ordered_keys = ["title", "date", "updated", "type", "status", "technology",
                    "tags", "keywords", "project", "certification",
                    "target_folder", "confidence", "source"]
    ordered = {k: fm[k] for k in ordered_keys if k in fm}
    ordered.update({k: v for k, v in fm.items() if k not in ordered})
    new_text = "---\n" + yaml.dump(ordered, allow_unicode=True, default_flow_style=False) + "---\n" + body
    md_path.write_text(new_text, encoding="utf-8")


def execute_moves(notes: list[dict], proposals: dict[str, str], dry_run: bool) -> None:
    moves = []
    stays = []
    new_folders = set()

    for n in notes:
        new_folder = proposals.get(n["file"])
        if not new_folder:
            print(f"[SKIP] No proposal for {n['file']}")
            continue
        current = n["current_folder"]
        if new_folder == current:
            stays.append(n["file"])
            continue
        dest_dir = _resolve_dest(new_folder)
        moves.append((n, new_folder, dest_dir))
        if new_folder.startswith("20-Learning/") and new_folder not in {
            "20-Learning/CCA-F", "20-Learning/Certifications",
            "20-Learning/Cognitive-PM-AI", "20-Learning/Antigravity",
            "20-Learning/Gemini-Enterprise",
        }:
            new_folders.add(new_folder)

    # Summary
    print(f"\n{'─'*60}")
    print(f"  Notas analizadas : {len(notes)}")
    print(f"  Sin cambios      : {len(stays)}")
    print(f"  A mover          : {len(moves)}")
    if new_folders:
        print(f"  Nuevas carpetas  : {', '.join(sorted(new_folders))}")
    print(f"{'─'*60}\n")

    if not moves:
        print("Nada que mover.")
        return

    # Group by destination for readability
    by_dest: dict[str, list] = {}
    for n, new_folder, dest_dir in moves:
        by_dest.setdefault(new_folder, []).append((n, dest_dir))

    for folder, items in sorted(by_dest.items()):
        print(f"\n  📁 {folder}  ({len(items)} notas)")
        for n, _ in items:
            src_folder = n["current_folder"] or n["path"].parent.name
            print(f"     ← {src_folder} / {n['title'][:60]}")

    if dry_run:
        print("\n[DRY RUN] Nada fue movido. Agrega --execute para aplicar.")
        return

    moved = 0
    for n, new_folder, dest_dir in moves:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / n["path"].name
        # Avoid overwriting
        if dest.exists() and dest != n["path"]:
            stem   = n["path"].stem
            suffix = n["path"].suffix
            dest   = dest_dir / f"{stem}_moved{suffix}"

        shutil.move(str(n["path"]), dest)
        _update_frontmatter_folder(dest, new_folder)
        print(f"  [MOVED] {n['file']} → {new_folder}/")
        moved += 1

    print(f"\n✓ {moved} notas movidas.")
    print("  Recuerda correr:  python build_dashboard.py && python build_embeddings.py")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Reorganize misclassified KB notes.")
    ap.add_argument("--folder",   default="10-Work",
                    help="Folder to analyze (relative to KB root, default: 10-Work)")
    ap.add_argument("--all",      action="store_true",
                    help="Analyze all top-level folders (except Archive and Journal)")
    ap.add_argument("--execute",  action="store_true",
                    help="Prompt to apply moves (default is dry-run preview)")
    args = ap.parse_args()

    if args.all:
        folders = ["10-Work", "20-Learning", "40-Reference"]
    else:
        folders = [args.folder]

    all_notes = []
    for folder_name in folders:
        fp = BASE / folder_name
        if not fp.is_dir():
            print(f"[WARN] Folder not found: {fp}")
            continue
        notes = read_notes(fp)
        print(f"[READ] {folder_name}: {len(notes)} notas")
        all_notes.extend(notes)

    if not all_notes:
        print("No hay notas para analizar.")
        return

    print(f"\nAnalizando {len(all_notes)} notas con Claude…")
    proposals = propose_folders(all_notes)
    print(f"Propuestas recibidas: {len(proposals)}")

    execute_moves(all_notes, proposals, dry_run=not args.execute)


if __name__ == "__main__":
    main()
