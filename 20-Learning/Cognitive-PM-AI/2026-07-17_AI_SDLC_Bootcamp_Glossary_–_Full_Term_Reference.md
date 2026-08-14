---
certification: ''
confidence: high
date: '2026-07-17'
keywords:
- ADR
- agent
- ATX
- AI Maturity Matrix
- AI Factory
- LLMOps
- RAG
- MCP
- HITL
- prompt injection
- fitness function
- delegation archetypes
- cognitive load map
- sigma calibration
- eval-as-monitor
- golden dataset
- handoff matrix
- spec-driven development
- OODA
- service blueprint
- digital labour
- Promptframe
- CONTEXT.md
- SPEC.md
- AI Eval Card
- kill-switch
- policy-as-code
- STRIDE
- LINDDUN
- AI gateway
- semantic caching
- replay store
- workload identity
project: AI SDLC Bootcamp
source: gmail-draft-1
status: to-review
tags:
- glossary
- agentic-ai
- SDLC
- ATX
- LLMOps
- prompt-engineering
- architecture
- security
- MCP
- RAG
- observability
- FinOps
- design
- delivery
target_folder: 20-Learning/Cognitive-PM-AI
technology: gen-ai
title: AI SDLC Bootcamp Glossary – Full Term Reference
type: resume
updated: null
---


## Core Concepts & Foundational Structures

### 7-Block Prompt Anatomy

The foundational structure under all named prompt frameworks:

1. **Role**
2. **Task**
3. **Context**
4. **Data/Input**
5. **Constraints**
6. **Output Format**
7. **Examples** (few-shot)

> Different frameworks reorder or emphasize different blocks; the anatomy itself is invariant.

Design's **Promptframe** is the 5-section reduction of this anatomy for UI generation.

---

### Named Prompt Frameworks

Five compact frameworks rotating the **7-block prompt anatomy** emphasis:

| Framework | Stands For | Best For |
|-----------|-----------|---------|
| **RTF** | Role / Task / Format | Daily tasks |
| **RACE** | Role / Action / Context / Expectations | Business rigor |
| **COAST** | Context / Objective / Audience / Style / Tone | Copy + voice |
| **ROSES** | Role / Objective / Scenario / Expected Solution / Steps | Complex problem-solving |
| **CRISPE** | Context / Role / Input / Steps / Parameters / Example | Technical handoff to AI build agents |

---

### Agent

> An AI system that perceives its environment, reasons about goals, and takes autonomous actions using tools. Unlike a simple chatbot, an agent can plan and execute multi-step tasks.

---

### Agentic Development

A software development approach where **AI agents** are autonomous participants in the **SDLC** — not just assistants — capable of writing, testing, and shipping code with minimal human direction.

---

### Autonomy Spectrum

The range from fully human-controlled to fully autonomous AI execution. Most teams operate somewhere in the middle, increasing autonomy as trust in agent reliability grows.

---

### Autonomy Matrix

Also *Decision Authority Matrix* — the operational contract from [[ATX]] agent mapping (Module 100) stating what an agent may decide alone versus what needs a human.

**Four bands:**

| Band | Description |
|------|-------------|
| Agent decides alone | No [[Human-in-the-Loop (HITL)]] |
| Agent acts, human notified after | Post-hoc notification |
| Agent proposes, human approves before action | Pre-approval required |
| Human takes over with agent supporting | Full human control |

Each band includes named triggers: value thresholds, sensitive-data changes, confidence below X, compliance flags. Finer-grained than the **Autonomy Spectrum**: it pins authority per decision, not per system.

---

### Digital Labour

> The third enterprise scaling mechanism after deterministic software and human headcount: GenAI agents that absorb cognitive load, reason over unstructured input, and act with bounded autonomy.

They scale like software but, being *statistical* rather than deterministic, must be governed like a workforce — designed with purpose, tested and calibrated, supervised, and **owned, not rented**. Renting pre-built vendor agents creates hidden outsourcing (lock-in, no compounding), so [[ATX]] caps it the way enterprises cap human outsourcing. Core concept of [[ATX]] in Module 100.

---

## ATX — Agentic Transformation Framework

> **ATX** (**Agentic Transformation Framework**) is EPAM's structured methodology for converting cognitive work into governed [[Digital Labour]] — the spine of Deep-level discovery in Module 100 — Consulting & SME.

**Five capability areas:**

