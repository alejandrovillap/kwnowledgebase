---
title: Openspec
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: [openspec, "spec-driven", "agentic-coding", brownfield, workflow, "llm-development"]
keywords: [OpenSpec, "spec-driven", brownfield, agentic coding, proposal, apply, archive, AGENTS.md, project constitution, specifications, LLM workflow]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Openspec

## General Impression

**Spec-Driven Adherence**: Implements a close approximation of a true spec-driven approach, with each change naturally contributing to existing documented features, thereby accumulating project knowledge. However, scalability is questionable due to model context limitations and the lack of specialized context management mechanisms (e.g., something similar to Claude Skills).

**Role Specialization**: Primarily targets the software developer role. The workflow is minimalist and lacks dedicated steps for business analysts or architects.

**Project Type Focus**: Claims to target primarily brownfield projects, emphasizing the ability to modify existing behavior (1→n), particularly when updates span multiple specifications.

**Quality Concerns**: Appears immature, with evident issues.

## Strengths

**Brownfield Specialization**: Optimized for projects with existing functionality, with workflows intended for updating or extending behavior rather than solely creating new features.

**Simple Structure and Commands**: Operates with only three AI agent commands (`proposal`, `apply`, `archive`) and a small set of templates, reducing complexity and lowering the learning curve.

**Project Constitution Equivalent**: Maintains a `project.md` guiding document, analogous to Spec-kit's constitution, ensuring consistency and shared standards.

**Streamlined Workflow**: Uses just two core phases (proposal → apply) plus archiving. Feels similar to Cursor's "plan" mode, but with greater emphasis on producing specifications along the way.

**Spec Archiving and Consolidation**: Moves past specifications into a dated archive folder and merges changes into a single scenario-based feature spec — provides historical traceability and enables reuse for related future features.

**Completion Verification**: Ensures that all tasks are marked complete before archiving, adding a quality gate that some other frameworks omit.

## Weaknesses

**Limited User Engagement for Clarification**: Interaction with the user is minimal. For ambiguous requests, the framework asks at most one or two clarifying questions before proceeding, and logs open questions in `design.md` rather than resolving them through discussion. This can lead to poor specifications for complex tasks.

**Instruction Gaps**: Some directives in `AGENTS.md` are vague (e.g., "Read relevant specs in `specs/[capability]/spec.md`" without defining relevance), relying heavily on agent capabilities without explicit guidance.

**Bugs**: Inconsistent command syntax and parameter references in `AGENTS.md` cause inevitable CLI command failures during archiving.

**Lack of Comprehensive Documentation**: Certain concepts (e.g., "spec deltas," "source of truth specs") appear in generated artifacts but are not well explained in OpenSpec's documentation.

**Single-Maintainer Risk**: As an open-source project primarily maintained by one individual, there are concerns about long-term support, scalability, and timely updates.
