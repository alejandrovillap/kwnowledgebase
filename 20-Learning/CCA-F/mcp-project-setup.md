---
title: MCP Project Setup — CLI Chatbot
date: 2026-04-02
type: project
technology: "gen-ai"
status: active
tags: [mcp, "cli-chatbot", "project-setup", uv, "anthropic-api"]
keywords: [MCP project, CLI chatbot, UV setup, main.py, mcp_client.py, mcp_server.py, read_doc_contents, edit_document, "in-memory documents", project structure, API key setup]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# MCP Project Setup — CLI Chatbot

Hands-on MCP project: building a CLI-based chatbot to understand how MCP clients and servers work together in practice.

## What We're Building

A CLI chatbot that lets users interact with a collection of documents through a command-line interface. Two main components:

- An **MCP client** that handles user interactions
- A custom **MCP server** that manages document operations

The server exposes two tools: `read_doc_contents` (read a document) and `edit_document` (update a document). All documents are stored in memory — no database required.

## Important Architecture Note

In real-world projects, you typically implement either an MCP client **or** an MCP server, not both. Options in practice:

- Build an **MCP server** to expose your service to other developers
- Build an **MCP client** to connect to existing MCP servers

Building both here is purely for educational purposes — to understand how they communicate.

## Project Setup Steps

1. Download and extract `cli_project.zip` to your preferred development directory
2. Open your code editor in the project folder
3. Add your Anthropic API key to the `.env` file
4. Install dependencies using UV (recommended) or pip
5. Run the starter application to verify everything works

## Running the Application

Navigate to the project directory in terminal. Key files: `main.py`, `mcp_client.py`, `mcp_server.py`.

```bash
# If using UV (recommended)
uv run main.py

# If using standard Python
python main.py
```

When the application starts successfully, you'll see a chat prompt. Test with a simple question like "what's 1+1?" — you should get a quick response from Claude.

## Why UV is Recommended

UV handles Python dependency resolution more reliably than pip for MCP projects, particularly for managing async dependencies and ensuring consistent environments across platforms.

## Project File Structure

| File | Role |
|---|---|
| `main.py` | Entry point — starts the chatbot loop |
| `mcp_client.py` | MCP client implementation — `list_tools()` and `call_tool()` |
| `mcp_server.py` | MCP server — exposes `read_doc_contents` and `edit_document` tools |
| `.env` | Environment variables — Anthropic API key |

## Exam Relevance

Falls in **D2 (Tool Design & MCP Integration)**. This project demonstrates the full MCP lifecycle: server declares capabilities, client discovers them via `list_tools()`, Claude selects tools based on schemas, client executes via `call_tool()`, results flow back to Claude. The `stdio` transport is used since client and server run on the same machine.
