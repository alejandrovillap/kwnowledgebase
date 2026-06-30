---
title: Implementing multiple turns
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["multi-turn", "conversation-loop", "tool-use", "claude-api", "stop-reason", "error-handling"]
keywords: ["multi-turn", conversation loop, tool_use, stop_reason, tool_result, tool_use_id, error handling, tool routing, run_tools]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Implementing Multiple Turns

Building a conversation system with tools requires a loop that keeps calling Claude until it stops requesting tool usage. When Claude no longer asks for tools, that signals it has a final response ready for the user.

## Detecting Tool Requests

The key to knowing whether Claude wants to use a tool lies in the **`stop_reason`** field of the response message. When Claude decides it needs to call a tool, this field is set to **`"tool_use"`**.

```python
if response.stop_reason != "tool_use":
    break  # Claude is done, no more tools needed
```

## The Conversation Loop

```python
def run_conversation(messages):
    while True:
        response = chat(messages, tools=[get_current_datetime_schema])
        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages
```

The loop continues until Claude provides a final answer without requesting any tools.

## Handling Multiple Tool Calls

Claude can request multiple tools in a single response. The message content is a list of blocks — filter for `tool_use` blocks and process each separately:

```python
def run_tools(message):
    tool_requests = [
        block for block in message.content if block.type == "tool_use"
    ]
    tool_result_blocks = []

    for tool_request in tool_requests:
        # Process each tool request...
```

## Tool Result Blocks

Each `tool_use` block must be answered with a corresponding `tool_result` block. The connection is maintained through matching IDs:

```python
tool_result_block = {
    "type": "tool_result",
    "tool_use_id": tool_request.id,   # ← must match the tool_use id
    "content": json.dumps(tool_output),
    "is_error": False
}
```

## Error Handling

When a tool fails, always provide a result block to Claude — never leave a `tool_use` unanswered:

```python
try:
    tool_output = run_tool(tool_request.name, tool_request.input)
    tool_result_block = {
        "type": "tool_result",
        "tool_use_id": tool_request.id,
        "content": json.dumps(tool_output),
        "is_error": False
    }
except Exception as e:
    tool_result_block = {
        "type": "tool_result",
        "tool_use_id": tool_request.id,
        "content": f"Error: {e}",
        "is_error": True
    }
```

## Scalable Tool Routing

For multiple tools, create a routing function that maps tool names to implementations:

```python
def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    elif tool_name == "another_tool":
        return another_tool(**tool_input)
    # Add more tools as needed
```

This keeps the core conversation logic clean regardless of how many tools you add.

## Complete Workflow

1. Send user message to Claude with available tools
2. Claude responds with text and/or tool requests
3. Execute all requested tools and create result blocks
4. Send tool results back as a user message
5. Repeat until Claude provides a final answer (`stop_reason != "tool_use"`)

The conversation history maintains complete context, allowing Claude to build upon previous tool results across multiple turns.
