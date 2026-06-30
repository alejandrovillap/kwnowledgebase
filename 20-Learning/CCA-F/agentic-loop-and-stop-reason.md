---
title: Agentic loop and stop reason
date: 2026-03-23
type: resume
technology: "gen-ai"
status: active
tags: ["agentic-loop", "stop-reason", "tool-use", "claude-api", "agent-pattern"]
keywords: [agentic loop, stop_reason, tool_use, end_turn, max_tokens, tool execution, agent loop pattern]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Agentic Loop and Stop Reason

## Core Pattern

The agentic loop is the fundamental pattern for building Claude agents. The `stop_reason` field in Claude's response is the central decision point that drives the loop.

```python
import anthropic
client = anthropic.Anthropic()

# 1. Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Gets the weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City"}
            },
            "required": ["location"]
        }
    }
]

def execute_tool(name, tool_input):
    if name == "get_weather":
        return f"Weather in {tool_input['location']}: 22°C, sunny"

def agent_loop(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:  # The loop
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # 🔑 CENTRAL DECISION: read stop_reason
        if response.stop_reason == "end_turn":
            # Claude finished → return final text
            return response.content[0].text

        elif response.stop_reason == "tool_use":
            # Claude wants to use a tool → execute it
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # ← very important
                        "content": result
                    })

            # Add results to history and repeat the loop
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "max_tokens":
            # Tokens exhausted → handle or continue
            break
```

## stop_reason Values

```
"tool_use"   → Claude needs a tool → system executes and returns result → loop continues
"end_turn"   → Claude finished → system presents final response → loop ends
"max_tokens" → token limit reached → handle explicitly (continue or escalate)

Anti-pattern: parsing text to detect if Claude finished
```

## Key Points

- `tool_use_id` must be included in `tool_result` — used to match response to request
- Claude stops completely when it wants a tool (`stop_reason: "tool_use"`) and waits for results before continuing
- The loop runs until `end_turn` or until a stopping condition is met
- Never parse Claude's text to detect completion — always use `stop_reason`
