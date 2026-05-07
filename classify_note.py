#!/usr/bin/env python3
"""
classify_note.py — Classify a handwritten note (OCR text) using Claude API.

Usage:
    python classify_note.py "path/to/note.txt"
    python classify_note.py --text "raw OCR text here"
    echo "note text" | python classify_note.py
"""

import sys
import json
import argparse
import os
import anthropic

SYSTEM_PROMPT = """You are a knowledge management assistant.
Given the OCR text of a handwritten note, return ONLY valid JSON:
{"title":"","date":"YYYY-MM-DD","type":"idea|case|lesson-learned|question|resume|meeting|journal","status":"active|to-review|archived","technology":"gen-ai|methodology|mixed|automation|other|null","tags":[],"keywords":[],"project":"","certification":"","target_folder":"","confidence":"high|medium|low"}
Folder options: 10-Work, 20-Learning, 20-Learning/CCA-F, 20-Learning/Certifications, 40-Reference, 50-Archive, Journal
No preamble. No explanation. JSON only."""


def _strip_fences(text: str) -> str:
    """Remove markdown code fences (```json ... ``` or ``` ... ```)."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop opening fence line and closing fence line
        start = 1
        end   = len(lines)
        if lines[-1].strip() == "```":
            end = -1
        text = "\n".join(lines[start:end]).strip()
    return text


def classify(ocr_text: str) -> dict:
    import logging
    log = logging.getLogger(__name__)

    client  = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": ocr_text}],
    )

    # Log stop reason to surface truncation issues early
    log.debug("stop_reason=%s  usage=%s", message.stop_reason, message.usage)

    if not message.content:
        raise ValueError(
            f"API returned an empty content list. "
            f"stop_reason={message.stop_reason!r}, usage={message.usage}"
        )

    raw = message.content[0].text
    log.debug("raw API response: %r", raw)

    cleaned = _strip_fences(raw)

    if not cleaned:
        raise ValueError(
            f"API response is empty after stripping fences. "
            f"Original response was: {raw!r}"
        )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON parsing failed ({exc}). "
            f"Cleaned response was: {cleaned!r}"
        ) from exc


def main():
    parser = argparse.ArgumentParser(description="Classify a handwritten note via OCR text.")
    parser.add_argument("file", nargs="?", help="Path to a .txt file with OCR text")
    parser.add_argument("--text", "-t", help="OCR text passed directly as a string")
    parser.add_argument("--save", "-s", action="store_true", help="Save JSON alongside input file")
    args = parser.parse_args()

    if args.text:
        ocr_text = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            ocr_text = f.read()
    elif not sys.stdin.isatty():
        ocr_text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    result = classify(ocr_text.strip())
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)

    if args.save and args.file:
        out_path = os.path.splitext(args.file)[0] + ".json"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nSaved to: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
