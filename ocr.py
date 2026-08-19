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

import io
import anthropic
from dotenv import load_dotenv
from mermaid_repair import repair_all_in_text as _repair_mermaid

load_dotenv(Path(__file__).parent / ".env")

BASE       = Path(__file__).parent
ASSETS_DIR = BASE / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# Minimum long-side resolution to send to Claude Vision (pixels)
MIN_RESOLUTION = 1800

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MEDIA_TYPES = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
}

OCR_SYSTEM = (
    "You are an expert OCR and visual-to-markdown converter. "
    "You extract text from handwritten notes and convert diagrams into structured Markdown and Mermaid syntax."
)

OCR_PROMPT = """\
Analyze this image carefully. It may contain handwritten text, diagrams, mind maps, flowcharts, or a mix of all.

Perform the following:

1. EXTRACT text: Read all handwritten or printed text accurately.
   - Resolve ambiguous letterforms using context
   - Fix obvious spelling errors from hard-to-read handwriting
   - Preserve structure (headings, bullets, indentation, groupings)
   - Do NOT invent content that is not visible

2. CONVERT every visual element and embed it inline in the "text" field at the position it appears.
   Use the most appropriate markdown representation per type:

   | Visual type              | Convert to                                              |
   |--------------------------|--------------------------------------------------------|
   | Flowchart / process flow | ```mermaid\nflowchart TD\n  A[Step] --> B[Step]\n```   |
   | Sequence / interaction   | ```mermaid\nsequenceDiagram\n  A->>B: action\n```       |
   | Mind map / radial        | Nested bullets: ## Central, - Branch, ·· - Sub-branch  |
   | Timeline / roadmap       | ```mermaid\ntimeline\n  title X\n  Y : event\n```       |
   | Org chart / hierarchy    | ```mermaid\ngraph TD\n  A --> B\n```                    |
   | Comparison matrix / 2x2  | Markdown table with | col | col | headers               |
   | Simple sketch / drawing  | > [Sketch: one-sentence description of what it shows]   |

   Rules for Mermaid:
   - Node labels must not contain parentheses () — use [] or {} instead
   - Keep node IDs short (A, B, C or meaningful short words)
   - Use --> for arrows, -- label --> for labeled arrows
   - Always close subgraph blocks

3. CLASSIFY each visual element found for metadata.

4. ASSESS your own confidence in the extraction:
   - "high"   — image is clear, all text legible, diagrams well-defined
   - "medium" — some words ambiguous, partial shadows, diagram connections uncertain
   - "low"    — significant portions unreadable (blur, glare, torn paper, heavy shadows),
                 or the diagram structure is too complex/overlapping to reconstruct faithfully
   List every specific region or element you were uncertain about in "uncertain_regions".

Return ONLY valid JSON — no preamble, no markdown fences around the JSON itself:
{
  "text": "full content with ALL visual elements converted and embedded inline as mermaid/markdown",
  "diagrams": [
    {
      "title": "short descriptive title",
      "type": "flowchart|mindmap|timeline|hierarchy|sequence|matrix|sketch|other",
      "description": "one-line summary of what it represents",
      "format": "mermaid|table|bullets|blockquote"
    }
  ],
  "confidence": "high|medium|low",
  "uncertain_regions": ["brief description of each unclear region or element"]
}
If no diagrams exist, use "diagrams": [].
If nothing was uncertain, use "uncertain_regions": []."""


# ── Classification prompt (Haiku — fast, cheap) ───────────────────────────────

_CLASSIFY_SYSTEM = "You classify document images by their primary visual content type. Reply with one word only."

_CLASSIFY_PROMPT = """\
Look at this image and identify its PRIMARY content type. Choose the single best label:

- text_only   — handwritten or printed text with no diagrams
- flowchart   — process flow, decision tree, step-by-step sequence with arrows
- mindmap     — radial/spider diagram centered on a central concept
- timeline    — chronological events, roadmap, milestones on a line
- matrix      — 2×2 quadrant, comparison grid, ranked table with drawn borders
- hierarchy   — org chart, tree structure, parent→child relationships
- sequence    — actor-to-actor interaction diagram, swim lanes, message flow
- mixed       — two or more of the above types, or unclear

Reply with ONLY the label (one word, lowercase). No explanation."""


# ── Shared JSON schema suffix (appended to every specialized prompt) ──────────

