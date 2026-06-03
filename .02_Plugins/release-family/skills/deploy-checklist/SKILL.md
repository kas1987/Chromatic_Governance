---
name: deploy-checklist
description: Build deployment preflight, execution, and post-deploy checklists for apps, services, packages, plugins, or local IDE tooling. Use when preparing deploy commands, smoke tests, environment checks, release gates, owner assignments, or go/no-go checklists.
---

# Deploy Checklist

Create a deployment checklist that reduces missed steps and makes go/no-go status obvious.

## Core procedure

1. Identify target environment, release artifact, deployment method, and owner.
2. Split the checklist into pre-deploy, deploy, post-deploy, and rollback readiness sections.
3. Include concrete checks for build, tests, env vars, secrets, migrations, monitoring, and docs.
4. Mark each item as required, optional, or conditional.
5. Include stop conditions and who can approve exceptions.
6. Keep the checklist operational, not narrative.

## Output structure

Use `references/deploy-checklist-template.md` for formal output. Otherwise provide:

```markdown
## Deploy checklist

### Pre-deploy
- [ ] ...

### Deploy
- [ ] ...

### Post-deploy validation
- [ ] ...

### Rollback readiness
- [ ] ...

### Stop conditions
- ...
```

## Guardrails

- Do not omit rollback readiness for production deployments.
- Do not mark an item complete unless evidence is present.
- If deployment details are unknown, provide a generic checklist and list required missing inputs.
- Include human approval for risky production changes.

## Related references

- `references/deploy-checklist-template.md`
- `references/release-gate-model.md`
