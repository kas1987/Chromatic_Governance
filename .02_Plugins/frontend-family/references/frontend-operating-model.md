# Frontend Operating Model

## Choose by outcome

- Asset recovery/migration: use `webpage-asset-extract`.
- Reusable styling: use `css-library` or `tailwind-system`.
- Reusable UI primitives: use `component-library`.
- Usability review: use `ui-best-practices`.
- Internal tools and metrics: use `quick-dashboard`.
- Custom app controls: use `interactive-gui`.
- Local-first utilities: use `local-apps`.
- Hosted/no-code/portfolio/prototype tools: use `external-ui-platforms`.
- 3D visuals or models: use `blender-3d-assets`.

## Required output discipline

Every frontend result should identify: target user, platform, runtime, asset sources, interaction states, accessibility requirements, responsive breakpoints, performance risks, and handoff artifacts.

## Model routing (front-end design lane)

Front-end work splits into two routing lanes — keep them separate so design
judgment is not down-routed to a code-tier model:

| Lane | Work | C-level | Model |
|---|---|---|---|
| **Design** | look-and-feel, layout, design tokens, novel UI framing | C4 | `opus` (the `frontend-experience-architect` agent / `visual-design` skill) |
| **Visual triage** | comparing renders, spotting visual regressions from screenshots | — | vision-capable model (`claude` / `gpt` / `qwen3-vl`) |
| **Implementation** | CSS/Tailwind, components, dashboards from an approved design | C2–C3 | `sonnet` (build skills) |
| **Mechanical** | asset extraction, token-file generation, formatting | C1 | `haiku` |

Rationale: front-end design is creative and knowledge-bound, where the
Sonnet/Opus crossover fails (`~/.claude/governance/subagent-token-efficiency.md`,
`model-effort-routing.md`). Implementation of an *already-approved* design is
known-pattern code → `sonnet`. Never route design judgment to a local/open model.
