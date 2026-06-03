# Subagent Governance Contract

> **Mandatory for all orchestrators.** Every subagent spawned by /swarm, /crank, /codex-team, or /council MUST comply with this contract. Orchestrators are responsible for injecting it — workers must not be trusted to self-regulate.

---

## Role Registry

Assign every subagent one of these roles before spawning. The role determines the `subagent_type`, permitted tools, and sandbox level.

| Role | subagent_type | Writes? | External Calls? | Bash? | Spawn Sub-Agents? |
|------|--------------|---------|-----------------|-------|-------------------|
| `EXPLORER` | `Explore` | No | WebFetch (read-only) | No | No |
| `JUDGE` | `Explore` | No | No | No | No |
| `EVIDENCE_JUDGE` | `Explore` | No | WebFetch + WebSearch | No | No |
| `HISTORIAN` | `Explore` | No | No | `git log/blame/show` only | No |
| `SPEC_WRITER` | `general-purpose` | Yes — spec files only | No | No | No |
| `IMPL_WORKER` | `general-purpose` | Yes — manifest only | build/test/lint only | Yes | No |
| `TEST_WORKER` | `general-purpose` | Yes — test files only | test runner only | Yes | No |
| `PLANNER` | `Plan` | No (reads only) | No | No | No |

**Key rule:** Never assign `general-purpose` to a role that only needs reads. `Explore` is runtime-enforced read-only; `general-purpose` is unrestricted by default and must be governed by prompt constraints.

### When to use EVIDENCE_JUDGE vs HISTORIAN vs JUDGE

| Need | Role |
|------|------|
| Review a plan, spec, or code — no external data needed | `JUDGE` |
| Review requires CVE lookups, changelog reads, or external benchmarks | `EVIDENCE_JUDGE` |
| Review requires reading git commit history, blame, or prior reverts | `HISTORIAN` |
| Broad codebase exploration before a review | `EXPLORER` |

`EVIDENCE_JUDGE` and `HISTORIAN` are still `subagent_type="Explore"` — they cannot write files. The distinction is governance-header-declared to inform the judge's prompt about what external lookups are permitted.

---

## Tool Restriction by Role

Claude Code does not expose a per-call `allowed_tools` parameter on the `Agent` tool. Restriction is enforced via:

1. **subagent_type selection** — `Explore` agents cannot write files (runtime-enforced)
2. **Mandatory governance header** injected into every prompt (see below)
3. **Codex sandbox level** for Codex CLI workers

### Permitted Tool Matrix

| Tool | EXPLORER | JUDGE | EVIDENCE_JUDGE | HISTORIAN | SPEC_WRITER | IMPL_WORKER | TEST_WORKER |
|------|----------|-------|----------------|-----------|-------------|-------------|-------------|
| Read | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Glob | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Grep | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Write | — | — | — | — | spec paths only | manifest only | test paths only |
| Edit | — | — | — | — | — | manifest only | test paths only |
| Bash | — | — | — | git log/blame/show | — | build/test/lint only | test runner only |
| Agent | — | — | — | — | — | — | — |
| WebFetch | ✓ | — | ✓ | — | — | — | — |
| WebSearch | ✓ | — | ✓ | — | — | — | — |

**Bash restrictions for IMPL_WORKER / TEST_WORKER:**
- Allowed: `go build`, `pytest`, `npm test`, `bash -n`, `jq`, `grep`, `ls`, `git diff`, `git status`
- Forbidden: `curl`, `wget`, `ssh`, `nc`, `python3 -c "import requests..."`, any external network call

---

## Codex Sandbox Requirements

When spawning Codex CLI workers, the `-s` flag is **mandatory** and must match the role:

| Role | Sandbox Flag | Rationale |
|------|-------------|-----------|
| `JUDGE` / `EXPLORER` | `-s read-only` | No writes needed; prevents accidents |
| `IMPL_WORKER` / `TEST_WORKER` / `SPEC_WRITER` | `-s workspace-write` | Default with `--full-auto` |
| Any role | `-s danger-full-access` | **Requires explicit user authorization.** Never use without documented justification. |

```bash
# Correct: judge/reviewer
codex exec -s read-only --full-auto -C "$(pwd)" -o output.md "Review the plan..."

# Correct: implementation worker
codex exec --full-auto -s workspace-write -C "$(pwd)" -o output.md "Implement the feature..."

# Wrong: never omit -s for judge roles
codex exec --full-auto -C "$(pwd)" -o output.md "Review..."   # BAD: defaults to workspace-write
```

---

## Mandatory Governance Header

Every worker prompt — regardless of backend (Task tool, Codex CLI, background agent) — MUST begin with this header, populated for the specific worker:

