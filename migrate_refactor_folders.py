#!/usr/bin/env python3
"""
migrate_refactor_folders.py — Reassign notes from deprecated folders.

Deprecated: 40-Reference, 50-Archive, 20-Learning/Certifications
Strategy:
  1. Read frontmatter (certification, tags, keywords, title, body)
  2. Heuristic match → no API call
  3. If ambiguous → call classify_note.classify() with the note content

Usage:
    python migrate_refactor_folders.py --dry-run   # preview only
    python migrate_refactor_folders.py             # apply
"""

import re
import shutil
import argparse
from pathlib import Path

import yaml

BASE = Path(__file__).parent

DEPRECATED = [
    BASE / "40-Reference",
    BASE / "50-Archive",
    BASE / "20-Learning" / "Certifications",
]

# Micro-folders created by the old NEW SUBFOLDER RULE — map them to canonical folders
MICRO_FOLDER_MAP = {
    "20-Learning/Coaching-ICF":   "20-Learning/Coaching",
    "20-Learning/Coaching-Metho": "20-Learning/Coaching",
    "20-Learning/Coaching-Frame": "20-Learning/Coaching",
    "20-Learning/Coaching-Conve": "20-Learning/Coaching",
    "20-Learning/RPA-Platform":   "20-Learning/RPA",
    "20-Learning/RPA-Tools":      "20-Learning/RPA",
    "20-Learning/RPA-Frameworks": "20-Learning/RPA",
    "20-Learning/Markdown":       "20-Learning",
    "20-Learning/Frameworks":     "20-Learning",
    "20-Learning/Prompt-Engineering": "20-Learning",
    "20-Learning/Prompt-En":      "20-Learning",
}

