---
name: llm-ide-handoff-packager
description: Convert PDRs, repo-router dispatch boards, project queues, audit findings, and agent tasks into execution-ready handoff packages for Cursor, Codex, Claude, Gemini, GitHub Issues, and local LLM/IDE agents. Use when operationalizing plans across other LLMs or IDEs, creating implementation briefs, generating target-specific task files, or packaging repo work into portable handoffs with allowed actions, blocked actions, acceptance criteria, and stop conditions.
---

# LLM / IDE Handoff Packager

Bridge planning and execution by turning governed work packets into target-specific, self-contained handoffs that can be executed without relying on hidden chat context.

## Operating rule

Every handoff must be independently executable. Include enough context, constraints, and evidence that the target agent can begin and stop safely without needing the originating conversation.

## Core procedure

1. **Identify the source material.** Confirm the input: PDR summary, dispatch board, queue item, or audit finding. Note any missing fields that would block execution.
2. **Identify the target environment.** Ask or infer: Cursor, Codex, Claude, Gemini, GitHub Issue, local LLM, or generic agent.
3. **Apply the universal handoff contract** (see below) to every task regardless of target.
4. **Adapt for the target environment:**
   - **Cursor** — include repo path assumptions, exact files to inspect, edit scope, test/validation commands, stop conditions when files are missing or architecture conflicts appear
   - **Codex** — include implementation goal, explicit diff boundaries, test command, PR summary draft, failure handling
   - **Claude** — include longer project background, decision history, review questions, critique and alternatives request
   - **Gemini** — include broad review target, comparison dimensions, visual/multimodal references
   - **GitHub Issue** — include concise title, labels, linked source docs, acceptance checklist, owner/agent role
   - **Local LLM** — keep compact; use classification/routing tasks; prefer JSONL-friendly outputs
5. **Validate before output.** Confirm each handoff has: a stop condition, named allowed and blocked actions, output expectations, and enough source references for the target to begin.
6. **Bundle batch handoffs** when multiple tasks share a common source; produce one package index plus individual task files.

## Universal handoff contract

Every handoff must include:

```yaml
task_id: string
title: string
source_project: string
source_files: list
objective: string
context: string
allowed_actions: list
blocked_actions: list
inputs_required: list
outputs_required: list
acceptance_criteria: list
stop_conditions: list
review_gate: string
handoff_target: cursor|codex|claude|gemini|github-issue|local-llm|generic
priority: p0|p1|p2|p3
status: ready|blocked|needs-human-decision
```

## Output format

```markdown
## Handoff Package — [Task ID]

**Target:** [Cursor / Codex / Claude / Gemini / GitHub Issue / Local LLM]
**Priority:** [P0–P3]
**Status:** [ready / blocked / needs-human-decision]

### Objective
...

### Context
...

### Source files
- ...

### Allowed actions
- ...

### Blocked actions
- ...

### Acceptance criteria
- [ ] ...

### Stop conditions
- Stop if: ...

### Review gate
...
```

## Guardrails

- Do not authorize destructive file or repo operations unless explicitly approved in the source task.
- Do not assume hidden context will be available to the target agent; include all needed references inline.
- Insert a `blocked` status with a missing-input note instead of guessing at incomplete inputs.
- Keep each handoff bounded and independently executable.

## Related references

- `references/ide-handoff-modes.md`
- `references/output-contracts.md`
