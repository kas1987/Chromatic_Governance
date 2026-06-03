# Release Gate Model

Use this model to classify release readiness.

## Status values

- `pass`: evidence satisfies the gate.
- `conditional`: acceptable only with explicit owner, mitigation, or waiver.
- `fail`: gate is unmet and should block release.
- `unknown`: evidence was not available.

## Core gates

| Gate | Required evidence | Default blocker condition |
|---|---|---|
| Scope | Included/excluded changes are clear | Unknown release contents |
| Build | Build/package completes | Build failure |
| Tests/evals | Relevant tests/evals pass | Failing critical path |
| Security | No known critical/high unmanaged risks | Secret leak, auth flaw, injection risk |
| Migration | Forward/rollback/recovery path documented | Irreversible change without backup |
| Observability | Health signals and thresholds known | No way to detect failure |
| Rollback | Rollback/recovery owner and steps known | No recovery path for high-risk release |
| Docs/comms | User/operator notes prepared | Breaking change without migration notes |

## Recommendation mapping

- `go`: all required gates pass, or only low-risk accepted issues remain.
- `conditional`: one or more gates need explicit waiver or mitigation.
- `no-go`: any critical blocker exists.
- `blocked`: release cannot be assessed because essential evidence is unavailable.
