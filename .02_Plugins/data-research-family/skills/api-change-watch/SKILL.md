---
name: api-change-watch
description: monitor or review API, SDK, framework, model, dependency, schema, or platform changes that could affect an implementation. use when the user asks what changed, whether an integration may break, or how to track breaking changes over time.
---

# API Change Watch

## Mission

Find changes that matter and convert them into impact, risk, and action items.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. Identify the API, SDK, dependency, model, platform, or schema and current version.
2. Review changelogs, migration guides, release notes, deprecation notices, and issue trackers.
3. Classify changes as breaking, behavior-changing, security-relevant, performance-relevant, feature addition, or documentation-only.
4. Map affected code paths, configs, data contracts, tests, and docs.
5. Assign impact and urgency.
6. Recommend validation tests and mitigation.
7. Route required implementation to RPI/release/QA/security.

## Guardrails

- Do not assume semantic versioning is followed perfectly.
- Treat security notices and deprecations as high-priority review items.
- Do not update dependencies automatically unless explicitly requested through another family.
- Mark unknown impact rather than guessing.

## Expected output

- Watched component
- Version/change summary
- Impact matrix
- Breaking/deprecation risks
- Required validation
- Recommended owner/handoff

## Reference loading

Load only when useful:

- `../../references/api-change-watch-template.md`
- `../../references/change-impact-matrix.md`
- `../../references/research-operating-model.md`
