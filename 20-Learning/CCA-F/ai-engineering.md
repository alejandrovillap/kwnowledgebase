---
title: AI Engineering
date: 2026-03-24
type: resume
technology: "gen-ai"
status: active
tags: ["ai-engineering", llm, "foundation-models", "generative-ai", "ml-engineering", mlops]
keywords: [AI engineering, LLM, foundation models, generative AI, ML engineering, MLOps, use cases]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# AI Engineering

## Large Language Models

### Language Model Types

**Masked Language Models**
- Trained to predict missing tokens using context from both before and after
- Used for non-generative tasks: sentiment analysis, text classification
- Provide understanding of overall context (e.g., code debugging)

**Autoregressive Language Models**
- Predict the next token using preceding tokens
- Generate one token after another
- Basis for generative models

A model that can generate open-ended outputs is called **generative** — based on probabilities.

## Self-Supervision

Language models can be trained using self-supervision. Supervision requires labeled data (expensive and slow). Self-supervision doesn't require labels — the training signal comes from the data itself (predicting masked or next tokens).

## Parameters

Variables within an ML model updated through training. More parameters = greater capacity to learn desired behaviors.

GPT = **Generative Pre-trained Transformer**

Old models processed only text. Recent models (multimodal LLMs) understand images, videos, 3D assets, protein structures, etc.

Adapting an existing powerful model is easier than creating one from scratch.

## From Foundation Models to AI Engineering

Building applications on top of foundation models spans three disciplines:

- **ML Engineering** — model training and optimization
- **ML Operations (MLOps)** — deployment, monitoring, scaling
- **AI Engineering** — leveraging general-purpose AI capabilities with low barrier to entry

### Why AI Engineering is accessible now

- General-purpose AI capabilities available via API
- Increased AI investments reducing costs
- Low entrance barrier to building AI applications

## Use Cases

- Programming
- Data analysis
- Customer support
- Marketing copy
- Other copy/content
- Research
- Web design
- Art

## Use Case Categories

- **Cost reduction** — automate repetitive tasks
- **Process efficiency** — streamline workflows
- **Growth** — new product/service capabilities
- **Accelerating innovation** — faster R&D cycles
- **Business continuity** — resilience and redundancy
