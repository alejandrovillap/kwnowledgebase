#!/usr/bin/env python3
"""
build_embeddings.py — Generate and store semantic embeddings for all KB notes.

Uses Voyage AI API (voyage-3-lite). Requires VOYAGE_API_KEY in .env.
Embeddings are saved to embeddings.npz — a numpy archive with:
  - paths   : array of relative paths (string keys)
  - ids     : array of note IDs aligned with paths
  - matrix  : (N, 512) float32 embedding matrix

Usage:
    python build_embeddings.py           # index all notes
    python build_embeddings.py --force   # re-embed even unchanged notes
"""

import json
import argparse
import hashlib
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from build_index import load_notes, BASE, FRONTMATTER_RE

EMBED_FILE  = BASE / "embeddings.npz"
HASH_FILE   = BASE / "embeddings_hashes.json"
MODEL_NAME  = "voyage-3-lite"
BATCH_SIZE  = 8   # free tier: 10K TPM, ~500 tok/note → 8 notes = 4K tok/batch
MAX_CHARS   = 2000   # chars of body used per note (title + tags + excerpt)


def _note_text(note: dict) -> str:
    """Build the text that gets embedded for a note."""
    parts = [note["title"]]
    if note.get("tags"):
        parts.append(" ".join(note["tags"]))
    if note.get("type"):
        parts.append(note["type"])
    # Body excerpt
    body = ""
    try:
        full = note["path"].read_text(encoding="utf-8-sig")
        m = FRONTMATTER_RE.match(full)
        body = (full[m.end():] if m else full).strip()
    except Exception:
        pass
    parts.append(body[:MAX_CHARS])
    return "\n".join(parts)


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _voyage_embed(texts: list[str], input_type: str = "document") -> list[np.ndarray]:
    """Call Voyage AI API and return list of normalized float32 vectors."""
    import time
    import voyageai
    vo = voyageai.Client()
    vecs = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        for attempt in range(5):
            try:
                result = vo.embed(batch, model=MODEL_NAME, input_type=input_type)
                break
            except voyageai.error.RateLimitError:
                wait = 22 * (attempt + 1)
                print(f"[embed] Rate limit — esperando {wait}s...")
                time.sleep(wait)
        else:
            raise RuntimeError("Voyage AI rate limit: demasiados reintentos")
        for emb in result.embeddings:
            v = np.array(emb, dtype=np.float32)
            v /= np.linalg.norm(v) + 1e-9
            vecs.append(v)
        done = min(i + BATCH_SIZE, len(texts))
        print(f"[embed] {done}/{len(texts)} embedidos")
        if done < len(texts):
            time.sleep(21)  # respetar 3 RPM
    return vecs


def build_embeddings(force: bool = False) -> int:
    notes = load_notes()
    if not notes:
        print("[WARN] No notes found.")
        return 0

    # Load previous hashes to skip unchanged notes
    hashes: dict[str, str] = {}
    if HASH_FILE.exists() and not force:
        hashes = json.loads(HASH_FILE.read_text(encoding="utf-8"))

    # Load existing embeddings
    existing_matrix: dict[str, np.ndarray] = {}
    if EMBED_FILE.exists() and not force:
        data = np.load(EMBED_FILE, allow_pickle=True)
        for path, vec in zip(data["paths"].tolist(), data["matrix"]):
            existing_matrix[path] = vec

    texts_to_embed, paths_to_embed, ids_to_embed = [], [], []
    skip_count = 0

    for idx, note in enumerate(notes):
        rel = str(note["rel"]).replace("\\", "/")
        text = _note_text(note)
        h = _hash(text)

        if rel in hashes and hashes[rel] == h and rel in existing_matrix:
            skip_count += 1
            continue

        texts_to_embed.append(text)
        paths_to_embed.append(rel)
        ids_to_embed.append(idx)
        hashes[rel] = h

    print(f"[embed] {skip_count} notas sin cambios (skip) · {len(texts_to_embed)} a embeber")

    if texts_to_embed:
        new_vecs = _voyage_embed(texts_to_embed, input_type="document")
        for rel, vec in zip(paths_to_embed, new_vecs):
            existing_matrix[rel] = vec

    # Rebuild aligned arrays
    all_paths, all_ids, all_vecs = [], [], []
    for idx, note in enumerate(notes):
        rel = str(note["rel"]).replace("\\", "/")
        if rel in existing_matrix:
            all_paths.append(rel)
            all_ids.append(idx)
            all_vecs.append(existing_matrix[rel])

    if not all_vecs:
        print("[WARN] No embeddings generated.")
        return 0

    matrix = np.array(all_vecs, dtype=np.float32)
    np.savez_compressed(
        EMBED_FILE,
        paths=np.array(all_paths),
        ids=np.array(all_ids, dtype=np.int32),
        matrix=matrix,
    )
    HASH_FILE.write_text(json.dumps(hashes, ensure_ascii=False), encoding="utf-8")

    print(f"[embed] Guardado: {EMBED_FILE.name} — {matrix.shape[0]} notas × {matrix.shape[1]} dims")
    return matrix.shape[0]


def semantic_search(query: str, k: int = 10) -> list[dict]:
    """
    Return top-k notes most similar to query.
    Loads embeddings from disk. Call after build_embeddings().
    """
    if not EMBED_FILE.exists():
        return []

    data = np.load(EMBED_FILE, allow_pickle=True)
    matrix = data["matrix"].astype(np.float32)
    paths  = data["paths"].tolist()
    ids    = data["ids"].tolist()

    q_vecs = _voyage_embed([query], input_type="query")
    q_vec  = q_vecs[0]
    scores = matrix @ q_vec
    top_k  = np.argsort(scores)[::-1][:k]

    return [
        {"path": paths[i], "id": int(ids[i]), "score": float(scores[i])}
        for i in top_k
    ]


def main():
    ap = argparse.ArgumentParser(description="Build semantic embeddings for the KB.")
    ap.add_argument("--force", action="store_true", help="Re-embed all notes even if unchanged")
    args = ap.parse_args()
    n = build_embeddings(force=args.force)
    print(f"[OK] {n} notas indexadas.")


if __name__ == "__main__":
    main()
