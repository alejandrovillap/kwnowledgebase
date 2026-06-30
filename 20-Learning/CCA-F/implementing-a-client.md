---
title: Implementing a client
date: 2026-04-03
type: resume
technology: "gen-ai"
status: active
tags: ["mcp-client", "client-session", "tool-execution", "python-sdk", "async-programming"]
keywords: [MCP client implementation, ClientSession, list_tools, call_tool, async, Python SDK, MCPClient, tool execution, server connection]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Implementing an MCP Client

Building the client side of an MCP integration — what allows your application to communicate with an MCP server and access its functionality.

## Architecture

In most real-world projects, you build either an MCP client **OR** an MCP server — not both. Building both is for learning purposes only.

The MCP client consists of two main components:
- **MCP Client** — a custom class you create to make using the session easier
- **Client Session** — the actual connection to the server (part of the MCP Python SDK)

The session requires proper resource cleanup when done. The custom `MCPClient` class handles that cleanup automatically using context managers.

## Two Core Methods

The application needs to do exactly two things with the MCP server:
1. Get a list of available tools to send to Claude
2. Execute tools when Claude requests them

### `list_tools()`

```python
async def list_tools(self) -> list[types.Tool]:
    result = await self.session().list_tools()
    return result.tools
```

Accesses the session, calls the built-in `list_tools()` function, returns the tools from the result.

### `call_tool()`

```python
async def call_tool(
    self, tool_name: str, tool_input: dict
) -> types.CallToolResult | None:
    return await self.session().call_tool(tool_name, tool_input)
```

Passes the tool name and input parameters (provided by Claude) to the server and returns the result.

## Testing the Client

```python
async with MCPClient(
    command="uv", args=["run", "mcp_server.py"]
) as client:
    result = await client.list_tools()
    print(result)
```

Running this should print your tool definitions (e.g., `read_doc_contents` and `edit_document`).

## Complete Application Flow

When a user asks "What is the contents of the report.pdf document?":

1. Your code uses the client to **get available tools**
2. These tools are sent to Claude along with the user's question
3. Claude decides to use the `read_doc_contents` tool (`stop_reason: "tool_use"`)
4. Your code uses the client to **execute that tool**
5. The result is sent back to Claude as a `tool_result` block
6. Claude formulates the final response

The client acts as the bridge between application logic and the MCP server — accessing server functionality without worrying about underlying connection details.