- Concepts
- Assessment
- Use-Case Scoring
- Agent Mapping
- Economics

ATX changes the unit of analysis from *processes* to *cognitive work*: it starts from a business problem, grounds every decision in token economics and [[Sigma calibration]], and builds platform assets that compound across waves instead of stacking isolated pilots. Deep katas 100.2.1–100.2.7 apply it to a client function; the same framework applies to the discovery function itself.

---

### Jobs to be Done (JTBD)

In [[ATX]], a **Job to be Done** is not a task but a *cognitive contract* between an actor and an outcome — *"resolve a billing dispute"* bundles understanding intent, validating identity, reconciling data, applying policy, choosing a resolution, and communicating it.

**JTBDs are the atomic unit of delegation:** they separate what must be *decided* from what must be *executed* and flag which parts are knowledge-, rule-, or exception-bound. Decomposing work into JTBDs precedes [[Cognitive Zones / Cognitive Breakpoints]] mapping in Module 100.

> The delegation-primitive sense ATX uses (Module 100, abbreviated *JtD*) is narrower than the classic Christensen demand-side reading used in Module 200 (PM/BA) for user segments and [[Opportunity Scoring]].

---

### Cognitive Load Map

The pre-classification artefact in [[ATX]] discovery (Module 100, Kata 100.2.3): a table scoring each micro-task across eight dimensions — built *before* any agent is proposed.

| Dimension | Scale |
|-----------|-------|
| Cognitive Load | High / Medium / Low |
| Input Structure | High / Medium / Low |
| Decision Determinism | High / Medium / Low |
| Exception Frequency | High / Medium / Low |
| Turn-Taking Degree | High / Medium / Low |
| Latency Constraint | High / Medium / Low |
| Compliance/Risk Sensitivity | High / Medium / Low |
| Tool/API Availability | High / Medium / Low |

Turns vague "complexity" into a precise topology that drives [[Delegation Archetypes]] assignment. Decomposed from the [[Jobs to be Done (JTBD)]] for the function under study.

---

### Cognitive Zones / Cognitive Breakpoints

Two units for reading a [[Jobs to be Done (JTBD)]] in [[ATX]]:

- **Cognitive Zones** — clusters of similar cognitive activity (intent recognition, retrieval, diagnosis, resolution, documentation), each with its own data dependencies, error tolerance, and latency.
- **Cognitive Breakpoints** — the points where control hands off (customer→agent, system→human, rule→judgment) where agents create disproportionate value *or* risk.

Mapping them precedes archetype assignment in Module 100 discovery.

---

### Delegation Archetypes

The five stable operating modes [[ATX]] assigns to each task — **design choices, not maturity levels**:

| Archetype | Description |
|-----------|-------------|
| **Human Only** | Tacit, ethical, or irreversible decisions |
| **Human-led + Automation Support** | Tools accelerate; judgment stays human |
| **Human-led + Agent Support** | Agent synthesises and recommends; human decides |
| **Agent-led + Human Oversight** | Execution delegated; supervision mandatory |
| **Fully Agentic** | Autonomous within defined bounds |

The archetype follows from the [[Cognitive Load Map]] scores; Module 100 Kata 100.2.3 forces every task into exactly one.

---

### Sigma Calibration

Treating an agent's output as a *distribution* rather than a single result, and tuning its variance before production ([[ATX]] economics, Module 100, Kata 100.2.5).

- **Wide sigma** — creative, variable output; acceptable for low-stakes generation
- **Narrow sigma** — consistent, predictable output; required for regulated or high-volume structured decisions

**Levers:** model selection, temperature, retrieval precision, prompt constraints, output validation, post-processing.

> Release only when the measured operating point (accuracy at cost) matches the business-case assumptions.

---

## Architecture & Context Layers

### Architecture Context Pack (ACP)

The full L3 architecture deliverable bundling the four context layers (Business / Product / Architecture / Engineering), ADRs, diagrams, fitness functions, and governance handoffs. Consumed by every downstream role module (500–900). See [[Context Pack]].

---

### Context Layer

> One of the four layers of context an L3 architect mines and maintains. Each layer is owned by a specific role, refreshed on specific triggers, and consumed by specific AI agents per the [[Handoff Matrix]]. If a layer is not in the repository, it does not exist for agents.

