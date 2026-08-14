---
certification: ''
confidence: high
date: 2026-01-01
keywords:
- SDLC
- AI augmented
- LLM
- GenAI
- deep learning
- NLP
- tokens
- prompts
- few-shot
- zero-shot
- chain of thought
- temperature
- AI phases
- software development
project: ''
source: notion-migration
status: active
tags:
- sdlc
- ai-augmented
- llm
- machine-learning
- nlp
- software-development
target_folder: 20-Learning/AI-SDLC
technology: gen-ai
title: 101 SDLC
type: resume
updated: '2026-07-31'
---
# 101 SDLC — AI-Augmented Software Development

The Software Development Life Cycle (SDLC) is the blueprint that guides the entire software creation process. Integrating AI is a transformative strategy to optimize all phases.

## Advantages of AI-Augmented SDLC

- **Boosts Efficiency** — automating repetitive tasks frees teams for higher-level work (user research, strategic planning, architecture)
- **Enhances Quality** — AI identifies defects and vulnerabilities early, enforces best practices, strengthens quality gates in CI/CD pipelines
- **Optimizes Costs** — early issue detection prevents costly rework; automation drives productivity savings
- **Fuels Innovation** — AI generates new ideas and enables faster experimentation

## AI Technology Stack

**Artificial Intelligence (AI)** — umbrella term for machines simulating human intelligence: speech recognition, NLP, text generation, decision-making.

**Machine Learning (ML)** — branch of AI detecting patterns and making predictions using algorithms and statistical techniques.

**Deep Learning (DL)** — subset of ML using multi-layered neural networks. State-of-the-art in object detection, speech recognition, language translation.

**Natural Language Processing (NLP)** — subset of AI covering human-computer language interaction. Takes human language as input, processes it, produces an action or response.

**Generative AI (GenAI)** — uses ML/deep learning to analyze massive datasets, identify patterns, and produce new original content (images, music, text, video).

**Large Language Models (LLMs)** — neural networks with many parameters trained on large text quantities. Process natural language inputs, predict next word, generate new text. Examples: ChatGPT, BERT, PaLM 2, Turing NLG.

**Small Language Models (SLMs)** — compact LLM versions, less training data, simpler architecture, faster development. Suitable for specific tasks and limited processing power. Examples: Gemma (Google), Phi-2 (Microsoft).

**GPT (Generative Pre-trained Transformer)** — uses transformer architecture pre-trained on massive text data. OpenAI's ChatGPT pioneered this approach.

## Key Concepts

### Tokens
LLMs break prompts into tokens (whole words, parts of words, punctuation). Two important considerations:
- **Token limits** — context window includes both prompt and response; check limits before use
- **Cost optimization** — some LLMs charge per token; keep prompts concise

### Knowledge Cutoff
Pre-trained transformers rely on training data cutoffs — they don't know about events after their training date and may have biases related to their training period.

## Crafting Effective Prompts — Essential Elements

- **Clarity and specificity** — clear, concise language with no room for misinterpretation
- **Role** — indicate the ideal role the LLM should take
- **Context** — provide relevant background information
- **Task instructions** — clearly state the desired action
- **Style and tone** — specify formal/informal, serious/playful
- **Formatting** — indicate preferred output format (bullets, essay, code)
- **Length** — specify desired output length if applicable
- **Examples** — include illustrative examples for creative tasks
- **Refine and iterate** — revise and test different prompts

## Prompting Techniques

**Few-shot learning** — provide a handful of examples to illustrate the desired task or outcome.

**Zero-shot learning** — no explicit examples; rely solely on clear instructions and context.

**Chain of Thought / Prompt Scaffolding** — series of interconnected prompts guiding the LLM through complex tasks step-by-step.

**Interactive engagement** — craft prompts that invite LLM responses soliciting further user input.

**Feedback loops** — provide feedback on responses, guiding the model toward desired outcomes through iterative prompting.

## Parameter Tuning (for applicable LLMs)

- **Temperature** — influences randomness/creativity. Higher = more creative but potentially less accurate.
- **Top K sampling** — limits options to top K most likely words. Lower K = less creative, more accurate.
- **Top P sampling** — focuses on word probability; ensures higher-likelihood words in context.

## SDLC Phases

1. Discovery
2. Planning
3. Analysis
4. Design
5. Development
6. Testing
