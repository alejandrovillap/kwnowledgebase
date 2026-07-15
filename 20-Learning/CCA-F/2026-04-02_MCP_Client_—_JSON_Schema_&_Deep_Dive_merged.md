---
certification: CCA
confidence: high
date: '2026-04-02'
keywords:
- .mcp.json
- CCA
- CallToolRequest
- D2
- D3
- HTTP
- HTTP/SSE
- JSON Schema
- JSON-RPC
- JSON-RPC 2.0
- ListToolsRequest
- MCP
- MCP client
- WebSocket
- additionalProperties
- anyOf
- client
- discovery
- message flow
- oneOf
- required
- routing
- stdio
- tool registry
- tool_use
- transport
project: null
source: notion-migration, notion-migration, notion-migration
status: active
tags:
- client
- discovery
- http-sse
- json-rpc
- json-schema
- mcp
- mcp-client
- message-flow
- routing
- stdio
- tool-discovery
- tool-registry
- transport
target_folder: 20-Learning/CCA-F
technology: gen-ai
title: MCP Client — JSON Schema & Deep Dive
type: resume
updated: '2026-07-13'
---

The MCP Client is the communication bridge between your server and MCP servers — the most underestimated piece of the protocol because it's "invisible," yet it handles all message passing, tool discovery, routing, serialization, and error propagation so your application can focus on logic rather than protocol details.

---

## Role & Responsibilities

The MCP Client serves as the access point to all tools an MCP server provides. It abstracts away the complexity of server communication, letting you focus on application logic while still accessing powerful external tools. Despite being invisible in normal operation, it is the core of the entire protocol.

---

## 5 Internal Mechanisms

### 1. Discovery — `tools/list`

The first thing the MCP Client does at startup is ask every connected Server: *"What tools do you have?"* Each Server responds with a list including name, description, and JSON Schema of parameters. The Client builds an internal **tool registry** — a map of `tool_name → Server`. This is what allows Claude to "know" which tools exist without having talked to the Servers directly.

### 2. Routing

When Claude emits a `tool_use` block with `name: "search_flights"`, the Client consults its registry and determines: *"that tool lives on Server A."* With 3 Servers and 15 total tools, the Client resolves the correct destination without Claude knowing anything about the topology.

### 3. Serialization — JSON-RPC 2.0

The Client takes the `arguments` from Claude's `tool_use` block and wraps them in the standard JSON-RPC 2.0 envelope. The `id` field is critical — it's the identifier that correlates the response with the original request, especially in streaming where fragments may arrive out of order.

### 4. Transport — stdio vs HTTP/SSE

| Transport | Description | Best for |
|---|---|---|
| **stdio** | Server runs as local process; Client writes to stdin, reads from stdout. Simple, fast, no network. | Development tools like Claude Code |
| **HTTP/SSE** | Server lives on another machine; Client sends HTTP POST, Server responds via Server-Sent Events. Supports streaming chunks. | Remote Servers or long responses |

### 5. Error Handling

The Server responds in two ways: `result` with content if successful, or `isError: true` if something failed. The Client does **not** silence errors — it returns them to Claude with full structure so the orchestrator can decide whether to retry, escalate to a human, or inform the user. This is the D5 error propagation mechanism.

**Key detail:** The Client is **stateless between sessions** but **stateful during a session** — it maintains the tool registry while the session is active, but on restart it re-runs discovery from scratch.

---

## MCP Message Types

| Message | Direction | Purpose |
|---|---|---|
| `ListToolsRequest` | Client → Server | "What tools do you have?" |
| `ListToolsResult` | Server → Client | List of available tools with schemas |
| `CallToolRequest` | Client → Server | "Execute this tool with these arguments" |
| `CallToolResult` | Server → Client | Tool execution result |

---

## Complete Request Flow

Example: user asks "What repositories do I have?"

