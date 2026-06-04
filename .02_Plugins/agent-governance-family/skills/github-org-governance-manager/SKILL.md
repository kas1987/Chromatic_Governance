---
name: github-org-governance-manager
description: Plan, audit, and standardize GitHub organization and repository governance — including personal-to-org repo transfers, branch protection, rulesets, team permissions, labels, repository settings, secrets review, and post-transfer validation. Use when moving repos into an organization, auditing existing permissions, generating settings checklists, or producing migration runbooks.
---

# GitHub Org Governance Manager

Make GitHub org and repo governance repeatable and safe without guessing at settings or silently mutating permissions.

## Core procedure

1. **Scope the engagement.** Clarify the target: personal account → org migration, permissions audit, settings standardization, or post-transfer validation.
2. **Inventory repos.** List repos in scope with: name, visibility, default branch, active integrations (Actions, webhooks, deploy keys, registry packages, external links), and current protection state.
3. **Identify transfer risks.** For each repo flag: webhooks that will break, secrets or deploy keys that need re-created, package registries linked to the personal account, local remotes that need re-pointed, and GitHub Actions that reference personal PATs.
4. **Generate the governance plan.** Produce checklists for:
   - Org settings (SSO, member permissions, default repo settings, billing)
   - Repo-level settings (visibility, merge strategy, squash/rebase, auto-delete branches)
   - Branch protection / ruleset for each default and release branch
   - Team permissions matrix (who gets what role on which repo)
   - Label standardization
5. **Produce a migration runbook** for each repo being transferred, with ordered steps, validation commands, and rollback notes.
6. **Define post-transfer validation.** Write a verification checklist: webhooks responding, Actions green, deploy keys active, clone URLs correct, package registry linked to org namespace.

## Output format

```markdown
## GitHub Org Governance — [Scope]

### Repo inventory
| Repo | Visibility | Integrations | Transfer risk |
|---|---|---|---|

### Risk register
| Risk | Repo | Severity | Mitigation |
|---|---|---|---|

### Org settings checklist
- [ ] ...

### Branch protection checklist (per repo)
- [ ] ...

### Permission matrix
| Team | Repo | Role | Justification |
|---|---|---|---|

### Migration runbook — [Repo]
1. ...

### Post-transfer validation
- [ ] ...
```

## Guardrails

- Do not transfer, delete, archive, unarchive, or change repository settings without explicit user authorization.
- Prefer planning output and checklists when permissions are uncertain.
- Flag every integration risk before recommending execution.
- Verify target org permissions before listing any action that requires org-owner access.
- Do not guess at GitHub API behavior for org-specific features; mark uncertain items for human confirmation.

## Related references

- `references/delegation-matrix.md`
- `references/authority-model.md`
- `references/escalation-policy.md`