```
## GOVERNANCE CONSTRAINTS
Role: <EXPLORER | JUDGE | EVIDENCE_JUDGE | HISTORIAN | SPEC_WRITER | IMPL_WORKER | TEST_WORKER>
Worker ID: <worker-N | judge-N | explorer-N>
Wave: <wave number or "1">

FILE SCOPE (the ONLY files you may create or modify):
<file1>
<file2>
... (list every file from metadata.files, one per line)
If no files listed above: you have READ-ONLY access.

PERMITTED ACTIONS:
- Read, Glob, Grep any file in the repo for context
- Bash for: build/test/lint commands ONLY (see below)
- Write/Edit ONLY the files listed in FILE SCOPE above

FORBIDDEN — DO NOT DO THESE:
- Spawn subagents (Agent tool) — blocked, escalate to lead instead
- Read credential/secret files: settings.json, .env, *.pem, *.key, *.token
- Run git add, git commit, git push — the lead commits
- Make external network calls (curl, wget, requests.get, fetch) without explicit permission
- Create, write, or modify ANY file outside your FILE SCOPE — no exceptions, no judgment calls
- Claim or modify tasks not pre-assigned to you

⚠️  SCOPE ENFORCEMENT: After this wave completes, the lead runs `git diff --name-only` and
compares against declared FILE SCOPE. ANY file you wrote outside your scope will be automatically
reverted and the wave will be re-run. Do not invent new subsystems, modules, or infrastructure
not listed in your FILE SCOPE — write your result and stop.

SCOPE VIOLATION PROTOCOL:
If you need to modify a file NOT in your FILE SCOPE:
1. STOP — do NOT touch the out-of-scope file
2. Write blocked result: {"type":"blocked","reason":"SCOPE-ESCAPE: <file> needed because <reason>"}
3. Signal the lead — they will decide

RESULT: Write your output to <result_path> before sending any signal.
```

### Role-Specific Permission Addendums

Append one of the following blocks **after** the base governance header when using specialized roles:

**For `EVIDENCE_JUDGE`** — add after PERMITTED ACTIONS:
```
EVIDENCE GATHERING (authorized for this role):
- WebFetch: allowed for CVE lookups (nvd.nist.gov, osv.dev, github.com/advisories), changelogs, published benchmarks, RFCs
- WebSearch: allowed for finding external evidence, prior art, and published research
- Every WebFetch/WebSearch result MUST be cited in your output with URL and access date
- DO NOT WebFetch internal company systems, paid research gates, or auth-required resources
```

**For `HISTORIAN`** — add after PERMITTED ACTIONS:
```
GIT HISTORY ACCESS (authorized for this role):
- Bash: restricted to git read-only commands ONLY: git log, git blame, git show, git diff (no HEAD modification), git shortlog
- DO NOT run: git add, git commit, git push, git reset, git rebase, git checkout, git switch
- Every git finding MUST be cited with commit hash and author in your output
```

### Required Variables

Before spawning, populate these for each worker:
- `<role>`: one of the 5 roles from the Role Registry
- `<worker-N>`: unique ID within the wave
- `<wave>`: current wave number
- `<file1>, <file2>...`: the task's `metadata.files` array
- `<result_path>`: `.agents/swarm/results/<task-id>.json` or the Codex `-o` output path

---

## Orchestrator Spawn Checklist

Before spawning any subagent wave, the orchestrator MUST verify:

```
[ ] Every worker has been assigned a role from the Role Registry
[ ] subagent_type matches the assigned role
[ ] Governance header is prepended to every worker prompt
[ ] FILE SCOPE is populated from metadata.files (not left blank)
[ ] Codex workers have explicit -s <sandbox-level> flag
[ ] No worker prompt includes Agent tool invocation instructions
[ ] result_path is defined and result dir exists
```

If any item is unchecked, the orchestrator MUST resolve it before spawning. An empty FILE SCOPE is a signal to pause planning, not to spawn unconstrained workers.

---

## Escalation Paths

Workers are not permitted to self-expand their scope. The lead handles all escalations:

| Worker signal | Lead action |
|--------------|-------------|
| `SCOPE-ESCAPE: <file>` | Create follow-up task, or expand manifest and retry |
| `blocked: external call needed` | Assess necessity; run the call from orchestrator context |
| `blocked: subagent needed for X` | Spawn a scoped explorer agent from orchestrator |
| Task timeout (>180s) | Classify as RETRY/DECOMPOSE/PRUNE per failure taxonomy |

---

## Anti-Patterns (Do NOT Do These)

| Anti-Pattern | Why It's Harmful | Correct Approach |
|-------------|-----------------|-----------------|
| `subagent_type="general-purpose"` for judges | Judges get write access; risk of accidental modification | Use `subagent_type="Explore"` |
| Empty FILE SCOPE | Worker operates unconstrained; scope creep, secret reads | Always populate from `metadata.files` before spawning |
| Omitting governance header | Worker self-regulates (unreliable) | Always prepend governance header |
| Codex workers without `-s` flag | Defaults to workspace-write even for read-only tasks | Match `-s` to role |
| Workers instructed to "do whatever it takes" | Overrides all governance constraints | Give specific, bounded task with acceptance criteria |
| Spawning workers before manifests are populated | Conflict detection skipped; workers collide | Use Step 1.5 (auto-manifest) before spawning |

---

## References

- [backend-claude-teams.md](backend-claude-teams.md) — concrete TaskCreate/Task spawn examples
- [backend-codex-subagents.md](backend-codex-subagents.md) — Codex CLI spawn patterns with sandbox flags
- [ralph-loop-contract.md](ralph-loop-contract.md) — fresh context isolation per wave
- [orchestration-as-prompt.md](orchestration-as-prompt.md) — how to structure worker prompts effectively
- [validation-contract.md](../validation-contract.md) — post-execution validation the lead runs
