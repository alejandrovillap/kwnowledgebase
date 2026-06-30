---
title: Prompt Engineering — Techniques
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["prompt-engineering", claude, "iterative-improvement", "output-guidelines", multishot, "xml-tags"]
keywords: [prompt engineering, clear and direct, specific, XML tags, examples, multishot, "one-shot", iterative improvement, output guidelines, process steps, eval cycle]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Prompt Engineering — Techniques

Prompt engineering is about taking a prompt you've written and improving it to get more reliable, higher-quality outputs. The process: write a baseline → evaluate → apply techniques → re-evaluate → repeat.

## The Iterative Cycle

1. **Set a goal** — define what you want the prompt to accomplish
2. **Write an initial prompt** — deliberately simple first attempt
3. **Evaluate** — run against your eval dataset, get a score
4. **Apply technique** — one change at a time
5. **Re-evaluate** — verify the change actually improved results

A score of 2.3/10 is normal for a first attempt. The goal is consistent improvement per iteration.

---

## Technique 1 — Being Clear and Direct

The first line is the most important part of your prompt. Use direct action verbs and state exactly what you want.

**Instead of:** "I need to know about those things people put on their roofs that use sun..."
**Use:** "Write three paragraphs about how solar panels work."

**Instead of:** "I was reading about renewable energy and geothermal sounds neat. What countries use it?"
**Use:** "Identify three countries that use geothermal energy. Include generation stats for each."

**Pattern:** `[Action verb] + [what to create] + [key constraints]`

Example improvement: "What should this person eat?" → "Generate a one-day meal plan for an athlete that meets their dietary restrictions."
**Score impact:** 2.32 → 3.92

---

## Technique 2 — Being Specific

Add guidelines that control what Claude produces. Two types:

### Output Quality Guidelines
List qualities the output should have: length, structure, specific attributes, tone. Example:
```
Guidelines:
1. Include accurate daily calorie amount
2. Show protein, fat, and carb amounts
3. Specify when to eat each meal
4. Use only foods that fit restrictions
5. List all portion sizes in grams
6. Keep budget-friendly if mentioned
```

### Process Steps
Tell Claude how to think through the problem step-by-step before answering. Use for complex reasoning tasks, decision-making, multi-angle analysis.

**Score impact of adding guidelines:** 3.92 → 7.86 (nearly doubled)

**When to use each:**
- Output guidelines → **almost always** (your consistency safety net)
- Process steps → complex problems, troubleshooting, critical thinking tasks

---

## Technique 3 — Structure with XML Tags

When prompts include large amounts of content, XML tags create clear boundaries between sections.

**Without tags:** Claude may struggle to distinguish instructions from data.
**With tags:** Clear delimiters make structure obvious.

```
<athlete_information>
- Height: 6'2"
- Weight: 180 lbs
- Goal: Build muscle
- Dietary restrictions: Vegetarian
</athlete_information>

Generate a meal plan based on the athlete information above.
```

Custom tag names work — use descriptive names (`<sales_records>` vs `<data>`, `<my_code>` vs `<code>`).

**Most valuable when:** including large amounts of context/data, mixing different content types (code + docs), working with complex prompts that interpolate multiple variables.

---

## Technique 4 — Providing Examples (One-shot / Multi-shot)

Show Claude what a good response looks like instead of describing it.

**One-shot:** single example to establish the pattern.
**Multi-shot:** multiple examples covering different scenarios and edge cases.

```
<sample_input>
Oh yeah, I really needed a flight delay tonight! Excellent!
</sample_input>

<ideal_output>
Negative
</ideal_output>

This example handles sarcasm — the tone appears positive but the meaning is negative.
```

**When to use examples:**
- Corner cases and edge scenarios (like sarcasm detection)
- Defining complex output formats (specific JSON structures)
- Showing exact style or tone required
- Ambiguous inputs with non-obvious correct handling

**Finding good examples:** use your highest-scoring eval outputs (score 10/10) as examples. Add context explaining **why** the output is ideal, not just the input/output pair.

**Always wrap examples in XML tags** — `<sample_input>` and `<ideal_output>` — to make the structure clear to Claude.

---

## Score Progression Example (Meal Planning Prompt)

| Version | Change Applied | Score |
|---------|---------------|-------|
| v1 | Basic ("What should this person eat?") | 2.32 |
| v2 | Clear + direct first line | 3.92 |
| v3 | Added output guidelines (6 specific rules) | 7.86 |
| v4 | Added examples from top-scoring outputs | 8.5+ |
