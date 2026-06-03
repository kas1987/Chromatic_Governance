# Interface Contract Template

```markdown
# Contract: <boundary name>

## Owner
<team/agent/module responsible>

## Producer
<what creates or exposes this interface>

## Consumer
<what depends on this interface>

## Purpose
<why this boundary exists>

## Inputs
| Field | Type | Required | Validation | Notes |
|---|---|---|---|---|

## Outputs
| Field | Type | Meaning | Notes |
|---|---|---|---|

## Side effects
- <files changed, network calls, database writes, logs, notifications>

## Error behavior
| Error | Cause | Consumer behavior |
|---|---|---|

## Idempotency
<safe to retry? duplicate behavior? unique keys?>

## Security and permissions
<auth, secrets, allowed tools, data exposure>

## Versioning and compatibility
<how breaking changes are handled>

## Contract tests
- Positive case:
- Negative case:
- Compatibility case:
```
