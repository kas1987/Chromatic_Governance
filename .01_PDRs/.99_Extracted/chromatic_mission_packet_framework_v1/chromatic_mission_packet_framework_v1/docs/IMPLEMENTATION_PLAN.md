# Implementation Plan

## Objective

Install the M1-M4 mission packet framework into Chromatic Harness v2 so local agents can execute structured missions with appropriate governance.

## Phase 1 — Add Base Files

Owner: quartermaster

- Add schemas.
- Add templates.
- Add docs.
- Add examples.
- Add validator.

Stop if repo tree placement conflicts with existing standards.

## Phase 2 — Validate Locally

Owner: sentinel

- Install `jsonschema` and `pyyaml` in dev environment.
- Run validator against examples.
- Confirm valid packets pass.
- Create an intentionally invalid packet and confirm it fails.

## Phase 3 — Add CI Advisory Gate

Owner: sentinel

- Add CI workflow or existing CI step.
- Run validation as advisory first.
- Record failures without blocking until schema is stable.

## Phase 4 — Integrate Router

Owner: auditor + cartographer

- Confirm mission levels map cleanly to existing complexity C1-C4.
- Confirm local workers receive only validated packets.
- Confirm M3/M4 escalate for review.

## Phase 5 — Operationalize

Owner: archivist

- Add closeout report pattern.
- Log mission outcomes.
- Track model performance.
- Promote learnings back into routing policy.
