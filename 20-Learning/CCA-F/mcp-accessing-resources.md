---
title: MCP Accessing resources
date: 2026-04-08
type: resume
technology: "gen-ai"
status: active
tags: [mcp, resources, "context-injection", "api-design", claude]
keywords: [MCP resources, ReadResourceRequest, ReadResourceResult, MIME type, JSON parsing, TextResourceContents, URI, autocomplete, context injection]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Accessing Resources

Resources in MCP allow your server to expose information that can be directly included in prompts, rather than requiring tool calls to access data. This creates a more efficient way to provide context to AI models.

## How Resources Work

When a user types something like `@document_name`, the client:
1. Recognizes this as a resource request
2. Sends a `ReadResourceRequest` to the MCP Server
3. Gets back a `ReadResourceResult` with the actual content
4. Injects that content directly into the prompt

**Key difference from tools:** resources provide data upfront as context; tools are actions Claude triggers during generation. Resources eliminate round-trips — the content is available before Claude starts responding.

## Implementation

```python
import json
from pydantic import AnyUrl

async def read_resource(self, uri: str) -> Any:
    result = await self.session().read_resource(AnyUrl(uri))
    resource = result.contents[0]

    if isinstance(resource, types.TextResourceContents):
        if resource.mimeType == "application/json":
            return json.loads(resource.text)

    return resource.text
```

The response includes:
- **content** — the actual content (text or data)
- **mimeType** — tells you how to parse it (`application/json` → parse as JSON, otherwise → return raw text)
- Other metadata about the resource

## User Experience

Once implemented, the CLI experience with resources:
1. User types `@` to trigger the resource selector
2. Autocomplete shows available resources
3. User selects with arrow keys and space
4. Resource content is included directly in the prompt
5. Claude responds immediately without additional tool calls

This creates a much smoother experience compared to having Claude make separate tool calls to access document contents. The resource becomes part of the **initial context**.

## Resources vs Tools vs Prompts

```
Tools     →  Claude DOES something (execute, modify, call API)
Resources →  Claude READS something (context injected upfront)
Prompts   →  pre-crafted instructions that GUIDE Claude

Resources = passive data
Tools     = active actions
Prompts   = reusable templates
```

Use resources when you have data that Claude needs as context from the start, not as a result of reasoning.
