---
name: readme-refresh
description: refresh project readme files for repos, packages, plugins, and internal tools. use when asked to update, rewrite, audit, or create a README; align installation, usage, architecture, commands, links, badges, examples, support notes, and status with the current implementation.
---

# Readme Refresh

## Mission

Produce a README that lets a new user understand what the project is, install it, run it, validate it, and find the next source of truth without reading the entire repository.

## Inputs to collect

- Existing README, if present
- Repository tree or package structure
- Install and run commands
- Current project status, supported platforms, and known limitations
- Links to docs, runbooks, APIs, or examples

## Procedure

1. Identify the target audience: user, contributor, operator, or agent.
2. Inspect existing docs and repo structure before rewriting. Do not trust stale README claims without checking nearby files.
3. Preserve accurate project identity, license, safety warnings, and operational constraints.
4. Replace vague promises with concrete commands, paths, examples, and verification steps.
5. Separate quick start from deep detail. Keep the first screen useful.
6. Add or repair links to API docs, runbooks, troubleshooting, changelog, and contribution docs when they exist.
7. Flag unresolved gaps instead of inventing capabilities.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Updated README content or patch plan
- List of verified commands and unverified commands
- Open documentation gaps
- Recommended follow-up docs

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/documentation-operating-model.md`
- `../../references/readme-template.md`
- `../../references/doc-quality-checklist.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
