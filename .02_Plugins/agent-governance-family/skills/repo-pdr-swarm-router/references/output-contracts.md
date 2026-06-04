# Output Contracts

## Executive Intake Summary
Use this order:
1. conclusion
2. highest-risk blockers
3. dispatch readiness percentage
4. next 3 actions
5. evidence status

## Dispatch Board Columns
- task_id
- priority
- agent_role
- mission
- status
- source_files
- dependencies
- acceptance_criteria
- stop_condition
- handoff_target

## Risk Register Columns
- risk_id
- severity
- category
- description
- evidence
- owner
- mitigation
- status

## Evidence Map Columns
- evidence_id
- source_path
- artifact_class
- supports
- confidence
- notes

## Readiness Score
Score out of 100:
- 20 points: source-of-truth identified
- 15 points: package inventory complete
- 15 points: router alignment clear
- 15 points: dependencies known
- 15 points: acceptance criteria present
- 10 points: risk register complete
- 10 points: stop conditions present

Readiness bands:
- 85-100: dispatch-ready
- 65-84: dispatchable with controls
- 40-64: partial dispatch only
- 0-39: intake blocked
