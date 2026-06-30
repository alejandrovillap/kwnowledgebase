---
certification: ''
confidence: medium
date: '2025-01-01'
keywords:
- allowedtools
- allowlist
- CLAUDE.md
- output-format
- json
- bash
- npx
- gate script
- severity
- pass-fail
- deploy
- merge
- block
- notify
- log
- roles
- skills
- config
project: Gusto External
status: active
tags:
- claude
- pipeline
- gate
- allowlist
- security
- automation
- CI-CD
target_folder: 10-Work
technology: gen-ai
title: Gusto External - Claude Pipeline Gate Architecture
type: idea
---

Gusto
Externo

Permises
allowlist
Read
Group
Bash (npntest)
explicit, segro

Config(Repo)
• claude/CLAUDE.md
roles/ *.md
skills/ *

rules  Pipeline
              claude - p
              --output-format json
              --allowedtools...

Print mode
one shot
terminal
     ↓ produce
Output
Json
parseable

Gate
Script decide
severity? pass/fail?

low                                    High

Pass                              High security
- Deploy                          Fail
- Merge                           - Block
- Continue                        - Notify
                                  - Log

![AI Security Gate Flowchart](../assets/2026-06-30-diagram-01.png)
> **Auto description:** A hand-drawn flowchart showing an AI pipeline security decision process. At the top, 'Gusto/Externo' feeds down into a 'Pipeline' stage that runs 'claude -p' with flags '--output-format json' and '--allowedtools...'. On the left is a Config(Repo) box listing configuration sources (claude/CLAUDE.md, roles/*.md, skills/*). On the right is a Permissions box listing allowlist, Read, Group, Bash(npntest), explicit/segro. The pipeline produces Output in JSON parseable format. This feeds into a diamond-shaped 'Gate / Script decide' decision node that evaluates severity/pass/fail. Two branches emerge: 'low' (left) leading to Pass actions (Deploy, Merge, Continue) and 'High' (right) leading to High security Fail actions (Block, Notify, Log). There are also 'restring tools' annotations near the top connecting to the pipeline stage.
