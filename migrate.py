#!/usr/bin/env python3
"""
migrate.py — Scan all .md files in the KnowledgeBase and add any missing frontmatter
             fields without overwriting existing values.

Usage:
    python migrate.py              # dry-run (shows what would change)
    python migrate.py --apply      # actually write changes
    python migrate.py --apply --path 10-Work/  # scope to a subfolder
"""

import re
import argparse
from pathlib import Path
from datetime import date

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install PyYAML")

BASE = Path(__file__).parent

# Canonical schema with safe defaults
SCHEMA: dict = {
    "title":         "",
    "date":          "",
    "type":          "idea",
    "status":        "to-review",
    "technology":    None,
    "tags":          [],
    "keywords":      [],
    "project":       "",
    "certification": "",
    "target_folder": "",
    "confidence":    "medium",
}

# Folders that are not part of the note corpus
SKIP_DIRS = {"00-Inbox", ".git", "assets", "__pycache__"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse(content: str) -> tuple[dict | None, str]:
    """Return (frontmatter_dict | None, body_after_fence)."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        body = content[m.end():]
        return fm, body
    except yaml.YAMLError:
        return None, content


def _merge(existing: dict) -> tuple[dict, list[str]]:
    """Add missing keys from SCHEMA. Returns (merged, added_keys)."""
    merged  = dict(existing)
    added   = []
    for key, default in SCHEMA.items():
        if key not in merged:
            merged[key] = default
            added.append(key)
    return merged, added


def _dump_frontmatter(fm: dict) -> str:
    # Preserve key order matching SCHEMA
    ordered = {k: fm.get(k) for k in SCHEMA if k in fm}
    ordered.update({k: v for k, v in fm.items() if k not in SCHEMA})
    return "---\n" + yaml.dump(ordered, allow_unicode=True, default_flow_style=False) + "---\n"


def _infer_date_from_name(path: Path) -> str:
    """Try to pull YYYY-MM-DD from filename."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    return m.group(1) if m else date.today().isoformat()


def process_file(md_path: Path, apply: bool) -> dict:
    content = md_path.read_text(encoding="utf-8")
    fm, body = _parse(content)

    result = {"file": str(md_path.relative_to(BASE)), "action": "ok", "added": []}

    if fm is None:
        # No frontmatter at all — create minimal one
        fm = {"title": md_path.stem, "date": _infer_date_from_name(md_path)}
        result["action"] = "created"

    merged, added = _merge(fm)

    # Auto-fill date if still empty
    if not merged.get("date"):
        merged["date"] = _infer_date_from_name(md_path)
        if "date" not in added:
            added.append("date (auto-filled)")

    if not added and result["action"] == "ok":
        return result

    result["added"] = added
    if result["action"] != "created":
        result["action"] = "updated"

    if apply:
        new_content = _dump_frontmatter(merged) + "\n" + body
        md_path.write_text(new_content, encoding="utf-8")

    return result


def migrate(root: Path, apply: bool) -> list[dict]:
    results = []
    for md_path in sorted(root.rglob("*.md")):
        # Skip files inside excluded directories
        if any(part in SKIP_DIRS for part in md_path.parts):
            continue
        results.append(process_file(md_path, apply))
    return results


def main():
    ap = argparse.ArgumentParser(description="Add missing frontmatter to all .md notes.")
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default is dry-run)")
    ap.add_argument("--path", type=Path, default=BASE,
                    help="Root path to scan (default: KnowledgeBase root)")
    args = ap.parse_args()

    root = args.path if args.path.is_absolute() else BASE / args.path
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[migrate] {mode} — scanning {root}\n")

    results = migrate(root, args.apply)

    changed = [r for r in results if r["action"] != "ok"]
    for r in changed:
        print(f"  [{r['action'].upper():8s}] {r['file']}")
        for field in r["added"]:
            print(f"             + {field}")

    print(f"\nTotal: {len(results)} files scanned, {len(changed)} modified.")
    if not args.apply and changed:
        print("Run with --apply to write changes.")


if __name__ == "__main__":
    main()
