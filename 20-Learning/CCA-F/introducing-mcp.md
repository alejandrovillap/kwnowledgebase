---
title: Introducing MCP
date: 2026-04-02
type: resume
technology: "gen-ai"
status: active
tags: [mcp, "model-context-protocol", "json-rpc", "claude-code", architecture, integration]
keywords: [MCP, Model Context Protocol, Host, MCP Client, MCP Server, "JSON-RPC 2.0", stdio, HTTP/SSE, tools, resources, prompts, architecture, integration]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Introducing MCP

Model Context Protocol (MCP) is a communication layer that provides Claude with context and tools without requiring you to write tedious integration code. It shifts the burden of tool definitions and execution away from your server to specialized MCP servers.

## The Problem MCP Solves

Without MCP, every integration (GitHub, Slack, databases, etc.) requires you to author tool schemas AND implement the functions yourself. For a complete GitHub integration, that means dozens of tools — repositories, pull requests, issues, projects, etc. — each requiring a schema definition and a function implementation to write, test, and maintain.

MCP shifts that burden: tool definitions and execution live inside dedicated MCP servers. You connect to them; you don't build them.

**Key insight:** MCP servers provide tool schemas and functions already defined for you, eliminating the need to build and maintain complex integrations.

## MCP Architecture — 3 Components

### Host
The application where everything lives — Claude.ai, Claude Code, or your own app built on the API. The Host contains two internal components: the LLM and the MCP Client. Users only interact with the Host.

### MCP Client
Lives inside the Host. The translator — takes Claude's decision (`"I want to execute tool X with these parameters"`) and converts it into a standardized JSON-RPC 2.0 message that any MCP Server can understand. One Client can connect to multiple Servers simultaneously. **The Client always initiates the conversation — Servers never call the Client on their own.**

### MCP Server
An independent process that exposes capabilities. Can live on the same machine (stdio communication) or on a remote server (HTTP/SSE communication). Each Server declares what it offers through three primitives:

- **Tools** — actions Claude can invoke (execute code, read a file, call an API)
- **Resources** — data Claude can read as context (a file, a DB row)
- **Prompts** — reusable instruction templates

## The Protocol

**JSON-RPC 2.0** — a mature, simple standard. The Client sends a `request` with `method` and `params`; the Server responds with `result` or `error`. That's the entire contract. Any Server that speaks JSON-RPC can connect to any Client, regardless of what language they're written in.

**The USB-C analogy:** MCP is the universal connector. Before MCP, every integration was a different proprietary cable.

## Transport Options

- **`stdio`** — Client and Server on the same machine, communicating via stdin/stdout. Simple, fast, no network. Ideal for local development tools (Claude Code, custom scripts).
- **`HTTP/SSE`** — Server lives elsewhere; Client sends HTTP POST, Server responds via Server-Sent Events. Supports streaming, ideal for remote Servers.

## Who Authors MCP Servers?

Anyone can create an MCP server. Often service providers release official implementations (e.g., AWS releasing an official MCP server for their services). You can also build your own for internal tools.

## MCP vs Direct Tool Use

MCP and tool use are complementary but different:
- **Tool use** — you write the schemas and functions yourself
- **MCP** — someone else already wrote the tool functions and schemas, packaged inside an MCP Server you connect to

MCP is about **who does the work** of creating and maintaining tools.
