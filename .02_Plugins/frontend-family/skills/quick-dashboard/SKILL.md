---
name: quick-dashboard
description: design or scaffold quick dashboards, admin panels, kpi views, internal tools, status boards, and monitoring uis. use when the user asks for dashboards, control panels, reporting views, metrics uis, or quick visual management interfaces.
---

# Quick Dashboard

1. Define the decision the dashboard must support.
2. Identify data sources, refresh cadence, confidence, and owner.
3. Choose layout: KPI strip, table, filters, status cards, timeline, chart grid, or control-room view.
4. Include loading, empty, stale data, and error states.
5. Produce a layout spec, component list, and implementation scaffold.

Use `references/dashboard-patterns.md`.

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
