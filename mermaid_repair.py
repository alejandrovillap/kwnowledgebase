#!/usr/bin/env python3
"""
mermaid_repair.py — Validate and auto-repair Mermaid diagrams in markdown text.

Three-stage pipeline (each stage only runs if the previous left a problem):
  1. Deterministic regex rules  — catches ~80% of errors, zero API cost
  2. mmdc validation            — exact error message (requires mermaid-cli)
  3. Claude repair call         — fixes anything stages 1-2 couldn't handle

Usage (module):
    from mermaid_repair import repair_all_in_text
    fixed_text, n = repair_all_in_text(raw_text, client=anthropic_client)

Usage (CLI):
    python mermaid_repair.py note.md            # repairs in-place
    python mermaid_repair.py note.md --dry-run  # prints diff, no write
    python mermaid_repair.py note.md --no-claude  # regex only, no API
"""

import os
import re
import subprocess
import tempfile
import argparse
from pathlib import Path


# ── Stage 1: Deterministic repair rules ──────────────────────────────────────
# Each entry: (compiled_pattern, replacement_string_or_callable)
# Applied in order — put safer/narrower rules first.

_RULES: list[tuple] = [
    # 1. Single arrow -> (not part of --> or <-->) → double arrow -->
    (re.compile(r'(?<![<\-])->(?!>)'), '-->'),

    # 2. Unquoted special chars in square-bracket labels: [cost: $5] → ["cost: $5"]
    #    Skip already-quoted labels and nested brackets.
    (
        re.compile(r'\[([^\]"\[]*[:#$&%@*][^\]"\[]*)\]'),
        lambda m: f'["{m.group(1)}"]',
    ),

    # 3. Same for round-bracket nodes: (cost: $5) → ("cost: $5")
    (
        re.compile(r'\(([^)"\']*[:#$&%@*][^)"\']*)\)'),
        lambda m: f'("{m.group(1)}")',
    ),

    # 4. flowchart / graph without a direction → add TD
    (re.compile(r'^(flowchart|graph)\s*$', re.MULTILINE), r'\1 TD'),

    # 5. Trailing whitespace on lines (breaks some parsers)
    (re.compile(r'[ \t]+$', re.MULTILINE), ''),

    # 6. Windows-style line endings → Unix
    (re.compile(r'\r\n?'), '\n'),
]


def _apply_rules(code: str) -> str:
    for pattern, repl in _RULES:
        code = pattern.sub(repl, code)
    return code


# ── Stage 2: mmdc validation ──────────────────────────────────────────────────

