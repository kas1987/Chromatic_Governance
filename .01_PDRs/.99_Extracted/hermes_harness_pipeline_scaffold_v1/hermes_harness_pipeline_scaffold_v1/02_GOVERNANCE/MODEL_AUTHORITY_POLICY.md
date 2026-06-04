# Model Authority Policy

## Purpose

Define what each model tier is allowed to decide, execute, and review.

## Authority Layers

| Layer | Authority | Can Decide | Cannot Decide |
|---|---|---|---|
| Frontier Planner | Claude/GPT/Gemini | architecture, PDRs, eval design, escalation interpretation | direct merge without CI |
| Local Worker | Hermes | bounded C1/C2 execution from mission packet | architecture changes, broad refactors, policy changes |
| Local Coder | Qwen Coder | bounded code edits and tests | unscoped redesigns |
| CI/Test Layer | automated tests | objective pass/fail | product judgment |
| GitHub Review | reviewer/bot/human | PR approval guidance | bypass governance |

## Core Rules

1. Local models do not invent scope.
2. Local models stop when required inputs are missing.
3. Local models stop when a forbidden file is required.
4. Local models stop after one failed retry unless mission says otherwise.
5. Frontier models are used for mission creation and exception review, not routine execution.
6. CI and tests are the default validation authority.

## Escalation Triggers

Escalate to frontier review when:

- acceptance criteria are ambiguous
- CI fails twice
- model proposes broad architecture change
- forbidden files are needed
- risk class is high
- privacy class exceeds local route policy
- implementation changes governance behavior
