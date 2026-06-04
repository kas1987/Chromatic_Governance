# Mission Packet - NW-REVIEW-INTAKE-001

## Task ID
NW-REVIEW-INTAKE-001

## Objective
Validate passive GitHub review intake workflow in Chromatic repo

## Source
- (no direct links)

## Owner Agent
Auditor

## Allowed Files
- (PR-level scope)

## Risk Level
low

## Confidence
90/100

## Acceptance Checks
- GitHub Action triggers on pull_request_review_comment
- review-findings.jsonl receives a valid JSONL record
- next-work.queue.json receives a deduped queue item

## Stop Conditions
- Lock cannot be acquired for this PR branch.
- Fix requires files outside the allowed_files list.
- Reviewer intent is unclear; request clarification before patching.
- Security or architecture finding with confidence < 90 requires human decision.
- Tests fail outside touched file scope.

## Notes
Phase 1 — passive intake only. No auto-patching.
