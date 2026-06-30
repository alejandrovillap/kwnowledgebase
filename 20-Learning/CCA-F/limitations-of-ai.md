---
title: Limitations of AI
date: 2026-04-09
type: concept
technology: "gen-ai"
status: active
tags: ["ai-limitations", "next-token-prediction", "working-memory", steerability, "knowledge-cutoff", hallucination, "mental-model"]
keywords: [AI capabilities, limitations, next token prediction, working memory, steerability, knowledge cutoff, hallucination, "fine-tuning", calibrated trust]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Limitations of AI

## Building a mental model of the machine

### AI Capabilities & Limitations Framework

Four properties that shape what AI can and can't do for you. Each sits on a spectrum — the further right, the more you should verify and compensate.

| Property | Capability Zone | Limitation Zone |
| --- | --- | --- |
| **Next Token Prediction** – *Where do AI answers come from?* | Well-worn paths: summarize, reformat, explain common concepts | Novel territory, sparse patterns, "true vs. sounds true" |
| **Knowledge** – *What does AI actually know?* | Frequent, recent-in-training, consistent: mainstream topics, popular languages | Rare, post-cutoff, niche, local, or contested topics |
| **Working Memory** – *What is the AI paying attention to right now?* | Material fits comfortably, session is current, you supply relevant context | Very long docs/conversations, expecting cross-session continuity (the cliff) |
| **Steerability** – *How much am I in control?* | Short, concrete, verifiable instructions ("respond as a table," "under 100 words") | Long reasoning chains, abstract asks, native precision |

"AI" is a broad term. The recommendation engine picking your next video, the spam filter in your inbox, the fraud model flagging a suspicious charge — all of that is AI, but none of it is generative. Those systems sort, rank, classify, and predict. They're enormously useful and running in the background of your life constantly, but they're not what this course is about. What's changed recently is the rise of generative AI: systems that produce new content — text, images, code, audio — rather than categorize existing content. Generative AI is built in two stages: pretraining, where it learns patterns from massive amounts of data, and fine-tuning, where it's shaped to be safe, ethical, and helpful.

At its core, generative AI is a prediction system — not uniformly capable or uniformly unreliable, but strong and weak along specific, predictable axes. Most of the time, the strength and the weakness come from the same underlying mechanism.

The four properties:
- **Next Token Prediction** — where do the answers come from? The model isn't looking things up; it's writing what comes next, one fragment at a time.
- **Knowledge** — what does it actually know? Broad but uneven, frozen at a training cutoff.
- **Working Memory** — what is it paying attention to right now? What's in the context window is what's available.
- **Steerability** — how much are you in control? Remarkably directable, but there can be a gap between what you intended and what landed.

The goal is **calibrated trust**: learning to ask where your task sits on each continuum, whether you're in well-trodden territory or near an edge, and what the stakes are if you're wrong.

### Key takeaways
- **Generative AI produces new content** rather than classifying existing content.
- **AI isn't uniformly capable or uniformly unreliable.** It's strong and weak along four predictable axes: Next Token Prediction, Knowledge, Working Memory, and Steerability.
- **Each property is a continuum.** The same mechanism gives you both the capability and the limitation.
- **Calibrated trust** means locating your task on the continuum, not granting or withholding trust wholesale.

---

## Pretraining, fine-tuning, and the fingerprints they leave

### How AI Gets Its Character

AI assistants are built in two stages. **Pretraining** teaches one thing: given everything so far, predict what comes next — repeated billions of times across enormous amounts of data. The result is a document completer with no concept of you or of helping. **Fine-tuning** is the second layer: the document completer gets trained again on curated examples of helpful behavior and reward signals shaped by human preferences. This is what turns raw prediction into the assistant you actually interact with.

Because fine-tuning relies on human judgments about what "good" looks like, the texture of those judgments shows up as fingerprints in the model's personality:
- **Sycophancy** — people prefer agreeable responses, so the model learns to validate you and back down under light pushback, even when it was right the first time.
- **Verbosity** — thoroughness scores better during training, so the model defaults to longer answers even when brevity would serve you better.
- **Over-caution** — conservative safety training means the model can hedge heavily or refuse requests that are actually fine.

These aren't bugs in one particular model; they're training artifacts that appear across all AI models, shaped differently by how each was fine-tuned.

### Key takeaways
- **Pretraining** produces a document completer by predicting "what comes next" across vast amounts of data.
- **Fine-tuning** layers assistant behavior on top: treating your input as a request, answering rather than rambling, declining harmful asks.
- **Fine-tuning uses human judgments** about good responses, and those judgments leave fingerprints: sycophancy, verbosity, occasional over-caution, and loose calibration between stated confidence and actual reliability.

---

## When Properties Collide

Most real-world AI failures are two properties meeting at the same time.

**Hallucinated citation = Next Token Prediction × Knowledge.** You ask about a niche topic and get a paper title, author names, a journal — none of it real. The model is generating what a plausible citation *looks like* while a knowledge gap sits underneath.
- *Fix:* verify specifics independently, or use source grounding.

**Long-conversation drift = Working Memory × Steerability.** You set careful constraints at the start; twenty messages later, half are being ignored. Your early context has faded, and steerability follows whatever instructions are most salient *right now*.
- *Fix:* re-supply critical context, or start fresh with the essentials up front.

**The diagnostic habit:** before reaching for a prompt fix, ask *which properties am I looking at?* A Knowledge problem and a Working Memory problem can look similar on the surface but need completely different responses.

### Key takeaways
- **Real-world failures are usually two properties interacting**, not one.
- **Diagnostic pairs:** Next Token Prediction + Knowledge (hallucinated specifics); Working Memory + Steerability (long-conversation drift).
- **Naming the properties at play** points you straight to the fix.
- **This diagnostic move is Discernment applied.**

---

## Closing Mental Model

**Two halves of one system.** The 4D Framework and the four properties aren't separate things to juggle. The 4Ds are what *you* do; the four properties are what you're responding to when you do them.

- Next Token Prediction sharpens Discernment (fluency and accuracy are independent variables).
- Working Memory sharpens Description (context is leverage, and the model doesn't remember everything).
- Steerability sharpens Delegation (you know where control is tight and where it's loose).

**Calibrated trust is a habit, not an attitude.** Before handing something to AI, run a quick internal check: well-worn territory or sparse? Recent topic or stable? Context comfortably inside the window? Instructions concrete, or room between words and intent? Then adjust accordingly.

**The shape stays useful.** Models will keep changing. Context windows grow, hallucination rates drop. But AI will keep being a predictor whose fluency runs ahead of its accuracy. That fact doesn't expire when the version number goes up.
