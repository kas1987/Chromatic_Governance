# Multi-Session IDE/LLM Collision Safety Playbook

**Version:** 2026-06-04  
**Scope:** Operating procedures for single and multi-agent mutations on Chromatic_Governance PR branches  
**Operators:** Claude IDE sessions, n8n workflows, Python dispatch agents  
**Reference:** `.00_PLANNING/locks/pr_branch_lock.schema.json`

---

## Core Rules

### Rule 1: One Agent Per Branch
**A single PR branch can have only ONE active mutating agent at any time.**

- Multiple agents may **inspect** (read, comment, propose) without locks
- Only ONE agent may **mutate** (commit, push, write files)
- Locks prevent accidental collisions and merge conflicts

### Rule 2: Read-Only Inspection is Free
**Inspecting a branch does NOT require a lock.**

- Code review, validation, diagnostics → no lock needed
- Suggesting changes in comments → no lock needed
- Only **writing to the branch or index** requires lock acquisition

### Rule 3: Locks Have TTL
**Expired locks can be replaced; stale locks will not block new work.**

- Default TTL: 30 minutes
- Max TTL: 24 hours
- Lock auto-expires if agent crashes or hangs

---

## Lock Lifecycle

```
            ┌──────────────┐
            │ New mutation │
            │   needed     │
            └──────┬───────┘
                   │
                   v
         ┌─────────────────────┐
         │ Attempt lock acquire │
         └────────┬────────────┘
                  │
       ┌──────────┴──────────┐
       │                     │
       v                     v
    SUCCESS             LOCKED/CONFLICT
       │                     │
       │           ┌─────────┴──────────┐
       │           │                    │
       │           v                    v
       │        QUEUED           WAIT FOR EXPIRY
       │        (try later)        (30+ min TTL)
       │           │                    │
       │           └────────┬───────────┘
       │                    │
       v                    v
    ┌──────────────────────────────┐
    │  Patch / Commit / Validate   │
    └──────┬───────────────────────┘
           │
           v
    ┌──────────────────────────────┐
    │  Comment / Push (to branch)  │
    └──────┬───────────────────────┘
           │
           v
    ┌──────────────────────────────┐
    │    Release lock              │
    └──────────────────────────────┘
           │
           v
    ┌──────────────────────────────┐
    │  PR ready for review/merge   │
    └──────────────────────────────┘
```

---

## Lock File Format & Location

**Location:** `.00_PLANNING/locks/PR-{number}.lock.json`

**Example:**
```json
{
  "lock_id": "LOCK-Chromatic_Governance-PR1",
  "repo": "kas1987/Chromatic_Governance",
  "pr_number": 1,
  "branch": "claude/test-coverage-analysis-XoxC1",
  "holder": "agent-dispatch-review-intake",
  "queue_item_id": "NW-REVIEW-INTAKE-002",
  "started_at": "2026-06-04T20:30:07.936257Z",
  "expires_at": "2026-06-04T21:00:07.936257Z",
  "ttl_minutes": 30
}
```

---

## Operating Procedures

### Procedure A: Claude IDE Session (Single User)

**Use case:** You're in VS Code, making manual edits to the PR branch

**Workflow:**
1. ✅ **No lock required** — you're the only active agent
2. Make your edits locally
3. Run local validation (tests, linting)
4. Commit with clear message
5. Push to branch
6. PR auto-checks run on GitHub

**When to lock (optional safeguard):**
- You're editing PR #1, and n8n workflow might also touch it simultaneously
- **Acquire lock:** `python .01_PDRs/scripts/lock_pr_branch.py acquire --repo kas1987/Chromatic_Governance --pr-number 1 --holder "claude-session-manual-edit" --ttl-minutes 60`
- After push and validation: **Release lock** → `python .01_PDRs/scripts/lock_pr_branch.py release --repo kas1987/Chromatic_Governance --pr-number 1`

---

### Procedure B: Python Dispatcher Auto-Mutation

**Use case:** Automated dispatcher (in `.03_Harness Governance/orchestration/`) mutates PR branch based on queue

