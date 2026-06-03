---
name: user-story
description: create or refine user stories, job stories, acceptance notes, and product intent from rough feature ideas, customer feedback, bug reports, roadmap items, or stakeholder requests. use when product work needs clear actors, outcomes, value, constraints, and testable behavior before engineering begins.
---

# User Story

## Mission

Convert vague product intent into concise, testable user stories that preserve user value, scope boundaries, and engineering handoff clarity.

## Inputs to collect

- Target user, role, or segment
- Problem, desired outcome, and current pain
- Feature idea, request, feedback, or bug context
- Constraints, non-goals, risks, and dependencies
- Evidence source: customer quote, analytics, stakeholder request, support ticket, or assumption

## Procedure

1. Identify the real user outcome before writing the story. Do not start from implementation details.
2. Separate user need, business value, and technical approach.
3. Write the story in one of these formats:
   - `As a <user>, I want <capability>, so that <outcome>.`
   - `When <situation>, I want to <action>, so I can <outcome>.`
   - `Given <context>, when <trigger>, then <result>.`
4. Add acceptance notes that are observable and testable.
5. Mark assumptions, unknowns, and evidence strength.
6. Identify non-goals to prevent scope creep.
7. If the story is too large, split by user value, workflow step, risk, or release stage.

## Guardrails

- Do not disguise implementation tasks as user stories unless the user is internal/developer-facing.
- Do not invent user evidence. Label inferred demand as assumption.
- Keep stories small enough to validate independently.
- Escalate security, privacy, compliance, or destructive behavior to the relevant review family.

## Expected output

- Story title
- User story or job story
- User value and business value
- Acceptance notes
- Non-goals
- Assumptions and open questions
- Suggested split, if oversized

## Reference loading

Load only when useful:

- `../../references/product-operating-model.md`
- `../../references/user-story-template.md`
- `../../references/requirements-template.md`
