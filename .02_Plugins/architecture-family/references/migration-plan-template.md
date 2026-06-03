# Migration Plan Template

```markdown
# Migration Plan: <change>

## Current state
<what exists now>

## Target state
<what should exist after migration>

## Risk rating
Low / Medium / High / Critical

## Affected surfaces
- Data:
- Files:
- APIs:
- Config:
- Agents/plugins:
- Users:

## Preflight
- Backup or snapshot:
- Compatibility check:
- Required approvals:
- Test evidence:

## Stages
### 1. Prepare
### 2. Add new path
### 3. Backfill or transform
### 4. Dual-run or compatibility window
### 5. Cutover
### 6. Validate
### 7. Remove old path

## Rollback / recovery
<how to recover if a stage fails>

## Success criteria
- <observable check>

## Stop conditions
- <condition that halts migration>
```

For live systems, prefer expand-and-contract: add the new path first, migrate safely, then remove the old path later.