**Workflow:**
1. **Check for lock:** Status query before any mutation
   ```bash
   python .01_PDRs/scripts/lock_pr_branch.py status \
     --repo kas1987/Chromatic_Governance \
     --pr-number 1
   ```
2. **If locked (active):**
   - Log "lock active, will retry"; exit cleanly
   - Add to retry queue with backoff (exponential, 5–30 min)
3. **If unlocked:**
   - **Acquire lock:**
     ```bash
     python .01_PDRs/scripts/lock_pr_branch.py acquire \
       --repo kas1987/Chromatic_Governance \
       --pr-number 1 \
       --holder "agent-dispatch-review-intake" \
       --queue-item-id "NW-REVIEW-INTAKE-002" \
       --ttl-minutes 30
     ```
   - **On success:** Proceed with mutation
   - **On failure (active lock):** Fail-fast; log and queue for retry
4. **Mutate:**
   - Fetch latest branch state
   - Apply changes to files
   - Run local validation
   - Commit with trace ID
   - Push to branch
5. **Release lock:**
   ```bash
   python .01_PDRs/scripts/lock_pr_branch.py release \
     --repo kas1987/Chromatic_Governance \
     --pr-number 1
   ```
6. **Log outcome:** Update `.agents/review-intake/logs/agent-dispatch-log.jsonl` with lock lifecycle

---

### Procedure C: n8n Workflow → Python Dispatcher Handoff

**Use case:** n8n workflow completes, signals Python dispatcher to patch and release lock

**Workflow (cooperative):**
1. **n8n workflow acquires implicit lock** (by writing to dispatch queue item with `"locked_by": "n8n-workflow-X"`)
2. **n8n sends webhook** to Python dispatcher:
   ```json
   {
     "event": "workflow_complete",
     "pr_number": 1,
     "workflow_id": "pdr-zip-intake-phase1",
     "findings": [...],
     "next_action": "dispatch"
   }
   ```
3. **Python dispatcher:**
   - Receives webhook
   - Calls `lock_pr_branch.py acquire` (fails if n8n still holds lock implicitly)
   - Applies findings to PR branch
   - Pushes and releases
4. **n8n optional cleanup:**
   - Webhook callback from dispatcher: "lock released, next workflow may proceed"

---

## Failure Modes & Recovery

| Failure | Symptom | Recovery |
|---------|---------|----------|
| **Agent crashes mid-patch** | Lock remains active; TTL expires in 30 min | Wait for TTL expiry, then acquire; or admin override (see below) |
| **Two agents acquire simultaneously** | Race condition (rare but possible on NFS) | Lock file not updated atomically; add retry loop with backoff (1–5 sec) |
| **Branch changes while agent has lock** | Agent's edits conflict with unexpected upstream change | Agent validates merge before commit; if conflict, release lock and escalate |
| **Lock acquired but agent never releases** | Stale lock persists after agent finishes | TTL auto-releases; or manual release via `release` command if safe |
| **Dispatcher doesn't respect lock** | Multiple agents mutating simultaneously | Validation: dispatcher tests lock on startup (see "Pre-Flight Checks" below) |

---

## Pre-Flight Checks (For Dispatcher)

Before deploying the dispatcher, validate lock behavior:

```bash
#!/bin/bash
# test-lock-collision.sh

REPO="kas1987/Chromatic_Governance"
PR=1

echo "[1/4] Testing lock acquire..."
python .01_PDRs/scripts/lock_pr_branch.py acquire \
  --repo "$REPO" --pr-number "$PR" \
  --holder "test-agent-1" --ttl-minutes 5
RESULT1=$?

echo "[2/4] Testing second acquire (should fail)..."
python .01_PDRs/scripts/lock_pr_branch.py acquire \
  --repo "$REPO" --pr-number "$PR" \
  --holder "test-agent-2" --ttl-minutes 5
RESULT2=$?

if [ $RESULT1 -eq 0 ] && [ $RESULT2 -eq 2 ]; then
  echo "[3/4] Release first lock..."
  python .01_PDRs/scripts/lock_pr_branch.py release \
    --repo "$REPO" --pr-number "$PR"
  
  echo "[4/4] Third acquire (should succeed)..."
  python .01_PDRs/scripts/lock_pr_branch.py acquire \
    --repo "$REPO" --pr-number "$PR" \
    --holder "test-agent-3" --ttl-minutes 5
  RESULT3=$?
  
  if [ $RESULT3 -eq 0 ]; then
    echo "✅ All lock tests passed!"
    python .01_PDRs/scripts/lock_pr_branch.py release \
      --repo "$REPO" --pr-number "$PR"
    exit 0
  fi
fi

echo "❌ Lock tests failed!"
exit 1
```

