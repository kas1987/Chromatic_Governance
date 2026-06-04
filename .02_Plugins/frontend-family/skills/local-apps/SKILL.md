---
name: local-apps
description: choose and scaffold local app approaches including tui, cli, local web dashboards, python gui, electron, tauri, and desktop-style tools. use when the user asks for a local app, terminal ui, desktop app, offline tool, or local-first workflow.
---

# Local Apps

1. Choose the lightest local surface: script, CLI, TUI, local web, desktop, or hybrid.
2. Consider file access, offline use, packaging, performance, and user comfort.
3. Recommend stack and folder structure.
4. Include install/run commands, state persistence, logging, and update approach.
5. For TUI, define keyboard shortcuts and screen states.

Use `references/local-app-patterns.md`.

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
