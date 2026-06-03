---
name: runbook
description: create or update operational runbooks for deploying, operating, monitoring, restoring, or maintaining a system. use when asked for runbooks, operational procedures, incident steps, maintenance guides, backup/restore instructions, escalation procedures, or on-call documentation.
---

# Runbook

## Mission

Create operator-ready procedures that reduce uncertainty during routine operations or incidents.

## Inputs to collect

- System name and purpose
- Environments and owners
- Known commands, dashboards, logs, alerts, and dependencies
- Recovery, rollback, or escalation requirements
- Risks and expected failure modes

## Procedure

1. Start with scope, owner, and when to use the runbook.
2. Separate routine operation from incident response.
3. Write commands as copy-safe blocks and include expected successful output where possible.
4. Add prechecks before destructive or state-changing steps.
5. Add rollback, verification, and escalation steps.
6. Cross-link observability, release, security, and troubleshooting references.
7. Flag any missing access, dashboards, secrets, or environment assumptions.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Runbook document
- Precheck and verification checklist
- Rollback and escalation instructions
- Open operational gaps

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/runbook-template.md`
- `../../references/troubleshooting-template.md`
- `../../references/documentation-operating-model.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
