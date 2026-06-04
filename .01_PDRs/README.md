# PDR Pipeline System

Chromatic Governance PDRs flow through a structured pipeline: **Backlog → In-Process → Completed → Reviewed → Archived**.

## Folder Structure

```
.01_PDRs/
├── Backlog/              # PDRs proposed, not yet prioritized
├── In-Process/           # PDRs actively being worked on
├── Completed/            # PDRs done, awaiting review
├── Reviewed/             # PDRs approved through governance
├── Archived/             # Historical PDRs
├── PDR_REGISTRY.json     # Single source of truth (metadata, transitions, audit trail)
├── pdr_sync.py           # Automation script (sync, promote, report)
├── chromatic_review_intake_pdr_extracted/  # Reference implementations
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
  "file_path": ".01_PDRs/In-Process/PDR-002-skill-ecosystem-technical-foundation.md",
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
   - **Target Status** (dropdown: Backlog, In-Process, Completed, Reviewed, Archived)
   - **Reason** (optional)
4. Workflow creates a PR with the change

## Constraints

### Allowed Transitions

| From State | Allowed Transitions |
|-----------|-------------------|
| **Backlog** | → In-Process |
| **In-Process** | → Completed, Backlog |
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

# 2. Move to In-Process when work starts
python pdr_sync.py promote PDR-005 In-Process "Phase 3 sprint started"

# 3. Sync local changes / folder moves
python pdr_sync.py sync

# 4. Mark complete when done
python pdr_sync.py promote PDR-005 Completed "Implementation complete; 95% coverage"

# 5. Governance review and approve
python pdr_sync.py promote PDR-005 Reviewed "Passed governance review on 2026-06-15"

# 6. Archive after successful adoption
python pdr_sync.py promote PDR-005 Archived "No longer needed; replaced by PDR-006"

# 7. Check report anytime
python pdr_sync.py report
```