```
1.  User Query          → User submits question to your server
2.  Tool Discovery      → Your server needs to know available tools to send to Claude
3.  List Tools Exchange → Your server asks MCP Client for available tools
4.  MCP Communication   → MCP Client sends ListToolsRequest to MCP Server
                          MCP Server responds with ListToolsResult
5.  Claude Request      → Your server sends user query + available tools to Claude
6.  Tool Use Decision   → Claude decides it needs to call a tool (returns tool_use block)
7.  Tool Execution Req  → Your server asks MCP Client to run the tool Claude specified
8.  External API Call   → MCP Client sends CallToolRequest to MCP Server
                          MCP Server makes actual GitHub API call
9.  Results Flow Back   → GitHub responds with repo data
                          Flows back through MCP Server as CallToolResult
10. Tool Result → Claude → Your server sends tool results back to Claude
11. Final Response      → Claude formulates final answer using repo data
12. User Gets Answer    → Your server delivers Claude's response to user
```

---

## `.mcp.json` — The Infrastructure Directory

The `.mcp.json` file tells the MCP Client what Servers exist, how to connect to them, and with what credentials. It is the directory of the entire MCP infrastructure.

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

The root key is always `mcpServers`. Each key is your local alias — it doesn't need to match anything internal to the Server.

### `stdio` vs `url` — The Architecture Decision

- **`stdio`** — Client **launches the process** (`node ./servers/flights.js`) and communicates via stdin/stdout. Server dies when Client dies. Best for local development tools.
- **`url`** — Server **already exists somewhere**. Client just points to it. Server lives independently. Best for external APIs, microservices, and shared team Servers.

### The Environment Variable Rule

```json
"API_KEY": "sk-real-key-here"      ← NEVER — hardcoded secrets in git
"API_KEY": "${AGENCIA_API_KEY}"    ← ALWAYS — resolved at runtime from env vars
```

`${VAR}` resolves at runtime from the process's environment variables. The `.mcp.json` can live in git without exposing any secrets. Real keys go in `.env`, which is in `.gitignore`.

### Hierarchy — Project Wins Over Global

If `~/.mcp.json` has a Server named `payments` and the project also has one named `payments`, the project's version wins for any session within that directory. Same hierarchy principle as `CLAUDE.md` — what's closest to the project has priority.

---

## JSON Schema — The Claude-Tool Contract

JSON Schema is the contract between Claude and tools. Without it, Claude doesn't know what parameters to send or in what format.

### Core Principle: Description Matters More Than Name

The most common anti-pattern: if you have 18 tools and Claude keeps choosing the wrong one, the problem is almost never the name — it's that `description` fields are vague or too similar. Claude doesn't search by name; it reasons by semantic description.

**Exam rule: maximum 4–5 tools per agent.** If you need more, distribute into specialized subagents.

### `required` vs Optional — The Contract is Strict

- Fields in `required` → Server expects them unconditionally. If Claude doesn't send them, the Server returns an error.
- Fields not in `required` → optional, but the Server must have a `default` value defined internally. No default + Claude doesn't send it = silent bug in production.

**Defensive pattern:** Schema validates before reaching the Server, AND the Server has defaults for all optional fields.

### Type-Specific Constraints

| Type | Key constraints | Exam pattern |
|---|---|---|
| **String** | `pattern` + `minLength` + `maxLength`; use `enum` for closed value sets (more readable than pattern alternatives) | Validating IATA codes |
| **Array** | `uniqueItems: true` | "How to prevent duplicate airports in a stopover list?" → Schema, not server-side validation |
| **Object** | `additionalProperties: false` | Rejects unexpected fields — critical for security; without it, Claude could send extra fields causing unexpected behavior |
| **anyOf** | `[{type: "string"}, {type: "null"}]` | Optional fields that can be explicitly null — different from just omitting from `required` because it signals to Claude the value can be intentionally null |

### `anyOf` vs `oneOf`

- `anyOf` — passes if the value matches **one or more** of the schemas (more permissive)
- `oneOf` — fails if the value matches **more than one** schema

For string-or-null optional fields, always use `anyOf` — it's more permissive and less prone to unexpected validation errors.
