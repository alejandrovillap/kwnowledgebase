---
title: Prompt Engineering
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["prompt-engineering", "iterative-improvement", "claude-code-assistant", "xml-tags", evaluation, "one-shot", "multi-shot"]
keywords: [prompt engineering, iterative improvement, clear and direct, specific, XML tags, examples, "one-shot", "multi-shot", PromptEvaluator, CCA, D4]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Prompt Engineering

Prompt engineering is about taking a prompt you've written and improving it to get more reliable, higher-quality outputs through iterative refinement — starting with a basic prompt, evaluating its performance, then systematically applying techniques to improve it.

## The Iterative Improvement Cycle

1. **Set a goal** — Define what you want your prompt to accomplish
2. **Write an initial prompt** — Create a basic first attempt
3. **Evaluate the prompt** — Test it against your criteria
4. **Apply prompt engineering techniques** — Use specific methods to improve performance
5. **Re-evaluate** — Verify that your changes actually improved the results

Repeat steps 4–5 until satisfied. Each iteration should show measurable improvement in evaluation scores.

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

Keep test cases low (2–3) during development. Don't be discouraged by low initial scores — a score of 2.3/10 is typical for a first attempt.

---

## Technique 1: Being Clear and Direct

The first line of your prompt is the most important. Focus on two principles:

**Clear** — Use simple language, state exactly what you want, lead with a straightforward statement of the task.

**Direct** — Use instructions, not questions. Start with action verbs: "Write," "Create," "Generate."

| Weak | Strong |
|---|---|
| "I need to know about solar panels, those things on roofs..." | "Write three paragraphs about how solar panels work." |
| "What countries use geothermal energy?" | "Identify three countries that use geothermal energy. Include generation stats for each." |

**Real-world impact:** Changing a weak first line improved evaluation score from 2.32 → 3.92.

---

## Technique 2: Being Specific

Provide clear guidelines or steps that direct Claude toward the output you want.

**Two types of specificity:**

**Output Quality Guidelines** — Control length, structure, format, attributes, tone:
```
Guidelines:
1. Include accurate daily calorie amount
2. Show protein, fat, and carb amounts
3. Specify when to eat each meal
4. Use only foods that fit restrictions
5. List all portion sizes in grams
```

**Process Steps** — Provide steps for Claude to follow systematically, especially for complex decisions or multi-angle analysis.

**When to use each:**
- Always include output guidelines
- Add process steps for troubleshooting, decision-making, critical thinking

**Real-world impact:** Adding guidelines improved score from 3.92 → 7.86 (nearly doubled).

---

## Technique 3: Structure with XML Tags

XML tags create clear boundaries when prompts contain large amounts of content, mixed data types, or interpolated variables.

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

---

## Technique 4: Providing Examples (Few-Shot Prompting)

Providing input/output pairs is one of the most effective techniques. This is called **one-shot** (single example) or **multi-shot** (multiple examples).

```xml
<sample_input>Oh yeah, I really needed a flight delay tonight! Excellent!</sample_input>
<ideal_output>Negative</ideal_output>

This example is negative because it uses sarcasm.
```

**When examples are most useful:**
- Handling corner cases (e.g., sarcasm in sentiment analysis)
- Defining complex output formats (specific JSON structures)
- Showing exact style or tone
- Demonstrating how to handle ambiguous inputs

**Finding good examples:** Use your highest-scoring evaluation outputs as examples. Add context explaining *why* the output is good, not just the input/output pair itself.

**Best practices:**
- Always use XML tags to structure examples clearly
- Be explicit: "Here is an example input with an ideal response"
- Include examples that address your most common failure cases
- Explain why your example outputs are considered ideal
