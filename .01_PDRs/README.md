# PDR Pipeline System

Chromatic Governance PDRs flow through a structured pipeline: **Backlog -> Pre-flight -> In-Process -> Completed -> Reviewed -> Archived**.

## Folder Structure

```
.01_PDRs/
├── .01_Backlog/          # PDRs proposed, not yet prioritized
├── .02_Pre-flight/       # Scope and intake checks complete, ready to start
├── .03_In-Process/       # PDRs actively being worked on
├── .04_Completed/        # PDRs done, awaiting review
├── .05_Reviewed/         # PDRs approved through governance
├── .00_Archived/         # Historical PDRs
├── .99_Extracted/        # Extracted scaffold bundles used during active work
├── PDR_REGISTRY.json     # Single source of truth (metadata, transitions, audit trail)
├── pdr_sync.py           # Automation script (sync, promote, report)
└── README.md             # This file
```

## PDR_REGISTRY.json

Central registry tracks:
- **PDR metadata** (id, title, phase, owner, completion %)
- **Status & file location** (synced with folder structure)
- **Transition history** (when → who → why)
- **Acceptance criteria** (gates for promotion)
- **Related issues/PRs** (cross-repo links)
- **Status workflow** (allowed transitions per state)

Example entry:
```json
{
  "id": "PDR-002",
  "title": "Skill Ecosystem Technical Foundation",
  "status": "In-Process",
  "phase": 2,
  "owner": "Claude",
  "file_path": ".01_PDRs/.03_In-Process/PDR-002-skill-ecosystem-technical-foundation.md",
  "transitions": [
    {"from": "Backlog", "to": "In-Process", "timestamp": "2026-02-01T10:30:00Z", "actor": "Claude", "reason": "Phase 2 implementation started"}
  ],
  "completion_percentage": 85,
  "acceptance_criteria": [
    "MCP skill server scaffold complete",
    "CI governance gates passing",
    "Access policy documented"
  ]
}
```

## Usage

### Manual File Organization

Simply move PDR files to the appropriate folder, then sync:

```bash
cd .01_PDRs
python pdr_sync.py sync
```

The script ensures folder location ↔ registry status consistency.

### Programmatic Promotion

Transition a PDR to a new status and move its file:

```bash
# Promote PDR-002 from In-Process to Completed
python pdr_sync.py promote PDR-002 Completed "All acceptance criteria met"

# Promote PDR-004 to Reviewed with reason
python pdr_sync.py promote PDR-004 Reviewed "Governance review passed; ready to archive"
```

The script:
1. ✅ Validates transition is allowed per workflow
2. 📁 Moves file to target folder
3. 📝 Updates registry status + file_path
4. 📋 Records transition with timestamp & reason

### Generate Status Report

```bash
python pdr_sync.py report
```

Output:
```
# PDR Pipeline Status Report

## Backlog (0)

## Pre-flight (0)

## In-Process (2)
- **PDR-002** — Skill Ecosystem Technical Foundation (85% complete)
- **PDR-004** — Review Intake System (90% complete)

## Completed (0)

## Reviewed (0)

## Archived (0)
```

### GitHub Actions Workflow

Use the automated promotion workflow:

1. Go to **Actions → PDR Status Update**
2. Click **Run workflow**
3. Fill in:
   - **PDR ID** (e.g., `PDR-002`)
  - **Target Status** (dropdown: Backlog, Pre-flight, In-Process, Completed, Reviewed, Archived)
   - **Reason** (optional)
4. Workflow creates a PR with the change

## Constraints

### Extracted Bundle Lifecycle

- Keep extracted bundles during Backlog, Pre-flight, In-Process, Completed, and Reviewed.
- Do not treat extracted bundles as the authoritative PDR source; they are scaffold snapshots.
- On promotion to Archived, extracted bundles are moved to `.00_Archived/_extracted/<PDR-ID>` automatically by `pdr_sync.py` when `extracted_path` is set in the registry.
- Hard delete is optional and should be a separate manual retention action after archive.

### ZIP Intake Policy

- Root-level `.zip` bundles under `.01_PDRs/` are tracked as backlog intake artifacts.
- ZIP intake artifacts live in `.01_PDRs/.01_Backlog/`.
- ZIPs remain intact while the work item is in Backlog.
- Moving a PDR to Pre-flight can auto-unpack its `zip_path` into `extracted_path` under `.99_Extracted/`.
- Moving a PDR from Pre-flight to In-Process is blocked unless extracted content exists and is non-empty.
- `python pdr_sync.py sync` auto-registers untracked ZIP files into `artifact_backlog` in `PDR_REGISTRY.json`.

### Automated ZIP Intake Review