# Folders that STAY (used for fallback)
FALLBACK_FOLDER = "20-Learning"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _read_note(md: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text)."""
    text = md.read_text(encoding="utf-8-sig")
    m = FRONTMATTER_RE.match(text)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
    else:
        fm, body = {}, text
    return fm, body


def _heuristic(fm: dict, body: str) -> str | None:
    """Return a folder key from metadata alone, or None if ambiguous."""
    cert   = str(fm.get("certification") or "").lower()
    title  = str(fm.get("title") or "").lower()
    tags   = " ".join(str(t) for t in (fm.get("tags") or [])).lower()
    kws    = " ".join(str(k) for k in (fm.get("keywords") or [])).lower()
    sample = (title + " " + tags + " " + kws + " " + body[:800]).lower()

    # PMI-ACP
    if any(kw in sample for kw in [
        "pmi-acp", "pmi acp", "agile certified", "agile practitioner",
        "servant leader", "agile mindset", "retrospective", "scrum master",
        "kanban", "scrumban", "extreme programming", "xp ", " xp\n",
        "agile manifesto", "agile principle", "lean agile", "agile coach",
    ]) or "pmi-acp" in cert or "pmi" in cert:
        return "20-Learning/PMI-ACP"

    # CCA-F
    if any(kw in sample for kw in [
        "cca-f", "ccaf", "claude code", "mcp server", "agentic architect",
        "anthropic", "claude sonnet", "claude opus", "model context protocol",
    ]) or "cca" in cert or "cca-f" in cert:
        return "20-Learning/CCA-F"

    # Gemini Enterprise
    if any(kw in sample for kw in [
        "gemini enterprise", "google workspace", "gemini for workspace",
        "dlp", "data loss prevention", "google ai", "vertex ai",
    ]) or "gemini" in cert:
        return "20-Learning/Gemini-Enterprise"

    # Cognitive PM AI
    if any(kw in sample for kw in [
        "cognitive pm", "pm ai", "project management ai", "cognición",
        "cognitive load", "mental model", "proyecto cognitivo",
    ]) or "cognitive" in cert or "pm-ai" in cert:
        return "20-Learning/Cognitive-PM-AI"

    # Antigravity
    if any(kw in sample for kw in [
        "antigravity", "soul framework", "agentic editor",
    ]) or "antigravity" in cert:
        return "20-Learning/Antigravity"

    # Journal
    if any(kw in sample for kw in [
        "diario", "reflexión personal", "reflexion personal",
        "coaching de vida", "personal development diary",
    ]) or fm.get("type") == "journal":
        return "Journal"

    # 10-Work
    if any(kw in sample for kw in [
        "client deliverable", "consulting engagement", "meeting with client",
        "proposal for", "stakeholder meeting",
    ]) or fm.get("type") in ("meeting", "resume"):
        return "10-Work"

    return None  # ambiguous → call classifier


def _classify_via_api(content: str) -> str:
    """Use Claude to classify the note. Returns folder key."""
    from classify_note import classify
    meta = classify(content)
    return meta.get("target_folder") or FALLBACK_FOLDER


def _new_path(folder_key: str, stem: str) -> Path:
    """Resolve destination path, handling collisions."""
    from file_note import _resolve_folder
    dest_dir, _ = _resolve_folder(folder_key)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (stem + ".md")
    counter = 1
    while dest.exists():
        dest = dest_dir / (f"{stem}_{counter}.md")
        counter += 1
    return dest


def migrate(dry_run: bool = False):
    api_calls = 0
    moved = 0
    skipped = 0

    for src_dir in DEPRECATED:
        if not src_dir.exists():
            print(f"[SKIP] {src_dir.name} — carpeta no existe en esta máquina")
            continue

        mds = sorted(src_dir.rglob("*.md"))
        print(f"\n{'='*60}")
        print(f"Procesando {src_dir.relative_to(BASE)}  ({len(mds)} notas)")
        print(f"{'='*60}")

        for md in mds:
            if md.name.startswith("_"):
                skipped += 1
                continue

            fm, body = _read_note(md)
            full_content = md.read_text(encoding="utf-8-sig")

            folder_key = _heuristic(fm, body)
            method = "heuristic"

            if folder_key is None:
                print(f"  [API]  {md.name} — heurística no determinante, llamando clasificador…")
                folder_key = _classify_via_api(full_content)
                method = "API"
                api_calls += 1

            dest = _new_path(folder_key, md.stem)

            print(f"  [{method.upper():<9}] {md.name}")
            print(f"             → {dest.relative_to(BASE)}")

            if not dry_run:
                # Update frontmatter target_folder
                new_fm = dict(fm)
                new_fm["target_folder"] = folder_key
                import io
                fm_yaml = yaml.dump(new_fm, allow_unicode=True, default_flow_style=False)
                new_content = f"---\n{fm_yaml}---\n{body}"
                dest.write_text(new_content, encoding="utf-8")
                # Remove original (don't use shutil.move — we already wrote dest)
                md.unlink()

            moved += 1

        # Remove directory if empty after migration
        if not dry_run and src_dir.exists():
            remaining = list(src_dir.rglob("*.md"))
            if not remaining:
                shutil.rmtree(src_dir, ignore_errors=True)
                print(f"\n  [DELETE] Carpeta {src_dir.name} eliminada (vacía)")
            else:
                print(f"\n  [WARN]   {src_dir.name} aún tiene {len(remaining)} archivos — revisar manualmente")

    # ── Consolidate micro-folders ──────────────────────────────────
    print(f"\n{'='*60}")
    print("Consolidando micro-carpetas de 20-Learning…")
    print(f"{'='*60}")

    for micro_key, canonical_key in MICRO_FOLDER_MAP.items():
        micro_path = BASE / Path(micro_key.replace("/", "/"))
        if not micro_path.exists():
            continue

        mds = sorted(micro_path.rglob("*.md"))
        if not mds:
            if not dry_run:
                shutil.rmtree(micro_path, ignore_errors=True)
            continue

        print(f"\n  {micro_key}  ({len(mds)} notas)  →  {canonical_key}")
        for md in mds:
            fm, body = _read_note(md)
            dest = _new_path(canonical_key, md.stem)
            print(f"    {md.name} → {dest.relative_to(BASE)}")
            if not dry_run:
                new_fm = dict(fm)
                new_fm["target_folder"] = canonical_key
                fm_yaml = yaml.dump(new_fm, allow_unicode=True, default_flow_style=False)
                new_content = f"---\n{fm_yaml}---\n{body}"
                dest.write_text(new_content, encoding="utf-8")
                md.unlink()
            moved += 1

        if not dry_run and micro_path.exists():
            remaining = list(micro_path.rglob("*.md"))
            if not remaining:
                shutil.rmtree(micro_path, ignore_errors=True)
                print(f"    [DELETE] {micro_key} eliminada (vacía)")

    # Also scan for any other unknown 20-Learning/* subfolders not in MICRO_FOLDER_MAP
    learning_path = BASE / "20-Learning"
    known_sub = {
        "PMI-ACP", "CCA-F", "Cognitive-PM-AI", "Antigravity",
        "Gemini-Enterprise", "RPA", "Coaching",
    }
    if learning_path.exists():
        for sub in sorted(learning_path.iterdir()):
            if sub.is_dir() and sub.name not in known_sub:
                mds = sorted(sub.rglob("*.md"))
                if not mds:
                    if not dry_run:
                        shutil.rmtree(sub, ignore_errors=True)
                    continue
                print(f"\n  [UNKNOWN] 20-Learning/{sub.name}  ({len(mds)} notas) → 20-Learning")
                for md in mds:
                    fm, body = _read_note(md)
                    dest = _new_path("20-Learning", md.stem)
                    print(f"    {md.name} → {dest.relative_to(BASE)}")
                    if not dry_run:
                        new_fm = dict(fm)
                        new_fm["target_folder"] = "20-Learning"
                        fm_yaml = yaml.dump(new_fm, allow_unicode=True, default_flow_style=False)
                        new_content = f"---\n{fm_yaml}---\n{body}"
                        dest.write_text(new_content, encoding="utf-8")
                        md.unlink()
                    moved += 1
                if not dry_run and sub.exists():
                    if not list(sub.rglob("*.md")):
                        shutil.rmtree(sub, ignore_errors=True)
                        print(f"    [DELETE] 20-Learning/{sub.name} eliminada (vacía)")

    print(f"\n{'='*60}")
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"{prefix}Completado: {moved} movidas, {skipped} omitidas, {api_calls} llamadas al API")
    if not dry_run:
        print("\nSiguiente paso: python3 build_dashboard.py && sudo systemctl restart kb")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    migrate(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
