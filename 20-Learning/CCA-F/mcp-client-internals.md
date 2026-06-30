---
title: MCP Client — Internals
date: 2026-04-02
type: resume
technology: "gen-ai"
status: active
tags: ["mcp-client", "json-rpc", "tool-registry", discovery, routing, transport]
keywords: [MCP client, discovery, routing, "JSON-RPC", stdio, HTTP/SSE, .mcp.json, JSON Schema, ListToolsRequest, CallToolRequest, tool registry, CCA, D2, D3]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Client — Internals

The MCP client is the most underestimated piece because it's "invisible" — but it's the core of the entire protocol. It serves as the communication bridge between your server and MCP servers, handling all message passing and protocol details.

## 5 Internal Mechanisms

### 1. Discovery — `tools/list`

The first thing the MCP Client does at startup is ask each connected Server: *"What tools do you have?"* Each Server responds with a list including name, description, and JSON Schema parameters. The Client builds an internal **tool registry** — a map of `tool_name → Server`. This is what allows Claude to "know" which tools exist without having talked to the Servers directly.

### 2. Routing

When Claude emits a `tool_use` block with `name: "search_flights"`, the Client consults its registry and determines: *"that tool lives on Server A."* If you have 3 Servers with 15 tools total, the Client resolves the correct destination without Claude knowing anything about the topology.

### 3. Serialization — JSON-RPC 2.0

The Client takes the `arguments` from Claude's `tool_use` block and wraps them in the standard JSON-RPC envelope. The `id` field is important — it's the identifier that correlates the response with the original request, especially in streaming where fragments may arrive out of order.

### 4. Transport — stdio vs HTTP/SSE

| Transport | Description | Best for |
|---|---|---|
| **stdio** | Server runs as local process; Client writes to stdin, reads from stdout. Simple, fast, no network. | Development tools like Claude Code |
| **HTTP/SSE** | Server lives on another server; Client sends HTTP POST, Server responds via Server-Sent Events. Supports streaming chunks. | Remote Servers or long responses |

### 5. Response Handling

The Server responds with either `result` (success) or `isError: true` (failure). The Client doesn't silence errors — it returns them to Claude with full structure so the orchestrator can decide whether to retry, escalate to a human, or inform the user. This is the D5 error propagation mechanism.

**Key exam detail:** The Client is **stateless between sessions** but **stateful during a session** — it maintains the tool registry while the session is active, but if you restart, it does discovery again from scratch.

## Message Types

| Message | Direction | Purpose |
|---|---|---|
| `ListToolsRequest` | Client → Server | "What tools do you have?" |
| `ListToolsResult` | Server → Client | List of available tools with schemas |
| `CallToolRequest` | Client → Server | "Execute this tool with these arguments" |
| `CallToolResult` | Server → Client | Tool execution result |

## Complete Flow (Example: "What repositories do I have?")

1. User submits query to your server
2. Your server asks MCP Client for tools → `ListToolsRequest` → `ListToolsResult`
3. Your server makes request to Claude with user question + available tools
4. Claude decides it needs a tool → returns `tool_use` block
5. Your server asks MCP Client to execute the tool → `CallToolRequest` → Server calls GitHub → `CallToolResult`
6. Your server sends tool results back to Claude
7. Claude responds with the formatted answer → your server passes it to the user

---

## `.mcp.json` — The Infrastructure Directory

The `.mcp.json` file tells the MCP Client what Servers exist, how to connect to them, and with what credentials. It's the directory of the entire MCP infrastructure.

### Structure

```json
{
  "mcpServers": {
    "flights": {
      "command": "node",
      "args": ["./servers/flights.js"],
      "env": {
        "API_KEY": "${AGENCIA_API_KEY}"
      }
    },
    "remote-payments": {
      "url": "https://payments-api.company.com/mcp"
    }
  }
}
```

### stdio vs url — Architecture Decision

- `stdio` — Client **launches the process**. The Server dies when the Client dies. Best for local development tools.
- `url` — Server **already exists somewhere**. The Client just points to it. Best for external APIs, microservices, shared team Servers.

### The Environment Variable Rule

```json
"API_KEY": "sk-real-key-here"    ← NEVER — hardcoded secrets in git
"API_KEY": "${AGENCIA_API_KEY}"  ← ALWAYS — resolved at runtime from env vars
```

The `.mcp.json` can live in git without exposing any secrets. Real keys go in `.env` which is in `.gitignore`.

### Hierarchy — Project wins over global

If `~/.mcp.json` has a Server named `payments` and the project also has one named `payments`, the project's version wins for any session in that directory. Same hierarchy principle as `CLAUDE.md` — closest to the project has priority.

---

## JSON Schema — The Tool Contract

JSON Schema is the contract between Claude and tools. Without it, Claude doesn't know what parameters to send or in what format.

### Why `description` is more important than `name`

The most common anti-pattern and exam favorite: if you have 18 tools and Claude keeps choosing the wrong one, the problem is almost never the name — it's that the `description` fields are vague or too similar. Claude doesn't search by name; it reasons by semantic description.

**Max 4–5 tools per agent.** If you need more, distribute into specialized subagents.

### `required` vs optional — strict contract

- Fields in `required` → Server expects them unconditionally. If Claude doesn't send them, the Server returns an error.
- Fields not in `required` → optional, but the Server must have a default value internally. No default + Claude doesn't send it = silent bug in production.

**Defensive pattern:** Schema validates before reaching the Server, AND the Server has defaults for all optional fields.

### Type-specific constraints

| Type | Key constraints | Exam pattern |
|---|---|---|
| **String** | `pattern` + `minLength` + `maxLength`; use `enum` for closed value sets | Validating IATA codes |
| **Array** | `uniqueItems: true` | "How to prevent duplicate airports in a stopover list?" → Schema, not server-side validation |
| **Object** | `additionalProperties: false` | Rejects unexpected fields — critical for security |
| **anyOf** | `[{type: "string"}, {type: "null"}]` | Optional fields that can be explicitly null |

### `anyOf` vs `oneOf`

- `anyOf` — passes if the value matches **one or more** of the schemas (more permissive)
- `oneOf` — fails if the value matches **more than one** schema

For string-or-null optional fields, always use `anyOf` — it's more permissive and less prone to unexpected validation errors.