| Layer | Owner | Consumed By |
|-------|-------|-------------|
| **Business Context** | Consultant / BA | AI BA and AI QA agents |
| **Product Context** | PM / BA | AI BA and AI QA agents |
| **Architecture Context** | Architect | AI DevOps and AI Engineer agents |
| **Engineering Context** | Lead Engineer | AI Engineer agents during Spec-Driven Development |

**Business Context** holds: strategy excerpts, value drivers, regulatory constraints (PCI DSS, GDPR), market boundaries, cost ceilings.

**Product Context** holds: feature scope, AI feature boundaries, user behaviours, success criteria, acceptance thresholds.

**Architecture Context** holds: system boundaries, integrations, NFR budgets, technology choices, fitness functions, trust boundaries, ADRs.

**Engineering Context** holds: repository map, code patterns, dependency graph, rule files (`CLAUDE.md`, `.cursorrules`), naming conventions, semantic-layer references. Seeded by the architect via the Engineering Context seed inside the [[Architecture Context Pack]].

---

### Context Pack

A version-controlled artefact that bundles the project knowledge AI agents need to produce accurate output. Three variants:

- **Industry Context Pack** *(Module 100 — Consulting & SME)* — domain knowledge: market, segments, regulatory context, value drivers, prior-art catalog. Survives past one engagement; reused across opportunity-discovery work.
- **Architecture Context Pack** *(Module 400 — Architecture)* — the full L3 architecture deliverable bundling the four context layers, ADRs, diagrams, fitness functions, and governance handoffs. Often abbreviated *ACP*. Consumed by every downstream role module (500–900).
- **Engineering Context Pack** *(Module 500 — Engineering)* — a repo-local artefact (repository map, pattern catalog, dependency notes, conventions) that the rule file references. The *Engineering Context seed* inside the Architecture Context Pack is its upstream input.

---

### ADR (Architecture Decision Record)

> A short structured document capturing the *why* behind one architecture decision: context, decision, alternatives considered, NFR budgets, status, and consequences.

Format introduced by **Michael Nygard (2011)**. The **L3 extension** adds agent-readable summaries, explicit NFR numbers, and traceability so AI agents can consume the decision as a constraint, not only humans as documentation. See [[Architecture Context Pack]].

---

### Handoff Matrix

The table that maps **Architecture Context layers** to the AI agents that consume them. Names which layer(s) feed which agent and which artefact each agent produces with that context. The architect's primary contract with the rest of the AI Factory.

---

### Governance Handoff

A short, version-controlled markdown note (one paragraph per target) addressed to a specific downstream AI agent — telling it what architectural constraints to respect and what not to do.

> Distinct from a governance document (which lives in SharePoint and is read by nobody). A handoff is pasted into the downstream agent's rule file, where it is enforced on every invocation.

---

### NFR (Non-Functional Requirement)

> A property of *how* a system performs, not *what* it does — latency, cost, quality, reliability. In AI-enabled systems, cost and quality become first-class NFR families.

An NFR without a measurable budget is an aspiration; without a [[Fitness Function]] enforcing it, the budget is still an aspiration.

---

### Fitness Function

An automated check that validates whether an architectural property (latency, cost, quality, conformance) still holds. Concept from *Building Evolutionary Architectures* (Ford, Parsons, Kua).

**Anatomy:** what is checked, when it fires, threshold, consequence of breach, owner.

> Without a fitness function, an [[NFR]] is an aspiration, not a constraint.

---

## Agent Architecture & Runtime

### Agent Runtime

The long-lived execution environment for an agent — distinguished from a REST API by:

- Long duration (minutes to days)
- Checkpointed state
- Non-determinism
- Variable cost
- Explicit human-in-the-loop placement

Architects specify: checkpoint placement, resumability contract, HITL triggers, failure budget, idempotency requirements, observability, and cost ceiling. See [[HITL]].

---

### Agent Harness

The control plane wrapping an autonomous agent: the loop that calls the model, dispatches tool calls, enforces time and cost budgets, collects decision-lineage traces, handles retries, and surfaces escalations.

> The harness owns *how* the agent runs; the sandbox owns *where* it runs.

See also **Agent Sandbox**. Module 800 Wide Theory Topic 5.

---

### Agent Sandbox

The isolated execution environment in which agent-generated actions run:

- Ephemeral microVM or container
- Scoped credentials
- Configurable TTL
- Network restrictions
- Snapshot/resume capability

