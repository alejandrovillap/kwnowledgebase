---
title: "MCP Client — JSON Schema & Deep Dive"
date: 2026-04-02
type: resume
technology: "gen-ai"
status: active
tags: ["mcp-client", "json-schema", "json-rpc", "tool-discovery", routing, stdio, "http-sse"]
keywords: [MCP client, JSON Schema, .mcp.json, stdio, HTTP/SSE, discovery, routing, "JSON-RPC 2.0", tool_use, required, additionalProperties, anyOf, oneOf, tool registry]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Client — JSON Schema & Deep Dive

## The 5 Internal Mechanisms

The MCP Client is the piece most underestimated because it's "invisible" — but it's the core of the entire protocol.

### 1. Discovery — `tools/list`

The first thing the MCP Client does on startup is ask every connected Server: *"what tools do you have?"*. Each Server responds with a list including name, description, and JSON Schema of parameters. The Client builds an internal **tool registry** — a map of `tool_name → Server`. This is what lets Claude "know" what tools exist without having spoken directly with the Servers.

### 2. Routing

When Claude emits a `tool_use` block with `name: "search_flights"`, the Client consults its registry and determines: *"that tool lives on Server A"*. With 3 Servers and 15 total tools, the Client resolves the correct destination without Claude knowing anything about the topology.

### 3. Serialization — JSON-RPC 2.0

The Client takes the `arguments` from Claude's `tool_use` block and wraps them in the standard JSON-RPC 2.0 envelope. The `id` field is critical — it's the identifier that correlates the response with the request, especially in streaming where fragments may arrive out of order.

### 4. Transport — stdio vs HTTP/SSE

The CCA exam evaluates this infrastructure decision:

- **`stdio`** — Server runs as a local process on the same machine. Client writes to stdin, reads from stdout. Simple, fast, no network. Ideal for development tools like Claude Code.
- **`HTTP/SSE`** — Server lives on another machine. Client sends HTTP POST, Server responds via Server-Sent Events. Enables response streaming, ideal for remote Servers or long responses.

### 5. Error Handling

The Server responds in two ways: `result` with content if successful, or `isError: true` if something failed. The Client does not silence errors — it returns them to Claude with full structure so the orchestrator can decide whether to retry, escalate to human, or inform the user. This is the D5 error propagation mechanism.

**Key exam detail:** The Client is **stateless between sessions** but **stateful during the session** — it maintains the tool registry while the session is active, but on restart it re-runs discovery from scratch.

---

## The `.mcp.json` File

`.mcp.json` tells the MCP Client what Servers exist, how to connect to them, and with what credentials — it's the directory of the entire MCP infrastructure.

### Structure

```json
{
  "mcpServers": {
    "my-server-alias": {
      "command": "node",
      "args": ["./servers/flights.js"]
    },
    "remote-api": {
      "url": "https://api.example.com/mcp"
    }
  }
}
```

The root key is always `mcpServers`. Each key is your local alias — it doesn't need to match anything internal to the Server.

### `stdio` vs `url` — the Architecture Decision

- **`stdio`** — Client **launches the process** (`node ./servers/flights.js`) and communicates via stdin/stdout. Server dies when Client dies. For local development tools.
- **`url`** — Server **already exists somewhere** — Client just points to it. Server lives independently. For external APIs, microservices, shared servers.

### Environment Variable Rule

```python
"API_KEY": "sk-real-key-here"          # ← NEVER
"API_KEY": "${AGENCIA_API_KEY}"         # ← ALWAYS
```

`${VAR}` resolves at runtime from the process's environment variables. The `.mcp.json` file can live in git without exposing any secrets. Real keys go in `.env` which is in `.gitignore`.

### Hierarchy — Project Beats Global

If `~/.mcp.json` has a Server named `payments` and the project also has one named `payments`, the project's wins for any session within that directory. Same hierarchy principle as `CLAUDE.md` — what's closest to the project has priority.

---

## JSON Schema — The Claude-Tool Contract

JSON Schema is the contract between Claude and tools. Without it, Claude doesn't know what parameters to send or in what format.

### Core Principle: Description Matters More Than Name

The most common anti-pattern and the exam's favorite: if you have 18 tools and Claude keeps picking the wrong one, the problem is almost never the name — it's that descriptions are vague or too similar. Claude doesn't search by name, it reasons by semantic description.

**Exam rule: maximum 4-5 tools per agent.** If you need more, distribute to specialized subagents.

### `required` vs Optional — The Contract is Strict

What's in `required` the Server expects without exception — if Claude doesn't send it, the Server returns an error. What's not in `required` is optional, but the Server must have a `default` value defined internally. Without a default and Claude doesn't send it: silent production bug.

**Correct defense pattern:** Schema validates before reaching the Server, AND Server has defaults for everything optional.

### Type Constraints

**String** — the trio `pattern` + `minLength` + `maxLength` works together. `enum` is preferable when the value set is closed and known — more readable than a `pattern` with alternatives.

**Array** — `uniqueItems: true` is the exam's correct answer when the question is *"how do you guarantee no duplicate airports in the layover list?"* Many people would add validation in the Server, but the correct answer is to declare it in the Schema.

**Object** — `additionalProperties: false` is critical for security. Without it, Claude could send extra fields the Server doesn't expect, causing unexpected behavior. With `false`, the Server rejects any field not declared in `properties`.

**Combiners** — most frequent exam pattern is `anyOf` with `null` for optional fields that can be explicitly absent. Difference from just not including in `required`: `anyOf: [type, null]` tells Claude the value can be intentionally null — not just omitted.

```
anyOf  →  value can match ANY of the schemas (more permissive)
oneOf  →  value must match EXACTLY ONE schema (fails if >1 match)
```

For string-or-null, always use `anyOf` — less prone to unexpected validation errors.
