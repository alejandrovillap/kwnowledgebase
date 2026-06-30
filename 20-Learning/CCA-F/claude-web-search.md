---
title: "Claude - Web Search"
date: 2026-03-26
type: resume
technology: "gen-ai"
status: active
tags: [claude, "web-search", "api-tools", citations, "domain-filtering"]
keywords: [web search, web_search_20250305, ServerToolUseBlock, WebSearchToolResultBlock, allowed_domains, citations, CCA]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Claude - Web Search

Claude includes a built-in web search tool that lets it search the internet for current or specialized information. Unlike other tools where you need to provide the implementation, Claude handles the entire search process automatically — you just need to provide a simple schema to enable it.

## Setting Up the Web Search Tool

```json
web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5
}
```

The `max_uses` field limits how many searches Claude can perform. Claude might do follow-up searches based on initial results, so this prevents excessive API calls. A single search returns multiple results, but Claude may decide additional searches are needed.

## How the Response Works

When Claude uses the web search tool, the response contains several types of blocks:

| Block type | Purpose |
|---|---|
| **Text blocks** | Claude's explanation of what it's doing |
| **ServerToolUseBlock** | Shows the exact search query Claude used |
| **WebSearchToolResultBlock** | Contains the search results |
| **WebSearchResultBlock** | Individual results with titles and URLs |
| **Citation blocks** | Text that supports Claude's statements |

The response structure lets you see exactly what Claude searched for and which sources it found. Citations include the specific text Claude used to support its answers, along with the source URLs.

## Restricting Search Domains

You can limit searches to specific domains using `allowed_domains`:

```json
web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
    "allowed_domains": ["nih.gov"]
}
```

Useful when you want reliable, authoritative sources — e.g., restricting to `nih.gov` for medical information ensures evidence-based answers instead of random blog content.

## Rendering Search Results

Different block types are designed for specific UI rendering:
- Render text blocks as regular content
- Display web search results as a list of sources at the top
- Show citations inline with the text, including source domain, page title, URL, and quoted text

This structure helps users understand how Claude arrived at its answers and provides transparency about sources being used.

## Practical Usage

The web search tool works best for:
- Current events and recent developments
- Specialized information not in Claude's training data
- Fact-checking and finding authoritative sources
- Research tasks requiring up-to-date information

Simply include the schema in your `tools` array when making API calls, and Claude will automatically decide when a web search would help answer the user's question.
