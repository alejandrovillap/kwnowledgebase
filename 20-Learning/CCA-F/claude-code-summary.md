---
title: Claude Code Summary
date: 2026-03-24
type: resume
technology: "gen-ai"
status: active
tags: ["claude-code", "prompt-engineering", "structured-output", "retry-loop", "context-window", handoff, observability]
keywords: [Claude Code, D4, D5, prompt engineering, structured output, retry loop, context window, handoff, reliability, idempotency, observability, confidence calibration]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Claude Code Summary

## Domain 4 â€” Prompt Engineering & Structured Output

**Central concept:** In a production system, Claude must be predictable. Prompt Engineering controls what it does. Structured Output controls how it delivers. Retry Loops guarantee that if it fails, it self-corrects.

### Pillar 1 â€” Prompt Engineering

The 5 elements of the perfect prompt â€” if one is missing, Claude decides for you:

| Element | What it defines |
|---------|----------------|
| Role | Who Claude is in this task |
| Context | What information it needs to know |
| Task | What it must do exactly |
| Format | How it should deliver the result |
| Limits | What it must NOT do |

**4 techniques:**

**System vs User Prompt** â€” the system prompt is the permanent framework. The user prompt is the current task. Critical behavioral restrictions **always** in the system prompt â€” the user controls the user prompt and can contradict them.

**Few-shot Examples** â€” show instead of explain. Two or three examples of input â†’ expected output. Claude infers the pattern and applies it. More effective than describing format in words.

**Chain of Thought** â€” ask Claude to reason step by step before responding. Reduces errors in complex tasks. Use when the task has multiple logical steps or when precision is critical. *"Think step by step before responding."*

**Roles and Personas** â€” assigning a role doesn't give Claude new capabilities, it activates existing ones with the right focus. *"You are a corporate lawyer specializing in SaaS contracts..."*

### Pillar 2 â€” Structured Output

If your code will process Claude's output, you need Structured Output. No exceptions.

**JSON Schema** â€” most common in production. Claude responds only with valid JSON. Common trap: Claude adds introductory text before the JSON. Solution: *"Respond ONLY with valid JSON. No text before or after. No explanations."*

**XML Tags** â€” ideal for separating sections with long free-text content. More readable than JSON with escaped strings.

**Enum** â€” when a field can only have specific values, define them explicitly. Without enum, Claude is creative â€” writes "critical", "urgent", "severe" for the same thing. With enum, it only chooses from the defined catalog.

Defense order:
```
1. Clear Structured Output  â†’  prevents the problem
2. Enum                     â†’  controls the values
3. Retry Loop               â†’  fixes it if it still fails
```

### Pillar 3 â€” Retry Loops

When Claude's output doesn't meet expected format, the system detects the error, communicates it to Claude with specific context, and Claude retries.

```
Claude generates output
        â†“
Your code validates
        â†“
Valid? â†’ Yes â†’ use the output
       â†’ No  â†’ attempts < max_retries?
                   â†’ Yes â†’ retry WITH the error as context
                   â†’ No  â†’ explicit fallback
```

```python
# BAD â€” same prompt each attempt
while attempt < max_retries:
    response = claude.complete(prompt)  # Claude doesn't know what to fix

# GOOD â€” the error as context
while attempt < max_retries:
    current_prompt = prompt + previous_error  # Claude knows exactly what to fix
```

Max retries + fallback â€” the loop is never infinite. Typically 3 attempts. If exhausted, fallback can be: human escalation, default value, or error log. Never return `None` unhandled.

---

## Domain 5 â€” Context Management & Reliability

**Central concept:** A reliable system doesn't just work well when everything is fine â€” it works well when something fails.

### Pillar 1 â€” Context Window Management

Claude has a fixed-size desk. 4 strategies:

| Strategy | What it does | When to use |
|----------|-------------|-------------|
| Summarization | Compresses old messages into summary | Long conversation without clear structure |
| Sliding Window | Keeps only N most recent messages | Only recent content matters |
| Selective Context Injection | Injects only what's relevant for current task | Data available from the start |
| External Memory | Saves to external DB, retrieves with tool | Very long history that needs querying |

**Exam trap:** `max_tokens` controls the length of Claude's response â€” NOT the context window size. They are different parameters. Increasing `max_tokens` does NOT resolve a `ContextWindowExceededError`.

**Context leakage** â€” a subagent with access to the orchestrator's full context when it only needs its task context. Solution: isolate each subagent's context â€” give it only what it needs.

### Pillar 2 â€” Handoff Patterns

When there's a transfer of control â€” between sessions, between agents, or from Claude to human â€” the **State Snapshot** guarantees continuity.

**3 types of handoff:**
- **Session to Session** â€” work interrupted. Agent generates State Snapshot before ending. New session reads it and continues exactly where it left off.
- **Agent to Agent** â€” chain specialization. Handoff Package contains only relevant context for the receiving agent â€” not the full history of the sender. Minimal Permissions applied to context.
- **Claude to Human** â€” controlled escalation. Escalation Package gives the human everything needed to decide without reconstructing context from scratch.

**5 elements of the State Snapshot â€” always present in any handoff:**
```
â‘  Original objective of the task
â‘¡ What has been completed so far
â‘¢ What remains to be done
â‘£ Important decisions made and why
â‘¤ Concrete next step
```

### Pillar 3 â€” Reliability & Confidence Calibration

Claude communicates not just its response but how confident it is. The system uses confidence to decide when to act automatically vs. when to involve a human.

**Confidence scale:**
```
85% â€” 100%  â†’  System acts automatically
60% â€”  84%  â†’  System notifies human to confirm
 0% â€”  59%  â†’  Escalates with full Escalation Package
```

```json
{
  "decision": "approve",
  "confidence": 0.87,
  "requires_human_review": false
}
```

**3 reliability patterns:**

**Graceful Degradation** â€” if one part fails, the system continues functioning partially. The agent reports what it couldn't do instead of crashing completely.

**Idempotency** â€” executing the same action twice produces the same result as executing it once. Pattern: check in log if action was already executed BEFORE executing it again. Critical in systems with retry loops and financial actions.

**Observability** â€” log every Claude decision, what tools it called, with what parameters, and the result. Without observability you can't audit or debug. If the system produces unexpected results and you don't know why â€” you're missing observability.

### Cross-domain Connections

```
D1 when to escalate      +  D5 how to escalate with Escalation Package
D2 Minimal Permissions   +  D5 Context Isolation per subagent
D4 Retry Loop            +  D5 Idempotency so retry doesn't duplicate
D3 CLAUDE.md             +  D5 Observability to audit behavior
```

### Failure Diagnosis Framework

```
Is it a saturated context problem?      â†’ Context Window Management
Is it a state transfer problem?         â†’ Handoff Patterns
Is it a duplicated action problem?      â†’ Idempotency
Is it a decision-under-uncertainty?     â†’ Confidence Calibration
Is it a partial failure problem?        â†’ Graceful Degradation
Is it a "I don't know what happened"?   â†’ Observability
```
