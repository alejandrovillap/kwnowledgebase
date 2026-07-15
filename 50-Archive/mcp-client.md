---
title: MCP Client
date: 2026-04-08
type: resume
technology: "gen-ai"
status: active
tags: [mcp, client, transport, stdio, "message-flow"]
keywords: [MCP, client, transport, stdio, HTTP, WebSocket, ListToolsRequest, CallToolRequest, message flow]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Client

## Role

The MCP client serves as the **communication bridge** between your server and MCP servers. It's your access point to all the tools an MCP server provides, handling message exchange and protocol details so your application doesn't have to.

## Transport Agnostic Communication

MCP is transport agnostic — the client and server can communicate over different protocols:

- **stdio** (most common) — client and server on same machine, communicating through standard input/output
- **HTTP**
- **WebSockets**
- Various other network protocols

## MCP Message Types

Once connected, client and server exchange specific message types:

**`ListToolsRequest / ListToolsResult`** — the client asks "what tools do you provide?" and receives a list of available tools.

**`CallToolRequest / CallToolResult`** — the client asks the server to run a specific tool with given arguments, then receives results.

## Complete Request Flow

Example: user asks "What repositories do I have?"

```
1.  User Query          → User submits question to your server
2.  Tool Discovery      → Your server needs to know available tools to send to Claude
3.  List Tools Exchange → Your server asks MCP client for available tools
4.  MCP Communication   → MCP client sends ListToolsRequest to MCP server
                          MCP server responds with ListToolsResult
5.  Claude Request      → Your server sends user query + available tools to Claude
6.  Tool Use Decision   → Claude decides it needs to call a tool
7.  Tool Execution Req  → Your server asks MCP client to run the tool Claude specified
8.  External API Call   → MCP client sends CallToolRequest to MCP server
                          MCP server makes actual GitHub API call
9.  Results Flow Back   → GitHub responds with repo data
                          Flows back through MCP server as CallToolResult
10. Tool Result → Claude → Your server sends tool results back to Claude
11. Final Response      → Claude formulates final answer using repo data
12. User Gets Answer    → Your server delivers Claude's response to user
```

Each component has a clear responsibility. The MCP client abstracts away the complexity of server communication, letting you focus on application logic while still accessing powerful external tools.
