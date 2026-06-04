# PDR-004: Chromatic Review Intake System

## Status
Implemented v1.1 — Phase 1 (passive intake) + Phase 2 (queue dispatch) live

## Date
2026-06-04

## Owner
Kris Sayresmith / Poly-Chromatic

## Reference
`chromatic_review_intake_pdr_extracted/chromatic_review_intake_pdr/05_DOCS/REVIEW_INTAKE_PDR.md`

---

## Executive Summary

GitHub review feedback — PR comments, inline annotations, CI failures, approval/rejection reviews — exists only as scattered GitHub events. Without a normalization layer, agents duplicate work, miss feedback, and collide on the same PR branch. This PDR integrates the Chromatic Review Intake bundle into the harness, converting raw GitHub events into a governed, deduplicated, confidence-gated Next Work Queue.

---

## Problem Statement

- Review comments are ephemeral — no structured record exists outside GitHub
- Multiple agents can pick up the same finding independently, causing redundant or conflicting patches
- CI failures have no standardized path to the work queue
- High-risk findings (security, architecture) receive no automatic escalation

---

## What was integrated

### Scripts (`.03_Harness Governance/scripts/`)
| File | Purpose |
|---|---|
| `review_intake.py` | Main ingest engine — normalizes 5 GitHub event types into findings + queue items |
| `classify_review_finding.py` | Classifies findings into 8 types; scores confidence 0–100; maps to agents |
| `lock_pr_branch.py` | File-based PR branch mutation lock with 30-min TTL; prevents agent collisions |
| `post_review_resolution.py` | Generates standardized Chromatic resolution comment for gh CLI piping |
| `update_next_work_queue.py` | Deterministic helper for upsert to `next-work.queue.json` |

### Schemas (`.03_Harness Governance/schemas/`)
- `review_finding.schema.json` — finding contract (finding_id, source, confidence_score, risk_level…)
- `next_work_item.schema.json` — queue item contract (id, status enum, specialties, acceptance_checks…)
- `agent_dispatch.schema.json` — dispatch record contract
- `pr_branch_lock.schema.json` — lock file contract

### Workflow (`.github/workflows/review-intake.yml`)
Triggers on: `pull_request_review`, `pull_request_review_comment`, `issue_comment`, `check_run`, `workflow_run`. Normalizes the event, enriches with classifier, writes deduplicated JSONL and updates queue. Commits results back to the branch.

### State and queue (`.agents/review-intake/`)
- `review-findings.jsonl` — append-only log of all normalized findings
- `next-work.queue.json` — governed work queue (seeded with NW-REVIEW-INTAKE-001, NW-REVIEW-INTAKE-002)
- `review-intake.state.json` — tracks last processed event and mode
- `locks/` — file-based PR branch mutation locks

---

## Architecture

```
GitHub Event
  → review_intake.py (normalize)
  → classify_review_finding.py (classify + score)
  → Confidence Gate
      ≥75 → ready
      40-74 → review-required
      <40 → blocked
      security/architecture <90 → needs-human-decision
  → .agents/review-intake/review-findings.jsonl (deduplicated)
  → .agents/review-intake/next-work.queue.json (upserted)
  → lock_pr_branch.py (acquire before mutation)
  → Agent Mission Packet
  → Scoped Patch + Validation
  → post_review_resolution.py (resolution comment)
  → .agents/review-intake/logs/review-resolution-log.jsonl
```

---

## Finding types and agent routing

| Type | Agent | Auto-fix default |
|---|---|---|
| `security` | Sentinel | needs-human-decision (<90) |
| `test_failure` | Auditor | ready (≥75) |
| `lint_style` | Janitor | ready (≥75) |
| `docs` | Archivist | ready (≥75) |
| `architecture` | Archivist | needs-human-decision (<90) |
| `bug_fix` | Sentinel | ready (≥75) |
| `repo_hygiene` | Janitor | ready (≥75) |
| `unclear` | Auditor | blocked (<75) |

---

## Confidence scoring formula

