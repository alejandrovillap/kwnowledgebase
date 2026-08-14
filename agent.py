#!/usr/bin/env python3
"""
agent.py — Orchestrate the full KnowledgeBase pipeline for a single file:
           ocr → classify → file_note → git_commit

Usage:
    python agent.py path/to/00-Inbox/raw/scan.pdf
    python agent.py scan.pdf --no-commit   (skip git step)
    python agent.py scan.pdf --dry-run     (OCR + classify only, no writes)
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [agent] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger("agent")

BASE = Path(__file__).parent


# ── Helpers ───────────────────────────────────────────────────────────────────

def _step(name: str):
    """Context manager that logs entry/exit and re-raises with context."""
    class _Ctx:
        def __enter__(self):
            log.info("-- %s ...", name)
            return self
        def __exit__(self, exc_type, exc_val, _tb):
            if exc_type:
                log.error("FAILED [%s]: %s", name, exc_val)
                return False  # re-raise
            log.info("-- %s OK", name)
            return False
    return _Ctx()


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run(file_path: str | Path, *, commit: bool = True, dry_run: bool = False) -> dict:
    """
    Run the full pipeline for one file.

    Returns a result dict:
        {
          "file":    str,
          "title":   str,
          "folder":  str,
          "date":    str,
          "success": bool,
          "error":   str | None,
        }
    """
    path = Path(file_path).resolve()
    log.info("=== Pipeline start: %s", path.name)
    started = datetime.now()

    result = {
        "file":    path.name,
        "title":   "",
        "folder":  "",
        "date":    "",
        "success": False,
        "error":   None,
    }

    try:
        # ── 1. OCR ────────────────────────────────────────────────────────────
        with _step("ocr"):
            from ocr import ocr
            ocr_result = ocr(path)
            text          = ocr_result["text"]
            markdown_body = ocr_result["markdown_body"]
            diagrams      = ocr_result["diagrams"]
            log.info("   extracted %d chars, %d diagram(s)",
                     len(text), len(diagrams))

        if not text.strip():
            raise ValueError("OCR returned empty text — aborting.")

        # ── 2. Classify ───────────────────────────────────────────────────────
        with _step("classify"):
            from classify_note import classify
            meta = classify(text.strip(), source_name=path.stem)
            # If no real date found, default to today (avoids 1970-01-01 / epoch dates)
            raw_date = meta.get("date") or ""
            if not raw_date or raw_date < "2020-01-01":
                meta["date"] = started.strftime("%Y-%m-%d")
                log.info("   date fallback → today (%s)", meta["date"])
            log.info("   title=%r  folder=%s  confidence=%s",
                     meta.get("title"), meta.get("target_folder"), meta.get("confidence"))
            result["title"]  = meta.get("title", "")
            result["folder"] = meta.get("target_folder", "")
            result["date"]   = meta.get("date", "")

        if dry_run:
            log.info("dry-run mode — stopping before file writes.")
            result["success"] = True
            return result

        # ── 3. File note (create or update) ──────────────────────────────────
        with _step("file_note"):
            from file_note import file_note, update_note, find_existing, _resolve_folder
            from ocr import _build_markdown_body

            existing_md = find_existing(path.name)

            if existing_md:
                log.info("   existing note found: %s — updating", existing_md.name)
                filed = update_note(
                    existing_md=existing_md,
                    markdown_body=markdown_body,
                    source_path=path,
                )
            else:
                folder_key = meta.get("target_folder", "40-Reference")
                _, depth   = _resolve_folder(folder_key)
                if depth != 1:
                    markdown_body = _build_markdown_body(text, diagrams, depth)
                filed = file_note(
                    text=text,
                    markdown_body=markdown_body,
                    meta=meta,
                    source_path=path,
                )

            result.update(filed)

        # ── 3b. Enrich: add rich markdown formatting ──────────────────────────
        with _step("format_note"):
            from enrich_notes import enrich_file
            note_md = result.get("dest_md")
            if note_md:
                enrich_file(Path(note_md), dry_run=False)
            else:
                log.warning("   no dest_md in result — skipping format step")

        # ── 4. Git commit ─────────────────────────────────────────────────────
        if commit:
            with _step("git_commit"):
                from git_commit import commit as git_commit
                is_update = result.get("updated", False)
                ok, msg = git_commit(
                    title=result["title"] or path.stem,
                    folder=result["folder"] or "40-Reference",
                    note_date=result["date"] or None,
                    update=is_update,
                )
                if not ok:
                    raise RuntimeError(msg)
                log.info("   %s", msg)

        # ── 5. Rebuild indexes ────────────────────────────────────────────────
        with _step("build_index"):
            from build_index import build_all
            counts = build_all()
            log.info("   global: %d notes | folders updated: %d",
                     counts.get("_global", 0), len(counts) - 1)

        # ── 6. Rebuild dashboard ──────────────────────────────────────────────
        with _step("build_dashboard"):
            from build_dashboard import build_dashboard
            dest = build_dashboard()
            log.info("   dashboard written to %s", dest.name)

        result["success"] = True

    except Exception as exc:
        result["error"] = str(exc)
        log.error("Pipeline FAILED for %s: %s", path.name, exc)

    elapsed = (datetime.now() - started).total_seconds()
    status  = "SUCCESS" if result["success"] else "FAILURE"
    log.info("=== Pipeline %s in %.1fs: %s", status, elapsed, path.name)
    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Run the full KB pipeline on a file.")
    ap.add_argument("file",        help="PDF or image file to process")
    ap.add_argument("--no-commit", action="store_true", help="Skip git commit step")
    ap.add_argument("--dry-run",   action="store_true",
                    help="OCR + classify only, no file writes or commits")
    args = ap.parse_args()

    result = run(
        args.file,
        commit=not args.no_commit,
        dry_run=args.dry_run,
    )
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
