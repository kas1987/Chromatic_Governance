---
name: troubleshooting
description: create or update troubleshooting guides for common failures, setup issues, runtime errors, agent workflow problems, deployment failures, and user support paths. use when asked to diagnose recurring issues, write known-issue docs, or document fixes and escalation paths.
---

# Troubleshooting

## Mission

Turn repeated problems into fast diagnosis paths with symptoms, causes, fixes, verification, and escalation.

## Inputs to collect

- Error messages, logs, screenshots, support tickets, or incident notes
- Affected environment and version
- Known fixes and reproduction steps
- Escalation contacts or ownership model

## Procedure

1. Group issues by symptom first, not by internal component.
2. For each issue capture symptoms, likely causes, checks, fixes, verification, and escalation.
3. Prioritize high-frequency and high-impact failures.
4. Include exact commands only when safe and environment-scoped.
5. Warn before destructive fixes or cache/data deletion.
6. Link to runbooks, observability docs, and security guidance when relevant.
7. Mark uncertain fixes as hypotheses requiring validation.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Troubleshooting guide
- Issue matrix
- Verification steps
- Escalation rules
- Unresolved recurring problems

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/troubleshooting-template.md`
- `../../references/doc-quality-checklist.md`
- `../../references/documentation-operating-model.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
