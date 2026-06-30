---
title: Claude API process
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["claude-api", tokenization, embedding, "request-lifecycle", "api-security"]
keywords: [API process, request lifecycle, tokenization, embedding, contextualization, generation, stop reason, max tokens, stop sequence, server architecture, API key security]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Claude API Process

Understanding the complete request lifecycle helps make better architectural decisions and debug issues more effectively.

## The Five-Step Request Flow

Every interaction with Claude follows a predictable pattern:

1. **Request to server** — your client (web/mobile app) sends a request to YOUR server
2. **Request to Anthropic API** — your server communicates with Anthropic API using the securely stored key
3. **Model processing** — Claude processes the request (tokenization → embedding → contextualization → generation)
4. **Response to server** — Anthropic API returns structured response to your server
5. **Response to client** — your server forwards the generated text back to the client

## Why You Need a Server

**Never make requests to the Anthropic API directly from client-side code.** API requests require a secret API key — exposing it in client code creates a serious security vulnerability. Anyone could extract the key and make unauthorized requests.

## Making API Requests

Every request must include:
- **API Key** — identifies your request to Anthropic
- **Model** — name of the model to use (e.g., `claude-sonnet-4-6`)
- **Messages** — list containing the user's input text
- **Max Tokens** — limit for how many tokens Claude can generate

Anthropic provides SDKs for Python, TypeScript/JavaScript, Go, and Ruby. Plain HTTP requests also work.

## Inside Claude's Processing

### Tokenization
Claude first breaks input text into tokens — whole words, parts of words, spaces, or symbols. Conceptually: ~1 word ≈ 1 token.

### Embedding
Each token gets converted into an embedding — a long list of numbers representing all possible meanings of that word. Words with multiple meanings (e.g., "quantum") produce embeddings capturing all those semantic relationships.

### Contextualization
Claude refines each embedding based on surrounding words to determine the most likely meaning in context. The numerical representations are adjusted to highlight the appropriate definition given the surrounding text.

### Generation
Contextualized embeddings pass through an output layer that calculates probabilities for each possible next word. Claude doesn't always pick the highest probability word — it uses a mix of probability and controlled randomness to create natural, varied responses. After selecting each word, Claude adds it to the sequence and repeats the entire process for the next word.

## When Claude Stops Generating

After each token, Claude checks:
- **Max tokens reached** — has it hit the limit you specified?
- **Natural ending** — did it generate an end-of-sequence token?
- **Stop sequence** — did it encounter a predefined stop phrase?

## The API Response

```json
{
  "content": [{"type": "text", "text": "...generated text..."}],
  "usage": {
    "input_tokens": 150,
    "output_tokens": 200
  },
  "stop_reason": "end_turn"
}
```

Fields returned:
- **content** — the generated text
- **usage** — count of input and output tokens (important for cost tracking)
- **stop_reason** — why generation ended (`end_turn`, `tool_use`, `max_tokens`, `stop_sequence`)

## Key Takeaways

- Design secure architectures that protect API keys (always server-side)
- Set appropriate token limits for your use case (`max_tokens` controls response length, NOT context window)
- Handle different `stop_reason` values in your application logic
- Debug by understanding which phase of the pipeline an issue occurs in