_JSON_SCHEMA = """
Confidence assessment:
- "high"   — image clear, all content legible and unambiguous
- "medium" — some words or connections uncertain
- "low"    — significant portions unreadable or structure unclear

Return ONLY valid JSON — no preamble, no fences:
{
  "text": "full extracted and converted content",
  "diagrams": [
    {
      "title": "short title",
      "type": "flowchart|mindmap|timeline|hierarchy|sequence|matrix|sketch|other",
      "description": "one-line description",
      "format": "mermaid|table|bullets|blockquote"
    }
  ],
  "confidence": "high|medium|low",
  "uncertain_regions": ["description of each unclear element"]
}
If no diagrams: "diagrams": []. If nothing uncertain: "uncertain_regions": []."""


# ── Few-shot examples per diagram type ───────────────────────────────────────
# One concrete input-description → expected-output example per type.
# These are embedded in each specialized prompt to anchor the format.

_EXAMPLES: dict[str, str] = {

"text_only": "",  # no diagram to illustrate

"flowchart": """\
EXAMPLE
Image contains: oval "Inicio", rectangle "Formulario de login",
diamond "¿Credenciales válidas?", yes-branch to rectangle "Cargar dashboard",
no-branch back to rectangle "Mostrar error", oval "Fin".

Expected output in the "text" field:
```mermaid
flowchart TD
  Start([Inicio]) --> Form[Formulario de login]
  Form --> Valid{Credenciales válidas?}
  Valid -- Sí --> Dashboard[Cargar dashboard]
  Valid -- No --> Err[Mostrar error]
  Err --> Form
  Dashboard --> End([Fin])
```
""",

"mindmap": """\
EXAMPLE
Image contains: central bubble "Estrategia de Producto", three branches:
"Mercado" with sub-items "Segmentos" and "Competidores",
"Roadmap" with sub-items "Q1" and "Q2",
"Métricas" with sub-items "Retención" and "Ingresos".

Expected output in the "text" field:
## Estrategia de Producto
- Mercado
  - Segmentos
  - Competidores
- Roadmap
  - Q1
  - Q2
- Métricas
  - Retención
  - Ingresos
""",

"timeline": """\
EXAMPLE
Image contains: horizontal line — "Ene 2024: Kickoff",
"Mar 2024: MVP, Beta usuarios", "Jun 2024: Lanzamiento v1.0", "Q4 2024: Escala".

Expected output in the "text" field:
```mermaid
timeline
  title Roadmap 2024
  Ene 2024 : Kickoff
  Mar 2024 : MVP
           : Beta usuarios
  Jun 2024 : Lanzamiento v1.0
  Q4 2024  : Escala
```
""",

"matrix": """\
EXAMPLE
Image contains: 2×2 cuadrante — eje X "Impacto" (bajo→alto), eje Y "Esfuerzo" (alto→bajo).
Cuadrante superior-izquierdo (Alto esfuerzo / Bajo impacto): "Limpieza legacy".
Cuadrante superior-derecho (Alto esfuerzo / Alto impacto): "Nueva API, Rediseño".
Cuadrante inferior-izquierdo (Bajo esfuerzo / Bajo impacto): "Corregir typos".
Cuadrante inferior-derecho (Bajo esfuerzo / Alto impacto): "Fix login, Actualizar docs".

Expected output in the "text" field:
| ↑ Esfuerzo \\ Impacto → | Bajo impacto | Alto impacto |
|---|---|---|
| **Alto esfuerzo** | Limpieza legacy | Nueva API; Rediseño |
| **Bajo esfuerzo** | Corregir typos | Fix login; Actualizar docs |
""",

"hierarchy": """\
EXAMPLE
Image contains: org chart — "CEO" en la cima, dos hijos "VP Ventas" y "VP Ingeniería",
VP Ventas tiene "Ejecutivo de Cuenta" y "Gerente de Ventas",
VP Ingeniería tiene "Backend" y "Frontend".

Expected output in the "text" field:
```mermaid
graph TD
  CEO[CEO] --> VPV[VP Ventas]
  CEO --> VPI[VP Ingeniería]
  VPV --> EC[Ejecutivo de Cuenta]
  VPV --> GV[Gerente de Ventas]
  VPI --> BE[Backend]
  VPI --> FE[Frontend]
```
""",

"sequence": """\
EXAMPLE
Image contains: tres actores — Usuario, Servidor, BD.
Mensajes en orden: Usuario→Servidor "POST /login",
Servidor→BD "SELECT usuario", BD→Servidor "registro",
Servidor→Usuario "200 OK + token".

Expected output in the "text" field:
```mermaid
sequenceDiagram
  participant U as Usuario
  participant S as Servidor
  participant DB as Base de Datos
  U->>S: POST /login
  S->>DB: SELECT usuario WHERE email = ?
  DB-->>S: Registro de usuario
  S-->>U: 200 OK + JWT token
```
""",

"mixed": "",  # generic prompt has no single illustrative example
}


