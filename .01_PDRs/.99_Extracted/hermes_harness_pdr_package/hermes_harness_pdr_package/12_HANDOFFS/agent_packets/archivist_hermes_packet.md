# Agent Handoff: Hermes Integration - archivist

## Agent Role

archivist

## Mission

Implement or review the Hermes local worker integration from the perspective of this agent specialty.

## Source Files

- 08_PDRS/PDR_HERMES_LOCAL_AGENT_WORKER.md
- 12_HANDOFFS/HERMES_IMPLEMENTATION_PLAN.md
- docs/governance/HERMES_ROUTING_POLICY.md
- docs/validation/HERMES_EVALUATION_PROTOCOL.md
- 09_DEPLOYMENT/config/routing/hermes-model-capability.example.yaml
- 09_DEPLOYMENT/config/routing/hermes-routing-patch.example.yaml

## Allowed Actions

- Read repo routing and governance files.
- Propose bounded patches.
- Add tests.
- Add docs.
- Record validation results.

## Blocked Actions

- Do not bypass governance gates.
- Do not promote Hermes to C3/C4 default routing without benchmark evidence.
- Do not change git autonomy thresholds.
- Do not delete existing provider routes.
- Do not modify secrets or credentials.

## Acceptance Criteria

- Findings are grounded in repo files.
- Any proposed patch is scoped and reversible.
- Stop conditions are preserved.
- Output includes validation evidence or explicit blockers.

## Stop Conditions

Stop and report if:

- Hermes model tag is not installed.
- Existing routing tests fail before changes.
- Provider selector behavior differs from expected architecture.
- Any patch requires changing secrets, env files, or production autonomy policy.
