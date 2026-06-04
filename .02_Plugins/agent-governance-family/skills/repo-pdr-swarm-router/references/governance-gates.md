# Governance Gates

## Gate 1: Source of Truth
Every dispatch item must identify its controlling source. If two sources conflict, prefer this hierarchy:
1. explicit current user instruction
2. current project router/governance document
3. CHROMATIC_TREES.md for tree rules
4. machine-readable worktree/manifest files
5. memory/learnings logs
6. bridge files such as Claude, Cursor, Codex, Agents
7. assistant inference

## Gate 2: Router Alignment
Every task needs one accountable agent role. Multi-agent work must name a primary owner and support agents.

## Gate 3: Evidence
Every claim needs file/path evidence, line citation, or an explicit `inferred` label.

## Gate 4: Dependency
Do not mark a task ready if its inputs, decisions, credentials, repo path, or acceptance tests are missing.

## Gate 5: Safety and Security
Never route secrets, credentials, private keys, tokens, or unsafe commands into a handoff. Replace with secret references and route to human decision if needed.

## Gate 6: Acceptance Criteria
Every task must state what done means. If done cannot be verified, status is `blocked` or `needs-human-decision`.

## Gate 7: Stop Condition
Every task must tell the agent when to stop and hand back control. This prevents autonomous drift.

## Gate 8: Repo Tree
If repo structure is involved, validate against ChromaticTrees or create a cartographer task to establish it.
