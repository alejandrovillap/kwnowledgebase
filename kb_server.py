#!/usr/bin/env python3
"""
kb_server.py — Local web server for KnowledgeBase.

Serves the dashboard and provides endpoints for:
  - File upload / camera capture → pipeline
  - Note editing (save note content)
  - Pipeline status (SSE stream)

Usage:
    python kb_server.py
    python kb_server.py --port 5001

Then open http://localhost:5000 in your browser.
"""

import os
import sys
import json
import shutil
import subprocess
import threading
import argparse
import time
import numpy as np
from pathlib import Path
from datetime import datetime

PYTHON = sys.executable

import anthropic
from dotenv import load_dotenv
from flask import (
    Flask, request, jsonify, send_file,
    Response, stream_with_context
)

load_dotenv(Path(__file__).parent / ".env")

from build_index import FRONTMATTER_RE

BASE = Path(__file__).parent
INBOX_RAW   = BASE / "00-Inbox" / "raw"
DASHBOARD   = BASE / "dashboard.html"
EMBED_FILE  = BASE / "embeddings.npz"

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    return jsonify({"error": str(e), "trace": traceback.format_exc()[-500:]}), 500

# ── Embedding index (loaded once at startup) ───────────────────────────────────

_embed_ready  = False
_embed_matrix = None   # (N, D) float32
_embed_paths  = None   # list[str]
_embed_ids    = None   # list[int]
_embed_lock   = threading.Lock()