`score = actionability(0.25) + file_scope(0.20) + testability(0.20) + risk_safety(0.15) + dedupe_certainty(0.10) + agent_fit(0.10)`

Penalty modifiers:
- Vague body (`maybe`, `consider`, `unclear`) → −15 actionability, −10 testability
- Body < 20 chars → −20 actionability

---

## Collision control

One active mutating agent per PR branch at any time. `lock_pr_branch.py acquire` fails with exit code 2 if an active (non-expired) lock exists. Multiple inspection-only agents can read freely. Locks expire in 30 minutes by default.

---

## Implementation phases

| Phase | Status | Description |
|---|---|---|
| 1 — Passive Intake | **Live** | Normalize events → findings.jsonl + queue |
| 2 — Queue Dispatch | **Live** | Dispatcher picks up `ready` items and creates mission packets |
| 3 — Agent Patching | Backlog | Scoped patch + lock + validation + resolution comment |
| 4 — Learning Loop | Backlog | Weekly pattern analysis → tool/template improvements |
| 5 — Central Collector | Future | GitHub App + SQLite across multiple repos |

---

## Acceptance criteria (Phase 1)

- [x] `pull_request_review_comment` event → normalized finding in `review-findings.jsonl`
- [x] Same event does not create a duplicate finding (dedupe_key check)
- [x] Low-confidence or vague findings not marked `ready`
- [x] Security and architecture findings require human decision at <90 confidence
- [x] `lock_pr_branch.py` blocks a second active mutator on the same PR
- [x] Expired locks are replaceable
- [x] 53 tests covering normalizers, classifier, scorer, queue upsert, and lock lifecycle

---

## Tests

53 tests in `.03_Harness Governance/scripts/tests/test_review_intake.py` covering:
- `classify_review_finding`: 11 body classification, 4 scoring, 3 enrich, 6 queue status tests
- `review_intake`: 3 stable_id, 3 append_jsonl_once, 5 normalizer, 4 normalize_event dispatch, 3 queue upsert tests
- `lock_pr_branch`: 5 lock lifecycle tests
- `update_next_work_queue`: 4 queue management tests
- `post_review_resolution`: 2 rendering tests

---

## Acceptance criteria (Phase 2 — Queue Dispatch)

- [x] Dispatcher polls `next-work.queue.json` and picks up `ready` items
- [x] Mission packet is generated per finding with agent routing, scope, and acceptance checks populated
- [x] `review-required` and `blocked` items are not dispatched without explicit human approval
- [x] Dispatcher acquires PR branch lock before handing off to a mutating agent
- [x] Dispatch event is appended to `agent-dispatch-log.jsonl`

## Acceptance criteria (Phase 3 — Agent Patching)

- [ ] Dispatched agent applies a scoped patch within the lock window
- [ ] Patch passes tests and lint before resolution comment is posted
- [ ] `post_review_resolution.py` generates a well-formed Chromatic resolution comment
- [ ] Resolution event is appended to `review-resolution-log.jsonl`
- [ ] Lock is released on both success and failure paths

## Acceptance criteria (Phase 4 — Learning Loop)

- [ ] Weekly analysis job runs against `reviewer-patterns.jsonl`
- [ ] Patterns with ≥3 occurrences generate a staged improvement proposal
- [ ] Proposals are written to a staging location; nothing is auto-implemented
- [ ] Analysis output is human-reviewable before any change is applied

## Acceptance criteria (Phase 5 — Central Collector)

- [ ] GitHub App installed and receiving webhook events from at least one repo
- [ ] Findings persisted in SQLite with schema conforming to `review_finding.schema.json`
- [ ] Multi-repo deduplication handles the same finding across branches/forks
- [ ] Migration path from JSONL to SQLite is documented and tested

---

## Open questions

1. Should queue changes be committed directly to the PR branch or via a separate housekeeping branch?
2. Which finding types should trigger immediate Slack/notification on creation?
3. When Phase 3 lands, should resolution comments be posted as draft until the agent requests review?
