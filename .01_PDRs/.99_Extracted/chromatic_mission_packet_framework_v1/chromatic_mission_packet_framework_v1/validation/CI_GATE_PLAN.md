# CI Gate Plan

## Phase 1 — Advisory

- Run validator on examples.
- Do not block PRs yet.
- Collect schema friction.

## Phase 2 — Required for New Packets

- Validate changed files under mission packet directories.
- Fail PRs only when new or edited mission packets are invalid.

## Phase 3 — Required for Execution

- Local agents may only execute packets that pass schema validation.
- M3/M4 packets require PDR and governance docs.

## Phase 4 — Audit Integration

- Store validation output as evidence.
- Link packet, PDR, CI logs, PR, and closeout report.
