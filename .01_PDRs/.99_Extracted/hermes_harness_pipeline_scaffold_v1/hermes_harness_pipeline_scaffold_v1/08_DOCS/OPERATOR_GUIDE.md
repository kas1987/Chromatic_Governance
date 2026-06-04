# Operator Guide: Using Frontier and Local Models Together

## Simple Rule

Use expensive models to define the work. Use local models to execute the work. Use CI to decide whether execution succeeded.

## Workflow

1. Frontier model creates PDR and mission packet.
2. Mission packet goes into queue/beads.
3. Router selects model based on complexity, risk, privacy, and capability.
4. Local model executes bounded task.
5. Local model produces eval receipt.
6. CI validates.
7. GitHub review handles PR.
8. Frontier model is called only for ambiguity, failure, or high-risk changes.

## Hermes Best Uses

- Read mission packet.
- Summarize task.
- Triage queue.
- Draft handoff.
- Generate eval receipt.
- Explain CI failure.
- Make simple docs/config changes.

## Qwen Best Uses

- Code edits.
- Tests.
- Refactors.
- Debugging.

## Frontier Best Uses

- PDR.
- Strategy.
- Architecture.
- Policy.
- Eval design.
- Exception review.

## Bad Pattern

```text
Ask Claude to implement everything.
```

## Good Pattern

```text
Ask Claude to create mission packet and eval.
Let local agents execute.
Let CI decide pass/fail.
Escalate only exceptions.
```
