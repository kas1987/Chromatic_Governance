---
name: tailwind-system
description: create tailwind design systems, presets, config tokens, utility conventions, component recipes, and best-practice tailwind workflows. use when the user asks about tailwind, utility-first css, class organization, or reusable tailwind ui patterns.
---

# Tailwind System

1. Define whether Tailwind is the primary style system or an app-level utility layer.
2. Create theme tokens in the Tailwind config or shared preset.
3. Define component recipes for repeated patterns.
4. Establish class ordering, responsive conventions, dark mode, and custom CSS escape hatches.
5. Include examples for common components and dashboard layouts.

Use `references/tailwind-system-guide.md`.

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
