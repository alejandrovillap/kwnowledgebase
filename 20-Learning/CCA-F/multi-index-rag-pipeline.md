---
title: "Multi-Index RAG Pipeline"
date: 2026-03-26
type: concept
technology: "gen-ai"
status: active
tags: ["multi-index-rag", "retrieval-fusion", "query-routing", rrf, "vector-search", bm25, "hybrid-search"]
keywords: [RAG, "multi-index", retrieval, RRF, reciprocal rank fusion, BM25, vector search, hybrid, context injection, query router]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Multi-Index RAG Pipeline

## The Problem

A single-index RAG mixes all documents in one vector space → imprecise retrieval when queries require information from multiple specialized sources simultaneously.

**Example:** "Can I return SKU-4521 purchased 20 days ago per my premium contract?" requires: legal policy (return terms) + product data (SKU details) + support history (similar cases resolved) — all at once.

## Definition

Multi-Index RAG Pipeline is a retrieval architecture that maintains **multiple specialized indexes** — each optimized for a specific data type — plus an **orchestrator** that decides which indexes to query, executes searches in parallel, fuses results, and injects them into Claude's context.

## The 5 Components

### ① Query Router — the orchestrator
The brain. Receives the user query and decides which indexes to consult (not always all of them).

```
Router based on rules — deterministic
  if query contains SKU-XXXX → query products index
  if query mentions "contract" → query legal index
  Fast but rigid — doesn't handle ambiguous cases

Router based on LLM — flexible
  Claude reads the query and decides which indexes are relevant
  Slower but handles complex natural language
  The same Claude that responds can act as router
```

### ② Specialized indexes — each optimized for its data type

```
Data type          Optimal strategy     Why
─────────────────────────────────────────────────────
Legal documents    Semantic             Formal language with technical synonyms
Products/SKUs      Lexical              Exact IDs — SKU-4521 is exact
Support tickets    Hybrid               Mix of formal and informal language
Source code        Lexical              Function names are exact
FAQs               Semantic             Users ask differently from how it's written
Financial data     Lexical              Numbers and codes are exact
```

### ③ Parallel execution
Once the router decides which indexes to query, searches run in parallel:

```
router decides: query legal index + products index
        ↓
search_legal(query)    ┐
                       ├── parallel ──→ results from both
search_products(query) ┘

Total time = slowest index — not the sum
```

### ④ Result Fusion — Reciprocal Rank Fusion (RRF)

Scores from different indexes are incomparable (BM25 score ≠ cosine similarity). RRF normalizes using **relative rankings** instead of absolute scores.

**RRF formula:**
```
RRF_score(d) = Σ(1 / (k + rank_i(d)))
```
Where k is a constant (often 60; use 1 for clearer results).

**Example with k=1:**
- VectorIndex: Section 2 (rank 1), Section 7 (rank 2), Section 6 (rank 3)
- BM25Index: Section 6 (rank 1), Section 2 (rank 2), Section 7 (rank 3)

Scores:
- Section 2: 1/(1+1) + 1/(1+2) = 0.833 → 🥇
- Section 6: 1/(1+3) + 1/(1+1) = 0.750 → 🥈
- Section 7: 1/(1+2) + 1/(1+3) = 0.583 → 🥉

**Optional re-ranker:** evaluates each (query, chunk) pair and reorders top-K with greater precision.

### ⑤ Selective Context Injection
Inject only top-K most relevant results from each index, respecting Claude's context window limit:

```
Available context window: 10,000 tokens
Allocation by index:
  Legal    → top-3 chunks → ~2,000 tokens
  Products → top-1 chunk  → ~500 tokens
  Support  → top-2 chunks → ~1,500 tokens
  Total                   → ~4,000 tokens
  Margin for response     → ~6,000 tokens
```

## 3 Indexing Patterns

**Pattern 1 — By content type:** One index per document type (legal, products, support). Most common. Each with optimal search strategy and chunking.

**Pattern 2 — By audience:** One index for customers, one for internal agents, one for executives. Same document may appear in multiple indexes at different detail levels.

**Pattern 3 — By temporality:** One index for current documents (smaller, faster), one for historical. Recent queries go to current index; history queries go to historical.

## Problems Multi-Index RAG Solves

```
Problem                             Solution
──────────────────────────────────────────────────────
Single index mixes content types    Specialized indexes by type
Semantic search fails with IDs      Products index uses lexical
Context saturated with irrelevant   Selective context injection per index
Latency from serial searches        Parallel searches across indexes
Incomparable scores across indexes  RRF for normalized fusion
```

## Exam Scenario

*"A support agent needs to answer questions involving company policies, specific product data by SKU, and similar previous cases. The current system has all documents in a single index and responses are imprecise."*

Correct answer: Multi-Index RAG Pipeline with:
- Legal index with semantic search and clause-level chunking
- Products index with lexical search by SKU
- Tickets index with hybrid search
- Query Router deciding which indexes to consult
- Parallel searches
- RRF for result fusion
- Selective Context Injection respecting context window

## Connection to Exam Domains

```
D1 — Hub-and-spoke       Query Router = orchestrator
                         Indexes = specialized subagents

D2 — Parallel vs Serial  Parallel searches across indexes
                         Exactly the Integration Patterns pattern

D2 — Context Injection   Retrieved chunks injected directly
                         No tools needed for static data retrieval

D5 — External Memory     Each index is specialized external memory
                         Claude doesn't load everything — queries what's needed

D5 — Context Window      Selective injection prevents saturating
                         context with irrelevant chunks
```

## Implementation Sketch

```python
class Retriever:
    def __init__(self, *indexes: SearchIndex):
        if len(indexes) == 0:
            raise ValueError("At least one index must be provided")
        self._indexes = list(indexes)

    def add_document(self, document: Dict[str, Any]):
        for index in self._indexes:
            index.add_document(document)

    def search(self, query_text: str, k: int = 1, k_rrf: int = 60):
        # Get results from all indexes in parallel
        # Apply RRF scoring formula
        # Return merged and sorted results
        pass
```

The `VectorIndex` and `BM25Index` both implement the same `SearchIndex` protocol (`add_document()` + `search()`). The Retriever wraps them, enabling easy addition of new index types without tight coupling.
