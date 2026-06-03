# Risk Register

| ID | Risk | Probability | Impact | Score | Mitigation | Owner |
|---|---|---:|---:|---:|---|---|
| R-001 | Shared PAT leaks | 3 | 5 | 15 | Prefer GitHub App tokens; no long-lived shared PATs | Human admin |
| R-002 | Agent modifies protected workflow | 3 | 5 | 15 | High-risk file review; CODEOWNERS; required approval | Maintainer |
| R-003 | Agent pushes directly to main | 2 | 5 | 10 | Branch protection; broker denies main target | Maintainer |
| R-004 | Prompt injection causes malicious diff | 4 | 4 | 16 | PR review, diff limits, tests, allow/deny paths | CodeSentinel owner |
| R-005 | Token logged accidentally | 2 | 5 | 10 | Redaction, no token logging, secret scanning | Broker owner |
| R-006 | App installed on too many repos | 2 | 4 | 8 | Selected repo installation; quarterly review | Admin |
| R-007 | Broker compromised | 2 | 5 | 10 | Key rotation, installation suspension, audit alerts | Security |
| R-008 | Agent performs mass deletion | 2 | 5 | 10 | Delete threshold control, require human approval | Maintainer |

Scoring: probability 1-5 x impact 1-5.
