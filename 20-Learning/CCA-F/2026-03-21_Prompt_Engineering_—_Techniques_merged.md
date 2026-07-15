---
certification: CCA
confidence: high
date: '2026-03-21'
keywords:
- CCA
- D4
- PromptEvaluator
- XML tags
- clear and direct
- eval cycle
- examples
- iterative improvement
- multi-shot
- multishot
- one-shot
- output guidelines
- process steps
- prompt engineering
- specific
project: null
source: notion-migration, notion-migration
status: active
tags:
- claude
- claude-code-assistant
- evaluation
- iterative-improvement
- multi-shot
- multishot
- one-shot
- output-guidelines
- prompt-engineering
- xml-tags
target_folder: 20-Learning/CCA-F
technology: gen-ai
title: Prompt Engineering — Techniques
type: resume
updated: '2026-07-13'
---

Prompt engineering is the practice of taking a prompt you've written and improving it to get more reliable, higher-quality outputs through iterative refinement — starting with a basic prompt, evaluating its performance, then systematically applying techniques to improve it. A score of 2.3/10 is normal for a first attempt; the goal is consistent, measurable improvement per iteration.

---

## The Iterative Improvement Cycle

1. **Set a goal** — Define what you want your prompt to accomplish
2. **Write an initial prompt** — Start deliberately simple
3. **Evaluate** — Run against your eval dataset, get a score
4. **Apply a technique** — One change at a time
5. **Re-evaluate** — Verify the change actually improved results

Repeat steps 4–5 until satisfied.

---

## Setting Up Your Evaluation Pipeline

Use a `PromptEvaluator` class to handle dataset generation and model grading:

```python
evaluator = PromptEvaluator(max_concurrent_tasks=5)
```

Start with low concurrency (3) to avoid rate limit errors. Generate test cases automatically:

```python
dataset = evaluator.generate_dataset(
    task_description="Write a compact, concise 1 day meal plan for a single athlete",
    prompt_inputs_spec={
        "height": "Athlete's height in cm",
        "weight": "Athlete's weight in kg",
        "goal": "Goal of the athlete",
        "restrictions": "Dietary restrictions of the athlete"
    },
    output_file="dataset.json",
    num_cases=3
)
```

Keep test cases low (2–3) during development.

---

## Technique 1: Being Clear and Direct

The first line of your prompt is the most important. Focus on two principles:

**Clear** — Use simple language, state exactly what you want, lead with a straightforward statement of the task.

**Direct** — Use instructions, not questions. Start with action verbs: "Write," "Create," "Generate."

**Pattern:** `[Action verb] + [what to create] + [key constraints]`

| Weak | Strong |
|---|---|
| "I need to know about those things people put on their roofs that use sun..." | "Write three paragraphs about how solar panels work." |
| "I was reading about renewable energy and geothermal sounds neat. What countries use it?" | "Identify three countries that use geothermal energy. Include generation stats for each." |
| "What should this person eat?" | "Generate a one-day meal plan for an athlete that meets their dietary restrictions." |

**Score impact:** 2.32 → 3.92

---

## Technique 2: Being Specific

Add clear guidelines or steps that direct Claude toward the output you want. There are two types:

### Output Quality Guidelines

Control length, structure, format, attributes, and tone by listing explicit qualities the output should have:

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

Tell Claude how to think through the problem step-by-step before answering. Use for complex reasoning tasks, decision-making, troubleshooting, or multi-angle analysis.

### When to Use Each

- **Output guidelines** → almost always (your consistency safety net)
- **Process steps** → complex problems, troubleshooting, critical thinking tasks

**Score impact of adding guidelines:** 3.92 → 7.86 (nearly doubled)

---

## Technique 3: Structure with XML Tags

XML tags create clear boundaries when prompts contain large amounts of content, mixed data types, or interpolated variables. Without tags, Claude may struggle to distinguish instructions from data; with tags, the structure is unambiguous.

```xml
<athlete_information>
- Height: 6'2"
- Weight: 180 lbs
- Goal: Build muscle
- Dietary restrictions: Vegetarian
</athlete_information>

Generate a meal plan based on the athlete information above.
```

**Best practices:**
- Use descriptive tag names: `<sales_records>` is better than `<data>`
- Wrap code separately from documentation: `<my_code>` and `<docs>`
- Use tags for examples too: `<sample_input>` and `<ideal_output>`

**Most valuable when:** including large amounts of context or data, mixing different content types (e.g., code + documentation), or working with complex prompts that interpolate multiple variables.

---

## Technique 4: Providing Examples (Few-Shot Prompting)

Show Claude what a good response looks like instead of only describing it. Providing input/output pairs is one of the most effective techniques overall.

- **One-shot:** A single example to establish the pattern
- **Multi-shot:** Multiple examples covering different scenarios and edge cases

```xml
<sample_input>Oh yeah, I really needed a flight delay tonight! Excellent!</sample_input>
<ideal_output>Negative</ideal_output>

This example handles sarcasm — the tone appears positive but the meaning is negative.
```

**When examples are most useful:**
- Corner cases and edge scenarios (e.g., sarcasm in sentiment analysis)
- Defining complex output formats (specific JSON structures)
- Showing exact style or tone required
- Demonstrating how to handle ambiguous inputs with non-obvious correct handling

**Finding good examples:** Use your highest-scoring evaluation outputs (score 10/10) as examples. Add context explaining *why* the output is ideal — not just the input/output pair itself.

**Always wrap examples in XML tags** (`<sample_input>` and `<ideal_output>`) to make the structure clear to Claude.

---

## Score Progression Example (Meal Planning Prompt)

| Version | Change Applied | Score |
|---------|---------------|-------|
| v1 | Basic ("What should this person eat?") | 2.32 |
| v2 | Clear + direct first line | 3.92 |
| v3 | Added output guidelines (6 specific rules) | 7.86 |
| v4 | Added examples from top-scoring outputs | 8.5+ |