def _mmdc_available() -> bool:
    try:
        r = subprocess.run(['mmdc', '--version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _validate_with_mmdc(code: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.mmd', delete=False, encoding='utf-8'
    ) as f:
        f.write(code)
        tmp_in = f.name
    tmp_out = tmp_in.replace('.mmd', '.svg')
    try:
        r = subprocess.run(
            ['mmdc', '-i', tmp_in, '-o', tmp_out],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0:
            return True, ''
        return False, (r.stderr or r.stdout).strip()[:400]
    except subprocess.TimeoutExpired:
        return False, 'mmdc timed out'
    finally:
        for p in (tmp_in, tmp_out):
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass


# ── Heuristic check (fallback when mmdc is not installed) ────────────────────

def _heuristic_error(code: str) -> str:
    """Return a description of the first suspicious pattern found, or ''."""
    if re.search(r'(?<![<\-])->(?!>)', code):
        return "single arrow -> (should be -->)"
    if re.search(r'\[[^\]"]*[:#$&%@*][^\]"]*\]', code):
        return "unquoted special character in node label"
    opens = len(re.findall(r'^\s*subgraph\b', code, re.M))
    ends  = len(re.findall(r'^\s*end\s*$',   code, re.M))
    if opens > ends:
        return f"unclosed subgraph ({opens} opens, {ends} ends)"
    # Node IDs with spaces (not inside quotes or brackets)
    if re.search(r'(?:^|\s)([A-Za-z][A-Za-z0-9]* [A-Za-z])(?=\s*-->|\s*---)', code, re.M):
        return "node ID contains spaces"
    return ''


# ── Stage 3: Claude repair ────────────────────────────────────────────────────

_REPAIR_SYSTEM = (
    "You are a Mermaid diagram syntax expert. "
    "Fix ONLY syntax errors — never add, remove, or rename nodes or edges."
)

_REPAIR_PROMPT = """\
The following Mermaid diagram has a syntax error. Fix it so it parses correctly.

Error: {error}

Diagram:
```mermaid
{code}
```

Fix rules:
- Node IDs must not contain spaces — use underscores or camelCase
- Labels with special characters (:, #, &, $, %) must be quoted: ["label: value"]
- Use --> for arrows (not ->)
- Every subgraph must have a matching `end` on its own line
- flowchart and graph must have a direction: TD, LR, BT, or RL

Return ONLY the corrected Mermaid code — no fences, no explanation, no preamble."""


def _claude_repair(code: str, error: str, client) -> str:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",  # narrow task → cheapest model
        max_tokens=1024,
        system=_REPAIR_SYSTEM,
        messages=[{
            "role": "user",
            "content": _REPAIR_PROMPT.format(code=code, error=error),
        }],
    )
    raw = msg.content[0].text.strip()
    # Strip fences if Claude added them anyway
    raw = re.sub(r'^```(?:mermaid)?\s*\n?', '', raw)
    raw = re.sub(r'\n?```\s*$',            '', raw)
    return raw.strip()


# ── Public API ────────────────────────────────────────────────────────────────

def repair_block(code: str, client=None, use_mmdc: bool | None = None) -> tuple[str, str]:
    """
    Repair a single Mermaid code block (content only, no fences).

    Returns (repaired_code, action) where action is one of:
      'ok'       — no changes needed
      'rules'    — fixed by regex rules only
      'claude'   — fixed by Claude (stage 3)
    """
    original = code
    code = _apply_rules(code)

    if use_mmdc is None:
        use_mmdc = _mmdc_available()

    if use_mmdc:
        valid, error = _validate_with_mmdc(code)
        if valid:
            return code, ('rules' if code != original else 'ok')
        if client:
            code = _claude_repair(code, error, client)
            return code, 'claude'
        return code, 'rules'  # mmdc says invalid but no client to repair

    # No mmdc — use heuristics
    error = _heuristic_error(code)
    if not error:
        return code, ('rules' if code != original else 'ok')
    if client:
        code = _claude_repair(code, error, client)
        return code, 'claude'
    return code, 'rules'


def repair_all_in_text(text: str, client=None, verbose: bool = False) -> tuple[str, int]:
    """
    Find every ```mermaid block in *text*, repair each one, and return the
    updated text along with a count of blocks that were actually changed.
    """
    pattern  = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL)
    use_mmdc = _mmdc_available()
    changed  = 0

    def _replace(m):
        nonlocal changed
        raw_code  = m.group(1).rstrip()
        fixed, action = repair_block(raw_code, client=client, use_mmdc=use_mmdc)
        if action != 'ok':
            changed += 1
            if verbose:
                print(f"  [mermaid] {action}: repaired block")
        return f'```mermaid\n{fixed}\n```'

    updated = pattern.sub(_replace, text)
    return updated, changed


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Validate and repair Mermaid blocks in a markdown file.")
    ap.add_argument("file",        help=".md file to repair")
    ap.add_argument("--dry-run",   action="store_true", help="Print result without writing")
    ap.add_argument("--no-claude", action="store_true", help="Apply regex rules only (no API call)")
    args = ap.parse_args()

    from dotenv import load_dotenv
    import anthropic
    load_dotenv(Path(__file__).parent / ".env")

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")

    client = None if args.no_claude else anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    fixed, n = repair_all_in_text(text, client=client, verbose=True)

    if n == 0:
        print("No Mermaid blocks needed repair.")
        return

    print(f"\nRepaired {n} Mermaid block(s).")

    if args.dry_run:
        # Show a simple diff
        for orig, new in zip(
            re.findall(r'```mermaid.*?```', text,  re.DOTALL),
            re.findall(r'```mermaid.*?```', fixed, re.DOTALL),
        ):
            if orig != new:
                print("\n── BEFORE ──")
                print(orig)
                print("── AFTER ──")
                print(new)
    else:
        path.write_text(fixed, encoding="utf-8")
        print(f"Written: {path}")


if __name__ == "__main__":
    main()
