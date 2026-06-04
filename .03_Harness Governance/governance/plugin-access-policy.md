# Plugin Access Policy

**Version:** 1.0  
**Date:** 2026-06-04  
**Owner:** Kris Sayresmith  
**Status:** Active

## Purpose

Map each broker permission profile to the plugin families that agents operating under that profile are authorized to load. This creates coherence between the broker's action-authority layer (`.03_Harness Governance/config/permission_profiles.yaml`) and the skill-content layer (`.02_Plugins/`).

This is a policy document, not enforced code. Agents and orchestrators should consult it when deciding which families to activate for a given session.

---

## Profile → family mapping

### `read_only`

**Broker permissions:** `contents: read`, `issues: read`, `pull_requests: read`, `metadata: read`  
**Intent:** Safe, non-mutating inspection of a repository.

**Allowed plugin families:**
| Family | Reason |
|---|---|
| `context-family` | Understand project state, review source-of-truth, read decision logs |
| `data-research-family` | Evidence gathering, source scans, documentation review |
| `docs-family` | Read and audit documentation; generate read-only reports |
| `observability-family` | Review logs, metrics, health signals; check context budget |

**Not allowed:**
- `rpi` (write-oriented delivery loop)
- `architecture-family`, `qa-eval-family`, `release-family` (imply change decisions)
- `agent-governance-family`, `security-family` (imply authority delegation)
- `toolchain-family`, `frontend-family`, `product-family` (write-capable or mutation-adjacent)

---

### `issue_triage`

**Broker permissions:** `contents: read`, `issues: write`, `pull_requests: write`, `metadata: read`  
**Intent:** Issue and PR triage without file writes. May comment and label.

**Allowed plugin families:**
| Family | Reason |
|---|---|
| `context-family` | Context mapping and session management for triage work |
| `data-research-family` | Research backing for triage decisions |
| `docs-family` | Read docs to support triage; update runbooks |
| `observability-family` | Triage incident reports, log signals, health checks |
| `product-family` | User stories, requirements review, feedback categorization |
| `agent-governance-family` | Delegate triage subtasks; escalate when human needed |

**Not allowed:**
- `rpi`, `architecture-family`, `release-family`, `qa-eval-family`, `security-family` (file-write or high-authority actions)
- `toolchain-family`, `frontend-family` (mutation-capable)

---

### `patch_standard`

**Broker permissions:** `contents: write`, `issues: write`, `pull_requests: write`, `checks: write`, `metadata: read`  
**Intent:** Full branch-and-PR patch workflow. May write files, open PRs, and run checks.

**Allowed plugin families:**
| Family | Reason |
|---|---|
| `rpi` | Full delivery loop — the primary activation for patch work |
| `context-family` | Session continuity, decision logging, handoffs |
| `architecture-family` | ADRs, interface contracts, module boundary decisions |
| `qa-eval-family` | Acceptance criteria, test plans, regression gates |
| `release-family` | Changelogs, deploy checklists, version bumps for the patch |
| `observability-family` | Health checks, post-patch monitoring |
| `security-family` | Security PR review, dependency risk, secrets audit |
| `agent-governance-family` | PDR routing, delegation, review chains |
| `toolchain-family` | Handoffs, harvesting, LLM/IDE handoff packaging |
| `docs-family` | Update documentation to match the patch |
| `data-research-family` | Evidence gathering to support patch decisions |
| `product-family` | Requirements and user stories when scope is uncertain |

**Not allowed:**
- `frontend-family` (unless the patch explicitly involves UI work — add explicitly if needed)

---

### `cleanup_limited`

**Broker permissions:** `contents: write`, `issues: write`, `pull_requests: write`, `metadata: read`  
**Allowed paths:** `docs/**`, `governance/**`, `README.md`, `*.md`  
**Blocked paths:** `.github/workflows/**`, `security/**`, `config/**`, `.env*`, `*.pem`, `*.key`  
**Intent:** Documentation, formatting, and repo hygiene only. No code or config changes.

**Allowed plugin families:**
| Family | Reason |
|---|---|
| `rpi` | `quick-execute` and `handoff-ready` for bounded cleanup tasks |
| `docs-family` | Core activation — README refresh, doc sync, runbooks |
| `toolchain-family` | Status checks, handoffs, system-audit |
| `context-family` | Memory registration after cleanup, session continuity |
| `agent-governance-family` | Delegation within cleanup scope; escalation when path is blocked |

**Not allowed:**
- `architecture-family`, `qa-eval-family`, `release-family`, `security-family` (out of cleanup scope)
- `frontend-family`, `product-family`, `data-research-family` (not relevant to hygiene tasks)

---

## Cross-profile rules

1. **A profile boundary is not a recommendation — it is a constraint.** Agents must not load families outside their allowed list even if the task seems to warrant it. Escalate to a higher-authority profile via the broker instead.
2. **`observability-family` is allowed in all profiles** because context monitoring (`context-monitor`) is a safety mechanism, not a capability expansion.
3. **`context-family` is allowed in all profiles** because memory registration, session handoffs, and source-of-truth audits are continuity tools, not action-authority tools.
4. **`agent-governance-family` escalation skills** (`escalation`, `authority-map`) are available in any profile to facilitate reaching human approval when an action exceeds profile scope.
5. **Adding families beyond this policy** requires a broker permission escalation (new profile or explicit task authorization), not agent self-authorization.

---

## Relationship to `permission_profiles.yaml`

This document is an additive governance layer. It does not modify `permission_profiles.yaml` or the broker's runtime logic. The authoritative source for action permissions remains `config/permission_profiles.yaml`. This document maps those action permissions to skill-content permissions so agents operate coherently within both governance planes.

When `permission_profiles.yaml` is updated, this document should be reviewed for consistency.
