# Mission Packet - NW-REVIEW-INTAKE-002

## Task ID
NW-REVIEW-INTAKE-002

## Objective
Enable PR branch lock before mutating agent patches

## Source
- (no direct links)

## Owner Agent
Chainbreaker

## Allowed Files
- (PR-level scope)

## Risk Level
medium

## Confidence
86/100

## Acceptance Checks
- lock_pr_branch.py acquire blocks second active mutator
- expired locks can be replaced
- release clears active lock

## Stop Conditions
- Lock cannot be acquired for this PR branch.
- Fix requires files outside the allowed_files list.
- Reviewer intent is unclear; request clarification before patching.
- Security or architecture finding with confidence < 90 requires human decision.
- Tests fail outside touched file scope.

## Notes
Required before allowing agents to push patches to any PR branch.