- `pdr_zip_intake.py` scans `.01_PDRs/.01_Backlog/*.zip` and keeps `.01_PDRs/.01_Backlog/.99_Dups/*.zip` tracked as current inventory.
- Historical/current/new ZIP states are recorded in SQLite at `.01_PDRs/.intake/zip_intake.db`.
- Event stream is logged to `.01_PDRs/.intake/zip_intake-log.jsonl`.
- Pipeline stage/status is correlated from `PDR_REGISTRY.json` (`artifact_backlog` and `pdrs`).
- PDR IDs are auto-detected from archive contents (e.g., `PDR-001`) and stored.
- An implementation signal is computed per ZIP: `not_implemented | preflight_ready | in_progress | implemented | unknown`.
- Implementation signal uses pipeline status + extracted readiness for local/repo implementation awareness.
- A duplicate gate computes `duplicate | redundant | possible_redundant | unique | unknown` with a confidence score.
- High-confidence `duplicate` or `redundant` ZIPs are moved into `.01_PDRs/.01_Backlog/.99_Dups/` automatically and the evidence is stored in SQLite.
- Workflow `.github/workflows/pdr-zip-intake.yml` runs automatically on ZIP drops.
- `.01_PDRs/AUTOMATION_WIRING_LOG.md` tracks which pipeline and intake processes should later be wired into `n8n`, `LangGraph`, `LangSmith`, or related automation tooling.
- `.01_PDRs/AUTOMATION_EXECUTION_BOARD.md` tracks implementation-ready phases, owners, priorities, and acceptance checks.
- `.01_PDRs/N8N_PHASE1_INTAKE_WORKFLOW_SPEC.md` defines the concrete Phase 1 event-bridge workflow for intake orchestration.
- `.01_PDRs/LANGGRAPH_DISPATCHER_SPEC.md` defines the queue-to-agent lock-safe dispatcher for multi-agent execution.
- `.03_Harness Governance/orchestration/README.md` links runnable n8n and LangGraph scaffolds aligned with those specs.

Manual run:

```bash
cd .01_PDRs
python pdr_zip_intake.py

# Test a single ZIP
python pdr_zip_intake.py --zip-name repo-pdr-swarm-router.zip
```

### GPT ZIP Drop Automation (Local + Repo)

If ZIPs are coming from ChatGPT (web or desktop), you have two easy options:

1. **Easiest: set ChatGPT/browser download folder to `.01_PDRs` directly**
  - Drop/download ZIP files straight into `.01_PDRs/`
  - Run local watcher for immediate intake:

```powershell
cd .01_PDRs
./start_zip_drop_watcher.ps1
```

2. **Keep normal Downloads folder, then import automatically**
  - Import all ZIPs from Downloads into `.01_PDRs` and intake each one:

```powershell
cd .01_PDRs
python pdr_zip_ingest.py import --source-dir "$env:USERPROFILE\Downloads"

# Move instead of copy
python pdr_zip_ingest.py import --source-dir "$env:USERPROFILE\Downloads" --move
```

3. **Repo-side automation (GitHub Actions)**
  - Once ZIPs are committed/pushed, `.github/workflows/pdr-zip-intake.yml` runs automatically.
  - This is event-based on push; local-only drops do not trigger GitHub Actions until pushed.

The local helper script supports three modes:

```powershell
python pdr_zip_ingest.py once
python pdr_zip_ingest.py watch --interval 5
python pdr_zip_ingest.py import --source-dir "$env:USERPROFILE\Downloads"
```

### Allowed Transitions

| From State | Allowed Transitions |
|-----------|-------------------|
| **Backlog** | -> Pre-flight |
| **Pre-flight** | -> In-Process, Backlog |
| **In-Process** | -> Completed, Pre-flight |
| **Completed** | → Reviewed, In-Process |
| **Reviewed** | → Archived |
| **Archived** | (final state) |

### Sync Conflicts

If a PDR file is in the wrong folder or missing:
- `pdr_sync.py sync` will detect and report the issue
- Manual correction + resync resolves inconsistencies
- Orphaned files (not in registry) are flagged but not deleted

## Integration

### With CI/CD

Add to `.github/workflows/governance.yml` to auto-sync before tests:

```yaml
- name: Sync PDR pipeline
  run: python .01_PDRs/pdr_sync.py sync
```

### With GitHub Issues

Link acceptance criteria to issues via related_issues in registry:

```json
"related_issues": ["#1", "#42"]
```

### With Pull Requests

Track phase progress via related_pr in registry — the PR dashboard will show all linked PDRs.

## Model Router

The Chromatic harness routes subagent and LLM calls through a 5-tier provider stack. All sessions in this repo route via the global shell router.

### Where the router lives

