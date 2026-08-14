#!/usr/bin/env python3
"""
build_embeddings.py — Generate and store semantic embeddings for all KB notes.

Uses sentence-transformers (all-MiniLM-L6-v2, ~80 MB, runs on CPU).
Embeddings are saved to embeddings.npz — a numpy archive with:
  - paths   : array of relative paths (string keys)
  - ids     : array of note IDs aligned with paths
  - matrix  : (N, 384) float32 embedding matrix

Usage:
    python build_embeddings.py           # index all notes
    python build_embeddings.py --force   # re-embed even unchanged notes
"""

import json
import argparse
import hashlib
import numpy as np
from pathlib import Path

from build_index import load_notes, BASE, FRONTMATTER_RE

EMBED_FILE  = BASE / "embeddings.npz"
HASH_FILE   = BASE / "embeddings_hashes.json"
MODEL_NAME  = "all-MiniLM-L6-v2"
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


def build_embeddings(force: bool = False) -> int:
    from sentence_transformers import SentenceTransformer

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

    print(f"[embed] Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

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
        new_vecs = model.encode(
            texts_to_embed,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True,
        )
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

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)

    data = np.load(EMBED_FILE, allow_pickle=True)
    matrix = data["matrix"].astype(np.float32)
    paths  = data["paths"].tolist()
    ids    = data["ids"].tolist()

    q_vec = model.encode([query], normalize_embeddings=True)[0].astype(np.float32)
    scores = matrix @ q_vec          # cosine similarity (normalized)
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
