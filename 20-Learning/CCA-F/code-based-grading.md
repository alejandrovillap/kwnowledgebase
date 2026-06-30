---
title: Code based grading
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: ["code-grading", "syntax-validation", "prompt-evaluation", "json-validation", "python-ast", "format-checking", "model-evaluation"]
keywords: [code grading, eval, syntax validation, JSON validation, Python AST, regex, grader, prompt evaluation, format checking, combined scoring]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Code Based Grading

When evaluating AI models that generate code, you need more than checking if the response makes sense — you also need to verify the generated code has valid syntax and follows the correct format.

## What Code Grading Validates

1. **Format** — response returns only the requested code type (Python, JSON, or Regex) without explanations
2. **Valid Syntax** — the generated code parses correctly as the intended language
3. **Task Following** — the response directly addresses what was asked and is accurate

The first two are handled by the **code grader**. Task following is evaluated by the **model grader**. Together they provide comprehensive evaluation.

## Syntax Validation Functions

Three helper functions attempt to parse the output and return a binary score:

```python
def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0

def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0
```

If parsing succeeds → 10 (valid syntax). If it fails → 0 (invalid syntax).

## Dataset Format Requirements

Test cases must specify the expected output format so the grader knows which validator to use:

```json
{
    "task": "Create a Python function to validate an AWS IAM username",
    "format": "python"
}
```

## Improving Prompt Clarity

Explicit format instructions reduce syntax errors:

```
* Respond only with Python, JSON, or a plain Regex
* Do not add any comments, commentary, or explanation
```

You can also use a pre-filled assistant message to encourage Claude to return raw code:

```python
add_assistant_message(messages, "```code")
```

This tells Claude to start generating code content directly.

## Combining Scores

Merge the model grader score (content quality) with the code grader score (technical correctness):

```python
model_grade = grade_by_model(test_case, output)
model_score = model_grade["score"]
syntax_score = grade_syntax(output, test_case)

score = (model_score + syntax_score) / 2
```

Equal weight to both content quality and technical correctness. Adjust weights based on what matters most for your use case.

## Key Principle

The baseline score isn't inherently good or bad — what matters is whether you can improve it by refining prompts. Code-based grading gives you a **quantitative** way to measure prompt engineering progress rather than relying on subjective assessment.
