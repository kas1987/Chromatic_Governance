# Agent Handoff: Sentinel — Patch Review Finding

## Mission
Patch a ready review finding after the dispatcher assigns it via `dispatch_queue.py`.

## Required inputs
- Queue item ID (`NW-...`)
- Source finding ID (`RF-...`)
- PR link / comment link
- `allowed_files` list from the mission packet
- Acceptance checks from the mission packet

## Steps

1. Acquire PR branch lock:
   ```bash
   python ".03_Harness Governance/scripts/lock_pr_branch.py" acquire \
     --repo <repo> --pr-number <N> --holder Sentinel --queue-item-id <NW-id>
   ```
2. Read the source finding from `review-findings.jsonl` and the linked PR context.
3. Edit only the files in `allowed_files`. Stop if the fix requires files outside that list.
4. Run acceptance checks.
5. Generate and post resolution comment:
   ```bash
   python ".03_Harness Governance/scripts/post_review_resolution.py" \
     --finding <RF-id> --task <NW-id> --agent Sentinel \
     --status Resolved --files <changed-files> --validation "<check-cmd>" \
     | gh pr comment <PR_NUM> --body-file -
   ```
6. Log the resolution:
   ```bash
   python ".03_Harness Governance/scripts/log_resolution.py" \
     --finding <RF-id> --task <NW-id> --agent Sentinel \
     --status resolved --summary "<one-line summary>" --files <files>
   ```
7. Release the lock:
   ```bash
   python ".03_Harness Governance/scripts/lock_pr_branch.py" release \
     --repo <repo> --pr-number <N>
   ```

## Stop conditions
- Lock cannot be acquired (exit code 2) — wait or escalate; do not proceed.
- Fix requires files outside `allowed_files` — release lock, mark blocked.
- Reviewer intent is unclear — release lock, mark `needs-clarification`.
- Security or architecture human gate (`needs-human-decision`) — do not patch.
- Tests fail in files you did not touch — mark blocked, create follow-up queue item.
