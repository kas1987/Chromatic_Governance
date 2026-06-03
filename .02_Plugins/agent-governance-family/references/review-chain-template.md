# Review Chain Template

| Stage | Reviewer | Evidence required | Pass criteria | Fail action | Human approval trigger |
|---|---|---|---|---|---|
| implementation | implementation reviewer | diff, tests run | scope matched, tests pass | return to owner | broad refactor beyond scope |
| security | security reviewer | risk notes, secrets check | no unacceptable risk | block or mitigate | secrets/prod/security exposure |
| QA/eval | QA reviewer | test output, eval cases | acceptance criteria pass | add/fix tests | pass criteria changed |
| release | release reviewer | changelog, rollback, deploy checklist | release gate passes | hold release | publish/deploy |

## Review rules

- The implementer cannot be the sole approver for high or critical risk work.
- Review evidence must include actual validation status, not intent to validate later.
