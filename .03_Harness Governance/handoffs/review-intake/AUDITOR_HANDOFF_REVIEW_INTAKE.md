# Agent Handoff: Auditor — Review Intake Validation

## Task ID
NW-REVIEW-INTAKE-001

## Mission
Validate that GitHub review events are converted into normalized findings and queue items. Phase 1 only — passive intake, no patching.

## Allowed files
- `.github/workflows/review-intake.yml`
- `.03_Harness Governance/scripts/review_intake.py`
- `.03_Harness Governance/scripts/classify_review_finding.py`
- `.03_Harness Governance/schemas/*.schema.json`
- `.agents/review-intake/review-findings.jsonl`
- `.agents/review-intake/next-work.queue.json`

## Blocked actions
- Do not push auto-fixes to any PR branch.
- Do not edit production deployment files.
- Do not change secrets or permissions beyond what is documented in the workflow.

## Acceptance criteria
- Sample event creates exactly one finding in `review-findings.jsonl`.
- Same event a second time does not duplicate the queue item.
- Low-confidence or vague comments are not marked `ready` for mutation.
- Output is valid JSON / JSONL.

## Stop conditions
- Event payload shape is unknown — log and exit.
- Queue file is malformed — halt, do not overwrite.
- Action permissions fail — escalate to human.
