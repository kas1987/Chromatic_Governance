---
name: dev-guide
description: create or update developer guides for onboarding, local setup, repo conventions, contribution flows, testing, architecture orientation, and plugin or service development. use when asked to help new contributors, document setup, write contributor docs, or standardize development workflow.
---

# Dev Guide

## Mission

Enable a new developer or agent to set up, understand, modify, test, and submit work safely.

## Inputs to collect

- Repo tree, package manager, runtime versions, and environment requirements
- Build, test, lint, and validation commands
- Branching, review, and release conventions
- Architecture notes and key directories

## Procedure

1. Define the target contributor: human dev, coding agent, operator, or reviewer.
2. Document setup from a clean machine or fresh checkout.
3. Include environment requirements, config files, and secrets handling without exposing secrets.
4. Map key directories and common workflows.
5. Document test and validation gates.
6. Explain contribution, PR, review, and release expectations.
7. Add troubleshooting links for common setup failures.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Developer guide draft or update
- Setup checklist
- Repo map
- Validation commands
- Contribution workflow notes

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/dev-guide-template.md`
- `../../references/doc-quality-checklist.md`
- `../../references/documentation-operating-model.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
