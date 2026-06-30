---
title: D1 — Agentic Architecture
date: 2026-01-01
type: resume
technology: "gen-ai"
status: active
tags: ["agentic-architecture", "multi-agent", orchestration, "hub-and-spoke", "claude-certification", "cca-exam"]
keywords: [agentic, agent, "multi-agent", "single-agent", orchestration, "hub-and-spoke", subagent, tool use, memory, RAG, pipeline, context window, routing, delegation, CCA, D1]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# D1 — Agentic Architecture (27% of CCA Exam)

## What Is an Agent?

An **agent** is a system where a model (Claude) takes a sequence of actions to complete a longer-horizon task, rather than responding to a single prompt. The model uses tools, decides what to do next based on results, and continues until the task is complete or it reaches a stopping condition.

Key distinction: a **prompt** is a single model call → response. An **agent** is a loop: observe → reason → act → observe again.

## Single-Agent Pattern

A single Claude instance that:
- Receives a task
- Selects and calls tools iteratively
- Synthesizes results
- Returns a final answer

Best for: bounded tasks with clear completion criteria, tasks that fit within a single context window, and lower complexity workflows.

## Multi-Agent Patterns

Used when tasks are too large for one context window, require parallelism, or benefit from specialization.

### Hub-and-Spoke (Orchestrator + Subagents)

The dominant pattern in the CCA exam:

```
[User] → [Orchestrator Agent]
                   ↓
    ┌──────────────┼──────────────┐
[Subagent A]  [Subagent B]  [Subagent C]
(Research)    (Summarize)   (Format)
    └──────────────┼──────────────┘
                   ↓
           [Orchestrator aggregates]
                   ↓
              [User receives result]
```

- **Orchestrator**: Plans, delegates, aggregates. Does not execute domain tasks directly.
- **Subagents**: Receive scoped tasks from the orchestrator. Each has a narrower context window and focused role.
- **Communication**: Via tool calls — the orchestrator calls subagents as tools; subagents return results as tool results.

### Sequential Pipeline

Agents pass output to the next agent in a defined sequence:
`Agent A → Agent B → Agent C → final output`

Best for: well-defined multi-step workflows with known stages (e.g., research → draft → review → format).

### Parallel Subagents

Orchestrator dispatches multiple subagents simultaneously (using batch tool calls). Results are aggregated after all return.

Best for: independent subtasks where speed matters (e.g., researching 5 topics simultaneously).

### Routing Pattern

A routing agent classifies the input and dispatches to the correct specialist agent. No aggregation needed — only one specialist is invoked per request.

## Tool Use in Agentic Contexts

Tools are how agents interact with the world. In an agentic loop:

1. Claude receives the task and available tool definitions
2. Claude issues a `tool_use` content block with `tool_use_id`, `name`, `input`
3. The system executes the tool and returns a `tool_result` content block with the same `tool_use_id`
4. Claude continues reasoning with the result in context
5. Loop continues until Claude returns a `text`-only response (no more tool calls)

**Critical**: The `tool_use_id` must match between request and result. Mismatches cause errors.

### Tool Design Principles (relevant to D1)

- Tools should be atomic and single-purpose
- Tool descriptions are part of the prompt — they consume tokens
- Too many tools degrade model performance (signal vs. noise)
- Tool schemas use JSON Schema; use `enum` for constrained inputs
- Long-running tools should have timeouts and error handling

## Memory Types

| Type | Where | Persists? | Best For |
|---|---|---|---|
| **In-context** | System/human/assistant turns | Until context window fills | Active reasoning, recent history |
| **External** | Database, vector store | Yes | Long-term facts, user preferences |
| **Cached** | Prompt cache (Anthropic) | Per cache TTL | Repeated system prompts, large documents |
| **In-weights** | Model training | Permanent | General knowledge |

In agentic systems, agents typically combine in-context (working memory) with external memory (for retrieval beyond context window).

## Retrieval-Augmented Generation (RAG) in Agents

RAG solves the context window limitation by retrieving only relevant chunks at query time.

### RAG Pipeline in an Agent

1. **Ingestion**: Documents → chunk → embed → store in vector DB
2. **Retrieval**: User query → embed → cosine similarity → top-K chunks
3. **Augmentation**: Chunks injected into Claude's prompt as context
4. **Generation**: Claude answers using retrieved context + its own knowledge

### When to Use RAG

- Knowledge base exceeds context window
- Information changes frequently (can't rely on model weights)
- Need to cite sources
- Multi-document synthesis required

### Chunking Strategy

- Chunk size: typically 256–512 tokens (matches embedding model limits)
- Overlap: 10-20% overlap between chunks to avoid cutting context at boundaries
- Metadata: store source, date, page number alongside each chunk

## Agent State Management

Agents need to track:
- **Task state**: What has been done, what remains
- **Tool state**: Results accumulated so far
- **Error state**: Failed steps, retry logic

State lives in the context window for the duration of the agent loop. For long tasks, relevant state should be summarized and compacted to avoid overflow.

## Context Window Management in Long Agentic Tasks

| Strategy | When |
|---|---|
| **Summarization** | After N turns, summarize prior history and replace with summary |
| **Sliding window** | Keep only last N messages in context |
| **External memory write** | Store completed subtask results externally, retrieve on demand |
| **Context handoff** | Pass only the relevant portion of context to subagents |

## Stopping Conditions

Agents need explicit stopping conditions:
- Task complete (model returns only text, no tool calls)
- Max iterations reached
- Error threshold exceeded
- Human-in-the-loop pause point triggered

Without stopping conditions, agents can loop indefinitely.

## Common Exam Traps — D1

- **Hub-and-spoke ≠ sequential pipeline**: Hub-and-spoke implies a central orchestrator coordinating multiple agents; sequential means output of one feeds into the next.
- **Subagents don't share context**: Each subagent starts with only what the orchestrator provides. They do not have access to the orchestrator's full context.
- **Tool descriptions cost tokens**: Poor tool descriptions that are long and vague waste context window and reduce tool selection accuracy.
- **RAG is not in-context learning**: RAG retrieves relevant text; in-context learning is when you include examples in the prompt. Different mechanisms.
- **Memory ≠ context window**: In-context memory is temporary; external memory persists across sessions.
- **tool_use_id must match**: The system must return results with the exact same `tool_use_id` as the tool call; otherwise Claude cannot correctly attribute results.
