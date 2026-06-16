# Session Retrospective — Hermes harness execution (`/loop` run)

**Date:** 2026-06-16
**PRs merged:** #28, #29, #30, #31, #32 (Chromatic_Governance / `Main`)
**Initiative:** PDR-008 "Hermes Local-Agent Harness" — work queue HERMES-005..008 + the HERMES-006 Phase-3 follow-up
**Mode:** `/loop "10 times on all Next Steps"` (dynamic, self-paced), human-in-loop

## What shipped

| # | PR | Squash | Deliverable |
|---|----|--------|-------------|
| HERMES-005 | #28 | `6577bc8` | `eval_receipt.schema.json` (7 required fields) + `validate_packet.py` + contract tests |
| HERMES-006 | #29 | `950b3a5` | Single Hermes CI gate (`hermes-gate.yml`) — 3 jobs, keyed on the eval-receipt contract, scoped to `.03_Harness Governance/**` |
| HERMES-007 | #30 | `f818465` | Sentinel + Auditor Hermes mission-packet handoffs, adapted to repo layout |
| HERMES-008 | #31 | `9641c7a` | Cartographer/Archivist/Quartermaster handoffs + runtime registration in `config/agents.yaml` (`status: inactive`) |
| HERMES-006 Phase-3 | #32 | `c114d14` | `receipt-required` gate job — fails a mission PR under `.03_Harness Governance/` that ships no eval receipt; `no-receipt` label escape hatch |

Each item landed as its own session branch → PR → squash-merge → local `Main` sync, with a dogfood eval receipt under `operations/receipts/`. PDR-008 HERMES-001..008 plus Phase-3 are now all landed.

## Learnings

### 1. A `no-receipt` escape hatch belongs *in-step*, not as a job-level `if:` skip
The Phase-3 gate needed a human override for genuine non-mission infra PRs. A job-level `if:` that skips the job leaves the check stranded as "pending" — which can block a merge under some branch-protection configs and reads as "never ran" rather than "waived."
**Action:** Implement label overrides as an in-step short-circuit (`grep` the labels → `echo ::notice` → `exit 0`) so a waived requirement reports **success**, not a skip. Keep the job's `if:` for the structural condition only (here: `github.event_name == 'pull_request'`).

### 2. `git diff --name-only` paths are repo-root-relative even under `defaults.run.working-directory`
`hermes-gate.yml` sets `working-directory: '.03_Harness Governance'`, which tempts you to write scope regexes relative to that dir. But `--name-only` always emits repo-root-relative paths, so the regex must include the `.03_Harness Governance/` prefix.
**Action:** Anchor scope/receipt regexes at the repo root (`^\.03_Harness Governance/...`) regardless of the job's cwd. Verified by simulating the exact gate loop locally against the committed diff before pushing.

### 3. Make a new gate self-consistent — it must pass its own introducing PR
The PR that *adds* the `receipt-required` job changes a mission file (`operations/eval-receipts.md`), so under its own new rule it needs a receipt. It shipped one (`hermes-006-phase3-receipt-required.eval_receipt.json`), giving `substantive=1 receipt=1 → PASS`.
**Action:** When introducing an enforcement gate, check that the introducing change satisfies the rule it adds (or carries the documented override). A gate that would reject its own PR is a design smell.

### 4. Additive-not-required keeps branch protection untouched
The four hermes-gate jobs run on PRs but are **not** in the repo's required-checks list (`Analyze (python)`, `CodeQL`, `dependency-review`, `lint`). Adding a fifth job therefore needed no admin/branch-protection change.
**Action:** Prefer additive gate jobs over editing required-checks when you don't have (or don't want to spend) admin authority — the job still surfaces red on the PR and can be promoted to required later.

### 5. Pre-merge, simulate the gate's own shell logic locally
The first local simulation returned empty (`substantive=0 receipt=0 → WOULD PASS`) because changes weren't committed yet (`HEAD == Main`, empty diff). Committing first, then re-running the exact bash loop, surfaced the real `substantive=1 receipt=1` result.
**Action:** Simulate CI diff logic against a **committed** branch tip, not the working tree — an uncommitted tree gives an empty `origin/base...HEAD` diff and a false pass.

## KPI snapshot

| KPI | Value |
|-----|-------|
| PRs landed this run | 5 (#28–#32) |
| CI green first try | 5/5 |
| Eval receipts in `operations/receipts/` | 4 |
| PDR-008 work queue | HERMES-001..008 + Phase-3 — all landed |
| Branch-protection changes required | 0 |

## Follow-up

- **HERMES-004 live write (human gate, NOT done):** apply the additive Hermes routing patch to `C:\.04_Prism\gen\src\routes\routing-matrix.json` (separate **Prism** production repo). Dry-run proof shows 10/10 existing intents byte-identical; `apply_status: pending_human_gate`. Needs explicit confirmation before the live cross-repo mutation.
- **End-to-end worker runs (operational):** dispatch Sentinel/Auditor/Cartographer/Archivist/Quartermaster missions against the live `hermes3:8b` Ollama worker and emit real receipts — needs the worker running + live agent execution, not a docs PR.
- **Runtime activation:** flip cartographer/archivist/quartermaster `status: inactive → active` in `config/agents.yaml` on first use.
- **Stale `bd in_progress` triage:** ~25 noise beads (next-step text captured as beads) still pollute the queue — same housekeeping sweep noted in the prior retro; out of scope here.