| File | Purpose |
|------|---------|
| `~/.claude/hooks/model-router.sh` | PreToolUse hook — fires before every Agent call |
| `~/.claude/config/provider-tiers.json` | Tier 0–4 provider + model config |
| `~/.claude/config/router-patterns.json` | Keyword patterns for task classification |
| `~/.claude/.agents/router/log.jsonl` | Per-decision audit log |
| `~/.claude/governance/multi-router-matrix.yaml` | Canonical policy (C-levels, T-levels, effort routing) |
| `C:\.00_Governance\cross-provider-model-routing.md` | Human-readable routing reference |

### Current tier map

| Tier | Provider | Model | When |
|------|----------|-------|------|
| T0 nano | Ollama local | `llama3.2:3b` | Tables, formatting, zero-judgment transforms |
| T1 micro | Featherless | `NousResearch/Hermes-3-Llama-3.1-8B` | Scaffold, boilerplate, seed templates |
| T2 small | OpenAI | `gpt-4o-mini` | Smoke tests, spec compliance, single-file PR review |
| T3 medium | Gemini | `gemini-2.5-flash` | Debug, root cause, multi-file integration |
| T4 large | Claude | `claude-sonnet-4-6` | Brainstorm, design, architecture — orchestrator default |

### Status

- **Ollama**: installed at `C:\Users\kas41\AppData\Local\Programs\Ollama\ollama.exe`, port 11434 live, no models loaded yet
- **Featherless**: key configured in `~/.claude/settings.json` (env: `FEATHERLESS_API_KEY`)
- **OpenAI / Gemini**: keys present
- **Router log**: `~/.claude/.agents/router/log.jsonl` — read to review routing decisions

### Loading an Ollama model

```powershell
ollama pull llama3.2:3b          # T0 nano
ollama pull qwen2.5-coder:14b   # best local coding model
ollama list                      # verify
```

### Concurrency limits

**Featherless Premium ($25/mo) — 4 total concurrency units**

| Model size | Units used | Max simultaneous |
|-----------|-----------|-----------------|
| 7B–15B (e.g. `Hermes-3-Llama-3.1-8B`) | 1 | **4 concurrent** |
| 24B–34B (e.g. `Qwen2.5-Coder-32B`) | 2 | **2 concurrent** |
| 70B–72B | 4 | **1 concurrent** |

Requests over the limit receive HTTP 429. Docs: https://featherless.ai/docs/concurrency-limits

**Ollama Cloud Pro ($20/mo)**

| Plan | Concurrent models | Usage |
|------|------------------|-------|
| Pro ($20/mo) | 3 | 50× Free |
| Max ($100/mo) | 10 | 5× Pro |

Session limits reset every 5h; weekly limits every 7d. Docs: https://ollama.com/settings/billing

### ART-HERMES Eval Results (2026-06-04)

Both `Qwen/Qwen2.5-Coder-32B-Instruct` and `gemini-2.5-flash` scored **100/100** across 3 C1/C2 tasks (mission comprehension, YAML edit, scope compliance). Gemini is **5.3× faster** (3.9s vs 20.8s avg). Full report: `.99_Extracted/hermes_eval_report.md`

**Swarm strategy:**
- C1 bulk: 4× `Hermes-3-8B` in parallel (1 unit each, fills Featherless 4-unit plan)
- C2 coding: 2× `Qwen2.5-Coder-32B` in parallel (2 units each)
- Latency-critical: `gemini-2.5-flash` (T3)

---

## Best Practices

1. **Update registry early** — add PDR entry before creating the file
2. **Use clear transition reasons** — audit trail helps future decisions
3. **Set realistic completion %** — helps prioritize work
4. **Review before promote to Reviewed** — acceptance criteria must pass
5. **Archive after 6 months** — keep in-use states lean
6. **Run sync before commits** — prevents folder/registry drift

## Example Workflow

```bash
# 1. New PDR proposed
python pdr_sync.py promote PDR-005 Backlog "Proposed for Phase 3"

# 2. Move to Pre-flight for intake checks
python pdr_sync.py promote PDR-005 Pre-flight "Scoping and dependencies validated"

# 3. Move to In-Process when work starts
python pdr_sync.py promote PDR-005 In-Process "Phase 3 sprint started"

# 4. Sync local changes / folder moves
python pdr_sync.py sync

# 5. Mark complete when done
python pdr_sync.py promote PDR-005 Completed "Implementation complete; 95% coverage"

# 6. Governance review and approve
python pdr_sync.py promote PDR-005 Reviewed "Passed governance review on 2026-06-15"

# 7. Archive after successful adoption
python pdr_sync.py promote PDR-005 Archived "No longer needed; replaced by PDR-006"

# 8. Check report anytime
python pdr_sync.py report
```
