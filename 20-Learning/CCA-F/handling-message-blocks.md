---
title: Handling message blocks
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: [claude, "tool-use", api, "message-blocks", "conversation-history"]
keywords: [message blocks, tool_use, "multi-block", conversation history, ToolUseBlock, text block, API, CCA]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Handling message blocks

When working with Claude's tool functionality, you'll encounter a new type of response structure different from simple text responses. Instead of just getting back a single text block, Claude can return **multi-block messages** that contain both text and tool usage information.

## Making Tool-Enabled API Calls

To enable Claude to use tools, include a `tools` parameter in your API call:

```python
messages = []
messages.append({
    "role": "user",
    "content": "What is the exact time, formatted as HH:MM:SS?"
})

response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=messages,
    tools=[get_current_datetime_schema],
)
```

The `tools` parameter takes a list of JSON schemas that describe the available functions Claude can call.

## Understanding Multi-Block Messages

When Claude decides to use a tool, it returns an assistant message with **multiple blocks** in the content list. A multi-block message typically contains:

- **Text Block** — Human-readable text explaining what Claude is doing (e.g., "I can help you find out the current time. Let me find that information for you.")
- **ToolUse Block** — Instructions for your code about which tool to call and what parameters to use.

The ToolUse block includes:
- An ID for tracking the tool call
- The name of the function to call (e.g., `get_current_datetime`)
- Input parameters formatted as a dictionary
- The type designation `"tool_use"`

## Managing Conversation History with Multi-Block Messages

Claude doesn't store conversation history — you need to manage it manually. When working with tool responses, you must **preserve the entire content structure**, including all blocks:

```python
messages.append({
    "role": "assistant",
    "content": response.content  # preserves both text block AND tool use block
})
```

This is crucial for maintaining conversation context when you make subsequent API calls.

## The Complete Tool Usage Flow

1. Send user message with tool schema to Claude
2. Receive assistant message with text block and tool use block
3. Extract tool information and execute the actual function
4. Send tool result back to Claude along with complete conversation history
5. Receive final response from Claude

Each step requires careful handling of the message structure so Claude has full context to provide accurate responses.

## Updating Helper Functions

If you've been using helper functions like `add_user_message()` and `add_assistant_message()`, update them to handle multi-block content. The versions that only support single text blocks need to accommodate more complex content structures that include tool use blocks.
