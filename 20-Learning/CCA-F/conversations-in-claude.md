---
title: Conversations in Claude
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["multi-turn-conversation", stateless, "conversation-history", "context-management", "anthropic-api", claude]
keywords: ["multi-turn conversation", stateless, conversation history, messages list, helper functions, context management, CCA]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Conversations in Claude

A crucial concept when working with the Anthropic API: **Claude doesn't store any conversation history**. Each request is completely independent, with no memory of previous exchanges. If you want multi-turn conversations where Claude remembers context, you must manage the conversation state yourself.

## The Problem with Stateless Conversations

If you ask Claude "What is quantum computing?" and get a response, then follow up with "Write another sentence" — Claude has no idea what you're referring to. It will write about something completely random because it has no memory of the prior exchange.

## How Multi-Turn Conversations Work

To maintain context, you need to:
1. Maintain a list of all messages in your code
2. Send the complete message history with every request

**The correct flow:**
1. Send your initial user message to Claude
2. Take Claude's response and add it to your message list as an assistant message
3. Add your follow-up question as another user message
4. Send the entire conversation history to Claude

## Building Helper Functions

```python
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message.content[0].text
```

## Putting It All Together

```python
# Start with an empty message list
messages = []

# Add the initial user question
add_user_message(messages, "Define quantum computing in one sentence")

# Get Claude's response
answer = chat(messages)

# Add Claude's response to the conversation history
add_assistant_message(messages, answer)

# Add a follow-up question
add_user_message(messages, "Write another sentence")

# Get the follow-up response with full context
final_answer = chat(messages)
```

Now Claude understands that "Write another sentence" refers to expanding on the quantum computing definition, because the complete conversation context was provided.

> **Note:** When using tools (multi-block messages), always append `response.content` — not just extracted text — to preserve both text blocks and tool use blocks in the history.