# ── Specialized prompts keyed by diagram type ─────────────────────────────────

def _with_example(base: str, example: str) -> str:
    """Append a few-shot example (if any) between base instructions and JSON schema."""
    if example:
        return base + "\n" + example + _JSON_SCHEMA
    return base + _JSON_SCHEMA


_SPECIALIZED_PROMPTS: dict[str, str] = {

"text_only": _with_example("""\
Extract all handwritten or printed text from this image.
- Read every word carefully; fix obvious spelling errors caused by handwriting ambiguity
- Preserve the original structure: headings, bullets, numbered lists, indentation
- Do NOT invent content that is not visible
- If a small sketch or symbol appears, describe it briefly as > [Symbol: ...]
""", _EXAMPLES["text_only"]),

"flowchart": _with_example("""\
Convert this flowchart/process diagram to Mermaid syntax.

IDENTIFY:
- Start and end nodes (oval/pill shapes)
- Process steps (rectangles)
- Decision points (diamonds) and their Yes/No/conditional branches
- Arrow directions and any text labels on arrows

CONVERT to ```mermaid\\nflowchart TD``` using:
  [process step]                 for rectangles
  {decision?}                    for diamonds
  ([start or end])               for ovals
  --> for plain arrows
  -- Sí --> or -- No -->         for labeled branches
  subgraph GroupName ... end     for grouped sections

Node ID rules: short camelCase — no spaces, no special characters, no accents.
Embed the mermaid block in the "text" field at the position the diagram appears.
Also extract any surrounding written text.
""", _EXAMPLES["flowchart"]),

"mindmap": _with_example("""\
Convert this mind map / radial diagram to structured markdown.

IDENTIFY:
- Central concept (the core bubble or hub)
- Primary branches (level 1)
- Secondary branches (level 2)
- Leaf ideas (level 3+)
- Any icons, emphasis, or colors that indicate priority

CONVERT using nested bullets:
  ## Central Concept
  - Primary branch
    - Secondary idea
      - Detail
  - Another primary branch
    - ...

If the map has fewer than 5 branches, ```mermaid mindmap``` is also acceptable:
  mindmap
    root((Central))
      BranchA
        SubA1
      BranchB

Choose whichever format preserves the hierarchy most faithfully.
Embed at the position the diagram appears. Also extract any surrounding text.
""", _EXAMPLES["mindmap"]),

"timeline": _with_example("""\
Convert this timeline or roadmap to Mermaid timeline syntax.

IDENTIFY:
- Time periods or date labels (years, quarters, months)
- Events or milestones belonging to each period
- Any phase groupings or section labels

CONVERT to:
  ```mermaid
  timeline
    title [Title if visible]
    Period1 : Event A
            : Event B
    Period2 : Event C
  ```

If dates are absent or the sequence is purely ordinal, use a numbered list:
  1. **Phase name** — description

Embed at the position the diagram appears. Also extract any surrounding text.
""", _EXAMPLES["timeline"]),

"matrix": _with_example("""\
Convert this matrix, 2×2 grid, or comparison table to markdown.

IDENTIFY:
- X-axis label (horizontal) and Y-axis label (vertical)
- Quadrant or cell labels
- Items placed in each cell/quadrant — list ALL of them
- Axis direction (low→high, now→future, etc.)

CONVERT to a markdown table. For a 2×2 quadrant, the table has 3 columns
(Y axis header | X-low column | X-high column) and 3 rows (header + 2 data rows):
  | ↑ Y-axis \\ X-axis → | Low X | High X |
  |---|---|---|
  | **High Y** | items here | items here |
  | **Low Y**  | items here | items here |

For a comparison table, use compared items as rows and attributes as columns.
Embed at the position the diagram appears. Also extract any surrounding text.
""", _EXAMPLES["matrix"]),

"hierarchy": _with_example("""\
Convert this hierarchy or org chart to a Mermaid graph.

IDENTIFY:
- Root node (topmost element)
- Every parent→child relationship at each level
- Any lateral/sibling links
- Node labels exactly as written

CONVERT to:
  ```mermaid
  graph TD
    Root[Label] --> A[Child]
    Root --> B[Child]
    A --> A1[Grandchild]
  ```

Node ID rules: short, no spaces, no accents — use camelCase or abbreviations.
Labels in [square brackets]. Quote labels with special chars: ["Label: value"].
Embed at the position the diagram appears. Also extract any surrounding text.
""", _EXAMPLES["hierarchy"]),

"sequence": _with_example("""\
Convert this sequence or interaction diagram to Mermaid sequenceDiagram syntax.

IDENTIFY:
- All participants / actors in the order they first appear
- Each message or interaction, in chronological order
- Synchronous (solid line) vs. response (dashed line) messages
- Any loops, alt/else blocks, or activation bars

CONVERT to:
  ```mermaid
  sequenceDiagram
    participant A as ActorA
    participant B as ActorB
    A->>B: request message
    B-->>A: response message
  ```

Arrow syntax:
  ->>   synchronous call      -->>  synchronous response
  -)    async fire-and-forget  --)   async response

Use loop [condition] ... end and alt [case] ... else [case] ... end if visible.
Embed at the position the diagram appears. Also extract any surrounding text.
""", _EXAMPLES["sequence"]),

"mixed": OCR_PROMPT,  # generic fallback for pages with multiple diagram types
}

