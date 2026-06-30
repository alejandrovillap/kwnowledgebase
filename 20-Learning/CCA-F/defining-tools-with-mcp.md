---
title: Defining Tools with MCP
date: 2026-04-02
type: resume
technology: "gen-ai"
status: active
tags: [mcp, fastmcp, "python-sdk", "tool-definition", decorators, stdio, sse]
keywords: [MCP, tools, FastMCP, Python SDK, decorator, tool definition, allowedTools, tool_choice, stdio, SSE, "built-in tools"]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Defining Tools with MCP

## Python SDK Approach

Building an MCP server becomes simple with the official Python SDK. Instead of writing complex JSON schemas manually, the SDK handles all that complexity with decorators and type hints.

### Setting Up the MCP Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")

# Documents stored in memory
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditure",
}
```

### Creating Tools with Decorators

The `@mcp.tool` decorator automatically generates the JSON schema Claude needs. `Field` from Pydantic provides parameter descriptions.

**Tool 1 — Read a document:**
```python
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

**Tool 2 — Edit a document:**
```python
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the document's content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(description="The new text to insert in place of the old text.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
```

**Benefits of SDK approach:**
- Automatic JSON schema generation from Python type hints
- Clean, readable code
- Built-in parameter validation through Pydantic
- Reduced boilerplate vs. manual schema writing
- Type safety and IDE support

---

## Where MCP Servers Live

The MCP Server can live anywhere. "Server" describes the **architectural role**, not the physical location.

### 3 scenarios the exam distinguishes:

**Type 1 — Local with stdio:** You write a `flights.js` or `flights.py` that follows MCP protocol. The `.mcp.json` tells the Host how to launch it with `node flights.js`. The process starts on your same machine and communicates via stdin/stdout. Most common when building your own tools for a project.

**Type 2 — Remote with HTTP/SSE:** The Server already exists on some server — a travel agency API, your own cloud microservice, or an MCP Server published by Anthropic or a third party. The Host just points to its URL. It doesn't launch it, just connects.

**Type 3 — Built-in:** `Read`, `Write`, `Edit`, `Bash`, `WebSearch` — these tools are provided by Anthropic directly within Claude Code. No Server to write or configure. They simply exist.

**Decision rule:**
```
Logic is yours and runs locally  → stdio with your own Server
Logic lives in an external API   → url pointing to that Server
Operation is on files/terminal   → built-in, configure nothing
```

**Exam anti-pattern:** Using `Bash` to read a file when `Read` exists. Rule: always prefer the specific built-in over generic Bash — safer, more predictable, Claude does it better.

---

## `allowedTools` — Surgical Tool Control

`allowedTools` is the Agent SDK mechanism that tells each subagent exactly which tools it can see. The flights subagent doesn't know `send_email` exists — it's not in its list. This eliminates ambiguity by design, not by prompt.

```
allowedTools  → controls WHAT tools the agent can see
tool_choice   → controls WHEN the agent must use a tool

tool_choice: "auto"   → Claude decides (default)
tool_choice: "any"    → Claude MUST use some tool
tool_choice: "tool"   → forces a specific tool
```

**Root problem with large tool sets:** Claude doesn't "search" for the right tool like a search engine — it *reasons* by comparing each tool's description to the user's intent. With 18 tools in context, that reasoning becomes ambiguous. Longer descriptions don't solve the problem — they mask it.

**Classic exam question:**
*"Your agent has 18 tools and keeps selecting the wrong one. What do you do?"*
- ❌ Improve tool descriptions
- ❌ Upgrade to larger model  
- ❌ Add examples in system prompt
- ✅ **Reduce to 4-5 tools per agent, distribute the rest to specialized subagents with `allowedTools`**
