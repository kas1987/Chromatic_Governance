# Automation Wiring Log

Last updated: 2026-06-04

## Purpose

This log is the return list for wiring the current PDR pipeline and review-intake system into orchestration tooling for multi-agent workflows.

Guiding rule:
- Keep deterministic policy and state decisions in the existing Python scripts and registry.
- Use orchestration tools to route events, manage agent state, schedule retries, send notifications, and capture traces.

## Tool Tags

| Tag | Meaning |
|---|---|
| `n8n` | Event routing, triggers, schedules, webhooks, notifications, external system glue |
| `langgraph` | Stateful multi-agent orchestration, branching control flow, resumable task graphs |
| `langsmith` | Tracing, evaluation, prompt/agent observability, run analytics |
| `github-app` | Centralized repo event collector beyond repo-local GitHub Actions |
| `scheduler` | Cron or recurring health/summary jobs |
| `dashboard` | Human-facing status board or analytics surface |

## Current ZIP Inventory Snapshot

| ZIP | Current path | Intake status | Notes |
|---|---|---|---|
| `chromatic-skill-utilization-roadmap-pdr.zip` | `.01_PDRs/.01_Backlog/` | `unique`, `not_implemented` | Still active backlog candidate |
| `repo-pdr-swarm-router.zip` | `.01_PDRs/.01_Backlog/` | `unique`, `not_implemented` | Still active backlog candidate |
| `claude_plugin_families_scaffold_v14_gold.zip` | `.01_PDRs/.01_Backlog/.99_Dups/` | `redundant`, confidence `0.97` | Auto-routed to duplicate shelf |
| `claude_plugin_families_scaffold.zip` | historical DB record | not re-scanned | No physical file currently present |
| `claude_plugin_families_scaffold_v13_frontend_core.zip` | historical DB record | not re-scanned | No physical file currently present |

## Process Register

