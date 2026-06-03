# Operations Runbook

## Normal request flow

1. Agent receives task.
2. Agent requests access from broker.
3. Broker validates policy.
4. Broker logs decision.
5. Broker issues or denies token.
6. Agent performs allowed action.
7. Agent opens PR for writes.
8. CI and review gates run.

## Dry-run rollout

1. Configure fake/example repo values.
2. Run policy tests.
3. Replace example repo with real repo.
4. Run read-only agent access.
5. Enable issue triage.
6. Enable patch agent on low-risk docs path.
7. Expand cautiously.

## Incident: token exposure suspected

1. Stop broker runtime.
2. Rotate GitHub App private key.
3. Suspend app installation if needed.
4. Search logs for token-like strings.
5. Review recent PRs and pushes.
6. Re-enable with stricter profiles.

## Incident: bad agent PR

1. Close PR without merge.
2. Label `agent-failed-control`.
3. Record cause in audit log or issue.
4. Patch policy or prompt guardrail.
5. Re-run from clean branch only.
