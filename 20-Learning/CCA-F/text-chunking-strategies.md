---
title: Text chunking strategies
date: 2026-03-26
type: resume
technology: "gen-ai"
status: active
tags: ["text-chunking", rag, "chunk-size", overlap, "semantic-chunking", "structure-based", cca]
keywords: [text chunking, RAG, chunk size, overlap, "size-based", "structure-based", semantic, "sentence-based", context injection, CCA, D2, D5]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Text chunking strategies

Text chunking is one of the most critical steps in building a RAG pipeline. How you break up documents directly impacts the quality of the entire system. Poor chunking leads to irrelevant context being injected into prompts, causing wrong answers.

## Why it matters — La manzanita

Imagine a 200-page legal contract. You have two options:

- **Option A** — Inject all 200 pages into Claude's context → saturates the context window, thousands of unnecessary tokens, Claude processes irrelevant information.
- **Option B** — Divide the contract into small sections, find only the relevant sections for the user's question, inject only those → Claude works with precise information, context window doesn't saturate.

Option B is **text chunking**.

## How chunking fits in the RAG flow

```
Large document (200 pages)
        ↓
Text Chunking — divide into small sections
        ↓
Each chunk converted to a vector embedding
        ↓
Stored in a Vector Database
        ↓
User asks a question
        ↓
System finds the most similar chunks in the Vector Database
        ↓
Context Injection — inject only those chunks
        ↓
Claude answers based on those chunks
```

## Strategy 1: Size-Based Chunking

Divide text into strings of equal length. Simplest approach, works with any document type.

```python
def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunk_text = text[start_idx:end_idx]
        chunks.append(chunk_text)

        start_idx = (
            end_idx - chunk_overlap if end_idx < len(text) else len(text)
        )

    return chunks
```

**Downsides:** Words get cut mid-sentence, chunks lose surrounding context, section headers may separate from their content. **Overlap** between chunks addresses this — each chunk includes some characters from neighboring chunks.

## Strategy 2: Structure-Based Chunking

Divide text based on the document's natural structure — headers, paragraphs, sections. Best for well-formatted documents like Markdown.

```python
def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)
```

**Limitation:** Only works when you have guarantees about document structure. Many real-world documents are plain text or PDFs without structural markers.

## Strategy 3: Semantic-Based Chunking

Most sophisticated — divide text into sentences, then use NLP to determine relatedness between consecutive sentences. Build chunks from groups of related sentences. Computationally expensive but produces the most relevant chunks.

## Strategy 4: Sentence-Based Chunking

Practical middle ground. Split text into sentences using regex, then group them with optional overlap:

```python
def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        current_chunk = sentences[start_idx:end_idx]
        chunks.append(" ".join(current_chunk))
        start_idx += max_sentences_per_chunk - overlap_sentences
        if start_idx < 0:
            start_idx = 0

    return chunks
```

## The Three Factors That Matter

| Factor | Details |
|---|---|
| **Chunk size** | Too small → lose context. Too large → saturate Claude's context. Ideal: 500–1500 tokens depending on document type |
| **Overlap** | Chunks overlap slightly. Prevents ideas that cross two chunks from being lost |
| **Division strategy** | Divide by logical structure — contracts by clauses, manuals by sections, books by chapters |

## Choosing Your Strategy

| Use case | Recommended strategy |
|---|---|
| Controlled document formatting (internal reports) | Structure-based — best results |
| General text documents | Sentence-based — good middle ground |
| Any content type including code | Size-based — reliable fallback |

Size-based with overlap is the go-to in production: simple, reliable, works with any document type.

## CCA Exam Connection

```
D2 Context Injection  →  inject the relevant chunks
D5 External Memory    →  Vector Database is the external memory
D5 Context Window     →  chunking prevents window saturation
D4 Structured Output  →  chunks are retrieved with structured queries
```

The full RAG pattern = External Memory + Context Injection + Text Chunking.

**Typical exam scenario:** "An agent needs to answer questions about a 500-page technical manual. The system is saturating Claude's context. What is the correct architectural solution?" → RAG + chunking + selective Context Injection — not injecting the entire manual.