> The sandbox protects the host system from agent actions; the harness protects the agent from runaway behaviour.

See also **Agent Harness**. Module 800 Wide Theory Topic 5.

---

### Bounded Runtime

The set of platform-enforced limits on an agent's execution:

- Maximum retries with exponential backoff and jitter
- Wall-clock time budget
- Per-run cost cap
- Fallback path on exhaustion
- Circuit breaker on dependency failure

> The default behaviour of an agent is unbounded — the platform either bounds it, or the bill does.

Module 800 extras.

---

### Orchestrator

An agent responsible for coordinating other agents (subagents). The orchestrator decomposes goals, delegates tasks, and synthesizes results.

---

### Subagent

An agent spawned and directed by an orchestrator agent to handle a specific subtask. Subagents enable parallelism and specialization within a multi-agent system.

---

### Custom Agent

An AI agent configured for a specific role or task, with a tailored system prompt, curated tool set, and domain-specific knowledge. More reliable than general-purpose agents for narrowly defined jobs.

---

### Skill / Agent Skill

A **Skill** is a reusable, packaged agent behavior — a higher-level capability that bundles a prompt template, tools, and logic for a specific repeatable task *(e.g., "review PR", "generate tests")*.

An **Agent Skill** is a reusable packaging primitive for *procedures and instructions* — distinct from MCP servers (which package *capabilities and data*) and from prompt content (which packages *one-off framing*). Anthropic published the open standard in October 2025: a folder with a `SKILL.md` frontmatter (name + description preloaded by progressive disclosure; body loaded on demand) and optional executable scripts.

> The architect's three-way choice — skill vs MCP server vs prompt content — is in Module 400 §4.9.3.2.

---

### System Prompt

The foundational instructions given to an agent that define its role, constraints, tools, and behavior. The most important configuration element of a custom agent.

---

### Tool

A function an agent can invoke during execution to interact with the real world — reading files, running code, calling APIs, querying databases, etc.

---

### Tool Calling

The mechanism by which an AI model selects and invokes a tool based on its reasoning. The model receives tool descriptions and decides when and how to use them.

---

### Memory

Mechanisms by which agents retain information:

- **In-context memory** — exists only within a single run
- **Persistent memory** — survives across runs and sessions

---

### Model

The underlying **large language model (LLM)** powering an agent. Common choices involve trade-offs between capability, speed, and cost.

---

### Context Window

The amount of text (tokens) an AI model can process in a single interaction. Agents must manage context carefully in long-running tasks to avoid exceeding this limit.

---

### Model Routing

The architectural pattern of classifying each request and routing it to the cheapest capable model tier (small / medium / large-reasoning).

> The single biggest cost lever in L3 architecture: typical savings 60–80% versus always-large.

Requires a cheap classifier, three-tier model serving, a cache layer, and a budget controller.

---

### Pipeline

A sequence of automated stages that process work from input to output. In AI SDLC, a pipeline might move a feature spec through implementation, testing, review, and deployment stages.

---

### Dark Factory

A fully automated development pipeline where AI agents handle execution end-to-end (from spec to deployment) with humans involved only at high-level decision points and escalations.

---

## MCP — Model Context Protocol

> **MCP** is the emerging integration standard for AI systems — *"USB-C for AI applications."* Defines how agents discover and use tools, access context (Resources, Prompts, Tools), and interact with external systems through a three-role model (Host / Client / Server).

Open standard originated by Anthropic, broadly adopted. Enables **Day 2 Design** composition: AI agents become informed co-authors rather than blind generators. MCP boundary scoping is system architecture, not protocol detail.

---

### MCP Server

A service that provides context and capabilities to AI agents via the MCP protocol. Exposes Resources, Prompts, and Tools.

> Architects decide boundaries between servers based on domain, security tier, lifecycle, scale, team ownership, and data source — *not* org chart.

---

### AI Gateway

A platform-capability proxy that sits between agents and LLM providers, centralising:

- Routing, caching tiers, fallback
- Per-tenant rate-limiting (Bulkhead)
- API-key vaulting
- Cost attribution
- Audit logging
- Guardrails

*Mature 2025 deployments: Kong AI Gateway, Portkey, LiteLLM, Cloudflare AI Gateway.* Architectural decision in Module 400 §4.9.8.2: build-vs-buy and what features live in the gateway vs in each feature.

---

## Observability & Evaluation

### LLM Observability

