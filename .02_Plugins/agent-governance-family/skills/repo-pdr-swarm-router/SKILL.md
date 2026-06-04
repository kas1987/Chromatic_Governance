---
name: repo-pdr-swarm-router
description: Ingest, decompose, govern, and route large repository PDR packages into agent-routable work queues with manifests, decision registers, risk registers, governance gates, and swarm-ready handoff packets. Use when the user provides repo PDR packages, audit bundles, project design records, implementation plans, backlog packs, or governance artifacts and wants them parsed, scored, split into agent assignments, and dispatched through the Chromatic router.
skill_api_version: 1
---

# Repo PDR Swarm Router

Turn large Repo PDR packages into governed, agent-routable work. Preserve the user's router as the authority, enforce Chromatic AI Harness practices, and produce audit-ready queue items rather than loose summaries.

## Operating rule

Never treat a Repo PDR as a normal document summary. Always convert it into a controlled execution system with ownership, evidence, stop conditions, and governance gates.

## Core procedure

1. **Intake the package.** Inspect the supplied PDR using available file, connector, repo, or archive tools. Build an artifact inventory: all files, paths, inferred purpose, artifact class, and evidence status. For large packages with many files, optionally run the intake script:

```bash
python agent-governance-family/scripts/parse_repo_pdr.py --input <path> --output <output-dir>
```

The script produces a manifest, queue seed, risk register, evidence map, and dispatch board.
2. **Classify every artifact** by role: requirements, decisions, constraints, risks, tasks, governance, or reference material.
3. **Extract and register** decisions already made, unresolved decisions, contradictions, non-negotiables, router rules, and runtime limits into a `decision_register` and `constraint_register`.
4. **Build the work queue.** Convert actionable tasks into queue items with `task_id`, dependencies, owner, priority, and stop conditions.
5. **Route through the Chromatic router.** Respect the user's router before inventing roles. Default routing if none is present:
   - `sentinel` — code quality, tests, CI, security, failure modes
   - `auditor` — governance, evidence, contradictions, acceptance gates
   - `chainbreaker` — blockers, cyclic dependencies, brittle workflows
   - `quartermaster` — assets, manifests, package readiness
   - `cartographer` — repo tree, folder standards, architecture maps
   - `archivist` — memory, decisions, logs, changelogs
   - `janitor` — cleanup, duplicates, stale files
6. **Apply governance gates** before any dispatch: source-of-truth gate, evidence gate, dependency gate, safety gate, acceptance-criteria gate, stop-condition gate. Mark items `blocked` or `needs-human-decision` if any gate fails.
7. **Produce swarm-ready outputs** (see Output format below).

## Output format

```markdown
## PDR Swarm Router — [Package Name]

### Executive intake summary
...

### PDR manifest
| File | Path | Role | Evidence status |
|---|---|---|---|

### Agent dispatch board
| Task ID | Agent | Mission | Priority | Status | Stop condition |
|---|---|---|---|---|---|

### Dependency list
...

### Risk register
| Risk | Severity | Mitigation |
|---|---|---|

### Priority queue (next 3–10 actions)
1. ...
```

Every dispatch packet must include: `task_id`, `agent_role`, `mission`, `source_files`, `evidence_required`, `allowed_actions`, `blocked_actions`, `acceptance_criteria`, `stop_condition`, `handoff_target`, `priority`, `status`.

Priority: P0 blocks governance/security; P1 blocks downstream tasks; P2 improves correctness; P3 polish/docs.

Status values: `ready` · `blocked` · `needs-human-decision` · `in-progress` · `review-required` · `done`

## Guardrails

- Do not dispatch work that lacks evidence, owner, acceptance criteria, and stop condition.
- If two files conflict, record the contradiction and route a decision task to `auditor` or the user — do not merge silently.
- If package contents are too large to inspect fully, produce a partial manifest, identify missing inputs, and create a `blocked` queue item.
- Treat `CHROMATIC_TREES.md` as source of truth for repo tree rules when present.

## Related references

- `references/pdr-intake.md` — artifact classification and extraction rules
- `references/router-map.md` — agent roles, routing rules, conflict resolution
- `references/governance-gates.md` — quality gates and blocked-work rules
- `references/output-contracts.md` — exact output schemas and handoff templates