VALID_TYPES = frozenset(_SPECIALIZED_PROMPTS)


# ── Image pre-processing ─────────────────────────────────────────────────────

def _deskew(img):
    """Detect and correct document tilt using OpenCV. Returns PIL Image."""
    try:
        import cv2
        import numpy as np

        img_rgb = np.array(img.convert("RGB"))
        gray    = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        # Otsu threshold — dark text becomes white foreground
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find coordinates of foreground pixels
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 200:
            return img  # not enough content to detect angle

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only correct if skew is significant and plausible
        if abs(angle) < 0.5 or abs(angle) > 15:
            return img

        (h, w) = img_rgb.shape[:2]
        M       = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        rotated = cv2.warpAffine(img_rgb, M, (w, h),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
        from PIL import Image
        return Image.fromarray(rotated)
    except ImportError:
        return img  # opencv not installed — skip


def _enhance_contrast(img):
    """Apply CLAHE (adaptive contrast) via OpenCV, falling back to PIL global contrast."""
    try:
        import cv2
        import numpy as np
        from PIL import Image

        lab   = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_eq  = clahe.apply(l)
        enhanced = cv2.merge([l_eq, a, b])
        return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB))
    except ImportError:
        from PIL import ImageEnhance
        return ImageEnhance.Contrast(img).enhance(1.4)


def _sanitize_json(raw: str) -> str:
    """Escape literal newlines/tabs inside JSON string values."""
    out = []
    in_string = False
    skip_next = False
    for ch in raw:
        if skip_next:
            out.append(ch)
            skip_next = False
        elif ch == '\\' and in_string:
            out.append(ch)
            skip_next = True
        elif ch == '"':
            in_string = not in_string
            out.append(ch)
        elif in_string and ch == '\n':
            out.append('\\n')
        elif in_string and ch == '\r':
            out.append('\\r')
        elif in_string and ch == '\t':
            out.append('\\t')
        else:
            out.append(ch)
    return ''.join(out)


def _regex_extract(raw: str) -> dict:
    """Regex fallback when JSON parsing fails (e.g. unescaped quotes in text)."""
    import re as _re
    # The "text" field is always first; the next field is always "diagrams"
    # Match greedily up to the last occurrence of the next-field marker
    text_m = _re.search(
        r'"text"\s*:\s*"(.*?)"\s*,\s*[\r\n]*\s*"(?:diagrams|confidence|uncertain_regions)"',
        raw, _re.DOTALL
    )
    if text_m:
        text_val = text_m.group(1).replace('\\n', '\n').replace('\\"', '"')
        # Reconstruct parseable JSON for remaining fields
        rest = '{"text":"",' + raw[text_m.end(1) + 1:].lstrip(', \r\n')
        try:
            d = json.loads(rest)
            d['text'] = text_val
            return d
        except Exception:
            pass
    # Ultimate fallback: return raw text with safe defaults
    return {
        "text": raw,
        "diagrams": [],
        "confidence": "low",
        "uncertain_regions": ["JSON parse failed — content extracted via fallback"],
    }


