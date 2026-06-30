---
title: RAG workflow
date: 2026-03-26
type: resume
technology: "gen-ai"
status: active
tags: ["rag-workflow", chunking, embeddings, "vector-database", "cosine-similarity", "hybrid-search", "semantic-search"]
keywords: [RAG workflow, chunking, embeddings, vector database, cosine similarity, cosine distance, BM25, lexical search, hybrid search, semantic search, normalization]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# RAG Workflow — Complete Pipeline

A step-by-step walkthrough of the complete RAG pipeline, showing how chunking, embeddings, vector search, and hybrid search work together.

## The 6-Step Pipeline

### Step 1: Chunk Your Source Text
Break the source document into manageable chunks. Example:
- Section 1: "This year saw significant strides in our understanding of XDR-47..."
- Section 2: "This division dedicated significant effort to studying various infection vectors in our distributed systems"

### Step 2: Generate Embeddings
Convert each text chunk into numerical embeddings using an embedding model.

Conceptual example (2D imaginary model):
- Medical research chunk → `[0.97, 0.34]` (very medical-focused, some software due to "bug")
- Software engineering chunk → `[0.30, 0.97]` (heavily software-focused, medical undertones from "infection vectors")

### Step 3: Normalize
The embedding API typically normalizes vectors to magnitude 1.0 automatically (unit circle). Normalized: `[0.944, 0.331]` and `[0.295, 0.955]`.

### Step 4 (prep): Store in Vector Database
Store normalized embeddings in a vector database — optimized for storing, comparing, and searching through long lists of numbers. **Pause here** — all preprocessing happens ahead of time. Now wait for a user query.

### Step 5: Process User Query
When user asks "What did the software engineering dept do this year?":
1. Run query through the same embedding model → `[0.1, 0.89]` → normalized `[0.112, 0.993]`
2. Send query embedding to vector database
3. Database returns the software engineering section (closest match)

### Step 6: Create the Final Prompt
Combine user question + most relevant chunk → send to Claude:

```
Answer the user's question about the financial document.

<user_question>
How many bugs did engineers fix this year?
</user_question>

<report>
## Section 2: Software Engineering
This division dedicated significant effort to studying various infection vectors...
</report>
```

## How Similarity Works: Cosine Similarity

The vector database uses **cosine similarity** — measures the cosine of the angle between two vectors.

```
Results range from -1 to 1
Values close to 1  → high similarity
Values close to 0  → no relationship
Values close to -1 → very different

cosine similarity = cos(θ) = (A · B) / (||A|| × ||B||)
```

In the example: query vs software engineering chunk = 0.983 (very high). Query vs medical chunk = 0.398 (much lower).

**Cosine Distance** = `1 - cosine similarity`. Values close to 0 = high similarity. Used in many vector DB docs.

**Threshold pattern:** system defines a threshold (e.g., 0.75) and only injects chunks that exceed it. Below-threshold chunks are discarded.

## Problem: Semantic Search Alone Isn't Enough

Semantic search might miss exact term matches. Example: searching for "INC-2023-Q4-011" — semantic search returns conceptually related sections but may miss the exact ID match.

## Hybrid Search: Semantic + Lexical (BM25)

**BM25 (Best Match 25)** — lexical search algorithm ideal for exact term matching in RAG systems:

1. **Tokenize** the query → ["a", "INC-2023-Q4-011"]
2. **Count term frequency** across all documents
3. **Weight by importance** — rare terms (INC-2023-Q4-011) get high weight; common words ("a") get low weight
4. **Return best matches** — documents with more instances of higher-weighted terms

```python
store = BM25Index()
for chunk in chunks:
    store.add_document({"content": chunk})

results = store.search("What happened with INC-2023-Q4-011?", 3)
```

**Hybrid strategy:** run semantic search AND lexical search in parallel, then merge results.

```
Semantic search  → finds conceptually related content (embeddings)
Lexical search   → finds exact term matches (BM25)
Merged results   → best of both for accuracy
```

BM25 excels at technical terms, IDs, and specific phrases. Semantic search excels at meaning and context. Together they cover all query types.
