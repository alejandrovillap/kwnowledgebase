---
title: "D2 - Tool Design & MCP Integration"
date: 2026-03-24
type: resume
technology: "gen-ai"
status: active
tags: ["tool-schema", mcp, "claude-tools", "integration-patterns", "api-design"]
keywords: [tool schema, MCP, tool design, description, integration patterns, sequential, parallel, context injection, minimal permissions, allowedTools, tool_choice]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# D2 — Tool Design & MCP Integration

## Tool Schema Design

### What is a Tool Schema?

When Claude needs to do something it can't do alone — query a database, call an API, execute code — it needs **tools**. Claude doesn't "call" a function directly; it needs an explanation, in language it understands, of what tools exist and how to use them. That explanation is the **Tool Schema**.

Think of it as a directory of phone extensions given to a new assistant: the person's name, when to call them, and what information to have ready before dialing. Without it, Claude would improvise. With it, it knows exactly which tool to use and when.

**Key insight:** Claude does NOT execute anything. Claude reads schemas, decides which to use, and produces a JSON with the call. Your code executes the function and returns the result.

```
Flow: User → Claude decides → Your code executes → Claude responds
Signal: stop_reason: "tool_use" means Claude is waiting for your code to run
```

### The 3 questions every Tool Schema must answer

- **What does it do?** → `name` field
- **When should I use it?** → `description` field  
- **What does it need?** → `input_schema` field

### Field 1: `name`
Rule: `snake_case`, verb + object, one action per tool.

| Bad | Good | Why |
|-----|------|-----|
| `orderTool` | `get_order_status` | No camelCase, explicit verb |
| `manage_orders` | `cancel_order` | "manage" is ambiguous |
| `data` | `search_products` | No context vs clear action |

Claude uses `name` as secondary hint when `description` is poor.

### Field 2: `description` — The Most Important Field
The classic trap: describing **what** the tool does instead of **when to use it**.

**Bad:** "Returns order status"
**Good:** "Use when the user wants to cancel, stop, abort, or no longer wants their order. Only applicable if the order has not yet shipped. Do NOT use for refunds or returns of delivered orders."

The 4 elements of a perfect description: **when to use** + **synonyms** (Claude connects "I don't want it" with "cancel") + **precondition** (not shipped) + **when NOT to use** (not for returns).

When Claude receives a user message, it reads all descriptions and reasons in natural language: "which tool fits best?" — exactly like reading a restaurant menu.

### Field 3: `input_schema`
JSON Schema that tells Claude what information to gather before calling the tool.

- `description` on each parameter must include the **expected format** — not just `"type": "string"`. Without it, Claude invents the format and your function fails.
- `required`: only what is strictly necessary. Inferrable fields go in `properties` but outside `required`.

```json
{
  "name": "get_order_status",
  "description": "Use when the user asks about order tracking or delivery updates",
  "input_schema": {
    "type": "object",
    "properties": {
      "order_id": {
        "type": "string",
        "description": "Order ID in format ORD-XXXX (e.g. ORD-1234)"
      }
    },
    "required": ["order_id"]
  }
}
```

---

## Model Context Protocol (MCP)

MCP is the **universal standard** that defines how any external service gives tools to Claude — like USB standardizing device connectors.

**Formal definition:** An open protocol that defines how servers expose tools, resources, and capabilities to Claude in a standardized way.

### 3 Actors (exam-specific terminology)
- **MCP Host** — the AI application using Claude (e.g., Claude.ai, Claude Code)
- **MCP Client** — the component within the Host that speaks the MCP protocol
- **MCP Server** — the external service that exposes tools (e.g., a server giving access to your database)

Relationship: Host contains Client → Client connects to Server.

### Transport mechanisms
```
stdio   → Client launches Server as child process on same machine
          Communication via standard input/output
          Use for: local tools, filesystem, same machine

SSE     → Client connects to Server over network via HTTP
(Server-Sent Events)
          Server lives elsewhere — another server, cloud, internet
          Use for: remote APIs, cloud services
```

### Lifecycle: 3 phases
```
Phase 1 — Initialize:  Client and Server present themselves
                        Exchange capabilities (what tools/resources each has)
                        Server says: "I have these tools and resources"
                        Client says: "I am this host with these capabilities"

Phase 2 — Operation:   Real work
                        Tools    → functions server executes (tool_call)
                        Resources → data server exposes (resource_read)
                        Prompts  → prompt templates server offers (prompt_get)

Phase 3 — Shutdown:    Client closes connection cleanly
```

### MCP Config files
```
.mcp.json        → project, team, in Git, shared
~/.claude.json   → personal, only me, never in Git
~ = personal     without ~ = project
```

---

## Integration Patterns

4 patterns for using tools intelligently:

### Pattern 1 — Sequential
Tools invoked in chain. Output of Tool A becomes input of Tool B. Claude waits for complete result before invoking next.

**Decision question:** Can Tool B execute without knowing Tool A's result? If yes → parallel. If no → sequential.

### Pattern 2 — Parallel
Claude invokes multiple tools simultaneously in one step. All receive parameters at the same time. Claude waits for all responses before processing results.

**Critical time detail:** total time = max (not sum). If Tool A=2s, Tool B=5s, Tool C=3s → total=5s. The bottleneck is always the slowest tool.

### Pattern 3 — Context Injection
Instead of invoking a tool to retrieve information already available when building the request, inject that information directly into the system prompt or user message.

**Decision rule:** Can this data change during the conversation? If no → inject into context. If yes → use a tool for real-time retrieval.

### Pattern 4 — Minimal Permissions
Each agent must have access **only** to the tools necessary for its specific function.

**3 reasons the exam evaluates:**
- **Security** — if a customer support agent has `delete_user` and Claude makes a reasoning error, damage is catastrophic. With minimal permissions, that error is impossible.
- **Precision** — more tools = more probability of wrong selection. 2 well-defined tools = zero ambiguity. 20 tools = noise.
- **Maintenance** — each agent has exactly what it needs → predictable, auditable, easy to debug.

### Decision Framework (exam order)
1. Do I have data I already know before calling Claude? → **Context Injection** first
2. Are the tools I need independent? → **Parallel**. If not → **Sequential**
3. Am I exposing more tools than necessary? → **Minimal Permissions**

---

## `tool_choice` and `allowedTools`

```
tool_choice: "auto"   → Claude decides whether to use a tool or respond directly (default)
tool_choice: "any"    → Claude MUST use some tool, it chooses which
tool_choice: "tool"   → forces a specific tool (deterministic flows, mandatory validation step)
  {"type": "tool", "name": "extract_metadata"}

allowedTools          → tells each subagent exactly which tools it can see
                        Subagent for flights doesn't know send_email exists → eliminates ambiguity by design
```

**tool_choice controls WHEN — allowedTools controls WHAT**

### Classic exam question
*"Your agent has 18 tools and keeps selecting the wrong one. What do you do?"*
- ❌ Improve tool descriptions
- ❌ Upgrade to larger model
- ❌ Add examples in system prompt
- ✅ **Reduce to 4-5 tools per agent and distribute the rest in specialized subagents with `allowedTools`**
