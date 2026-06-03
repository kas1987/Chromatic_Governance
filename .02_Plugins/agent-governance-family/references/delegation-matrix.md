# Delegation Matrix

| Task type | Primary family / agent | Reviewer | Default authority | Human gate |
|---|---|---|---|---|
| Context compression | context-family | coordinator | Draft/update notes | Conflicting source of truth |
| Security review | security-family | human or architect | Recommend only | Secrets, production, exploit risk |
| QA/eval | qa-eval-family | release or coordinator | Create/execute tests | Changing pass criteria |
| Architecture | architecture-family | human or senior reviewer | Recommend/design | Irreversible migration |
| Release | release-family | human | Prepare checklist | Deploy/publish |
| Tooling | toolchain-family | security if scripts execute | Advisory scripts | Destructive command |
| Observability | observability-family | release or SRE | Analyze/recommend | Production alert changes |
| Docs | docs-family | product or owner | Draft/update docs | Public/legal-sensitive docs |
| Research | data-research-family | product or architect | Read-only findings | External claims used in release |

## Delegation prompt shape

- Mission:
- Allowed scope:
- Denied scope:
- Inputs:
- Expected output:
- Evidence required:
- Stop conditions:
- Reviewer:
