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
- ZIPs remain intact while the work item is in Backlog.
- Moving a PDR to Pre-flight can auto-unpack its `zip_path` into `extracted_path` under `.99_Extracted/`.
- Moving a PDR from Pre-flight to In-Process is blocked unless extracted content exists and is non-empty.
- `python pdr_sync.py sync` auto-registers untracked ZIP files into `artifact_backlog` in `PDR_REGISTRY.json`.

### Automated ZIP Intake Review

- `pdr_zip_intake.py` scans `.01_PDRs/*.zip` and auto-reviews integrity (`zipfile` validation + file count).
- Historical/current/new ZIP states are recorded in SQLite at `.01_PDRs/.intake/zip_intake.db`.
- Event stream is logged to `.01_PDRs/.intake/zip_intake-log.jsonl`.
- Pipeline stage/status is correlated from `PDR_REGISTRY.json` (`artifact_backlog` and `pdrs`).
- PDR IDs are auto-detected from archive contents (e.g., `PDR-001`) and stored.
- An implementation signal is computed per ZIP: `not_implemented | preflight_ready | in_progress | implemented | unknown`.
- Implementation signal uses pipeline status + extracted readiness for local/repo implementation awareness.
- Workflow `.github/workflows/pdr-zip-intake.yml` runs automatically on ZIP drops.

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