> The discipline of knowing whether an AI system is *worth* running, not merely whether it is running.

Extends traditional APM (latency, errors, throughput) with five additional layers:

1. Instrumentation
2. Spans/traces
3. Session-level grouping
4. Online evaluation (production scoring for faithfulness, relevance, hallucination, safety, tool-selection)
5. Quality-aware alerting with drift detection

> A successful HTTP 200 response can contain a hallucinated or harmful answer — no APM alert fires; only observability that scores behaviour catches it.

Module 800 Deep Theory Topic 2.

---

### LLMOps

The end-to-end discipline of running LLM-based features reliably in production, spanning:

- **Inner loop:** experiment → evaluate → iterate on prompts and models
- **Outer loop:** deploy → monitor → collect feedback → retrain or fine-tune

Extends MLOps with LLM-specific concerns: prompt versioning, token economics, hallucination monitoring, provider management, and eval-as-monitor. Module 800 Wide Theory Topic 1.

---

### Decision Lineage

The observability primitive that records *why* an agent took a decision, not just *what* it did. Each decision span captures:

- Inputs (prompt hashes, prior tool outputs, model version)
- Reasoning text or full prompt
- Chosen branch with confidence
- Outcome (tool result, used in final answer)

Complements execution lineage (which records what happened).

> Without decision lineage, post-incident reconstruction of agent behaviour is guesswork.

Module 800 Deep Theory Topic 3.

---

### Eval-as-Monitor

The practice of promoting a QA eval suite beyond CI into a production monitoring shape: the same test cases that gate merges also run on a sample of live traffic on a defined schedule, with eval pass rate declared as an **SLI** and drift detection configured against a rolling baseline.

> A QA eval that does not run in CI or production is ceremonial quality.

Module 800 Deep Theory Topic 7.

---

### Golden Dataset

A version-controlled set of representative `input → expected-output` (or `input → graded-rubric`) pairs used to evaluate an AI feature the same way every time — typically stored as **JSONL** so a harness can replay it on each prompt or model change.

In Module 200 the PM/BA builds a ~20-prompt golden set (Deep kata K 2.D.4) covering happy paths, error paths, and edge cases, then runs it across model and prompt configurations to gate release. Feeds the [[AI Eval Card]] thresholds; its live-traffic counterpart is [[Eval-as-monitor]].

---

### LLM-as-Judge

An evaluation pattern where a second LLM call scores an AI feature's output against a written rubric (pass/fail or graded), used when the correct answer is open-ended and exact-match scoring fails.

> The rubric and its calibration are human-owned: a judge prompt that has not been checked against human labels measures nothing.

In Module 200, acceptance criteria are written so they are evaluable by a human *or* an LLM-as-judge (Deep kata K 2.D.3).

---

### Eval-Gated

Describes a release decision bound to a measured evaluation result rather than a sign-off opinion: the feature ships only if its [[golden dataset]] pass rate clears a named threshold on the [[AI Eval Card]].

In Module 200 the release-readiness brief (Deep kata K 2.D.7) states the eval-gated bar a release manager can check without re-running discovery.

---

### Replay Store

An append-only store of agent traces sufficient to reproduce a production failure in CI.

**Required fields:** model id and version, decode parameters (temperature, top-p, top-k, seed), full input, retrieved-context hash, system-prompt hash and skill versions loaded, tool calls with arguments and results, timestamps.

Same write as the Event Sourcing audit log (Module 400 §4.9.9); two reads: compliance (proves what happened) and replay (reproduces a failure). Module 400 §4.9.7.

---

### Trajectory-Tolerant Evaluation

An evaluation pattern for non-deterministic systems that scores the *outcome* and the *path quality* of a replayed trace, not the exact tool sequence (non-determinism persists even at temperature=0). Pairs with the [[Replay Store]]. Module 400 §4.9.7.

---

## Caching Architecture

### Prompt-Prefix Caching

A lossless caching tier that reuses the provider-managed cache of a stable prompt prefix across calls. Anthropic, OpenAI, and Gemini all implement this.

- Achieves ≥90% input-token-cost and ≥85% latency reduction on cached prefixes
- Only effective if the prompt is structured *stable-first, variable-last*

> Putting the user message before the system prompt makes the cache useless.

Architectural constraint on every team writing prompts. Module 400 §4.9.8.3 tier 2.

---

### Semantic Caching

