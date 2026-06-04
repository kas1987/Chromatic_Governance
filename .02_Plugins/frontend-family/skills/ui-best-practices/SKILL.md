---
name: ui-best-practices
description: review and improve ui/ux designs for usability, accessibility, responsiveness, information architecture, forms, interaction states, and performance. use when the user asks for frontend best practices, ui critique, ux review, or design polish.
---

# UI Best Practices

1. Identify the user's goal, target audience, device, and task frequency.
2. Review layout, hierarchy, navigation, forms, states, responsiveness, accessibility, and performance.
3. Separate must-fix issues from polish.
4. Provide concrete changes and examples.
5. Include keyboard, screen-reader, and contrast considerations where relevant.

Use `references/ui-ux-review-checklist.md`.

## Core procedure

See skill description above and `references/` subdirectory for detailed guidance.
Follow the numbered steps in this document, produce the specified output artifacts,
and verify against the guardrails before completing the task.

## Output format

Deliverables as described in the skill body above. Typically includes source files,
component definitions, or documentation placed at paths specified in the skill steps.

## Guardrails

- Limit changes to UI/frontend layer only; do not modify backend logic or APIs
- Validate accessibility (WCAG AA minimum) for any user-facing components produced
- Do not introduce new dependencies without explicit user approval
