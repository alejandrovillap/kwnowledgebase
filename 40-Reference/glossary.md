---
title: "Glossary — AI & Project Risk"
date: 2026-01-01
type: reference
technology: "gen-ai"
status: active
tags: [glossary, "ai-terms", "ml-definitions", "risk-management", "llm-concepts"]
keywords: [glossary, AI terms, confabulation, hallucination, context window, embeddings, LLM agent, "fine-tuning", red teaming, reinforcement learning, "few-shot learning", model card, risk management, VUCA]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Glossary — AI & Project Risk

Key terms across AI/ML and project risk management domains.

## AI / ML Terms

**Adversarial Attacks:** Deliberate attempts to manipulate AI systems, exploiting vulnerabilities to cause malfunctions, incorrect outputs, or unintended behaviors.

**Artificial Intelligence (AI):** A machine-based system that can, for human-defined objectives, make predictions, recommendations, or decisions influencing real or virtual environments. (15 U.S. Code § 9401)

**Chain of Thought (CoT):** Method for unlocking reasoning in LLMs by encouraging step-by-step thinking. Benefits are most pronounced in large models (100B+ parameters).

**Confabulation:** An LLM generating output that is not based on real-world input — false, nonsensical, or nonexistent references — often presented confidently. Preferred over "hallucinate" among AI researchers as it avoids anthropomorphizing the technology.

**Context Window:** The maximum amount of text an AI model can process at one time, measured in tokens. Represents the model's "working memory."

**Data Augmentation:** Artificially generating new data from existing data by making small modifications (geometric transformations for images, word replacements for text) to expand training datasets.

**Dataset Contamination:** Unintended overlap between training data and evaluation datasets, causing overestimation of a model's generalization capabilities.

**Deep Learning:** A subset of ML using neural networks with multiple layers to automatically learn hierarchical representations of data.

**Embeddings:** Numerical vector representations of data that capture relationships and features in a lower-dimensional space. Used to encode words, images, or graphs for ML processing.

**Few-Shot Learning:** Providing examples of expected inputs and outputs in the model's context window, improving performance by leveraging the autoregressive nature of LLMs.

**Fine-Tuning:** Adapting a pre-trained model to perform specific tasks by training further on task-specific data. Typically a supervised learning task.

**Foundation Model (LxM):** A model trained on vast datasets applicable across a wide range of use cases.

**Generative Pre-Trained Transformer (GPT):** A neural network based on the transformer architecture, pre-trained on large unlabeled text datasets, able to generate novel human-like content.

**Hallucinate:** An incorrect response or false information from an AI system presented as factual.

**Large Language Model (LLM):** A neural model trained on vast text data to understand and generate language.

**LLM Agent:** An advanced AI system using LLMs to perform complex tasks, make decisions, and interact autonomously. Four components: LLM core, Planning, Memory, Tool Use.

**Model Card:** Short document accompanying an ML model that provides benchmarked evaluation across conditions, intended use context, performance evaluation procedures, and other relevant information.

**Natural Language Processing (NLP):** AI subfield enabling computers to understand, interpret, generate, and work with human language.

**One-Shot Learning:** Training a model to recognize new patterns after being exposed to a single example.

**Red Teaming:** In AI context: rapidly or continuously testing a model by evaluators under conditions other than normal operation, analogous to penetration testing.

**Reinforcement Learning:** ML where an agent learns by interacting with an environment and optimizing a reward function.

**Self-Supervised Learning (SSL):** Training paradigm where the model generates its own supervisory signals from data, without external labels.

**Transformer:** A deep learning architecture using multi-head attention. Became widely used in NLP and underpins most modern LLMs.

**Transfer Learning:** Reusing knowledge from one task to improve performance on a related task.

**Zero-Shot Learning:** A model predicting classes at test time that were not observed during training.

## Risk Management Terms

**AI Risk Plan Framework:** Structured approach to integrating AI into project risk management, covering identification, assessment, mitigation, and monitoring.

**Ambiguity Risk:** Uncertainty about how project objectives or scope will unfold, especially in innovation projects.

**Contingency Planning:** Preparing flexible response strategies for critical risks; AI-driven plans adjust based on real-time data.

**Emergent Risk:** Unpredictable events with severe negative impacts — "unknown unknowns" (e.g., COVID-19 pandemic).

**Idempotency:** Ensuring an action produces the same result when executed multiple times — critical to avoid duplicate effects in retry loops.

**Monte Carlo Simulation:** Probabilistic tool offering range-based estimates for schedules and budgets, showing the likelihood of different outcomes.

**Predictive Analytics:** AI capability to process data and forecast probable consequences of different choices.

**Qualitative Risk Analysis:** Assessing probability and impact using qualitative measures (very low to very high).

**Quantitative Risk Analysis:** Assessing probability and impact using tools like expected value analysis and Monte Carlo simulations.

**Risk Register:** Detailed log recording potential risks, their characteristics, and planned responses throughout a project lifecycle.

**Strategic Risk:** Risks affecting long-term goals, influenced by external changes, managed at portfolio and program levels.

**Transfer (risk strategy):** Shifting responsibility for a risk to another party via insurance or outsourcing.

**Variability Risk:** Systemic uncertainty in schedule and cost estimates due to unclear work scope or fluctuating resource productivity.

**VUCA:** Volatility, Uncertainty, Complexity, Ambiguity — acronym describing the challenging environment in modern project risk management.
