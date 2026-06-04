---
name: component-library
description: plan and document reusable frontend component libraries, component apis, variants, states, accessibility, tests, and usage examples. use when the user asks for ui components, design system primitives, reusable react/vue/svelte components, or component governance.
---

# Component Library

1. Identify framework and design-token source.
2. Define component inventory and priority.
3. For each component, specify anatomy, props/API, variants, states, accessibility, examples, and tests.
4. Separate primitive components from composed application components.
5. Include Storybook or equivalent documentation guidance when useful.

Use `references/component-library-blueprint.md`.

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
