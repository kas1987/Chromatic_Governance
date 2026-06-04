---
name: interactive-gui
description: plan and scaffold interactive guis, ui/ux platforms, web apps, control panels, demos, and low-code style interfaces. use when the user asks for an interactive interface, clickable prototype, gui app, visual workflow, or local/hosted ui surface.
---

# Interactive GUI

1. Clarify runtime: browser, local, desktop, hosted, embedded, or prototype.
2. Clarify interaction complexity: forms, drag/drop, canvas, charts, 3D, real-time, auth, data editing.
3. Choose framework or platform by use case and constraints.
4. Specify screens, components, state model, and event flow.
5. Produce a scaffold plan or implementation tree.

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
