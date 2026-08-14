---
certification: ''
confidence: high
date: 2026-03-01
keywords:
- prompt engineering
- clear instructions
- persona
- delimiters
- subtasks
- best practices
- LLM
- prompt design
project: ''
source: notion-migration
status: active
tags:
- prompt-engineering
- prompt-design
- llm-best-practices
- clear-instructions
- persona-assignment
target_folder: 40-Reference
technology: gen-ai
title: Text Prompt Best Practices
type: reference
updated: '2026-07-31'
---
# Text Prompt Best Practices

**1. Give Clear Instructions:** Unclear prompts may result in generic or inaccurate outputs. Be sure to include relevant details, such as the desired output format and context.

**2. Assign a Persona:** Begin your prompt by assigning a specific role to the AI assistant.

Examples:
- *"You are a senior marketing professional specializing in social media campaigns…"*
- *"As a user experience expert, you are capable of…"*

**3. Use Delimiters to Structure Your Prompt:** Delimiters can help organize the prompt clearly. This example uses three quotes as delimiters:

*The following is a part of a Wikipedia article on Language Models:*

*"""A language model is a probabilistic model of a natural language. In 1980, the first significant statistical language model was proposed, and during the decade IBM performed 'Shannon-style' experiments, in which potential sources for language modeling improvement were identified by observing and analyzing the performance of human subjects in predicting or correcting text."""*

In this prompt, markdown-style ticks are used with the label "python":

*How can we make this function more efficient with lru_cache?*

```python
def fib(n):
    if n in {0, 1}:
        return n
    return fib(n-1) + fib(n-2)
```

**4. Break Tasks into Subtasks:** Divide complex tasks into manageable steps.