def _voyage_encode(texts: list[str], input_type: str = "query") -> np.ndarray:
    """Call Voyage AI and return (N, D) float32 matrix, rows normalized."""
    import time, voyageai
    vo = voyageai.Client()
    for attempt in range(4):
        try:
            result = vo.embed(texts, model="voyage-3-lite", input_type=input_type)
            break
        except voyageai.error.RateLimitError:
            time.sleep(22 * (attempt + 1))
    else:
        raise RuntimeError("Voyage AI rate limit")
    vecs = np.array(result.embeddings, dtype=np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
    return vecs / norms


def _load_embeddings():
    global _embed_ready, _embed_matrix, _embed_paths, _embed_ids
    if not EMBED_FILE.exists():
        return
    try:
        data = np.load(EMBED_FILE, allow_pickle=True)
        with _embed_lock:
            _embed_matrix = data["matrix"].astype(np.float32)
            _embed_paths  = data["paths"].tolist()
            _embed_ids    = data["ids"].tolist()
            _embed_ready  = True
        print(f"[embed] Loaded {_embed_matrix.shape[0]} embeddings")
    except Exception as e:
        print(f"[embed] Could not load embeddings: {e}")


# Load embeddings in background so server starts immediately
threading.Thread(target=_load_embeddings, daemon=True).start()

# ── Pipeline state ─────────────────────────────────────────────────────────────

_pipeline_lock   = threading.Lock()
_pipeline_events = []   # list of {"type": "log"|"done"|"error", "msg": str}
_pipeline_running = False


def _run_pipeline(file_path: Path):
    global _pipeline_running
    _pipeline_events.clear()

    def emit(msg: str, kind: str = "log"):
        _pipeline_events.append({"type": kind, "msg": msg, "ts": time.time()})

    emit(f"Procesando: {file_path.name}")
    try:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        proc = subprocess.Popen(
            [PYTHON, str(BASE / "agent.py"), str(file_path)],
            cwd=str(BASE),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        for line in proc.stdout:
            emit(line.rstrip())
        proc.wait()
        if proc.returncode == 0:
            emit("Pipeline completado — dashboard actualizado.", "done")
        else:
            emit(f"Pipeline terminó con código {proc.returncode}", "error")
    except Exception as e:
        emit(str(e), "error")
    finally:
        _pipeline_running = False


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the dashboard HTML."""
    if not DASHBOARD.exists():
        return "Dashboard not built yet. Run: python build_dashboard.py", 503
    return send_file(DASHBOARD)


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/upload", methods=["POST"])
def upload():
    """
    Accept a file upload (image or PDF) and run it through the pipeline.

    Form fields:
      file — the uploaded file (required)
    """
    global _pipeline_running

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = Path(f.filename).suffix.lower()
    if ext not in {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".tiff"}:
        return jsonify({"error": f"Unsupported type: {ext}"}), 415

    INBOX_RAW.mkdir(parents=True, exist_ok=True)

    # Unique filename: timestamp + original name
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f.filename.replace(" ", "_")
    dest = INBOX_RAW / f"{ts}_{safe_name}"
    f.save(str(dest))

    with _pipeline_lock:
        if _pipeline_running:
            return jsonify({"error": "Pipeline already running, try again shortly"}), 409
        _pipeline_running = True
        _pipeline_events.clear()

    t = threading.Thread(target=_run_pipeline, args=(dest,), daemon=True)
    t.start()

    return jsonify({"ok": True, "file": dest.name, "msg": "Pipeline iniciado"})


@app.route("/status")
def status_stream():
    """
    SSE stream of pipeline events.
    The client can subscribe and get real-time log lines.
    """
    def generate():
        sent = 0
        while True:
            current = _pipeline_events[sent:]
            for ev in current:
                data = json.dumps(ev, ensure_ascii=False)
                yield f"data: {data}\n\n"
                sent += 1
            if not _pipeline_running and sent >= len(_pipeline_events):
                break
            time.sleep(0.3)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/note/save", methods=["POST"])
def save_note():
    """
    Save edited note content back to disk and rebuild dashboard.

    JSON body:
      path   — relative path to the .md file (from notes[].path)
      content — new full content (frontmatter + body)
    """
    data = request.get_json(silent=True)
    if not data or "path" not in data or "content" not in data:
        return jsonify({"error": "Missing path or content"}), 400

    rel = Path(data["path"])
    # Security: must stay inside BASE and be a .md file
    try:
        dest = (BASE / rel).resolve()
        dest.relative_to(BASE.resolve())
    except (ValueError, Exception):
        return jsonify({"error": "Invalid path"}), 403

    if dest.suffix != ".md":
        return jsonify({"error": "Only .md files allowed"}), 403

    if not dest.exists():
        return jsonify({"error": "Note not found"}), 404

    # Backup the original before overwriting
    backup = dest.with_suffix(".md.bak")
    shutil.copy2(dest, backup)

    dest.write_text(data["content"], encoding="utf-8")

    # Rebuild dashboard in background
    def rebuild():
        try:
            subprocess.run(
                [PYTHON, str(BASE / "build_dashboard.py")],
                cwd=str(BASE), capture_output=True
            )
        except Exception:
            pass

    threading.Thread(target=rebuild, daemon=True).start()

    return jsonify({"ok": True, "saved": str(rel)})


@app.route("/search")
def semantic_search():
    """
    Semantic search over note embeddings.
    Query params:
      q  — search query (required)
      k  — number of results (default 10, max 30)
    Returns: [{id, path, score}, ...]
    """
    query = request.args.get("q", "").strip()
    k     = min(int(request.args.get("k", 10)), 30)

    if not query:
        return jsonify({"error": "Missing query"}), 400

    with _embed_lock:
        if not _embed_ready or _embed_matrix is None:
            return jsonify({"error": "Embeddings not ready. Run: python build_embeddings.py", "ready": False}), 503
        matrix = _embed_matrix
        paths  = _embed_paths
        ids    = _embed_ids

    q_vec  = _voyage_encode([query], input_type="query")[0]
    scores = matrix @ q_vec
    top_k  = np.argsort(scores)[::-1][:k]

    results = [
        {"id": int(ids[i]), "path": paths[i], "score": round(float(scores[i]), 4)}
        for i in top_k
    ]

    return jsonify({"results": results, "query": query, "ready": True})


@app.route("/embed/status")
def embed_status():
    """Check if embeddings are loaded and ready."""
    with _embed_lock:
        ready = _embed_ready and _embed_matrix is not None
        n     = int(_embed_matrix.shape[0]) if ready else 0
    return jsonify({"ready": ready, "count": n})


@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat with Claude about your vault using RAG.

    JSON body:
      query   — user question (required)
      history — [{role, content}, ...] prior turns (optional)
      k       — number of notes to retrieve as context (default 6)

    Returns SSE stream:
      {type: "sources", notes: [{id, path, title, score}, ...]}
      {type: "text",    content: "..."}   ← streamed token by token
      {type: "done"}
    """
    data    = request.get_json(silent=True) or {}
    query   = data.get("query", "").strip()
    history = data.get("history", [])
    k       = min(int(data.get("k", 6)), 15)

    if not query:
        return jsonify({"error": "Missing query"}), 400

    with _embed_lock:
        if not _embed_ready or _embed_matrix is None:
            return jsonify({"error": "Embeddings not ready. Run: python build_embeddings.py"}), 503
        matrix = _embed_matrix
        paths  = _embed_paths
        ids    = _embed_ids

    q_vec  = _voyage_encode([query], input_type="query")[0]
    scores = matrix @ q_vec
    top_k  = np.argsort(scores)[::-1][:k]
    raw_sources = [
        {"id": int(ids[i]), "path": paths[i], "score": round(float(scores[i]), 4)}
        for i in top_k if scores[i] > 0.15
    ]

    # Read note bodies from disk (may have been edited)
    sources = []
    context_blocks = []
    for s in raw_sources:
        note_path = BASE / s["path"]
        title = Path(s["path"]).stem.replace("_", " ").replace("-", " ")
        body  = ""
        try:
            full = note_path.read_text(encoding="utf-8-sig")
            m    = FRONTMATTER_RE.match(full)
            body = (full[m.end():] if m else full).strip()
            # Try to extract title from frontmatter
            import yaml
            if m:
                fm = yaml.safe_load(m.group(1)) or {}
                title = fm.get("title", title)
        except Exception:
            pass

        sources.append({**s, "title": title})
        context_blocks.append(
            f"### [{s['id']}] {title}\n{body[:2500]}"
        )

    context_text = "\n\n---\n\n".join(context_blocks)

    system_prompt = f"""Eres un asistente de conocimiento personal que ayuda al usuario a explorar y entender su base de conocimiento.

Tienes acceso a las notas más relevantes del vault del usuario. Responde en el mismo idioma que la pregunta.
Sé conciso y directo. Cita las notas con [ID] cuando uses información de ellas.
Si la respuesta no está en las notas, dilo claramente — no inventes información.

NOTAS RELEVANTES DEL VAULT:

{context_text}"""

    def generate():
        try:
            # Emit sources before streaming text
            yield f"data: {json.dumps({'type': 'sources', 'notes': sources}, ensure_ascii=False)}\n\n"

            client = anthropic.Anthropic()
            messages = [
                *[{"role": m["role"], "content": m["content"]} for m in history],
                {"role": "user", "content": query},
            ]

            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1500,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'type': 'text', 'content': text}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/note/read")
def read_note():
    """
    Return raw note content for editing.
    Query param: path — relative path to the .md file
    """
    rel = request.args.get("path", "")
    if not rel:
        return jsonify({"error": "Missing path"}), 400

    try:
        dest = (BASE / Path(rel)).resolve()
        dest.relative_to(BASE.resolve())
    except Exception:
        return jsonify({"error": "Invalid path"}), 403

    if not dest.exists():
        return jsonify({"error": "Not found"}), 404

    content = dest.read_text(encoding="utf-8-sig")
    return jsonify({"content": content, "path": rel})


TRASH = BASE / "_trash"

@app.route("/note/from-url", methods=["POST"])
def note_from_url():
    data  = request.get_json(silent=True) or {}
    url   = (data.get("url")   or "").strip()
    title = (data.get("title") or "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400

    try:
        import requests as req
        from bs4 import BeautifulSoup
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-419,es;q=0.9,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        session = req.Session()
        resp    = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        if resp.status_code == 403:
            return jsonify({"error": f"El sitio bloqueó el acceso automático (403). Copia el texto manualmente y usa ✏️ Nueva."}), 422
        resp.raise_for_status()
        soup    = BeautifulSoup(resp.text, "html.parser")

        # Remove noise elements
        for tag in soup(["script","style","nav","footer","header","aside","form","noscript"]):
            tag.decompose()

        page_title = soup.title.string.strip() if soup.title else ""
        # Prefer <article> or <main>, fall back to <body>
        container  = soup.find("article") or soup.find("main") or soup.body or soup
        text       = container.get_text(separator="\n", strip=True)
        # Collapse excessive blank lines
        import re
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        if not text:
            return jsonify({"error": "No se pudo extraer contenido de la URL"}), 422

        used_title = title or page_title or url
        full_text  = f"# {used_title}\n\nFuente: {url}\n\n{text}"

        from classify_note import classify
        from file_note import file_note
        from datetime import date as _date

        meta = classify(full_text)
        meta["date"]   = _date.today().isoformat()
        meta["source"] = url
        if title:
            meta["title"] = title
        elif page_title:
            meta["title"] = page_title

        body = f"Fuente: [{url}]({url})\n\n{text}"
        result = file_note(text=full_text, markdown_body=body, meta=meta)

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    subprocess.run([PYTHON, str(BASE / "build_dashboard.py")], cwd=str(BASE), capture_output=True)
    threading.Thread(target=lambda: subprocess.run(
        [PYTHON, str(BASE / "build_embeddings.py")], cwd=str(BASE), capture_output=True),
        daemon=True).start()

    import os
    rel_path = os.path.relpath(result["dest_md"], str(BASE)).replace("\\", "/")
    return jsonify({"ok": True, "folder": result["folder"], "title": result["title"], "path": rel_path})


@app.route("/note/move", methods=["POST"])
def move_note():
    import shutil, yaml, re
    data       = request.get_json(silent=True) or {}
    rel        = (data.get("path")   or "").strip()
    new_folder = (data.get("folder") or "").strip()
    if not rel or not new_folder:
        return jsonify({"error": "path and folder required"}), 400
    try:
        src = (BASE / rel).resolve()
        src.relative_to(BASE.resolve())
    except Exception:
        return jsonify({"error": "invalid path"}), 403
    if not src.exists():
        return jsonify({"error": "not found"}), 404

    from file_note import _resolve_folder
    dest_dir, _ = _resolve_folder(new_folder)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if dest == src:
        return jsonify({"ok": True, "path": rel})

    # Avoid overwrite
    if dest.exists():
        dest = dest_dir / (src.stem + "_moved" + src.suffix)

    # Update frontmatter
    fm_re   = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    content = src.read_text(encoding="utf-8-sig")
    m       = fm_re.match(content)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        fm["target_folder"] = new_folder
        from datetime import date as _date
        fm["updated"] = _date.today().isoformat()
        body = content[m.end():]
        content = "---\n" + yaml.dump(fm, allow_unicode=True, default_flow_style=False) + "---\n" + body

    shutil.move(str(src), str(dest))
    dest.write_text(content, encoding="utf-8")

    new_rel = str(dest.relative_to(BASE)).replace("\\", "/")
    subprocess.run([PYTHON, str(BASE / "build_dashboard.py")], cwd=str(BASE), capture_output=True)
    return jsonify({"ok": True, "path": new_rel})


@app.route("/note/delete", methods=["POST"])
def delete_note():
    data = request.get_json(silent=True) or {}
    rel  = (data.get("path") or "").strip()
    if not rel:
        return jsonify({"error": "path required"}), 400
    try:
        dest = (BASE / rel).resolve()
        dest.relative_to(BASE.resolve())
    except Exception:
        return jsonify({"error": "invalid path"}), 403
    if not dest.exists():
        return jsonify({"error": "not found"}), 404

    TRASH.mkdir(exist_ok=True)
    from datetime import datetime
    import yaml, re
    stamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    trash_name = f"{stamp}_{dest.name}"
    trash_dest = TRASH / trash_name

    # Inject _trash_source into frontmatter
    content = dest.read_text(encoding="utf-8-sig")
    fm_re   = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    m       = fm_re.match(content)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        fm["_trash_source"] = rel
        body = content[m.end():]
        new_content = "---\n" + yaml.dump(fm, allow_unicode=True, default_flow_style=False) + "---\n" + body
        trash_dest.write_text(new_content, encoding="utf-8")
    else:
        import shutil
        shutil.copy2(str(dest), str(trash_dest))
        trash_dest.write_text(f"---\n_trash_source: {rel}\n---\n" + content, encoding="utf-8")

    dest.unlink()
    subprocess.run([PYTHON, str(BASE / "build_dashboard.py")], cwd=str(BASE), capture_output=True)
    threading.Thread(target=lambda: subprocess.run(
        [PYTHON, str(BASE / "build_embeddings.py")], cwd=str(BASE), capture_output=True),
        daemon=True).start()
    return jsonify({"ok": True})


@app.route("/trash/list")
def trash_list():
    TRASH.mkdir(exist_ok=True)
    import yaml, re
    fm_re = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    items = []
    for f in sorted(TRASH.glob("*.md"), reverse=True):
        try:
            content = f.read_text(encoding="utf-8-sig")
            m = fm_re.match(content)
            fm = yaml.safe_load(m.group(1)) if m else {}
            fm = fm or {}
            items.append({
                "trash_name": f.name,
                "title":  fm.get("title") or f.stem,
                "source": fm.get("_trash_source", ""),
                "folder": fm.get("target_folder", ""),
                "date":   fm.get("date", ""),
            })
        except Exception:
            continue
    return jsonify(items)


@app.route("/trash/restore", methods=["POST"])
def trash_restore():
    data = request.get_json(silent=True) or {}
    name = (data.get("trash_name") or "").strip()
    if not name:
        return jsonify({"error": "trash_name required"}), 400
    src = TRASH / name
    if not src.exists():
        return jsonify({"error": "not found in trash"}), 404

    import yaml, re
    fm_re   = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    content = src.read_text(encoding="utf-8-sig")
    m       = fm_re.match(content)
    fm      = yaml.safe_load(m.group(1)) if m else {}
    fm      = fm or {}
    source  = fm.get("_trash_source", "")

    if source:
        dest = BASE / source
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Remove _trash_source from frontmatter
        fm.pop("_trash_source", None)
        body = content[m.end():] if m else content
        restored = "---\n" + yaml.dump(fm, allow_unicode=True, default_flow_style=False) + "---\n" + body
        dest.write_text(restored, encoding="utf-8")
    else:
        return jsonify({"error": "no source path in trash metadata"}), 400

    src.unlink()
    subprocess.run([PYTHON, str(BASE / "build_dashboard.py")], cwd=str(BASE), capture_output=True)
    return jsonify({"ok": True, "restored_to": source})


@app.route("/trash/purge", methods=["POST"])
def trash_purge():
    data = request.get_json(silent=True) or {}
    name = (data.get("trash_name") or "").strip()
    if not name:
        return jsonify({"error": "trash_name required"}), 400
    src = TRASH / name
    if src.exists():
        src.unlink()
    return jsonify({"ok": True})


@app.route("/note/create", methods=["POST"])
def create_note():
    data  = request.get_json(silent=True) or {}
    title  = (data.get("title")  or "").strip()
    body   = (data.get("body")   or "").strip()
    folder = (data.get("folder") or "").strip() or None
    if not body and not title:
        return jsonify({"error": "title or body required"}), 400
    text = (f"# {title}\n\n" if title else "") + body

    try:
        from classify_note import classify
        from file_note import file_note
        from datetime import date as _date
        meta = classify(text)
        if title:
            meta["title"] = title
        if folder:
            meta["target_folder"] = folder
        meta["date"] = _date.today().isoformat()

        result = file_note(text=text, markdown_body=body, meta=meta)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    subprocess.run([PYTHON, str(BASE / "build_dashboard.py")],
                   cwd=str(BASE), capture_output=True)

    threading.Thread(
        target=lambda: subprocess.run(
            [PYTHON, str(BASE / "build_embeddings.py")],
            cwd=str(BASE), capture_output=True),
        daemon=True).start()

    import os
    rel_path = os.path.relpath(result["dest_md"], str(BASE)).replace("\\", "/")
    return jsonify({"ok": True, "folder": result["folder"], "title": result["title"], "path": rel_path})


# ── Link suggestions ──────────────────────────────────────────────────────────

LINKS_REJECTED = BASE / "links_rejected.json"

def _load_rejected() -> set:
    if not LINKS_REJECTED.exists():
        return set()
    try:
        data = json.loads(LINKS_REJECTED.read_text(encoding="utf-8"))
        return {(r["a"], r["b"]) for r in data}
    except Exception:
        return set()

def _save_rejected(rejected: set):
    data = [{"a": a, "b": b} for a, b in sorted(rejected)]
    LINKS_REJECTED.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


@app.route("/links/suggest")
def links_suggest():
    threshold = float(request.args.get("threshold", 0.70))
    max_n     = min(int(request.args.get("max", 80)), 300)

    with _embed_lock:
        if not _embed_ready or _embed_matrix is None:
            return jsonify({"error": "Embeddings not ready"}), 503
        matrix = _embed_matrix.copy()
        paths  = list(_embed_paths)
        ids    = list(_embed_ids)

    import re, yaml
    wiki_re   = re.compile(r'\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]')
    rejected  = _load_rejected()

    # Build per-note metadata
    id_to_title  = {}
    id_to_links  = {}   # id → set of lowercased link targets
    id_to_tags   = {}   # id → frozenset of tags
    id_to_folder = {}   # id → top-level folder (e.g. "20-Learning")
    id_to_path   = dict(zip(ids, paths))

    for note_id, rel_path in id_to_path.items():
        note_file = BASE / rel_path
        title = Path(rel_path).stem.replace("_", " ")
        links: set = set()
        tags:  set = set()
        folder = Path(rel_path).parts[0] if Path(rel_path).parts else ""
        try:
            full = note_file.read_text(encoding="utf-8-sig")
            m    = FRONTMATTER_RE.match(full)
            body = full[m.end():] if m else full
            if m:
                fm    = yaml.safe_load(m.group(1)) or {}
                title = fm.get("title", title)
                raw_tags = fm.get("tags") or []
                if isinstance(raw_tags, list):
                    tags = {str(t).lower().strip() for t in raw_tags if t}
            for lm in wiki_re.finditer(body):
                links.add(lm.group(1).strip().lower())
        except Exception:
            pass
        id_to_title[note_id]  = title
        id_to_links[note_id]  = links
        id_to_tags[note_id]   = frozenset(tags)
        id_to_folder[note_id] = folder

    # Thresholds:
    #   same folder OR shared tags → base threshold (default 0.70)
    #   cross-folder, no shared tags → strict threshold (0.85)
    strict_threshold = max(threshold, 0.85)

    # Compute similarity matrix and collect pairs above threshold
    n   = len(ids)
    sim = matrix @ matrix.T   # (N, N)

    suggestions = []
    seen: set   = set()

    for i in range(n):
        for j in range(i + 1, n):
            score = float(sim[i, j])
            if score < threshold:
                continue
            a, b = ids[i], ids[j]
            pair = (min(a, b), max(a, b))
            if pair in seen:
                continue
            if pair in rejected:
                continue

            # Apply stricter threshold for cross-folder pairs with no shared tags
            shared_tags   = id_to_tags.get(a, frozenset()) & id_to_tags.get(b, frozenset())
            same_folder   = id_to_folder.get(a) == id_to_folder.get(b)
            if not same_folder and not shared_tags and score < strict_threshold:
                continue

            ta = id_to_title.get(a, "")
            tb = id_to_title.get(b, "")
            if tb.lower() in id_to_links.get(a, set()):
                continue
            if ta.lower() in id_to_links.get(b, set()):
                continue
            seen.add(pair)
            suggestions.append({"from_id": a, "from_title": ta,
                                 "to_id": b,   "to_title": tb,
                                 "score": round(score, 3),
                                 "shared_tags": sorted(shared_tags)})

    suggestions.sort(key=lambda s: s["score"], reverse=True)
    return jsonify({"suggestions": suggestions[:max_n], "total": len(suggestions)})


@app.route("/links/apply", methods=["POST"])
def links_apply():
    data      = request.get_json(silent=True) or {}
    from_id   = data.get("from_id")
    link_text = (data.get("link_text") or "").strip()
    if from_id is None or not link_text:
        return jsonify({"error": "from_id and link_text required"}), 400

    with _embed_lock:
        id_to_path = dict(zip(_embed_ids, _embed_paths))

    rel_path = id_to_path.get(from_id)
    if not rel_path:
        return jsonify({"error": "Note not found in embed index"}), 404

    note_file = BASE / rel_path
    if not note_file.exists():
        return jsonify({"error": "File not found"}), 404

    content = note_file.read_text(encoding="utf-8-sig")
    import re
    rel_re  = re.compile(r'(## Relacionadas\n)(.*?)(\Z)', re.DOTALL)
    link_md = f"- [[{link_text}]]"
    m       = rel_re.search(content)
    if m:
        new_content = content[:m.start(2)] + link_md + "\n" + content[m.start(2):]
    else:
        new_content = content.rstrip() + f"\n\n## Relacionadas\n{link_md}\n"

    note_file.write_text(new_content, encoding="utf-8")
    subprocess.run([PYTHON, str(BASE / "build_dashboard.py")], cwd=str(BASE), capture_output=True)
    return jsonify({"ok": True})


@app.route("/links/reject", methods=["POST"])
def links_reject():
    data    = request.get_json(silent=True) or {}
    from_id = data.get("from_id")
    to_id   = data.get("to_id")
    if from_id is None or to_id is None:
        return jsonify({"error": "from_id and to_id required"}), 400
    rejected = _load_rejected()
    rejected.add((min(from_id, to_id), max(from_id, to_id)))
    _save_rejected(rejected)
    return jsonify({"ok": True})


@app.route("/links/graph")
def links_graph():
    """Return nodes + edges for the knowledge graph."""
    import re, yaml
    wiki_re = re.compile(r'\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]')

    from build_index import load_notes
    notes    = load_notes()
    id_map   = {}   # title.lower() → note index
    note_out = []

    for i, note in enumerate(notes):
        rel = str(note["rel"]).replace("\\", "/")
        id_map[note["title"].lower()] = i
        note_out.append({"id": i, "title": note["title"],
                         "folder": note["folder_key"], "path": rel})

    edges = []
    seen_edges: set = set()
    for i, note in enumerate(notes):
        try:
            full = note["path"].read_text(encoding="utf-8-sig")
            m    = FRONTMATTER_RE.match(full)
            body = full[m.end():] if m else full
        except Exception:
            continue
        for lm in wiki_re.finditer(body):
            target = lm.group(1).strip().lower()
            j = id_map.get(target)
            if j is None or j == i:
                continue
            pair = (min(i, j), max(i, j))
            if pair in seen_edges:
                continue
            seen_edges.add(pair)
            edges.append({"source": i, "target": j})

    return jsonify({"nodes": note_out, "edges": edges})


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="KnowledgeBase local server")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    print(f"\n  KB Server  →  http://{args.host}:{args.port}")
    print(f"  Dashboard  →  http://{args.host}:{args.port}/")
    print(f"  Upload     →  POST http://{args.host}:{args.port}/upload")
    print(f"  Status     →  GET  http://{args.host}:{args.port}/status  (SSE)\n")

    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
