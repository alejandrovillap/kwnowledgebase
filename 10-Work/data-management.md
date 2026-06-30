---
title: Data Management — Embeddings and Vectorization
date: 2026-01-01
type: resume
technology: "gen-ai"
status: active
tags: [embeddings, vectorization, tokenization, bert, rag, "text-processing"]
keywords: [embeddings, vectorization, tokenization, "TF-IDF", BM25, Word2Vec, GLoVE, BERT, transformer encoder, chunking, 512 tokens, positional encoding, ALiBi, RoPE, MTEB, Matryoshka embedding]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Data Management — Embeddings and Vectorization

## From Text to Numbers

ML models cannot use raw text as input. Text must be tokenized and then vectorized into numerical representations.

**Tokenization:** Breaking text into smallest processable units (tokens can be words, subwords, or characters). Different tokenization strategies affect model behavior for different inputs.

**Vectorization:** Converting tokens into numerical vectors that capture meaning.

## Vectorization Approaches

### Lexical (Term-based)
**TF-IDF (Term Frequency–Inverse Document Frequency):** Importance of a term is determined by how *much* it occurs in a single document and how *little* it occurs in the corpus overall.

**BM25:** An extension of TF-IDF. Widely used for lexical/keyword search. Cannot capture semantic representations.

### Semantic (Dense)
**Word2Vec, GLoVE, fasttext:** Algorithms trained on a corpus to capture semantic relationships between words. Can learn that "king" - "man" + "woman" ≈ "queen."

### Deep Learning (Contextual)
**BERT and transformer-based encoders:** Use the *encoder* component of the transformer architecture. Pre-trained on vast data. Can be fine-tuned for specific tasks or domain data.

These contextual embeddings are used for: classification tasks, clustering, and retrieval (the basis of RAG pipelines).

## Key Limitation: Token Window

Most embedding models have a **512-token input limit** — one of the main reasons documents must be chunked before embedding.

Recent improvements through positional encoding techniques (ALiBi, RoPE algorithms) have extended this limit up to **8,192 tokens**.

## Evaluation

The **Massive Text Embedding Benchmark (MTEB)** on HuggingFace provides standardized benchmarks across models and datasets for multiple domains. Use it to compare embedding models before selecting one for a project.

## Recent Advances

- **Matryoshka embedding models:** Reduce embedding dimensions while preserving quality — important for reducing storage and computation costs at scale.
- **Quantization:** Further compresses embedding size without proportional quality loss.

## Connection to RAG

Embeddings are the foundation of the Retrieval-Augmented Generation pipeline: documents are chunked → chunks are embedded → embeddings stored in a vector database → at query time, query is embedded → cosine similarity finds nearest chunks → chunks injected as context into Claude's prompt.
