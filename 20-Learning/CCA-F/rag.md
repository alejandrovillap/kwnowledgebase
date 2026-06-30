---
title: RAG
date: 2026-03-26
type: resume
technology: "gen-ai"
status: active
tags: [rag, "retrieval-augmented-generation", chunking, "context-injection", "vector-database", "prompt-stuffing"]
keywords: [RAG, retrieval augmented generation, chunking, context injection, vector database, prompt stuffing, external memory, D5, architecture pattern]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# RAG — Retrieval Augmented Generation

RAG is a technique for working with large documents that are too big to fit into a single prompt. Instead of cramming everything into one massive prompt, RAG breaks documents into chunks and only includes the most relevant pieces when answering questions.

## The Problem

Claude has knowledge up to its training cutoff — it doesn't know what happened after, nor your company's internal documents, nor your customer database. And for large documents (e.g., an 800-page financial report), there are hard limits on how much text you can include in a prompt.

## Option 1: Prompt Stuffing (Bad)

Extract all text and stuff it into your prompt along with the question. Problems:
- Hard limit on prompt length — document may be too long
- Claude becomes less effective with very long prompts
- Larger prompts cost more and take longer to process

## Option 2: RAG (Correct)

Break the document into smaller chunks during preprocessing. When a user asks a question, find the chunks most relevant to their question and include only those in the prompt.

**The flow:**

```
User asks something
        ↓
Your system searches a database
for the most relevant documents/chunks
        ↓
Inject those documents into Claude's context
        ↓
Claude responds based on those documents
— not on its training
```

## Benefits vs Challenges

**Benefits:** Claude focuses on only the most relevant content, scales to very large documents, works with multiple documents, smaller prompts cost less and run faster.

**Challenges:** requires a preprocessing step to chunk documents, need a search mechanism to find "relevant" chunks, included chunks might not contain all the context Claude needs, many chunking strategies with different trade-offs.

## When to Use RAG

RAG trades simplicity for scalability and efficiency. It's especially valuable when working with very large documents, multiple documents, or when optimizing for cost and performance. For small, stable documents — simple prompt injection may be sufficient.

## Connection to CCA Exam

RAG isn't an explicit CCA domain but appears in two scenario types:
- **Multi-Agent Research System** — an agent searching internal documents before responding uses RAG
- **Customer Support Resolution Agent** — an agent consulting the company knowledge base uses RAG

The exam asks when to use RAG as an architecture pattern, not how to implement it technically. The answer is always: when Claude needs information it doesn't have in its training that changes frequently.

## RAG vs D5 Strategies

```
RAG             = retrieve relevant documents BEFORE the question
External Memory = retrieve relevant context DURING the task

Both = Context Injection at scale — instead of static data you already have,
       you dynamically retrieve the most relevant documents from a large knowledge base
```

RAG is External Memory (D5) applied to documents.
