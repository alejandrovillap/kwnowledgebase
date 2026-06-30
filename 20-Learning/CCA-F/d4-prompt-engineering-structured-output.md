---
title: "D4 — Prompt Engineering & Structured Output"
date: 2026-03-25
type: resume
technology: "gen-ai"
status: active
tags: ["prompt-engineering", "structured-output", claude, "system-prompt", "few-shot", "chain-of-thought", "json-schema"]
keywords: [prompt engineering, structured output, retry loop, "few-shot", chain of thought, JSON schema, XML tags, enum, system prompt, user prompt, max retries, fallback, D4]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# D4 — Prompt Engineering & Structured Output

Claude is a language model — it processes text and generates text. Its output depends directly on the quality of its input. Prompt Engineering is the discipline of writing instructions precise enough to produce **predictable and consistent** outputs in a production system.

```
Casual use    → "Summarize this document"
               Claude decides format, length, what to include

Production    → "Summarize this document in exactly 3 bullets,
               each max 15 words, focused on business decisions,
               in JSON format with key 'bullets'"
               Predictable, parseable, reliable output
```

---

## Pillar 1 — Prompt Engineering

### The 4 Techniques

**1. System vs User Prompt** — The system prompt is the permanent framework that doesn't change. The user prompt is the current task. **Exam trap:** if you put a critical restriction only in the user prompt, the user can write something that contradicts it and Claude will follow the user. Security and behavior restrictions always go in the system prompt.

**2. Few-shot Examples** — Instead of explaining the format you want, show Claude two or three examples of input → expected output. Claude infers the pattern and applies it alone. The most powerful technique when you need very specific outputs — more effective than describing the format in words.

**3. Chain of Thought** — For complex tasks requiring reasoning, ask Claude to think out loud before responding. Reduces errors because Claude verifies its own process before concluding. **When to use:** when the task has multiple logical steps or when precision is critical. *"Think step by step before responding."*

**4. Roles & Personas** — Assigning a role doesn't give Claude new capabilities, it activates existing ones with the right focus. *"You are a corporate lawyer specializing in SaaS contracts..."* doesn't turn Claude into a lawyer — it tells it to use its legal knowledge with expert tone and depth.

### The Perfect Prompt — 5 Elements

The exam gives you a bad prompt and asks what's missing. Always evaluate these five:

```
1. ROLE      → who Claude is in this task
2. CONTEXT   → what information it needs to know
3. TASK      → what it must do exactly
4. FORMAT    → how it should deliver the result
5. LIMITS    → what it must NOT do
```

**A prompt with all five produces predictable outputs. A prompt missing any leaves decisions to Claude — and Claude decides for you.**

---

## Pillar 2 — Structured Output

If your code will process Claude's output, you need Structured Output. No exceptions.

### The 3 Techniques

**1. JSON Schema** — most used in production systems. Tell Claude exactly what fields you want, in what structure, and that it should respond **only** with valid JSON. **Exam trap:** Claude sometimes adds introductory text before the JSON — *"Here's the analysis: {...}"*. Solution: *"Respond ONLY with valid JSON. No text before or after. No markdown."*

**2. XML Tags** — ideal when you need to separate sections within a longer response. Instead of pure JSON, Claude wraps each section in tags your code can easily extract. **When to prefer XML over JSON:** when a section's content is long free text — XML is more readable and manageable than JSON with escaped strings.

**3. Enum** — when a field can only have predefined values. Without enum, Claude is creative — writes "critical", "urgent", "severe" for the same thing. With enum, Claude only chooses from the defined catalog. **Exam question:** *"The system fails to classify tickets because Claude uses different values each time"* — the answer is always: add enum.

### Connection with Domain 2

```
Tool Schema       →  defines what Claude RECEIVES from your code
Structured Output →  defines what Claude DELIVERS to your code
```

Same principle, opposite direction. The `input_schema` in tool definitions and Structured Output are two sides of the same contract.

### Defense Order

```
1. Clear Structured Output  →  prevents the problem
2. Enum                     →  controls the values
3. Retry Loop               →  fixes it if it still fails
```

---

## Pillar 3 — Retry Loops

When Claude's output doesn't meet the expected format, the system detects the error, communicates it to Claude with specific context, and Claude retries.

### The Loop Pattern

```
Claude generates output
        ↓
Your code validates
        ↓
Valid? → Yes → use the output
       → No  → attempts < max_retries?
                   → Yes → retry WITH the error as context
                   → No  → explicit fallback
```

### Error as Input — The Critical Difference

```python
# BAD — same prompt each attempt
while attempt < max_retries:
    response = claude.complete(prompt)  # Claude doesn't know what to fix

# GOOD — the error as context
while attempt < max_retries:
    current_prompt = prompt + previous_error  # Claude knows exactly what to fix
```

### 3 Key Concepts

1. **Validate before using** — always verify Claude's output before processing. Don't assume Claude delivered correctly. Validation can be as simple as attempting JSON parse — if it fails, you know you need a retry.

2. **The error as input** — show Claude exactly what it delivered, what the specific error was, and what it needs to correct. Claude uses that context to self-correct.

3. **Max retries + fallback** — the loop is never infinite. Typically 3 attempts. If exhausted, fallback can be: human escalation, default value, or error log for later review. Never return `None` unhandled.

---

## The Three Pillars Connected

```
Prompt Engineering  →  tell Claude exactly what to do
        ↓
Structured Output   →  tell Claude exactly how to deliver the result
        ↓
Retry Loop          →  if it doesn't meet format, it self-corrects
```

A reliability chain: Prompt Engineering reduces error probability. Structured Output defines what an error is. Retry Loop fixes it when it occurs.
