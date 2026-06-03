---
name: api-docs
description: create, refresh, or audit api documentation for codebases, services, libraries, cli tools, schemas, and plugin interfaces. use when asked for endpoint docs, function docs, request/response examples, interface contracts, generated documentation plans, or developer-facing API reference material.
---

# API Docs

## Mission

Document interfaces so callers know what exists, how to call it, what inputs are valid, what outputs mean, and how errors behave.

## Inputs to collect

- Source files, routes, schemas, OpenAPI specs, types, or interface contracts
- Authentication and permission model
- Known examples or tests
- Version and deprecation status

## Procedure

1. Inventory public interfaces first. Do not document private helpers as public API unless requested.
2. For each interface capture purpose, inputs, outputs, errors, side effects, permissions, and examples.
3. Use source code, tests, and schemas as higher authority than old docs.
4. Call out breaking changes, deprecated parameters, and unstable behavior.
5. Include minimal working examples before exhaustive reference tables.
6. Cross-link to architecture contracts and troubleshooting material when relevant.
7. Mark unknowns explicitly as TODO rather than guessing.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- API reference draft or update plan
- Interface inventory
- Example calls and responses
- Error and permission notes
- Doc gaps needing owner review

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/api-docs-template.md`
- `../../references/doc-quality-checklist.md`
- `../../references/documentation-operating-model.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
