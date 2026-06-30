---
title: Claude Tools — Implementation
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["claude-tools", "tool-result", "multi-turn", "conversation-loop", "api-implementation", "tool-use-id"]
keywords: [tool result block, tool_use_id, is_error, "multi-turn tools", conversation loop, run_tools, add_user_message, text_from_message, ToolParam, refactoring helpers]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Claude Tools — Implementation

Completing the tool use workflow: executing functions, returning results to Claude, and handling multi-tool multi-turn conversations.

## Sending Tool Results Back

After Claude requests a tool call, you execute the function and send the results back. This completes the loop by giving Claude the information it requested.

### Running the Tool Function

When Claude responds with a tool use block, extract the input parameters and call your function:

```python
# Access the tool parameters Claude wants to pass
response.content[1].input

# Unpack dict as keyword arguments
get_current_datetime(**response.content[1].input)
```

### Tool Result Block Structure

The result goes inside a user message as a `tool_result` block:

```python
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": response.content[1].id,  # Must match the ToolUse block ID
        "content": "15:04:22",                   # Serialized as string
        "is_error": False
    }]
})
```

**Key properties:**
- `tool_use_id` — must match the `id` of the ToolUse block this result responds to
- `content` — output from running your tool, serialized as a string
- `is_error` — set to `True` if an error occurred

### Making the Final Request

When sending the follow-up request, still include the tool schema even if no further tool call is expected — Claude needs it to understand the tool references in conversation history:

```python
client.messages.create(
    model=model,
    max_tokens=1000,
    messages=messages,
    tools=[get_current_datetime_schema]
)
```

## Handling Multiple Tool Calls

Claude can request multiple tool calls in a single response (e.g., "What's 10+10 and 30+30?" → two ToolUse blocks). Each call gets a unique ID. You must match those IDs when returning results — order doesn't matter as long as IDs align.

## Multi-Tool Conversations

For a question like "What day is 103 days from today?", Claude needs to chain two tools sequentially:

1. User asks the question
2. Claude requests `get_current_datetime`
3. Your code returns the result
4. Claude requests `add_duration_to_datetime`
5. Your code returns the result
6. Claude provides the final answer

This creates a multi-turn loop that your application must handle automatically.

### The Conversation Loop

```python
def run_conversation(messages):
    while True:
        response = chat(messages)
        add_user_message(messages, response)

        if response isn't asking for a tool:
            break

        tool_result_blocks = run_tools(response)
        add_user_message(tool_result_blocks)

    return messages
```

## Refactoring Helper Functions

### Flexible Message Handler

Update `add_user_message` to handle strings, block lists, or full Message objects:

```python
from anthropic.types import Message

def add_user_message(messages, message):
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message
    }
    messages.append(user_message)
```

### Updated Chat Function

Accept a list of tools and return the full message object:

```python
def chat(messages, system=None, temperature=1.0, stop_sequences=[], tools=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    if tools:
        params["tools"] = tools
    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message
```

### Text Extraction Helper

Extract readable text from complex message objects:

```python
def text_from_message(message):
    return "\n".join(
        [block.text for block in message.content if block.type == "text"]
    )
```

## Why These Improvements Matter

- **Flexible message handling** — helper functions work with different message formats
- **Tool support in chat** — the chat function passes tool schemas through cleanly
- **Full message returns** — complete message objects preserve all blocks (not just text)
- **Text extraction utility** — simple way to get readable output from complex responses

## Exam Relevance

Falls in **D1 (Agentic Architecture)** and **D2 (Tool Design)**. The multi-turn tool loop is the agentic loop in practice: `stop_reason: "tool_use"` → execute → return result → repeat until `stop_reason: "end_turn"`.
