---
title: Model Based Grading
date: 2026-03-21
type: concept
technology: "gen-ai"
status: active
tags: ["model-grading", evaluation, "prompt-engineering", "llm-assessment", "code-graders"]
keywords: [model grading, grader, evaluation, grade_by_model, strengths weaknesses reasoning score, run_eval, run_test_case, average score, code grader, human grader, evaluation criteria]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Model Based Grading

One of three grader types in prompt evaluation workflows. A grader takes model output and returns a measurable signal — typically a number 1–10 where 10 = high quality.

## Three Types of Graders

**Code graders** — programmatic checks: output length, word presence/absence, JSON/Python/regex syntax validation, readability scores. Requirement: returns a usable numeric signal.

**Model graders** — feed the output into a second API call for evaluation. Highly flexible: assesses quality, instruction following, completeness, helpfulness, safety.

**Human graders** — most flexible but time-consuming. Useful for general quality, depth, comprehensiveness, conciseness, relevance.

## When to Use Each

For code generation prompts, the criteria split naturally:
- **Format** (returns only Python/JSON/Regex without explanation) → Code grader
- **Valid Syntax** (produced code compiles/parses) → Code grader
- **Task Following** (code actually solves the user's problem) → Model grader (requires flexibility)

## Implementing a Model Grader

```python
def grade_by_model(test_case, output):
    eval_prompt = """
    You are an expert code reviewer. Evaluate this AI-generated solution.

    Task: {task}
    Solution: {solution}

    Provide your evaluation as a structured JSON object with:
    - "strengths": An array of 1-3 key strengths
    - "weaknesses": An array of 1-3 key areas for improvement
    - "reasoning": A concise explanation of your assessment
    - "score": A number between 1-10
    """

    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")

    eval_text = chat(messages, stop_sequences=["```"])
    return json.loads(eval_text)
```

**Key insight:** Always ask for strengths, weaknesses, and reasoning alongside the score. Without this context, models default to middling scores around 6.

## Integrating into the Eval Workflow

```python
def run_test_case(test_case):
    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)
    score = model_grade["score"]
    reasoning = model_grade["reasoning"]

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
    }

from statistics import mean

def run_eval(dataset):
    results = []
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean([result["score"] for result in results])
    print(f"Average score: {average_score}")
    return results
```

The average score gives you an objective metric to track as you iterate on your prompt. Model graders can be somewhat capricious but provide a consistent baseline for measuring improvement direction.

## Exam Relevance

Falls in **D4 (Prompt Engineering)**. Connects to the eval pipeline: write baseline prompt → run_eval → get average score → apply one technique → re-evaluate → compare scores. Model grading is the practical alternative to code-based grading when the evaluation criterion requires subjective judgment (quality, helpfulness, instruction-following).
