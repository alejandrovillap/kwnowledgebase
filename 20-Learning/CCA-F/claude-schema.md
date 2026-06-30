---
title: Claude Schema — JSON Schema for Tool Use
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["json-schema", "claude-tools", "tool-use", "schema-generation", "type-safety", "function-documentation"]
keywords: [JSON Schema, tool schema, name description input_schema, ToolParam, type safety, schema generation, function documentation, tool description best practices]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Claude Schema — JSON Schema for Tool Use

How to write the JSON schema that tells Claude what arguments a function expects, when to use it, and how to call it correctly.

## What a Tool Schema Is

After writing a tool function, you create a JSON schema that acts as documentation Claude reads to understand the tool. JSON Schema is a widely-used data validation specification — the AI community adopted it because it cleanly describes function parameters.

**The complete tool specification has three parts:**
- `name` — a clear, descriptive name (e.g., `get_weather`)
- `description` — what the tool does, when to use it, what it returns
- `input_schema` — the actual JSON schema describing the function's arguments

## Writing Effective Descriptions

The description is the most important part for Claude's decision-making. Best practices:

- Aim for 3-4 sentences explaining what the tool does
- Describe **when Claude should use it** (not just what it does)
- Explain what kind of data it returns
- Provide detailed descriptions for each argument

## Generating Schemas with Claude

Instead of writing JSON schemas from scratch, use Claude to generate them:

1. Copy your tool function code
2. Ask Claude to write a JSON schema for tool calling
3. Include the Anthropic documentation on tool use as context
4. Claude generates a properly formatted schema following best practices

Example prompt: *"Write a valid JSON schema spec for the purposes of tool calling for this function. Follow the best practices listed in the attached documentation."*

## Implementing the Schema in Code

Use the naming pattern `function_name` / `function_name_schema` to keep schemas matched to their functions:

```python
def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)

get_current_datetime_schema = {
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            }
        },
        "required": []
    }
}
```

## Adding Type Safety with ToolParam

Import and use the `ToolParam` type from the Anthropic library for better type checking:

```python
from anthropic.types import ToolParam

get_current_datetime_schema = ToolParam({
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format",
    # ... rest of schema
})
```

Not strictly required for functionality, but prevents type errors when passing the schema to Claude's API and makes code more robust.

## Exam Relevance

Falls in **D2 (Tool Design & MCP Integration)**. Schema quality directly determines whether Claude calls the right tool at the right time. A well-written `description` acts as a prompt — it tells Claude the exact conditions under which to invoke that tool.

Key D2 rule: `required` should only include truly imprescindible fields. Optional fields with defaults keep the schema flexible without losing guidance.
