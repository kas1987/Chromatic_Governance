---
name: eval-suite
description: create evaluation suites for llm agents, prompt workflows, tool-using agents, code assistants, plugin skills, or natural-language automation. use when measuring agent quality, comparing prompts/models, detecting instruction drift, or building pass/fail eval cases.
---

# Eval Suite

Use this skill when normal unit tests are not enough because behavior is probabilistic, language-based, or agentic.

## Inputs

- Agent, skill, prompt, or workflow being evaluated.
- Target behavior and unacceptable behavior.
- Representative tasks or transcripts.
- Tools/connectors the agent may use.
- Scoring preference: binary, rubric, numeric, or comparative.

## Procedure

1. **Define eval purpose**:
   - Regression detection.
   - Model/prompt comparison.
   - Safety compliance.
   - Tool-use quality.
   - Output quality.
2. **Build case categories**:
   - Happy path.
   - Ambiguous input.
   - Missing context.
   - Adversarial or prompt-injection input.
   - Tool failure.
   - Boundary/permission case.
3. **Write each eval case** with:

```markdown
ID:
Input:
Allowed context/tools:
Expected behavior:
Disallowed behavior:
Scoring rule:
```

4. **Choose scoring**:
   - Binary for hard requirements.
   - Rubric for writing/reasoning quality.
   - Numeric only when score definitions are clear.
5. **Define pass thresholds** by category.
6. **Include evaluator notes** so future agents score consistently.
7. **Add drift review cadence** for changing prompts, models, or tools.

## Output format

```markdown
# Eval Suite
## Purpose
## Scope
## Case matrix
## Scoring rubric
## Pass thresholds
## Failure triage
## Maintenance rules
```

## Scoring rules

Never score only on whether the answer sounds confident. Score on task completion, groundedness, policy compliance, tool discipline, and recoverability.

## Guardrails

- Do not treat untested code as complete.
- Separate expected behavior from current behavior.
- Mark inferred requirements as assumptions until confirmed.
- Prefer small, repeatable checks over one large vague review.
- Escalate when the pass/fail rule depends on product judgement, legal/security risk, data loss, payment behavior, authentication, or deployment.
- When uncertain, output a conservative test gap rather than claiming coverage.

## Handoff format

Return results using:

```markdown
# QA/Eval Result
## Scope
## Inputs reviewed
## Pass/fail summary
## Critical gaps
## Recommended checks
## Evidence / files referenced
## Next actions
```