| ID | Process | Current implementation | Source of truth | Return tags | Recommended next wiring |
|---|---|---|---|---|---|
| `PDR-AUTO-001` | Local ZIP drop detection | `pdr_zip_ingest.py watch` polls `.01_Backlog` | watcher state JSON + backlog folder | `n8n`, `scheduler` | Replace polling-first flow with folder/webhook trigger into `pdr_zip_intake.py` and alert on failure |
| `PDR-AUTO-002` | ZIP import from Downloads | `pdr_zip_ingest.py import` copies/moves ZIPs into backlog | backlog folder | `n8n` | Add manual or scheduled import workflow with duplicate-aware intake call and summary notification |
| `PDR-AUTO-003` | ZIP intake scan | `pdr_zip_intake.py` reviews integrity, hash, file count, PDR ID, implementation state | SQLite + JSONL in `.01_PDRs/.intake/` | `n8n`, `langsmith`, `dashboard` | Keep scanner deterministic; wrap with orchestration that records run traces and publishes scan summaries |
| `PDR-AUTO-004` | Duplicate/redundancy gate | `pdr_zip_intake.py` compares ZIP contents against `.02_Plugins` and routes high-confidence duplicates to `.99_Dups` | SQLite duplicate fields + `.99_Dups` shelf | `n8n`, `langsmith`, `dashboard` | Emit duplicate decision events, confidence thresholds, and reviewer override path |
| `PDR-AUTO-005` | Artifact backlog registration | `pdr_sync.py` auto-registers backlog ZIPs into `artifact_backlog` | `PDR_REGISTRY.json` | `n8n` | Trigger sync after intake/import events so registry state stays fresh without manual runs |
| `PDR-AUTO-006` | Backlog to Pre-flight extraction | `pdr_sync.py promote` unpacks ZIP to `.99_Extracted` on `Pre-flight` | extracted folder + `PDR_REGISTRY.json` | `n8n`, `langgraph` | Model this as an orchestrated transition with explicit success/failure branch and retry-safe unpack step |
| `PDR-AUTO-007` | Pre-flight readiness gate | `pdr_sync.py` blocks `In-Process` unless extracted bundle exists and is non-empty | extracted folder + registry status | `langgraph`, `dashboard` | Add graph guard node before agent dispatch; surface blocked reasons to operator dashboard |
| `PDR-AUTO-008` | PDR stage promotion | `pdr_sync.py promote` plus `.github/workflows/pdr-promotion.yml` | `PDR_REGISTRY.json` | `n8n`, `langgraph`, `github-app` | Move toward event-driven status transitions with approval checkpoints and audit callbacks |
| `PDR-AUTO-009` | Pipeline reporting | `pdr_sync.py report` provides stage summary | `PDR_REGISTRY.json` | `n8n`, `scheduler`, `dashboard` | Schedule recurring digest to issue/comment/slack/email and expose a lightweight board |
| `PDR-AUTO-010` | Repo-side ZIP intake | `.github/workflows/pdr-zip-intake.yml` runs on pushed ZIP changes | workflow artifacts + SQLite/JSONL outputs | `github-app`, `n8n` | Preserve GitHub Actions for repo checks; add central orchestration only for aggregation and notifications |
| `PDR-AUTO-011` | Review event normalization | `review_intake.py` handles PR review, inline comment, issue comment, check, and workflow events | `.agents/review-intake/review-findings.jsonl` | `github-app`, `n8n`, `langsmith` | Promote from repo-local workflow to central event collector with traceable event processing |
| `PDR-AUTO-012` | Confidence scoring and queue upsert | `classify_review_finding.py` and queue writers score findings and update work queue | `.agents/review-intake/next-work.queue.json` | `langgraph`, `langsmith`, `dashboard` | Add stateful dispatch policy that can re-score, retry, or escalate based on agent outcomes |
| `PDR-AUTO-013` | PR branch mutation lock | `lock_pr_branch.py` enforces one active mutating agent per PR branch | lock files under `.agents/review-intake/locks/` | `langgraph`, `dashboard` | Use lock status as graph state so only one writer branch can execute at a time across agents |
| `PDR-AUTO-014` | Mission packet dispatch | playbooks/handoff docs exist, but dispatch remains mostly manual/backlog | queue items + handoff docs | `langgraph`, `n8n` | Build orchestrated dispatch from ready queue item -> agent task packet -> scoped execution record |
| `PDR-AUTO-015` | Patch, validation, and PR resolution loop | resolution tooling exists, but end-to-end agent mutation loop is still backlog | review-resolution log + PR comment body | `langgraph`, `langsmith`, `github-app` | Implement graph with scoped patch, validation fan-out, resolution comment, and failure rollback branches |
| `PDR-AUTO-016` | Learning loop and trend review | documented in PDR/playbooks; not automated yet | review findings + resolution logs + intake DB | `langsmith`, `scheduler`, `dashboard` | Schedule weekly evaluations, error clustering, and repeated-pattern reports |
| `PDR-AUTO-017` | Notification and escalation layer | partially implied in docs, not centralized | current logs and GitHub comments | `n8n`, `github-app` | Route failures, blocked states, and human-gate items to operator channels |
| `PDR-AUTO-018` | Multi-agent intake-to-execution control plane | not yet implemented | distributed local files today | `langgraph`, `langsmith`, `dashboard`, `github-app` | Build a control graph spanning intake, queueing, lock acquisition, agent execution, and telemetry |

## Recommended Sequencing

| Phase | Focus | Processes |
|---|---|---|
| `A` | Event bridge and visibility | `PDR-AUTO-001`, `002`, `003`, `009`, `017` |
| `B` | Registry-aware routing | `PDR-AUTO-005`, `006`, `007`, `008` |
| `C` | Review-intake centralization | `PDR-AUTO-010`, `011`, `012`, `013` |
| `D` | Multi-agent execution loop | `PDR-AUTO-014`, `015`, `018` |
| `E` | Measurement and continuous improvement | `PDR-AUTO-004`, `016` |

## Constraints To Preserve

- `PDR_REGISTRY.json` remains the authoritative state for PDR stage and artifact status.
- SQLite and JSONL logs remain the audit trail even if orchestration tooling is added.
- Duplicate/redundancy decisions stay evidence-backed and overrideable.
- GitHub Actions remain acceptable for repo-local governance gates; orchestration should aggregate, not silently replace, those checks.
- Any multi-agent mutation path must honor branch locks before write operations.

## Immediate Follow-Up Candidates

| Candidate | Why it should come next |
|---|---|
| `n8n` Phase 1 event bridge | Fastest way to unify local ZIP drops, imports, and notifications without rewriting policy code |
| `LangGraph` queue-to-agent dispatcher | Needed once multiple agents can consume ready queue items and must respect locks and stop conditions |
| `LangSmith` trace instrumentation around intake and dispatch | Needed before multi-agent rollout so failures, retries, and prompt drift are observable |

## Execution Artifacts

- Execution board: `AUTOMATION_EXECUTION_BOARD.md`
- n8n Phase 1 spec: `N8N_PHASE1_INTAKE_WORKFLOW_SPEC.md`
- LangGraph dispatcher spec: `LANGGRAPH_DISPATCHER_SPEC.md`