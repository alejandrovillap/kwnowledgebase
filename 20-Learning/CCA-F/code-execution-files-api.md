---
title: Code execution and the Files API
date: 2026-04-02
type: resume
technology: "gen-ai"
status: active
tags: ["files-api", "code-execution", "anthropic-api", "docker-sandbox", "python-analysis"]
keywords: [Files API, code execution, file_id, sandbox, Docker, TTL, batch processing, data analysis, container_upload, code_execution_output, prompt caching comparison]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Code Execution and the Files API

Two Anthropic API features that work exceptionally well together, enabling complex computational delegation to Claude.

## Files API

An alternative way to handle file uploads. Instead of encoding files as base64 in every message, upload once and reference by ID.

**How it works:**
1. Upload your file (image, PDF, CSV, etc.) with a separate API call
2. Receive a `file_id` in the response metadata
3. Reference that `file_id` in future messages — no re-uploading

```python
# Step 1: Upload once
response = client.beta.files.upload(
    file=("ventas_2025.csv", open("ventas_2025.csv", "rb"), "text/csv")
)
file_id = response.id  # "file_abc123"

# Step 2: Reference in any subsequent call
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "file", "file_id": file_id}  # ← just the ID
            },
            {"type": "text", "text": "Summarize this file"}
        ]
    }]
)
```

**Supported file types:** PDF, TXT, CSV, HTML, MD, PNG, JPG, GIF, WebP.

**TTL:** files persist **30 days** or until manually deleted with `client.beta.files.delete(file_id)`.

## Code Execution Tool

A server-based tool (no implementation required from you). Include a predefined tool schema in your request and Claude can execute Python code in an isolated Docker container.

```python
chat(
    messages,
    tools=[{"type": "code_execution_20250522", "name": "code_execution"}]
)
```

**What the sandbox CAN do:** Pandas, NumPy, Matplotlib, file processing (CSV, JSON, Excel), complex math, generate visualizations as image files.

**What it CANNOT do:** network access, external API calls, persistence between sessions (sandbox destroyed after the conversation).

Claude may execute code multiple times in a single response, iteratively building up its analysis.

## Combining Both — The Full Workflow

Since Docker containers have no network access, Files API is the primary way to get data in and out of the execution environment.

```python
# 1. Upload data file
file_metadata = upload('streaming.csv')

# 2. Send to Claude with code execution enabled
messages = []
add_user_message(messages, [
    {
        "type": "text",
        "text": "Run a detailed analysis to determine major drivers of churn. Include at least one detailed plot."
    },
    {"type": "container_upload", "file_id": file_metadata.id},
])

chat(messages, tools=[{"type": "code_execution_20250522", "name": "code_execution"}])
```

**Response blocks you'll receive:**
- `text` blocks — Claude's analysis and explanations
- `server_tool_use` blocks — the actual Python code Claude ran
- `code_execution_tool_result` blocks — output from execution
- `code_execution_output` blocks — contain file IDs for generated files (plots, reports)

To download a generated visualization:
```python
download_file("file_id_from_response")
```

## Files API vs Prompt Caching

Easy to confuse — both "save things." Key differences:

| | Prompt Caching | Files API |
|---|---|---|
| **What it saves** | Processed tokens | Raw files |
| **Purpose** | Avoid reprocessing context | Avoid re-uploading files |
| **TTL** | 5 minutes | 30 days |
| **Savings** | Input token cost | Bandwidth + tokens |
| **Access** | Automatic on cache hit | Explicit by `file_id` |

## Use Cases Beyond Data Analysis

- Image processing and manipulation
- Document parsing and transformation
- Mathematical computations and modeling
- Report generation with custom formatting

## Exam Relevance

Falls in **D4 (Prompt Engineering)** and touches **D5 (Context & Reliability)**. Document Extraction Pipeline scenarios (S6) almost always involve Files API to handle large documents without exceeding the context window.

Typical exam question: *"What is the correct way to process 50 PDFs in batch?"* → **Files API** for document storage + **Message Batches API** for parallel processing + **Code Execution** if data transformation is needed.
