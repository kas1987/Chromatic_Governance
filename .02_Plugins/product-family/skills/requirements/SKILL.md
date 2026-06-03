---
name: requirements
description: turn product ideas, feature requests, stakeholder notes, and discovery findings into functional requirements, non-functional requirements, constraints, dependencies, assumptions, and open questions. use before planning, architecture, QA, or implementation when scope needs to be precise and testable.
---

# Requirements

## Mission

Produce requirements that engineering, QA, design, and agents can execute against without guessing.

## Inputs to collect

- Problem statement and target users
- Desired outcomes and success metrics
- Existing behavior and proposed behavior
- Functional requirements
- Non-functional requirements: performance, reliability, security, accessibility, compatibility, observability
- Dependencies, constraints, and non-goals
- Evidence and decision owner, when known

## Procedure

1. Start with the problem and outcome, not the feature mechanism.
2. Classify every requirement as functional, non-functional, constraint, dependency, or assumption.
3. Convert vague words into measurable conditions where possible.
4. Separate must-have launch criteria from later enhancements.
5. Identify conflicts with existing docs, architecture, security, or release constraints.
6. Attach acceptance criteria or hand off to `qa-eval-family/acceptance-criteria`.
7. Produce a requirements package suitable for planning or architecture review.

## Guardrails

- Do not over-specify implementation when product intent is enough.
- Do not leave ambiguous requirements unmarked.
- Do not treat stakeholder preference as validated user need without evidence.
- Surface tradeoffs when requirements conflict.

## Expected output

- Problem statement
- Goals and non-goals
- Functional requirements
- Non-functional requirements
- Constraints and dependencies
- Assumptions and open questions
- Launch criteria
- Recommended next family: architecture, QA/eval, security, or release

## Reference loading

Load only when useful:

- `../../references/requirements-template.md`
- `../../references/product-operating-model.md`
- `../../references/product-risk-model.md`
