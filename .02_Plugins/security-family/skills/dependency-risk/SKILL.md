---
name: dependency-risk
description: Review dependency additions, upgrades, lockfile changes, package scripts, licenses, and supply-chain exposure for projects or plugins. Use when the user asks whether a library is safe, when dependencies changed, before installing packages, before release, or when generated code introduces new third-party packages.
---

# Dependency Risk

Assess whether dependencies increase security, license, maintenance, or operational risk.

## Core procedure

1. Identify changed manifests and lockfiles: `package.json`, `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Cargo.toml`, `go.mod`, Dockerfiles, GitHub Actions, and plugin configs.
2. List new, removed, and upgraded dependencies.
3. Check high-risk indicators: install/postinstall scripts, broad permissions, network access, native binaries, typosquatting, low maintainer activity, unknown publisher, unpinned versions, and transitive bloat.
4. Classify dependency purpose: runtime, dev, build, test, optional, or unused.
5. Review license compatibility when the project may be distributed.
6. Recommend actions: pin versions, replace package, vendor minimal code, isolate in sandbox, add scanning, or defer.

## Output format

```markdown
## Dependency risk review

**Scope:** ...
**Overall risk:** low / medium / high

### Dependency changes
| Package | Change | Purpose | Risk | Reason | Recommendation |
|---|---|---|---|---|---|

### Supply-chain controls
- ...

### Decision
Proceed / proceed with controls / block until resolved
```

## Guardrails

- Do not install or upgrade dependencies without explicit user approval.
- Treat install scripts and native binaries as elevated risk.
- If current package reputation or vulnerability status matters, use current authoritative sources before making factual claims.
- Do not rely on memory for recent CVEs or package status.

## Related references

- `references/security-review-checklist.md`
