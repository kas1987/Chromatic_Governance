# PDR: Hermes Local Agent Pipeline for Chromatic Harness v2

## Status

Draft v1 for local-agent implementation.

## Problem

The harness currently benefits from frontier models for design, planning, synthesis, and complex review, but relying on frontier models for repeated execution wastes capability and cost. Local models such as Hermes, Qwen, Llama, and Gemma can perform structured execution if given bounded mission packets, explicit acceptance criteria, schemas, tests, and stop conditions.

## Goal

Create a pipeline where frontier models generate reusable mission packets and local models execute bounded work under governance, validation, and CI.

## Non-Goal

This does not replace Claude, GPT, Gemini, or other frontier models. It limits their use to mission architecture, eval design, exception review, and high-risk ambiguity.

## Design Principle

```text
Frontier models design the rails.
Local agents run on the rails.
CI proves whether the train stayed on track.
```

## Proposed Architecture

```text
PDR / Strategy
  -> Mission Packet
  -> Governance Gates
  -> Router Selection
  -> Worker Agent Execution
  -> Eval + CI
  -> GitHub Review
  -> Escalation if needed
```

## Model Roles

| Tier | Model Class | Authority | Default Work |
|---|---|---|---|
| Frontier | Claude, GPT, Gemini Pro | Architecture and exception review | PDR, mission packets, eval design, ambiguous failures |
| Local Agentic | Hermes | Structured execution | queue triage, handoffs, mission packet reading, C1/C2 tasks |
| Local Coding | Qwen Coder | Code implementation | bounded code edits, tests, refactors |
| Local General | Llama/Gemma | support work | summaries, docs, low-risk reasoning |
| Control | tests, CI, schemas | pass/fail authority | objective validation |
| Review | GitHub bots/humans | merge confidence | code review and PR checks |

## Complexity Routing

| Complexity | Description | Default Route |
|---|---|---|
| C1 | mechanical | Hermes or small local model |
| C2 | structured bounded task | Hermes for ops/docs, Qwen for code |
| C3 | reasoning/integration | Gemini/Claude/GPT or strong local only after eval |
| C4 | novel architecture/design | frontier model |

## Governance Requirements

Every mission packet must include:

- objective
- allowed files
- forbidden files
- acceptance criteria
- validation commands
- stop conditions
- risk class
- privacy class
- expected output format
- escalation rules

## Implementation Phases

### Phase 1: Static Scaffold

Create schemas, routing proposals, governance docs, and seed mission packets.

### Phase 2: Capability Registry Patch

Add Hermes to the model capability registry and route it only for low-risk C1/C2 workloads.

### Phase 3: Routing Patch

Add Hermes to desktop and remote Ollama routes, behind availability checks and privacy gates.

### Phase 4: Eval Harness

Run repeatable evals for:

- mission packet comprehension
- bead triage
- handoff summarization
- CI failure explanation
- simple docs patch execution

### Phase 5: CI/GitHub Integration

Require all local-agent PRs to include test results, eval receipts, and mission packet references.

## Success Criteria

Hermes is promoted only if it:

- passes mission packet comprehension evals
- produces valid structured outputs
- does not exceed allowed scope
- respects stop conditions
- reduces frontier model usage for C1/C2 tasks
- maintains or improves CI pass rate

## Rollback Criteria

Disable Hermes routing if:

- it repeatedly ignores scope
- it produces invalid schema outputs
- it fails safety/stop-condition tests
- it increases CI failures without clear benefit
- it causes duplicated or scattered work

## Open Questions

1. Which exact Hermes build/tag should be standard in Ollama?
2. Should Hermes be first-choice for C2 docs/ops, or second behind Qwen?
3. Should local-agent execution require branch-per-mission?
4. Should every local-agent PR require an eval receipt artifact?
