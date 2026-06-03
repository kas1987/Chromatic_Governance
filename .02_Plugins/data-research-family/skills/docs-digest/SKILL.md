---
name: docs-digest
description: digest official documentation, technical references, standards, SDK docs, changelogs, README files, or API guides into actionable implementation guidance. use when the user asks what docs say, how to use an API, what changed, or how to convert documentation into build steps.
---

# Docs Digest

## Mission

Turn documentation into accurate, scoped implementation guidance.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. Identify the exact documentation version, product, SDK, framework, or standard.
2. Extract required setup, auth, configuration, limits, and examples.
3. Separate normative requirements from examples and recommendations.
4. Capture version-specific or platform-specific behavior.
5. List gotchas, limits, deprecations, and migration notes.
6. Translate docs into implementation checklist or handoff.
7. Route implementation work to architecture, RPI, QA/eval, or security as needed.

## Guardrails

- Use official docs as the primary source for technical behavior.
- Do not assume older documentation still applies.
- Do not invent parameters, flags, or API behavior.
- Mark unclear docs and recommend verification tests.

## Expected output

- Document scope
- Key facts
- Setup/config checklist
- Limits and gotchas
- Implementation guidance
- Open questions
- Handoff

## Reference loading

Load only when useful:

- `../../references/docs-digest-template.md`
- `../../references/api-change-watch-template.md`
- `../../references/citation-quality-rules.md`
