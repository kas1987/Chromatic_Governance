---
name: handoff-ready
description: Placeholder for the Handoff Ready workflow in the RPI Lifecycle plugin. Invoke when the user asks for handoff ready within this plugin family scope.
---

# Handoff Ready

## Status

Placeholder scaffold. Build the detailed skill procedure in the next phase.

## Intended purpose

Full research, planning, implementation, review, and iteration lifecycle for scoped delivery work.

## Required future sections

1. Trigger conditions
2. Inputs and assumptions
3. Step-by-step procedure
4. Guardrails and escalation conditions
5. Expected outputs
6. Handoff format
7. Examples

## Current behavior guidance

Until this skill is implemented, treat it as an intent marker only. Do not perform destructive actions or external-system operations solely because this placeholder exists.

## Core procedure

This skill is a placeholder for a future implementation. Until implemented, document
intent in `.agents/handoff/` and use the `/handoff` skill for session continuity.

## Output format

A structured handoff document placed at `.agents/handoff/YYYY-MM-DD-<topic>.md`
containing session context, pause point, key files, and a continuation prompt.

## Guardrails

- This skill must not be invoked for destructive or irreversible operations
- Until fully implemented, delegate to `/handoff` for session continuity needs
- Do not invent behavior not described in the required-future-sections list