**Run before deployment:**
```bash
bash .03_Harness\ Governance/scripts/test-lock-collision.sh
```

---

## Admin Procedures

### Manual Lock Release (Emergency)

**If a lock is stuck and TTL hasn't expired:**
```bash
# Check lock status
python .01_PDRs/scripts/lock_pr_branch.py status \
  --repo kas1987/Chromatic_Governance \
  --pr-number 1

# Force-release (admin only; requires human approval)
rm .00_PLANNING/locks/PR-1.lock.json

# Verify cleared
python .01_PDRs/scripts/lock_pr_branch.py status \
  --repo kas1987/Chromatic_Governance \
  --pr-number 1
# Should print: unlocked
```

**Conditions for emergency release:**
- Agent holding lock has crashed or hung
- TTL is not set to auto-expire soon (> 4 hours old)
- No active work is happening on the branch
- Human has visually verified branch state is safe

### Audit Lock History

Lock files are stored in `.00_PLANNING/locks/` and are NOT gitignored. This provides an audit trail:
```bash
# See all lock activity
git log --follow -- '.00_PLANNING/locks/PR-*.lock.json'

# See what agent last held PR #1
cat .00_PLANNING/locks/PR-1.lock.json | jq .
```

---

## Integration with Current Workflow

### For `.03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py`

**Add to dispatcher before `apply_writeback()`:**
```python
from pathlib import Path
import subprocess
import json

def acquire_pr_lock(repo: str, pr_number: int, holder: str, queue_item_id: str, ttl: int = 30) -> bool:
    """Return True if lock acquired, False if already held."""
    result = subprocess.run(
        [
            "python", ".01_PDRs/scripts/lock_pr_branch.py", "acquire",
            "--repo", repo, "--pr-number", str(pr_number),
            "--holder", holder, "--queue-item-id", queue_item_id,
            "--ttl-minutes", str(ttl)
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0

def release_pr_lock(repo: str, pr_number: int) -> bool:
    """Return True if lock released."""
    result = subprocess.run(
        [
            "python", ".01_PDRs/scripts/lock_pr_branch.py", "release",
            "--repo", repo, "--pr-number", str(pr_number)
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0

# In run_simulation() or apply_writeback():
if acquire_pr_lock("kas1987/Chromatic_Governance", 1, "agent-dispatch-review-intake", queue_item_id):
    try:
        apply_writeback(...)  # existing code
    finally:
        release_pr_lock("kas1987/Chromatic_Governance", 1)
else:
    log_dispatch_event("lock_collision", queue_item_id, "PR #1 is locked; will retry")
    # Add to retry queue with backoff
```

---

## Current Status: Single-User Setup

For your current profile (solo, occasional IDE sessions):
- ✅ Lock system is in place; ready to use
- ✅ No immediate collision risk
- ⚠️ Optional: Wire into dispatcher when multi-agent complexity increases
- ⚠️ Recommended: Document your workflow habits (commit often, communicate intent)

---

## Escalation & Future

**When to escalate lock requirements:**
- 3+ agents working on the same repo simultaneously
- Rapid iteration cycles where collisions become frequent
- Integration with multiple n8n workflows + Python dispatch waves

**Then move to:**
- Centralized lock server (Redis, etcd) instead of file-based
- Transaction log and lock state machine
- Automatic escalation/retry with configurable backoff

---

## See Also

- `multi-session-safety-and-gemini-billing.md` — Full collision safety reference
- `.01_PDRs/scripts/lock_pr_branch.py` — Lock implementation
- `.03_Harness Governance/orchestration/README.md` — Dispatcher docs
- `.agents/review-intake/next-work.queue.json` — Queue structure
