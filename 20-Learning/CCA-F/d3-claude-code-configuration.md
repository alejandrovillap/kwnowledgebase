---
title: "D3 - Claude Code Configuration and Workflows"
date: 2026-03-24
type: resume
technology: "gen-ai"
status: active
tags: ["claude-code", configuration, "ci-cd", "slash-commands", workflow, "github-actions"]
keywords: [CLAUDE.md, slash commands, CI/CD, headless, GitHub Actions, D3, configuration, workflow, project level, global level, local level, triggers, pull request, review]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# D3 — Claude Code Configuration and Workflows

Domain 3 has three pillars: CLAUDE.md, Slash Commands, and CI/CD Integration. They work together as a system.

---

## Pillar 1 — CLAUDE.md

**The analogy:** you hired a brilliant employee (Claude Code) who is an expert but doesn't know your organization. CLAUDE.md is the onboarding manual Claude reads at the start of every session to understand how to work in **your** specific project.

Without CLAUDE.md, Claude arrives with no context — doesn't know your stack, your rules, which files are untouchable. With CLAUDE.md, it arrives informed and ready to work within your standards.

**Formal definition:** CLAUDE.md is a Markdown file that Claude Code reads automatically when starting a session. It contains persistent instructions, project context, code standards, and constraints that apply to all interactions within that project.

### The 3-Level Hierarchy

Three levels of CLAUDE.md are read **simultaneously** at session start:

- **Global** (`~/.claude/CLAUDE.md`) — applies to **all** your projects. Personal developer preferences: response language, code style you always use, behaviors you want in any project.
- **Project** (`./CLAUDE.md` at repo root) — applies to **that specific project**. Stack, constraints, team standards.
- **Local** (`./src/CLAUDE.md` in a subdirectory) — applies only when Claude works **inside that folder**. Module-specific or component-specific instructions.

**Priority rule:** closest to the current work wins. If Global says "comments in Spanish" but Project says "comments in English", Claude uses English within that project.

### What Does NOT Go in CLAUDE.md — Exam Trap

The exam asks this frequently. Never include:
- Secrets, API keys, passwords — never in plain text in a repo file
- Instructions that change with each task — those go in the direct message
- Context that only applies once — CLAUDE.md is for **persistent** instructions

---

## Pillar 2 — Slash Commands

Slash Commands are documented processes in natural language that Claude Code executes automatically when invoked. Not application code — instructions for Claude.

**The analogy:** tasks you do every day (review code before commit, generate function docs, create sprint report) require writing long instructions each time. Slash Commands are shortcuts — define the long instruction once, give it a short name, and from then on just type `/review` and Claude knows exactly what to do.

**Formal definition:** Slash Commands are custom commands that automate repetitive instructions in Claude Code. Defined as `.md` files, invoked by typing `/name` directly in the Claude Code terminal.

### `$ARGUMENTS`

The variable that receives what you type after the command. `/review src/payments.py` → Claude reads `src/payments.py` and executes all command instructions on that file. Without `$ARGUMENTS`, the command always does the same thing without context.

### Scope: Project vs Global

- **Project** — lives in the repo, versioned with git, entire team uses it
- **Global** — lives on your machine only, works in any project

### Common Commands the Exam Mentions

| Command | Purpose |
|---------|---------|
| `/review` | Code review before commit |
| `/test` | Generate or run tests for a file |
| `/explain` | Explain what a code block does |
| `/fix` | Fix a specific bug |
| `/document` | Generate documentation for a function or module |
| `/standup` | Generate report of work done (useful for PMs) |

### Connection with CLAUDE.md — Exam Trap

When you run `/review`, Claude reads the command **AND** CLAUDE.md simultaneously. The review automatically respects project standards without repeating them in the command.

CLAUDE.md = the project's framework. Slash Commands = standard processes that operate within that framework.

---

## Pillar 3 — CI/CD Integration

**The analogy:** tasks that should happen **automatically**, without anyone initiating them manually — every time code is pushed, every PR opened, every night.

**Formal definition:** CI/CD Integration is the capability to run Claude Code in **headless mode** — without interface, without human present — as part of an automated CI/CD pipeline.

The key word is **headless** — no interface, no one watching. Claude receives a task, executes it, delivers the result, and the pipeline continues.

### The 4 Triggers the Exam Evaluates

- **`push`** — someone pushes code → Claude reviews for bugs
- **`pull_request`** — someone opens a PR → Claude reviews and comments before the team sees it
- **`schedule`** — scheduled tasks (nightly reports, daily summaries)
- **PR comment** — someone writes `@claude review this` → Claude responds in the PR thread

### GitHub Actions as Orchestrator

GitHub Actions ≠ Claude. GitHub Actions is the system that detects the trigger, launches Claude Code with the correct task, and handles the result. **Claude is the executor. GitHub Actions is the orchestrator.**

---

## The 3 Pillars Working Together

```
Someone opens a PR  →  GitHub Actions detects the trigger
        ↓
Claude Code starts in headless mode
        ↓
Reads CLAUDE.md  →  knows the project standards
        ↓
Executes /review  →  the Slash Command with review instructions
        ↓
Comments on the PR with findings
        ↓
Pipeline continues or blocks based on result
```
