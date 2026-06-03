---
name: doc-audit
description: audit documentation quality, freshness, completeness, contradictions, broken links, outdated commands, missing ownership, and mismatch between docs and implementation. use when asked to review docs, find stale documentation, check documentation health, or prepare a doc cleanup plan.
---

# Doc Audit

## Mission

Find documentation drift and prioritize fixes by user impact, operational risk, and implementation mismatch.

## Inputs to collect

- Docs directory, README files, runbooks, API docs, changelogs, and repo structure
- Current implementation files, tests, configs, or release notes
- Known project status and owners

## Procedure

1. Inventory docs and classify by type: README, guide, runbook, API reference, troubleshooting, architecture, policy, release.
2. Check freshness signals, but treat content as the real source. Recent modification time does not prove correctness.
3. Compare claims against source files, tests, configs, manifests, and scripts.
4. Find contradictions, broken links, obsolete commands, missing prerequisites, and orphaned docs.
5. Score findings by severity: blocker, high, medium, low.
6. Recommend delete, merge, rewrite, verify, or owner-review actions.
7. Do not silently rewrite large docs during an audit unless requested.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Doc audit report
- Finding table with severity and evidence
- Recommended fixes
- Docs to archive, merge, or rewrite

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/doc-audit-template.md`
- `../../references/doc-quality-checklist.md`
- `../../references/documentation-operating-model.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
