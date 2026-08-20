#!/usr/bin/env python3
"""
git_commit.py — Stage all KB changes and commit with a structured message.

Usage (CLI):
    python git_commit.py --title "My Note" --folder "10-Work"
    python git_commit.py --title "My Note" --folder "10-Work" --date 2026-05-06

Usage (module):
    from git_commit import commit
    commit(title="My Note", folder="10-Work")  # returns (success, message)
"""

import subprocess
import argparse
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent


def _run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def commit(title: str, folder: str, note_date: str | None = None, update: bool = False) -> tuple[bool, str]:
    """
    Stage all changes under BASE and create a commit.

    Returns:
        (success: bool, message: str)
    """
    d = note_date or date.today().isoformat()

    # Check if this is even a git repo
    code, _, _ = _run(["git", "rev-parse", "--git-dir"], BASE)
    if code != 0:
        # Init repo if it doesn't exist yet
        _run(["git", "init"], BASE)
        _run(["git", "checkout", "-b", "main"], BASE)

    # Stage everything
    code, out, err = _run(["git", "add", "-A"], BASE)
    if code != 0:
        return False, f"git add failed: {err}"

    # Check if there is anything to commit
    code, status, _ = _run(["git", "status", "--porcelain"], BASE)
    if not status:
        return True, "Nothing to commit — working tree clean."

    prefix = "[agent][update]" if update else "[agent]"
    msg = f"{prefix} {d} - {title} → {folder}"
    code, out, err = _run(["git", "commit", "-m", msg], BASE)
    if code != 0:
        return False, f"git commit failed: {err or out}"

    # Push to remote — non-fatal: note is safe locally even if push fails
    push_code, _, push_err = _run(["git", "push"], BASE)
    if push_code != 0:
        return True, f"{msg} [WARN: push failed: {push_err[:120]}]"

    return True, msg


def main():
    ap = argparse.ArgumentParser(description="Commit KnowledgeBase changes.")
    ap.add_argument("--title",  required=True, help="Note title")
    ap.add_argument("--folder", required=True, help="Target folder (e.g. 10-Work)")
    ap.add_argument("--date",   default=None,  help="Date override (YYYY-MM-DD)")
    args = ap.parse_args()

    ok, msg = commit(title=args.title, folder=args.folder, note_date=args.date)
    print(("[OK] " if ok else "[FAIL] ") + msg)


if __name__ == "__main__":
    main()
