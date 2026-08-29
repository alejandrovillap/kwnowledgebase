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
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE = Path(__file__).parent

# Curated descriptions for known folders.
# Any folder discovered on disk but missing here gets a generic description.
_FOLDER_DESCRIPTIONS: dict[str, str] = {
    "10-Work":                    "STRICTLY for active work outputs: client projects, deliverables, meeting notes with clients/stakeholders, consulting engagements, work proposals. NOT for studying topics, learning frameworks, or certification prep.",
    "20-Learning/PMI-ACP":        "PMI Agile Certified Practitioner: agile frameworks, Scrum, Kanban, servant leadership, agile mindset, exam prep, retrospectives, user stories, velocity, sprint, backlog.",
    "20-Learning/CCA-F":          "Anthropic CCA-F certification: Claude Code, MCP, agentic architecture, exam domains D1-D5, prompt engineering with Claude. NOT for OpenAI/ChatGPT content.",
    "20-Learning/Cognitive-PM-AI":"Cognitive PM AI course: cognition, AI applied to project management, mental models.",
    "20-Learning/Antigravity":    "Antigravity Platform: agentic editor, soul framework, IDE, platform design.",
    "20-Learning/Gemini-Enterprise":"Google Gemini Enterprise: workspace AI, DLP, change management, deployment.",
    "20-Learning/RPA":            "Robotic Process Automation: UiPath, Automation Anywhere, bots, workflow automation, RPA tools.",
    "20-Learning/Coaching":       "Coaching methodologies: ICF, coaching conversations, coaching frameworks, mentoring.",
    "20-Learning/OpenAI":         "OpenAI platform: GPT-4, ChatGPT, OpenAI API, DALL-E, Whisper, fine-tuning, OpenAI tools.",
    "20-Learning/Deep-Learning":  "Deep learning and neural networks: PyTorch, TensorFlow, CNNs, transformers, model training.",
    "20-Learning/English-Grammar":"English language learning: grammar rules, vocabulary, writing skills.",
    "20-Learning":                "Use for ALL other learning content. This is the default when nothing above fits.",
    "Journal":                    "Personal reflections, emotions, personal development diary.",
}

_SKIP_DIRS = {".git", "__pycache__", "00-Inbox", "assets", "Kanban"}


def _build_folder_list() -> str:
    """Scan vault on disk and build the folder-rules section of the prompt."""
    lines: list[str] = []
    roots = ["10-Work", "20-Learning", "Journal"]

    for root in roots:
        root_path = BASE / root
        if not root_path.exists():
            continue

        # Subfolders first (most specific), then root
        for sub in sorted(root_path.iterdir()):
            if sub.is_dir() and sub.name not in _SKIP_DIRS and not sub.name.startswith("."):
                key = f"{root}/{sub.name}"
                desc = _FOLDER_DESCRIPTIONS.get(key, f"Notes about {sub.name}.")
                lines.append(f"{key} — {desc}")

        # Root folder itself
        if root in _FOLDER_DESCRIPTIONS:
            lines.append(f"{root} — {_FOLDER_DESCRIPTIONS[root]}")

    return "\n".join(lines)


_PROMPT_TEMPLATE = """You are a knowledge management assistant for a personal learning vault.

Given OCR text of a note, return ONLY valid JSON:
{{"title":"","date":"YYYY-MM-DD","type":"idea|case|lesson-learned|question|resume|meeting|journal","status":"active|to-review|archived","technology":"gen-ai|methodology|mixed|automation|other|null","tags":[],"keywords":[],"project":"","certification":"","target_folder":"","confidence":"high|medium|low"}}

FOLDER RULES — read carefully:

{folder_list}

STRICT RULES:
- Do NOT invent new subfolder names. Use ONLY the exact folder keys listed above.
- Do NOT use 40-Reference, 50-Archive, or 20-Learning/Certifications — these no longer exist.
- When in doubt, use 20-Learning.

No preamble. No explanation. JSON only."""


def _get_system_prompt() -> str:
    return _PROMPT_TEMPLATE.format(folder_list=_build_folder_list())


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


def classify(ocr_text: str, source_name: str = "") -> dict:
    import logging
    log = logging.getLogger(__name__)

    client  = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    user_content = ocr_text
    if source_name:
        user_content = f"[Source file: {source_name}]\n\n{ocr_text}"
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_get_system_prompt(),
        messages=[{"role": "user", "content": user_content}],
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
