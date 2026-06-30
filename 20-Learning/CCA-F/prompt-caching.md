---
title: Prompt Caching
date: 2026-04-02
type: resume
technology: "gen-ai"
status: active
tags: ["prompt-caching", "cache-control", "token-cost", claude, optimization]
keywords: [prompt caching, cache_control, ephemeral, TTL, cache breakpoint, token cost, cache hit, cache miss, agentic loop]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Prompt Caching

## What is Prompt Caching?

A feature that speeds up Claude's responses and reduces cost by reusing computational work from previous requests. Instead of discarding preprocessing work after each request, Claude saves and reuses it when you send similar content again.

**The analogy:** Hiring a consultant and reading them a 500-page company manual before every call is expensive and slow. Prompt caching is like giving them the manual once — on subsequent calls they already have the context and only hear the new question.

## How It Works

Without caching, Claude does substantial preprocessing on every request: tokenization, embeddings, context analysis. All this gets discarded after each response — wasteful when follow-up requests contain the same content.

With caching, the first request writes preprocessing work to cache. Follow-up requests read from cache instead of reprocessing identical content.

## Technical Implementation

Mark cache blocks with `"cache_control": {"type": "ephemeral"}`:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "Your 50,000 tokens of context here...",
            "cache_control": {"type": "ephemeral"}  # ← marks the block
        }
    ],
    messages=[{"role": "user", "content": "Specific question?"}]
)
```

**Tool schema caching:**
```python
if tools:
    tools_clone = tools.copy()
    last_tool = tools_clone[-1].copy()
    last_tool["cache_control"] = {"type": "ephemeral"}
    tools_clone[-1] = last_tool
    params["tools"] = tools_clone
```

## Cost Impact

| Token type | Relative cost |
|-----------|--------------|
| Cache write (first time) | 25% more than normal input |
| Cache read | 90% cheaper than normal input |
| Normal (no cache) | 100% (base) |

The break-even arrives quickly if you reuse the same context 2+ times.

## Cache Rules

### Rule 1: Cache is positional — breaks at first change
Claude caches from the **beginning of the prompt to the marked point**. If any token *before* the marker changes, all cache after that point is invalidated.

```
[Stable system prompt]     ← cacheable ✅
[Context documents]        ← cacheable ✅
[Message history]          ← cacheable ✅ (if unchanged)
[New user message]         ← NEVER cached, it's dynamic
```

**Golden rule: put the most stable content first, most dynamic last.**

### Rule 2: Minimum tokens to activate cache

| Model | Minimum to cache |
|-------|-----------------|
| Claude Opus | 1,024 tokens |
| Claude Sonnet / Haiku | 2,048 tokens |

If your block is smaller than the threshold, Claude silently ignores it — no cache, no error. This is a common silent bug in production.

### Rule 3: Cache lasts 5 minutes (with renewal)
TTL is **5 minutes from last access**. Each time a request hits that cache, the clock resets. In an agent with short loops (seconds between calls), the cache practically never expires. In batch systems where jobs are spaced more than 5 minutes apart, you lose cache between jobs.

### Rule 4: Up to 4 cache breakpoints per request
```python
system=[
    {"type": "text", "text": base_instructions,
     "cache_control": {"type": "ephemeral"}},   # breakpoint 1
    {"type": "text", "text": long_documents,
     "cache_control": {"type": "ephemeral"}},   # breakpoint 2
]
```

### Rule 5: Cache is per model and per API key
- Switching from `claude-sonnet-4-6` to `claude-opus-4-6` → separate caches
- Different API keys → no shared cache, even with identical content

### Rule 6: Content must be byte-identical
For a cache hit, tokens must be **exactly the same** as the previous request. One different character = miss.

**Trap with tool definitions:** if your code generates definitions dynamically (e.g., sorting a dictionary), order may vary between calls and break the cache. Solution: always serialize tools in the same deterministic order.

### Rule 7: Cache tokens reported separately
```json
"usage": {
  "input_tokens": 12,
  "cache_creation_input_tokens": 45000,
  "cache_read_input_tokens": 45000,
  "output_tokens": 200
}
```

If you see `cache_read_input_tokens: 0` on all calls after the first, investigate why the cache is being invalidated.

## What Can Be Cached

- System prompt
- Message history
- Documents or long tools in context
- Tool definitions

**What is NOT cached:** the current `messages` (the user's real-time question)

## Correct Pattern for Multi-Turn Agent

```
[System prompt]              cache_control ✅  ← writes once
[Tool definitions]           cache_control ✅  ← writes once
[Turn 1 user + assistant]    cache_control ✅  ← extends each turn
[Turn 2 user + assistant]    cache_control ✅
[Turn N-1 ...]               cache_control ✅
[Turn N — current message]               ❌  ← no cache, it's new
```

Each new turn, move the breakpoint to the end of the accumulated history. You only pay fresh tokens for the new message — everything before reads from cache.

## Best Use Cases

- Document analysis workflows (multiple questions about the same large document)
- Iterative editing where base content is constant
- Conversations with long fixed system prompts
- Agents with multi-turn loops where tool definitions don't change

## Exam Relevance

Touches **D4 (batch cost optimization)** and **D1 (agentic loop design)**.

Typical exam scenarios: *"Why isn't this agent getting cache hits?"* — the answer is almost always one of these three:
1. Block is below minimum token threshold
2. Content is not byte-identical between calls
3. Dynamic content is mixed before the breakpoint
