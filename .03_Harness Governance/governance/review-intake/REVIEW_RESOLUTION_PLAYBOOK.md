# Review Resolution Playbook

## Purpose

Ensure every agent fix is proven back to the PR with evidence before the finding is marked resolved.

## Required resolution comment format

```markdown
## Chromatic Review Resolution

**Finding:** RF-...
**Queue Item:** NW-...
**Status:** Resolved | Blocked | Needs Reviewer Clarification
**Agent:** Sentinel
**Confidence:** 86/100

### Change made
...

### Validation
- `pytest tests/test_affected.py -v`
- `ruff check src/affected.py`

### Files changed
- `src/affected.py`

### Notes
...
```

Generate with: `python scripts/post_review_resolution.py --finding RF-... --task NW-... --agent Sentinel`

## Rules

1. Do not mark a finding resolved without validation output or a documented reason.
2. If tests fail outside the touched scope, mark blocked and create a follow-up queue item.
3. If reviewer intent is unclear, ask for clarification rather than guessing.
4. After posting, run `log_resolution.py` to update the queue and write the resolution log.

## Resolution workflow

```
patch applied
  → run acceptance checks
  → post_review_resolution.py | gh pr comment <PR_NUM> --body-file -
  → log_resolution.py --finding RF-... --task NW-... --agent <agent> --status resolved
  → lock_pr_branch.py release
```
