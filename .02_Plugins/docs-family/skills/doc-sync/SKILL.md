---
name: doc-sync
description: synchronize documentation with recent code, config, API, release, architecture, or workflow changes. use when asked to update docs after implementation, keep docs aligned with PRs, reconcile README/runbook/API docs, or create doc patches from a change summary.
---

# Doc Sync

## Mission

Apply targeted documentation updates that reflect actual changes while preserving source-of-truth hierarchy.

## Inputs to collect

- Change summary, diff, PR notes, release notes, or implementation files
- Affected docs and source-of-truth rules
- Audience and required output format

## Procedure

1. Identify what changed and which docs are affected.
2. Determine source-of-truth priority: code/tests/configs over stale docs; release and architecture records over informal notes.
3. Update only the sections that need synchronization unless a rewrite is requested.
4. Preserve accurate warnings, constraints, versions, and unsupported cases.
5. Add changelog or release-note pointers when user-facing behavior changed.
6. Run a doc audit pass on touched docs for broken links and contradictions.
7. Report anything that still needs human or owner verification.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Documentation patch or updated text
- Affected-docs list
- Verification notes
- Remaining gaps and owner-review items

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/doc-sync-checklist.md`
- `../../references/documentation-operating-model.md`
- `../../references/doc-quality-checklist.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
