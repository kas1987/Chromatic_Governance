# Agent Router Handoff

## Router responsibility

The router decides which agent may request access and forwards only validated access requests to the broker.

## Router must provide

```json
{
  "agent_id": "code_sentinel",
  "repo": "example-org/example-repo",
  "profile": "patch_standard",
  "task_id": "GOV-001",
  "branch": "agent/codesentinel/GOV-001-policy-fix",
  "target_branch": "main",
  "action": "patch"
}
```

## Router must not provide

- Raw GitHub App private key.
- Long-lived PAT.
- Admin permission requests.
- Requests without task IDs for write actions.

## Escalation

Escalate to human review when:

- The agent asks for admin/secrets/workflow mutation.
- More than 25 files are changed.
- High-risk paths are touched.
- The patch affects auth, CI, deployment, or production config.
