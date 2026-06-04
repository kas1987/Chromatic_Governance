---
name: external-ui-platforms
description: evaluate public or external ui/ux platforms, low-code tools, prototype builders, hosted dashboards, and design/development platforms. use when the user asks which ui platform, builder, dashboard tool, or prototyping platform fits a use case.
---

# External UI Platforms

1. Define use case, audience, data sensitivity, auth, budget, export needs, and team skill.
2. Compare hosted builders, low-code tools, design platforms, and custom-coded options.
3. Call out vendor lock-in and data/security constraints.
4. Recommend best fit, fallback, and avoid list.
5. Provide an implementation path.

Use `references/interactive-gui-platforms.md`.

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
