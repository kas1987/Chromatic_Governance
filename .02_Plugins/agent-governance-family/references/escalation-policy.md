# Escalation Policy

Escalate before continuing when any condition is true:

- The next action is destructive or irreversible.
- The action touches production, deployment, billing, customer data, legal/financial claims, credentials, or security posture.
- Tests, validation, or audits fail and the agent proposes to bypass them.
- Two authoritative sources conflict.
- The user request is ambiguous and multiple interpretations carry materially different risk.
- An agent needs broader tool access than originally delegated.
- The work would create external side effects such as emails, tickets, API calls, purchases, or public publishing.

## Escalation request template

```markdown
## Escalation request

**Requested action:** ...
**Why escalation is required:** ...
**Risk level:** ...
**Evidence:** ...
**Options:**
1. ...
2. ...
**Recommendation:** ...
**Safe fallback:** ...
```