A lossy caching tier that returns a prior answer when a new query's embedding is similar enough to a cached query (typical threshold 0.85–0.95).

**Three architectural decisions:**

1. Similarity threshold
2. Partitioning (by tenant / user / sensitivity to prevent PII bleed across users)
3. Staleness signal (when the underlying knowledge changes)

Module 400 §4.9.8.3 tier 3.

---

## Security & Compliance

### Threat Model

A structured enumeration of how a system could be attacked, scored by severity and exploitability, with each threat traced to a mitigation in a specific artefact and an owner. Produced design-time (and updated when the architecture changes); complements (does not replace) a pentest.

> A model that doesn't trace to file-path mitigations is wall decoration.

Module 900 Kata 900.2.1 walks through producing one with an agent and human-editing it.

---

### STRIDE

Threat modelling framework with six categories:

- **S**poofing
- **T**ampering
- **R**epudiation
- **I**nformation disclosure
- **D**enial of service
- **E**levation of privilege

Used in Module 900 Kata 900.2.1 as the framework an agent enumerates threats against a system decomposition.

---

### LINDDUN

Privacy-focused threat modelling framework. Categories:

- **L**inkability
- **I**dentifiability
- **N**on-repudiation
- **D**etectability
- **D**isclosure of information
- **U**nawareness
- **N**on-compliance

Used alongside or in place of **STRIDE** when the system is privacy-sensitive (PII, health, finance). See Module 900 §1.2 Intermediate.

---

### Prompt Injection

A class of attack where untrusted text (user input, retrieved content, document, tool output) reaches the model and is interpreted as instructions, bypassing the system prompt or escalating privileges.

- **Direct prompt injection** — uses user input
- **Indirect prompt injection** — uses retrieved content or tool output

Listed in OWASP Top 10 for LLM Applications. Validated by the red-team eval suite, not by system-prompt wording. See Module 900 §1.1 Topic 6.

---

### Indirect Prompt Injection

A prompt-injection variant where adversarial instructions arrive inside content the agent reads — retrieved documents, tool outputs, emails, web pages, screenshots — rather than from direct user input.

> The highest-leverage attack pattern at L3 because the agent's authority exceeds the attacker's.

**EchoLeak** (CVE-2025-32711, CVSS 9.3) is the canonical 2025 case. See [[Prompt injection]] and Module 400 §4.9.10.

---

### Jailbreak

Technique to bypass an LLM's safety restrictions in order to elicit harmful, biased, or restricted output. One of the AI-specific risks Module 900 §1.1 Topic 6 covers; validated via the red-team eval suite (see Kata 900.2.3), not by intent or system-prompt wording.

---

### Excessive Agency

> A security-relevant property of an agentic system where the agent has tools, scopes, or permissions that exceed its actual job.

Listed in **OWASP Top 10 for LLM Applications**. The mitigation is **least-privilege tool design** — two narrow tools beat one wide one. See Module 900 §1.2 Expert.

---

### Kill-Switch

A documented, tested, time-bounded mechanism to halt an agent (or class of agents) in production without redeploying. Must be:

- (a) Invocable by a person with phone access
- (b) Testable in production-equivalent conditions
- (c) Observable so you know it ran

Treated as a first-class security control in Module 900; kill-switch invocation is human-owned.

---

### Secure-by-Design

The L3 security pattern where security requirements drive the spec, an agent checks every SDLC stage as work moves through it, and humans gate the irreversibles.

*Contrast with **security-as-review** — the L2 pattern where security signs off only at the end.* Module 900 §1.1 Topic 2.

---

### Content Safety

The named filter stages in the Pipe-and-Filter pipeline that classify inputs and outputs against a versioned policy — *Llama Guard, Azure Prompt Shields, OpenAI Moderation* are common implementations.

- One filter **before** the LLM (input classification)
- One filter **after** (output classification)

> Not a black box; the policy has an eval suite and a release process.

One of five OWASP LLM01 controls (Module 400 §4.9.10 control 4).

---

### Egress Filter

A filter stage in the Pipe-and-Filter pipeline that inspects the model's output *before* it reaches downstream tools or the user. Blocks:

- URLs to unapproved domains
- Tool calls outside an allow-list
- Structured payloads carrying secrets
- Image references with embedded query parameters (the EchoLeak exfiltration channel)

One of five OWASP LLM01 controls (Module 400 §4.9.10 control 3).

---

### HITL Gate

