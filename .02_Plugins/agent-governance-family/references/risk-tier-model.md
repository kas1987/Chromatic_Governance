# Risk Tier Model

| Tier | Meaning | Examples | Required gate |
|---|---|---|---|
| low | Local, reversible, read-only or minor docs | Summaries, notes, non-sensitive docs | Agent self-check |
| medium | Bounded edits with testable impact | Code changes, config updates, test additions | Peer/specialist review |
| high | Security, credentials, data migration, dependency, release prep | Auth changes, package upgrades, DB migrations | Independent review + human awareness |
| critical | Production, irreversible, external side effects, legal/financial/security exposure | Deploy, delete data, send external comms, publish | Explicit human approval |