def _preprocess(img_data: bytes) -> bytes:
    """
    Prepare an image for Claude Vision:
      1. Flatten alpha / convert to RGB
      2. Upscale to MIN_RESOLUTION on the long side (Lanczos)
      3. Deskew (opencv) — corrects tilt up to 15°
      4. Adaptive contrast via CLAHE (opencv) or PIL fallback
      5. Unsharp mask — sharpens text and diagram edges
    Returns PNG bytes. Requires Pillow; opencv optional but recommended.
    """
    try:
        from PIL import Image, ImageFilter

        img = Image.open(io.BytesIO(img_data))

        # Flatten transparency onto white background
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Upscale if below minimum resolution
        long_side = max(img.size)
        if long_side < MIN_RESOLUTION:
            scale = MIN_RESOLUTION / long_side
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)),
                Image.LANCZOS,
            )

        img = _deskew(img)
        img = _enhance_contrast(img)

        # Unsharp mask — radius 1.5px, 130% strength, threshold 3
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=130, threshold=3))

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    except ImportError:
        # Pillow not installed — return original bytes unchanged
        return img_data


# ── Classification (Haiku — fast, cheap) ─────────────────────────────────────

def _classify(client: anthropic.Anthropic, img_b64: str, media_type: str) -> str:
    """Return one of VALID_TYPES describing the primary content of the image."""
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        system=_CLASSIFY_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                {"type": "text", "text": _CLASSIFY_PROMPT},
            ],
        }],
    )
    label = msg.content[0].text.strip().lower().split()[0]
    return label if label in VALID_TYPES else "mixed"


# ── Claude Vision call ────────────────────────────────────────────────────────

def _vision(client: anthropic.Anthropic, img_b64: str, media_type: str, *, repair: bool = True) -> dict:
    # Step 1: classify image type (Haiku — ~10 tokens out, very cheap)
    content_type = _classify(client, img_b64, media_type)
    prompt       = _SPECIALIZED_PROMPTS[content_type]

    # Step 2: full extraction with the specialized prompt (Sonnet)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=OCR_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    if msg.stop_reason == "max_tokens":
        raise ValueError(
            f"OCR response truncated (max_tokens reached). "
            f"Input was too large — try a smaller image or fewer pages."
        )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
    brace_start = raw.find("{")
    brace_end   = raw.rfind("}")
    if brace_start != -1 and brace_end != -1:
        raw = raw[brace_start : brace_end + 1]
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        try:
            result = json.loads(_sanitize_json(raw))
        except json.JSONDecodeError:
            result = _regex_extract(raw)

    # Tag the result with the detected type for downstream use
    result["content_type"] = content_type

    # Stage 3: repair Mermaid blocks in the extracted text
    if repair and result.get("text"):
        result["text"], _ = _repair_mermaid(result["text"], client=client)

    return result


# ── PDF processing ────────────────────────────────────────────────────────────

def _process_pdf(pdf_path: Path, client: anthropic.Anthropic, today: str) -> tuple[str, list[dict]]:
    try:
        import fitz
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF support: pip install PyMuPDF")

    doc = fitz.open(str(pdf_path))
    text_parts:    list[str]  = []
    diagrams:      list[dict] = []
    confidences:   list[str]  = []
    uncertain_all: list[str]  = []
    content_types: list[str]  = []
    diag_idx = 0

    for page in doc:
        pix      = page.get_pixmap(matrix=fitz.Matrix(3, 3))   # 3× for handwritten/diagram fidelity
        img_data = _preprocess(pix.tobytes("png"))
        img_b64  = base64.standard_b64encode(img_data).decode()

        result = _vision(client, img_b64, "image/png")
        if result.get("text"):
            text_parts.append(result["text"])
        confidences.append(result.get("confidence", "medium"))
        uncertain_all.extend(result.get("uncertain_regions", []))
        content_types.append(result.get("content_type", "mixed"))

        for diag in result.get("diagrams", []):
            diag_idx += 1
            filename = f"{today}-diagram-{diag_idx:02d}.png"
            (ASSETS_DIR / filename).write_bytes(img_data)
            diagrams.append({"title": diag.get("title", f"diagram-{diag_idx:02d}"),
                             "description": diag.get("description", ""),
                             "filename": filename})

    doc.close()
    _rank = {"high": 0, "medium": 1, "low": 2}
    confidence   = max(confidences,   key=lambda c: _rank.get(c, 1)) if confidences else "medium"
    # If all pages share the same type use it; otherwise "mixed"
    unique_types = set(content_types)
    content_type = content_types[0] if len(unique_types) == 1 else "mixed"
    return "\n\n".join(text_parts), diagrams, confidence, uncertain_all, content_type


