# Source-of-Truth Rules

Use these rules when ranking files, resolving conflicts, or deciding what context to preserve.

## Authority ranking

1. Explicit current user instruction.
2. Current repository files inspected during this session.
3. Project-level steering docs such as `CLAUDE.md`, `AGENTS.md`, `README.md`, `docs/architecture/*`, `docs/decisions/*`.
4. Test results and command outputs from the current working tree.
5. Issue tracker or task board entries.
6. Older conversation notes, generated summaries, or stale docs.

## Conflict handling

When sources disagree:

1. State the conflict plainly.
2. Identify the highest-authority source.
3. Preserve the lower-authority source as stale/suspect unless the user says otherwise.
4. Do not silently merge contradictory instructions.
5. Ask for confirmation only when the conflict blocks the task or creates material risk.

## Context pruning rules

Keep:

- User goals and constraints.
- Current state and next actions.
- Accepted decisions and rationale.
- File paths and commands needed to resume.
- Risks, blockers, and unresolved questions.

Remove or compress:

- Repeated explanations.
- Outdated plans replaced by newer decisions.
- Routine command output after the result is captured.
- Speculative ideas not selected for action.

## Durable memory update rule

Only write durable memory/context updates when they are useful beyond the current task. Avoid storing transient observations, temporary guesses, or low-value chatter.
