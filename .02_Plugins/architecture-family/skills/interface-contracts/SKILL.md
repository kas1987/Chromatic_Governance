---
name: interface-contracts
description: define or review explicit contracts between modules, services, APIs, plugins, agents, tools, files, schemas, commands, events, or external systems. use when behavior crosses a boundary and needs stable inputs, outputs, errors, ownership, compatibility, versioning, and test obligations.
---

# Interface Contracts


Use this skill to make boundaries explicit before agents implement or refactor across them.

## Inputs

Collect or infer:

- Boundary being defined: API, CLI, module, event, schema, file, plugin, agent, or MCP/tool call.
- Producers and consumers.
- Input and output shapes.
- Error behavior and retries.
- Versioning and compatibility expectations.
- Security and permission constraints.

## Procedure

1. **Name the boundary** and its owner.
2. **Define producer and consumer responsibilities**.
3. **Specify contract fields**:
   - Inputs.
   - Outputs.
   - Side effects.
   - Errors.
   - Idempotency.
   - Timeouts and retries.
   - Auth/permission assumptions.
   - Versioning and deprecation.
4. **List forbidden dependencies** that would violate the boundary.
5. **Define contract tests** using examples and negative cases.
6. **Identify rollout requirements** when changing an existing contract.

Use `references/interface-contract-template.md` as the default format.

## Output standard

Produce a contract that can be reviewed by both sides of the boundary and converted into tests.

## Guardrails

- Do not rely on implicit behavior across component boundaries.
- Do not let consumers reach into producer internals.
- Do not change a public contract without migration and compatibility notes.
- Escalate if the contract exposes secrets, user data, destructive operations, or external write access.


## Handoff format

Return results using:

```markdown
# Architecture Result
## Scope
## Inputs reviewed
## Executive finding
## Decisions / recommendations
## Risks and tradeoffs
## Required follow-ups
## Files or interfaces affected
## Evidence / assumptions
```
