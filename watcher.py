#!/usr/bin/env python3
"""
watcher.py — Monitor the Boox sync folder for new PDF or image files.
             Copies each file to 00-Inbox/raw/ (original stays intact) then
             triggers agent.py on the copy.

Usage:
    python watcher.py
    python watcher.py --source path/to/folder   (override watch folder)
    python watcher.py --inbox  path/to/raw/     (override staging folder)
"""

import sys
import time
import shutil
import logging
import argparse
import subprocess
from pathlib import Path

try:
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("watchdog is required: pip install watchdog", file=sys.stderr)
    sys.exit(1)

BASE        = Path(__file__).parent
BOOX_FOLDER = Path(r"C:\Users\villa\OneDrive\onyx\TabUltraCPro\Notebooks")
INBOX_RAW   = BASE / "00-Inbox" / "raw"
AGENT       = BASE / "agent.py"

SUPPORTED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [watcher] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("watcher")


def _is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTS


def _wait_for_stable(path: Path, timeout: float = 10.0, interval: float = 0.5) -> bool:
    """Wait until the file stops growing (i.e. fully written)."""
    deadline = time.monotonic() + timeout
    prev_size = -1
    while time.monotonic() < deadline:
        try:
            cur_size = path.stat().st_size
        except FileNotFoundError:
            return False
        if cur_size == prev_size and cur_size > 0:
            return True
        prev_size = cur_size
        time.sleep(interval)
    return False


def _copy_to_inbox(src: Path, inbox: Path) -> Path:
    """Copy src into inbox, avoiding collisions by appending a counter."""
    inbox.mkdir(parents=True, exist_ok=True)
    dest = inbox / src.name
    if dest.exists():
        stem, suffix = src.stem, src.suffix
        for i in range(1, 1000):
            dest = inbox / f"{stem}_{i}{suffix}"
            if not dest.exists():
                break
    shutil.copy2(src, dest)
    return dest


def _trigger(src: Path, inbox: Path) -> None:
    log.info("Boox file detected: %s", src.name)
    if not _wait_for_stable(src):
        log.warning("File %s did not stabilise — skipping.", src.name)
        return

    copy = _copy_to_inbox(src, inbox)
    log.info("Copied → %s", copy)
    log.info("Running pipeline for %s …", copy.name)

    result = subprocess.run(
        [sys.executable, str(AGENT), str(copy)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log.info("Pipeline succeeded for %s", copy.name)
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                log.info("  %s", line)
    else:
        log.error("Pipeline FAILED for %s (exit %d)", copy.name, result.returncode)
        if result.stderr.strip():
            for line in result.stderr.strip().splitlines():
                log.error("  %s", line)


class _Handler(FileSystemEventHandler):
    def __init__(self, inbox: Path):
        super().__init__()
        self.inbox = inbox

    def on_created(self, event):
        if not event.is_directory:
            path = Path(event.src_path)
            if _is_supported(path):
                _trigger(path, self.inbox)

    def on_moved(self, event):
        # Covers files synced into the folder via OneDrive (appear as moves)
        if not event.is_directory:
            path = Path(event.dest_path)
            if _is_supported(path):
                _trigger(path, self.inbox)


def watch(source: Path, inbox: Path, poll_interval: int = 10) -> None:
    if not source.exists():
        log.warning("Source folder does not exist yet: %s", source)
    inbox.mkdir(parents=True, exist_ok=True)

    log.info("Watching : %s", source)
    log.info("Staging  : %s", inbox)
    log.info("Poll interval: %ds  (Ctrl-C to stop)", poll_interval)

    # PollingObserver is required for OneDrive folders — native filesystem
    # events are not fired reliably when OneDrive materialises synced files.
    observer = PollingObserver(timeout=poll_interval)
    observer.schedule(_Handler(inbox), str(source), recursive=True)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        log.info("Stopping watcher …")
    finally:
        observer.stop()
        observer.join()
        log.info("Watcher stopped.")


def main():
    ap = argparse.ArgumentParser(description="Watch Boox sync folder and run KB pipeline.")
    ap.add_argument("--source", type=Path, default=BOOX_FOLDER,
                    help=f"Folder to watch (default: {BOOX_FOLDER})")
    ap.add_argument("--inbox",  type=Path, default=INBOX_RAW,
                    help=f"Staging folder (default: {INBOX_RAW})")
    ap.add_argument("--interval", type=int, default=10,
                    help="Polling interval in seconds (default: 10)")
    args = ap.parse_args()
    watch(args.source, args.inbox, args.interval)


if __name__ == "__main__":
    main()
