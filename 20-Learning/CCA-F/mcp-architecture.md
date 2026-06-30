---
title: MCP Architecture
date: 2026-04-10
type: resume
technology: "gen-ai"
status: active
tags: [mcp, architecture, "json-rpc", "client-server", tools, resources, prompts]
keywords: [MCP, architecture, host, client, server, stdio, SSE, primitives, tools, resources, prompts, lifecycle, "JSON-RPC"]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Architecture

## Architecture Overview

The Model Context Protocol (MCP) defines how AI applications connect to external services. MCP SDKs abstract many concerns, making the **data layer protocol** the most relevant section for developers — it defines how MCP servers provide context to AI applications.

## Scope

MCP includes: MCP Specification, MCP SDKs (multiple languages), MCP Development Tools (including MCP Inspector), and MCP Reference Server Implementations. MCP focuses solely on the protocol for context exchange — it does not dictate how AI applications use LLMs or manage provided context.

## Participants

MCP follows a client-server architecture:

- **MCP Host** — the AI application that coordinates and manages one or multiple MCP clients (e.g., Claude Code, Claude Desktop, VS Code)
- **MCP Client** — a component within the host that maintains a dedicated connection to one MCP server
- **MCP Server** — a program that provides context to MCP clients

One host → one client per server. Local MCP servers (stdio) typically serve a single client; remote MCP servers (Streamable HTTP) serve many clients.

## Layers

MCP consists of two layers:

- **Data layer** — JSON-RPC 2.0 based protocol for client-server communication: lifecycle management, tools, resources, prompts, notifications
- **Transport layer** — communication mechanisms: stdio (local processes) and Streamable HTTP (remote servers)

## Transport Mechanisms

```
stdio transport         → standard input/output streams, same machine, no network overhead
Streamable HTTP         → HTTP POST + optional Server-Sent Events, remote servers
                          supports OAuth, bearer tokens, API keys
```

## Data Layer Protocol — Primitives

**Server-exposed primitives:**

- **Tools** — executable functions AI can invoke (file operations, API calls, database queries)
- **Resources** — data sources providing contextual information (file contents, DB records)
- **Prompts** — reusable templates structuring LLM interactions

Each primitive type has `*/list` (discovery), `*/get` (retrieval), and `tools/call` (execution) methods. Listings are dynamic — clients discover then invoke.

**Client-exposed primitives:**

- **Sampling** — servers request LLM completions via `sampling/complete` (model-independent)
- **Elicitation** — servers request user input via `elicitation/request`
- **Logging** — servers send log messages to clients

**Cross-cutting utility:**
- **Tasks (Experimental)** — durable execution wrappers for deferred results and status tracking

## Lifecycle Management

MCP is a **stateful protocol** with 3 lifecycle phases:

```
Initialize  → capability negotiation handshake
              client sends protocolVersion + capabilities
              server responds with its capabilities
              client sends notifications/initialized when ready

Operation   → tools/list, tools/call, resources/list, resources/read
              prompts/list, prompts/get
              real-time notifications when server state changes

Shutdown    → client closes connection cleanly
```

### Capability Negotiation Example

```json
// Client → Server (initialize request)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": { "elicitation": {} },
    "clientInfo": { "name": "example-client", "version": "1.0.0" }
  }
}
// Server declares: tools (with listChanged:true) + resources
// Client sends: notifications/initialized
```

## Notifications

Real-time updates — no `id` field (no response required). Servers send `notifications/tools/list_changed` when tool availability changes. Clients re-request `tools/list` upon receiving the notification. Enables dynamic, event-driven tool discovery without polling.

## Tool Execution Flow

```
1. Client → tools/list        → discovers available tools
2. Client → tools/call        → invokes with arguments
3. Server → content array     → returns structured results
4. AI application routes result back to LLM as conversation context
```

## How AI Applications Use MCP

```python
# Initialization
async with stdio_client(server_config) as (read, write):
    async with ClientSession(read, write) as session:
        init_response = await session.initialize()
        if init_response.capabilities.tools:
            app.register_mcp_server(session, supports_tools=True)

# Tool discovery
for session in app.mcp_server_sessions():
    tools_response = await session.list_tools()
    available_tools.extend(tools_response.tools)

# Tool execution
async def handle_tool_call(conversation, tool_name, arguments):
    session = app.find_mcp_session_for_tool(tool_name)
    result = await session.call_tool(tool_name, arguments)
    conversation.add_tool_result(result.content)

# Notification handling
async def handle_tools_changed_notification(session):
    tools_response = await session.list_tools()
    app.update_available_tools(session, tools_response.tools)
```
