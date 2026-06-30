---
title: Text embeddings
date: 2026-03-26
type: resume
technology: "gen-ai"
status: active
tags: ["text-embeddings", "semantic-search", "vector-database", rag, voyageai, chunking, "cosine-similarity"]
keywords: [text embeddings, semantic search, VoyageAI, vector, cosine similarity, RAG, chunking, vector database, embedding model, "high-dimensional space"]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Text Embeddings

After breaking a document into chunks, the next RAG step is finding which chunks are most relevant to a user's question. Embeddings enable search by meaning, not by exact words.

## The Problem

You have 10,000 document chunks. A user asks *"when can I cancel?"* but the relevant chunk says *"contract termination conditions"* — different words, same meaning. Keyword search misses it. You need to search by **meaning**.

## What Is a Text Embedding

A text embedding is a numerical representation of the meaning contained in text — converting words and sentences into a format that computers can work with mathematically.

```
"termination conditions"     →  [0.23, -0.87, 0.45, 0.12, ...]
"when can I cancel?"         →  [0.21, -0.85, 0.44, 0.14, ...]
"Italian cooking recipes"    →  [0.89,  0.34, -0.67, 0.91, ...]
```

The first two vectors are very similar — similar meanings. The third is completely different.

**Key caveat:** we don't know precisely what each number in the embedding represents. The meaning of each dimension is learned during model training and isn't directly interpretable.

## The Library Analogy

Imagine a library with 10,000 books. Instead of reading each book to find the relevant one, each book has a card with coordinates on a map — books on similar topics have nearby coordinates. When you search, you convert your question into coordinates and find the nearest books on the map. No reading — just comparing positions. That's exactly what an embedding does: converts text into coordinates in a space of meaning.

## The 3 Components That Work Together

```
Text Chunking   →  divides the document into manageable pieces
Text Embedding  →  converts each piece into coordinates of meaning
Vector Database →  stores the coordinates and searches by similarity
```

- Without chunking: embeddings would be of complete documents — too general to be useful
- Without embeddings: you can only search by exact words — you miss synonym matches
- Without Vector Database: nowhere to store or efficiently search the vectors

## VoyageAI for Embeddings

Anthropic doesn't currently provide embedding generation. Recommended provider: **VoyageAI**.

```python
# .env file
VOYAGE_API_KEY="your_key_here"

# Implementation
from dotenv import load_dotenv
import voyageai

load_dotenv()
client = voyageai.Client()

def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = client.embed([text], model=model, input_type=input_type)
    return result.embeddings[0]
```

## Complete RAG Flow with Embeddings

```
PHASE 1 — Preparation (done once)

Large document
        ↓
Text Chunking — divide into sections
        ↓
Text Embedding — convert each chunk into vector
        ↓
Vector Database — store the vectors

PHASE 2 — Query (done for each question)

User asks something
        ↓
Text Embedding — convert question into vector
        ↓
Similarity search in Vector Database
        ↓
Retrieve N most similar chunks
        ↓
Context Injection — inject those chunks into Claude
        ↓
Claude responds
```

## Cosine Similarity

The mathematical measure that compares how "close" two vectors are in meaning space.

```
formula: cosine similarity = cos(θ) = (A · B) / (||A|| × ||B||)

θ = 0°   → vectors point same direction → similarity 1.0 → same meaning
θ = 90°  → perpendicular vectors        → similarity 0.0 → no relation
θ = 180° → opposite vectors             → similarity -1.0 → opposite meanings
```

**Practical thresholds:**
```
Similarity 1.0  → identical — same meaning
Similarity 0.8+ → very relevant — use them
Similarity 0.5  → related but not direct
Similarity 0.0  → no relation — discard
```

The system defines a threshold (e.g., 0.75) and only injects chunks exceeding it into Claude's context.

**Cosine Similarity vs Pearson Correlation:**
- Pearson measures linear correlation between variables; centered on the mean; detects linear relationship
- Cosine Similarity measures the angle between vectors in n-dimensional space; doesn't require centering; scales efficiently to thousands of dimensions

Cosine similarity is ideal for embeddings because vectors can have 1,536+ dimensions. Pearson would work mathematically but cosine is computationally more efficient at that scale.

## Exam Connection

The exam evaluates that you understand the complete pattern:

```
Problem:  system needs to search large documents
          by meaning, not exact words

Solution: RAG = Chunking + Embedding + Vector DB
          + Selective Context Injection
```

Connects to D5 — External Memory. The Vector Database is exactly the D5 external memory applied to documents. Claude doesn't load all documents — it queries the database and retrieves only the relevant ones.
