---
name: css-library
description: design and maintain reusable css libraries, design tokens, base styles, utilities, layout systems, component css, and documentation. use when the user asks how to build, organize, govern, or refactor css for a project or shared ui system.
---

# CSS Library

1. Identify whether the project needs plain CSS, CSS modules, Sass, CSS-in-JS, Tailwind, or a hybrid.
2. Define tokens first: color, typography, spacing, radius, shadow, motion, z-index, breakpoints.
3. Define base/reset, layout primitives, utilities, and component styles.
4. Add state, accessibility, responsive, and theming rules.
5. Produce a file tree, naming convention, and example usage.
6. Include governance: what belongs in the library and what remains app-specific.

Use `references/css-library-standards.md`.

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
