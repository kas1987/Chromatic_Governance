# Scope Matrix

| Work scope | Recommended plugins | Notes |
|---|---|---|
| New feature | `rpi`, `product-family`, `architecture-family`, `qa-eval-family`, `context-family` | Start with user value and acceptance gates. |
| Small low-risk fix | `rpi`, `qa-eval-family` | Use `quick-execute`, then lightweight validation. |
| Bug fix | `rpi`, `observability-family`, `qa-eval-family` | Start from reproduction and failure analysis. |
| Security review | `security-family`, `architecture-family`, `context-family` | Avoid code modification until risk is understood. |
| Release prep | `release-family`, `qa-eval-family`, `docs-family`, `observability-family` | Require rollback, changelog, deploy checklist, and health signals. |
| Research task | `data-research-family`, `product-family`, `context-family` | Prefer read-only evidence gathering and citation audit. |
| Major refactor | `architecture-family`, `rpi`, `qa-eval-family`, `context-family`, `toolchain-family` | Use worktrees and regression gates. |
| Multi-agent sprint | `agent-governance-family`, `rpi`, `toolchain-family`, `context-family` | Define authority and review chain first. |
| Frontend/UI/UX work | `frontend-family`, `product-family`, `docs-family`, `qa-eval-family` | Use for webpage asset extraction, CSS/Tailwind libraries, dashboards, local GUIs, public UI platforms, and 3D assets. |
| Documentation pass | `docs-family`, `context-family`, `rpi` | Sync docs to actual code and decisions. |
| Incident / production issue | `observability-family`, `release-family`, `rpi`, `security-family` | Triage first, then rollback or patch. |
| Plugin ecosystem maintenance | `toolchain-family`, `docs-family`, `qa-eval-family`, `agent-governance-family` | Audit structure, docs, skill quality, and permissions. |

## Loading rule

Default to 2-4 plugin families per mission. More than 5 loaded families should be treated as a sign that scope needs splitting.