A wired-in **Human-in-the-Loop** trigger bound to *categories of action* rather than specific tools:

- Any irreversible write
- Any external send
- Any financial action above a tenant-defined threshold
- Any data classification ≥ confidential

The agent presents intent; a human confirms. One of five OWASP LLM01 controls (Module 400 §4.9.10 control 5).

---

### Policy-as-Code

The practice of expressing platform enforcement rules (PII redaction, model allowlists, rate limits, cost caps, safety filters) as version-controlled, CI-tested configuration files that a gateway applies on every request.

> A policy that is not in version control and not under test is documentation, not control.

Each policy should carry at least one positive test, one negative test, and one edge case. Module 800 Deep Theory Topic 1.

---

### Workload Identity

An OAuth identity mode where the access token represents the *agent itself* as a service principal (typically via client-credentials grant), not a human user. Used for background agents, scheduled tasks, and service-to-service calls where no human is in the loop at call time.

*Contrasted with **delegated user identity** (OAuth 2.1 + PKCE) for consent-bearing actions.* The architect picks per MCP server. Module 400 §4.9.3.1.

---

### Responsible AI

The set of design-time and operations-time concerns that determine whether an AI capability is safe to ship:

- Bias and fairness
- Contestability and recourse
- Traceability of training and reference data
- Transparency and explainability
- Environmental cost
- Alignment with company AI principles and external regimes (EU AI Act risk-tier, SR 11-7, sector-specific guidance)

> Treated as a **discovery-stage** concern in Module 100 (the opportunity brief carries a Responsible-AI section), not a security-stage cleanup.

---

### Security & Compliance Pack

The carry-forward artefact of Module 900 — a version-controlled directory containing:

- **(Wide)** A review pack: brief, stage map, triaged findings, sign-off
- **(Deep)** A requirements rubric, threat model, red-team report, and evidence pack

Consumed by Module 1000 (residual-risk reporting, exception register, sign-off chain) and Module 1111 (Assembly Line portfolio).

---

## Human-in-the-Loop & Escalation

### Human-in-the-Loop (HITL)

> A design pattern where humans review or approve agent actions at defined checkpoints in a workflow. Balances automation efficiency with human oversight.

---

### Escalation

The act of an agent pausing its work and surfacing uncertainty or a decision to a human. Well-designed agents know their limits and escalate appropriately rather than proceeding with low confidence.

---

## AI Maturity & Delivery Frameworks

### AI Maturity Matrix

The **EPAM AI Maturity Program Framework** model that scores delivery maturity across five dimensions:

| Dimension | L1 (Assisted) | → | L3 (Frontier) |
|-----------|--------------|---|--------------|
| AI Capabilities | — | — | — |
| Reusability | — | — | — |
| AI Champions | — | — | — |
| Performance Tracking | — | — | — |
| DAU (Daily Active Use) | — | — | — |

Maturity is a **profile across the five**, not a single number, and is scored at team level. The bootcamp's destination is L3 (Frontier); the full diagnostic is Module 020 — introduced in Module 010. See also [[AI-SDLC Maturity Framework]].

---

### AI-SDLC Maturity Framework

The canonical EPAM rubric (in [`resources/ai-sdlc-maturity-framework.md`](ai-sdlc-maturity-framework.md)) that scores teams L0–L3 across the SDLC phases (intake, plan, build, validate, handoff, learn) on:

- AI Capabilities
- Reusability
- Performance Tracking
- DAU

Distinct from but compatible with [[AI Maturity Matrix]] — the matrix scores a team across dimensions; the framework names the per-phase evidence behind each dimension's score. Module 1000 (Delivery & PM) evaluates against this rubric in Kata K 10.D.1 and uses it as the spine of the 90-day adoption plan (K 10.D.7).

---

### AI Factory

EPAM's term for an AI-native delivery team — a team that produces software *and* the reusable artefacts (prompts, agents, skills, rule files, playbooks, workflow templates) that compound across engagements instead of dying with the chat window.

**The L3 distinction reads in three places:**

- Every retro produces a version-controlled artefact
- Every core role has a named [[AI Champion]] with protected time
- [[AI-OPEX]] is treated as a delivery metric attributed per team / feature / model

Module 1000 (Delivery & PM) trains the delivery manager who runs the team toward that standard; the [[Handoff Matrix]] is the architect's primary contract with the rest of the AI Factory.
