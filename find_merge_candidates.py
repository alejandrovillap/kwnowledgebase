#!/usr/bin/env python3
"""
find_merge_candidates.py — Find notes that likely cover the same topic.

Strategy:
  1. Tag-overlap: pairs sharing 3+ tags
  2. Title similarity: fuzzy match on normalized title
  3. Same folder bonus

Usage:
    python find_merge_candidates.py          # print candidates to stdout
    python find_merge_candidates.py --json   # output as JSON for other tools
"""

import re
import json
import argparse
from pathlib import Path
from itertools import combinations

try:
    import yaml
except ImportError:
    raise ImportError("pip install PyYAML")

BASE = Path(__file__).parent
SKIP_DIRS  = {"00-Inbox", ".git", "assets", "__pycache__"}
SKIP_FILES = {"_index.md", "dashboard.html"}
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _load_notes():
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
            body = content[m.end():].strip() if m else content.strip()
        except Exception:
            continue

        rel = md.relative_to(BASE)
        parts = rel.parts
        folder = "/".join(parts[:-1]) if len(parts) > 1 else ""

        notes.append({
            "path":   md,
            "rel":    str(rel),
            "folder": folder,
            "title":  fm.get("title") or md.stem,
            "date":   str(fm.get("date", "")),
            "tags":   set(fm.get("tags") or []),
            "type":   fm.get("type", ""),
            "body":   body,
            "chars":  len(body),
        })
    return notes


def _norm_title(t: str) -> str:
    """Normalize title for fuzzy comparison."""
    t = t.lower()
    # strip subtitles after — / : / -
    for sep in [" — ", " - ", ": ", " | "]:
        if sep in t:
            t = t.split(sep)[0]
    # strip common suffixes like "lo que yo entiendo", "reflexion", "overview"
    for suffix in ["lo que yo entiendo", "reflexion", "overview", "summary",
                   "cheat sheet", "quick reference", "guia", "guía"]:
        t = t.replace(suffix, "")
    # keep only alphanum + spaces
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _title_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity between two normalized titles."""
    wa = set(_norm_title(a).split())
    wb = set(_norm_title(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _tag_overlap(a: set, b: set) -> int:
    return len(a & b)


def find_candidates(notes: list[dict], min_tags: int = 3, min_title_sim: float = 0.4) -> list[dict]:
    """Return scored pairs that are candidates for merging."""
    candidates = []
    for a, b in combinations(notes, 2):
        tag_shared = _tag_overlap(a["tags"], b["tags"])
        title_sim  = _title_similarity(a["title"], b["title"])
        same_folder = a["folder"] == b["folder"]

        score = tag_shared * 2 + title_sim * 5 + (2 if same_folder else 0)

        if tag_shared >= min_tags or title_sim >= min_title_sim:
            candidates.append({
                "score":       round(score, 2),
                "tag_overlap": tag_shared,
                "title_sim":   round(title_sim, 2),
                "same_folder": same_folder,
                "a": {
                    "rel":    a["rel"],
                    "title":  a["title"],
                    "folder": a["folder"],
                    "date":   a["date"],
                    "tags":   sorted(a["tags"]),
                    "chars":  a["chars"],
                },
                "b": {
                    "rel":    b["rel"],
                    "title":  b["title"],
                    "folder": b["folder"],
                    "date":   b["date"],
                    "tags":   sorted(b["tags"]),
                    "chars":  b["chars"],
                },
                "shared_tags": sorted(a["tags"] & b["tags"]),
            })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="Output as JSON")
    ap.add_argument("--min-tags", type=int, default=3)
    ap.add_argument("--min-title", type=float, default=0.4)
    ap.add_argument("--top", type=int, default=30, help="Show top N candidates")
    args = ap.parse_args()

    notes = _load_notes()
    candidates = find_candidates(notes, min_tags=args.min_tags, min_title_sim=args.min_title)

    if args.json:
        print(json.dumps(candidates[:args.top], ensure_ascii=False, indent=2))
        return

    print(f"Escaneando {len(notes)} notas — {len(candidates)} candidatos de fusion encontrados\n")
    print(f"{'#':>3}  {'Score':>5}  {'Tags':>4}  {'Sim':>4}  {'Folder?':>6}  Notas")
    print("-" * 90)
    for i, c in enumerate(candidates[:args.top], 1):
        same = "SI" if c["same_folder"] else "no"
        print(f"{i:>3}  {c['score']:>5.1f}  {c['tag_overlap']:>4}  {c['title_sim']:>4.2f}  {same:>6}")
        print(f"     A: [{c['a']['folder']}] {c['a']['title']} ({c['a']['chars']}c)")
        print(f"     B: [{c['b']['folder']}] {c['b']['title']} ({c['b']['chars']}c)")
        print(f"     Tags compartidos: {', '.join(c['shared_tags'][:8])}")
        print()


if __name__ == "__main__":
    main()
