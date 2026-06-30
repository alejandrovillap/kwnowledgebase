---
title: MCP Defining prompts
date: 2026-04-08
type: resume
technology: "gen-ai"
status: active
tags: [mcp, "prompt-template", fastmcp, decorator, "slash-command", "prompt-engineering"]
keywords: [MCP prompts, prompt template, FastMCP, decorator, UserMessage, slash command, MCP Inspector, reusability, domain knowledge, prompt engineering]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Defining Prompts

Prompts in MCP servers let you define pre-built, high-quality instructions that clients can use instead of writing their own prompts from scratch. Think of them as carefully crafted templates that give better results than what users might come up with on their own.

## Why Use MCP Prompts?

Users can already ask Claude to do most tasks directly. But they'll get much better results if you provide a thoroughly tested, specialized prompt that handles edge cases and follows best practices.

As the MCP server author, you spend time crafting, testing, and evaluating prompts that work consistently across different scenarios. Users benefit from this expertise without having to become prompt engineering experts themselves.

**Key insight:** prompts let you encode domain knowledge and tested expertise into reusable templates that improve results for all clients.

## Implementation

Prompts use the same decorator pattern as tools and resources:

```python
@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""

    return [
        base.UserMessage(prompt)
    ]
```

The function returns a **list of messages** that get sent directly to Claude. You can include multiple user and assistant messages to create more complex conversation flows.

## User Experience

Users invoke prompts via slash commands in the client:
1. User types `/` to see available commands
2. Selects `format` and specifies a document ID
3. Claude uses the pre-built prompt to read and reformat the document
4. Result: clean markdown with proper headers, lists, and formatting

## Testing

Use the **MCP Inspector** to test prompts before deploying. The inspector shows exactly what messages will be sent to Claude, including how variables get interpolated into the template. Verify the prompt looks correct before users start relying on it.

## Key Benefits

- **Consistency** — users get reliable results every time
- **Expertise** — encode domain knowledge into prompts
- **Reusability** — multiple client applications can use the same prompts
- **Maintenance** — update prompts in one place to improve all clients

## When to Use Prompts vs Tools vs Resources

```
Tools     →  actions that DO something (run code, call API, modify data)
Resources →  data that Claude can READ (files, docs, databases)
Prompts   →  pre-crafted instructions that GUIDE Claude's behavior
```

Prompts work best when specialized for your MCP server's domain:
- Document management server → prompts for formatting, summarizing, analyzing
- Data analysis server → prompts for generating reports or visualizations

The goal: prompts so well-crafted that users prefer them over writing their own instructions from scratch.
