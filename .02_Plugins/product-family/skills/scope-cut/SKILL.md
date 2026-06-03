---
name: scope-cut
description: reduce bloated or risky product scope into a smaller, shippable, testable release. use when a feature, sprint, MVP, roadmap item, or agent plan is too large, unclear, expensive, risky, or drifting beyond the intended outcome.
---

# Scope Cut

## Mission

Protect speed and quality by cutting scope without cutting the core user value.

## Inputs to collect

- Current proposed scope
- Target user and primary outcome
- Deadline, release target, or resource constraint
- Must-haves, nice-to-haves, and disputed items
- Risks, dependencies, and validation needs
- Current implementation state, if any

## Procedure

1. Name the core user outcome in one sentence.
2. Classify scope into:
   - Core path
   - Support path
   - Delight layer
   - Admin/internal layer
   - Risky/unknown layer
3. Protect only the minimum path needed to deliver and test the outcome.
4. Move non-essential items into follow-up releases.
5. Cut by dependency, complexity, uncertainty, or low-value polish first.
6. Define what is explicitly out of scope.
7. Return a smaller plan with validation criteria.

## Guardrails

- Do not cut safety, privacy, migration, or rollback requirements just to save time.
- Do not cut observability for production-impacting work.
- Do not hide deferred work; record it as follow-up backlog.
- Preserve the user's ability to validate whether the release mattered.

## Expected output

- Original scope summary
- Keep / cut / defer table
- Revised MVP scope
- Non-goals
- Risks introduced by cuts
- Follow-up backlog
- Validation plan

## Reference loading

Load only when useful:

- `../../references/scope-cut-playbook.md`
- `../../references/mvp-template.md`
- `../../references/prioritization-models.md`
