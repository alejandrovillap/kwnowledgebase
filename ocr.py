#!/usr/bin/env python3
"""
ocr.py — Extract text (and diagrams) from a PDF or image via Claude Vision.

Usage:
    python ocr.py path/to/file.pdf
    python ocr.py path/to/scan.png --json
    result = ocr("file.pdf")  # returns dict when used as a module
"""

import os
import sys
import json
import base64
import shutil
import argparse
from pathlib import Path
from datetime import date

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE       = Path(__file__).parent
ASSETS_DIR = BASE / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MEDIA_TYPES = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
}

OCR_SYSTEM = (
    "You are an expert OCR and document analysis assistant. "
    "You extract text from handwritten notes and scanned documents with high accuracy."
)

OCR_PROMPT = """\
Analyze this image carefully. Perform two tasks:

1. EXTRACT all text verbatim. Preserve structure: headings, bullets, numbering, indentation.
2. IDENTIFY non-text visual elements: diagrams, flowcharts, mind maps, charts, sketches, tables with drawn borders.
   For each, produce a short title and a detailed description.

Return ONLY valid JSON — no preamble, no fences:
{
  "text": "full extracted text",
  "diagrams": [
    {"title": "short title", "description": "detailed description of what it shows"}
  ]
}
If no diagrams, use "diagrams": []."""


# ── Claude Vision call ────────────────────────────────────────────────────────

def _vision(client: anthropic.Anthropic, img_b64: str, media_type: str) -> dict:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=OCR_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                {"type": "text", "text": OCR_PROMPT},
            ],
        }],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
    return json.loads(raw)


# ── PDF processing ────────────────────────────────────────────────────────────

def _process_pdf(pdf_path: Path, client: anthropic.Anthropic, today: str) -> tuple[str, list[dict]]:
    try:
        import fitz
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF support: pip install PyMuPDF")

    doc = fitz.open(str(pdf_path))
    text_parts: list[str] = []
    diagrams:   list[dict] = []
    diag_idx = 0

    for page in doc:
        pix      = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        img_b64  = base64.standard_b64encode(img_data).decode()

        result = _vision(client, img_b64, "image/png")
        if result.get("text"):
            text_parts.append(result["text"])

        for diag in result.get("diagrams", []):
            diag_idx += 1
            filename = f"{today}-diagram-{diag_idx:02d}.png"
            (ASSETS_DIR / filename).write_bytes(img_data)
            diagrams.append({"title": diag.get("title", f"diagram-{diag_idx:02d}"),
                             "description": diag.get("description", ""),
                             "filename": filename})

    doc.close()
    return "\n\n".join(text_parts), diagrams


# ── Image processing ──────────────────────────────────────────────────────────

def _process_image(img_path: Path, client: anthropic.Anthropic, today: str) -> tuple[str, list[dict]]:
    media_type = MEDIA_TYPES.get(img_path.suffix.lower(), "image/png")
    img_b64    = base64.standard_b64encode(img_path.read_bytes()).decode()

    result   = _vision(client, img_b64, media_type)
    text     = result.get("text", "")
    diagrams = []

    for idx, diag in enumerate(result.get("diagrams", []), 1):
        filename = f"{today}-diagram-{idx:02d}.png"
        dest     = ASSETS_DIR / filename
        if img_path.suffix.lower() == ".png":
            shutil.copy2(img_path, dest)
        else:
            try:
                from PIL import Image
                Image.open(img_path).save(dest, "PNG")
            except ImportError:
                shutil.copy2(img_path, dest)
        diagrams.append({"title": diag.get("title", f"diagram-{idx:02d}"),
                         "description": diag.get("description", ""),
                         "filename": filename})

    return text, diagrams


# ── Markdown body builder ─────────────────────────────────────────────────────

def _build_markdown_body(text: str, diagrams: list[dict], depth: int = 1) -> str:
    rel = "../" * depth
    body = text
    for d in diagrams:
        body += (
            f"\n\n![{d['title']}]({rel}assets/{d['filename']})\n"
            f"> **Auto description:** {d['description']}"
        )
    return body


# ── Public API ────────────────────────────────────────────────────────────────

def ocr(file_path: str | Path, folder_depth: int = 1) -> dict:
    """
    Returns:
        {
          "text":          str,   # raw extracted text
          "markdown_body": str,   # text + diagram references
          "diagrams":      list   # [{title, description, filename}]
        }
    folder_depth: levels below KnowledgeBase root where the .md will live
                  (1 for 10-Work, 2 for 20-Learning/CCA-F, etc.)
    """
    path   = Path(file_path)
    today  = date.today().isoformat()
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    ext = path.suffix.lower()
    if ext == ".pdf":
        text, diagrams = _process_pdf(path, client, today)
    elif ext in IMAGE_EXTS:
        text, diagrams = _process_image(path, client, today)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf {' '.join(IMAGE_EXTS)}")

    return {
        "text":          text,
        "markdown_body": _build_markdown_body(text, diagrams, folder_depth),
        "diagrams":      diagrams,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="OCR a PDF or image via Claude Vision.")
    ap.add_argument("file",    help="PDF or image file")
    ap.add_argument("--json",  action="store_true", help="Output full JSON result")
    ap.add_argument("--depth", type=int, default=1,
                    help="Folder depth for relative asset paths (default 1)")
    args = ap.parse_args()

    result = ocr(args.file, folder_depth=args.depth)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["markdown_body"])


if __name__ == "__main__":
    main()
