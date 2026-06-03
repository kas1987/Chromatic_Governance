# Agent Permission Matrix

| Agent | Role | Contents | Issues | PRs | Checks | Actions | Admin | Direct main push |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| repo_scout | Discovery/read-only analysis | read | read | read | none | none | none | no |
| auditor | Governance and risk review | read | write | read | none | read | none | no |
| triage_agent | Issue/task organization | read | write | write | none | none | none | no |
| code_sentinel | Patch creation and PRs | write | write | write | write | read | none | no |
| janitor | Cleanup and formatting | write limited | write | write | none | none | none | no |
| release_agent | Release prep | read | write | write | write | read | none | no |
| human_admin | Owner/maintainer | admin | admin | admin | admin | admin | admin | controlled |

## Notes

- `write limited` means file allow/deny lists must be active.
- `admin` permissions are not granted through the agent broker.
- `Actions: read` lets agents inspect workflow state but not mutate secrets or settings.
