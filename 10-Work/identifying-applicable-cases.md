---
title: Identifying Applicable Cases
date: 2026-01-01
type: reference
technology: "gen-ai"
status: active
tags: ["llm-use-cases", ner, "sentiment-analysis", "content-generation", "semantic-search", "text-classification", rag]
keywords: [LLM use cases, NLP, NER, sentiment analysis, content generation, semantic search, text classification, RAG, OCR, summarization, Gen AI, applicable cases]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Identifying Applicable Cases for Gen AI

A guide to identifying business requirements or technical tasks well-suited for LLMs and Gen AI tools. Main focus areas: structuring unstructured data, content generation, and advanced text processing.

---

## Structuring Unstructured Data

### Text-to-Structured Query Translation
LLMs translate natural language queries into SQL, Jira queries, LogQL, etc. Enables non-technical users to interact with databases without learning query languages. Use for "talk to your data" interfaces for management, rapid prototyping of data exploration tools.

### Named Entity Recognition (NER) & Data Extraction
LLMs extract specific information from natural language with minimal examples and no extensive training data. Use cases: extracting flight details from confirmation emails, identifying action items from meeting notes, automating form completion.

### Sentiment Analysis
Beyond simple positive/negative — detects complex emotions and attitudes. Applications: customer feedback analysis, social media monitoring, brand perception tracking.

### Multimodal Input Processing
- **Voice** — transcription + understanding for hands-free checklists, medical documentation, accessibility features
- **Image/Video** — visual input → textual descriptions, searchable image databases, video summarization
- **OCR** — especially useful for complex cases and handwritten text (dedicated tools may be more cost-effective at scale)

### Web Scraping & Document Parsing
LLMs handle edge cases and inconsistent formats in HTML pages and PDFs. Best practice: use traditional methods for initial parsing; apply LLMs for understanding context from parsed content; use embeddings to filter irrelevant content before LLM processing.

---

## Content Generation and Manipulation

### Summarization
Adjustable length, target audience (technical vs. non-technical), multi-lingual. LLMs can tailor output to specific requirements.

### Text Styling and Rewriting
Simplify technical content for general audiences, adapt marketing copy for demographics, generate multiple content versions for A/B testing.

### Code Generation and Analysis
Code completion, explanation and documentation, test case generation, code review and bug detection.

### Question Answering Systems
1. Simple Q&A — one-off questions without context preservation
2. Contextual dialogue — maintaining conversation history for follow-up
3. Active dialogue — LLM-driven conversations following specific scripts or goals

---

## Advanced Text Processing

### Semantic Search
LLM-generated embeddings enable meaning-based search. **Limitations:** reduced effectiveness with numerical data; challenges with abbreviations and domain-specific terminology.

### Text Classification
LLMs classify into complex categories with minimal examples, often outperforming traditional ML for intricate tasks. Best practices: request confidence scores and explanations alongside classifications; use hierarchical classification for large numbers of categories.

### Text Clustering
LLM-generated embeddings + traditional clustering algorithms to group similar texts even without predefined categories.

---

## Automation of Repetitive Tasks
Data entry and validation, report generation, email drafting and response suggestion, simple decision-making based on textual inputs. Use LLM-powered agents or workflows for multi-step automation scenarios.

---

## Considerations and Limitations

1. Avoid Gen AI for critical decisions without human validation (healthcare, finance)
2. LLMs are primarily pattern-matching tools, not logical reasoning engines — outputs may be inconsistent in complex scenarios
3. Evaluate cost-effectiveness vs. traditional approaches for large-scale applications
4. Be aware of regulatory restrictions (EU AI Act, data processing regulations)
5. For problems with clear algorithmic solutions, traditional software may be more appropriate

Additional:
- Implement safeguards against prompt injection attacks
- Respect intellectual property rights for Gen AI-generated content
- Protect sensitive data — avoid sending it to external AI models
- Implement transparency measures (confidence scores, explanation requests)
- Consider human-in-the-loop for critical applications