# ── Image processing ──────────────────────────────────────────────────────────

def _process_image(img_path: Path, client: anthropic.Anthropic, today: str) -> tuple[str, list[dict], str, list[str], str]:
    img_data = _preprocess(img_path.read_bytes())   # always PNG after preprocessing
    img_b64  = base64.standard_b64encode(img_data).decode()

    result   = _vision(client, img_b64, "image/png")
    text     = result.get("text", "")
    diagrams = []

    for idx, diag in enumerate(result.get("diagrams", []), 1):
        filename = f"{today}-diagram-{idx:02d}.png"
        (ASSETS_DIR / filename).write_bytes(img_data)   # save the preprocessed version
        diagrams.append({"title": diag.get("title", f"diagram-{idx:02d}"),
                         "description": diag.get("description", ""),
                         "filename": filename})

    return (
        text, diagrams,
        result.get("confidence", "medium"),
        result.get("uncertain_regions", []),
        result.get("content_type", "mixed"),
    )


# ── Confidence banner ────────────────────────────────────────────────────────

_CONFIDENCE_EMOJI = {"high": "✅", "medium": "⚠️", "low": "🔴"}

def _confidence_banner(confidence: str, uncertain_regions: list[str]) -> str:
    """Return a markdown blockquote banner when review is suggested, else ''."""
    if confidence == "high" and not uncertain_regions:
        return ""
    emoji = _CONFIDENCE_EMOJI.get(confidence, "⚠️")
    label = {"high": "alta", "medium": "media", "low": "baja"}.get(confidence, confidence)
    lines = [f"{emoji} **Revisión sugerida** — Confianza OCR: {label}"]
    if uncertain_regions:
        items = "; ".join(uncertain_regions)
        lines.append(f"Regiones inciertas: {items}")
    return "> " + "  \n> ".join(lines)


# ── Markdown body builder ─────────────────────────────────────────────────────

def _build_markdown_body(
    text: str,
    diagrams: list[dict],
    depth: int = 1,
    confidence: str = "high",
    uncertain_regions: list[str] | None = None,
) -> str:
    rel    = "../" * depth
    banner = _confidence_banner(confidence, uncertain_regions or [])
    body   = (banner + "\n\n" + text) if banner else text
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
          "text":             str,          # raw extracted text (with mermaid blocks)
          "markdown_body":    str,          # text + confidence banner + diagram refs
          "diagrams":         list[dict],   # [{title, description, filename}]
          "confidence":       str,          # "high" | "medium" | "low"
          "uncertain_regions":list[str],    # regions Claude was unsure about
          "needs_review":     bool,         # True when confidence is medium or low
          "content_type":     str,          # detected type: flowchart|mindmap|timeline|…
        }
    folder_depth: levels below KnowledgeBase root where the .md will live
                  (1 for 10-Work, 2 for 20-Learning/CCA-F, etc.)
    """
    path   = Path(file_path)
    today  = date.today().isoformat()
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    ext = path.suffix.lower()
    if ext == ".pdf":
        text, diagrams, confidence, uncertain, content_type = _process_pdf(path, client, today)
    elif ext in IMAGE_EXTS:
        text, diagrams, confidence, uncertain, content_type = _process_image(path, client, today)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf {' '.join(IMAGE_EXTS)}")

    return {
        "text":              text,
        "markdown_body":     _build_markdown_body(text, diagrams, folder_depth, confidence, uncertain),
        "diagrams":          diagrams,
        "confidence":        confidence,
        "uncertain_regions": uncertain,
        "needs_review":      confidence != "high",
        "content_type":      content_type,
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
        conf  = result["confidence"]
        ctype = result["content_type"]
        emoji = {"high": "✅", "medium": "⚠️", "low": "🔴"}.get(conf, "?")
        print(f"\n{emoji}  Confianza OCR: {conf.upper()}  |  Tipo: {ctype}", file=sys.stderr)
        if result["uncertain_regions"]:
            for r in result["uncertain_regions"]:
                print(f"   • {r}", file=sys.stderr)
        print(file=sys.stderr)
        print(result["markdown_body"])


if __name__ == "__main__":
    main()
