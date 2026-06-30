---
title: MCP
date: 2026-04-08
type: resume
technology: "gen-ai"
status: active
tags: [mcp, "claude-tools", "server-primitives", "model-control", "app-control", "user-control"]
keywords: [MCP, tools, resources, prompts, "model-controlled", "app-controlled", "user-controlled", primitives]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP — Core Server Primitives

## The Three Primitives

Now that we've built our MCP server, let's review the three core server primitives and understand when to use each. The key insight: **each primitive is controlled by a different part of your application stack.**

### Tools: Model-Controlled
Tools are controlled entirely by Claude. The AI model decides when to call these functions, and results are used directly by Claude to accomplish tasks.

Tools give Claude additional capabilities it can use autonomously. When you ask Claude to "calculate the square root of 3 using JavaScript," Claude decides to use a JavaScript execution tool to run the calculation.

**Use when:** Need to give Claude new capabilities to act on.

### Resources: App-Controlled
Resources are controlled by your application code. Your app decides when to fetch resource data and how to use it — typically for UI elements or to add context to conversations.

Examples:
- Fetching data to populate autocomplete options in the UI
- Retrieving content to augment prompts with additional context
- The "Add from Google Drive" feature in Claude's interface — the app determines which documents to show and handles injecting their content into chat context

**Use when:** Need to get data into your app for UI or context injection.

### Prompts: User-Controlled
Prompts are triggered by user actions. Users decide when to run these predefined workflows through UI interactions like button clicks, menu selections, or slash commands.

Examples: The workflow buttons below Claude's chat input — predefined, optimized workflows users can start with a single click.

**Use when:** Want to create predefined workflows that users can trigger on demand.

---

## Quick Decision Guide

```
Need to give Claude new capabilities?          → Tools
Need to get data into your app for UI/context? → Resources
Want predefined workflows for users?           → Prompts
```

Each serves a different part of your application stack:
- **Tools** serve the model
- **Resources** serve your app
- **Prompts** serve your users
