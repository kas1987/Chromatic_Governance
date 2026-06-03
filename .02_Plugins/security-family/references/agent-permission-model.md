# Agent Permission Model

Use deny-by-default. Grant capabilities only for the current mission.

## Capability classes

| Capability | Meaning | Default |
|---|---|---|
| read-files | inspect repo/project files | allow for scoped paths |
| write-files | modify or create files | require task scope |
| execute-local | run scripts/tests/commands | require sandbox check |
| install-dependencies | add or install packages | require approval |
| network | call external resources | require purpose and source validation |
| secrets | read env vars/tokens/keys | deny unless explicitly needed |
| external-api | use MCP/API actions | scope to exact service/action |
| git-write | commit/branch/tag/push | require approval |
| deploy | release to users/production | require human approval |

## Separation of duties

- Researcher: read-only, may summarize, may recommend.
- Builder: read/write scoped project files, may run tests, no deployment.
- Reviewer: read-only by default, may request changes, should not modify reviewed code unless asked.
- Release manager: may package and validate, deployment requires approval.
- Security reviewer: read-only by default, can propose blocking controls.

## Approval gates

Require explicit human approval for:

- destructive file operations
- credential access
- external network calls with sensitive data
- dependency installation from unknown sources
- CI/CD modification
- deployment or publication
- permission expansion
- running untrusted code
