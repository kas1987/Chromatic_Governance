# Skill Bridge Map — Poly-Chromatic Operating Skills ↔ Plugin Families

**Version:** 0.15.0  
**Purpose:** Resolve ambiguity for agents that know both the Poly-Chromatic operating-skill stack (used in ChatGPT and cross-LLM contexts) and the Claude Code plugin-family ecosystem. These are two separate activation systems; this document maps their overlaps, gaps, and guidance.

---

## How to read this map

| Column | Meaning |
|---|---|
| **Poly-Chromatic skill** | Skill from the ChatGPT/cross-LLM operating stack |
| **Plugin family equivalent** | Nearest Claude Code plugin-family skill(s) |
| **Relationship** | `exact` · `partial` · `gap` |
| **When to use which** | Guidance on choosing between the two |

---

## Mapping table

### `project-level-operator`
- **Plugin equivalent:** `rpi/discovery` + `product-family/mvp-plan` + `agent-governance-family/parallel-plan`
- **Relationship:** partial
- **Guidance:** `project-level-operator` converts scattered goals into a full project state, queue, and routing plan in one pass. In the plugin ecosystem, use `rpi/discovery` to scope the task, `product-family/mvp-plan` to define objective and cut scope, and `agent-governance-family/parallel-plan` to assign concurrent work. The three together approximate the operating skill's output.

---

### `repo-pdr-swarm-router`
- **Plugin equivalent:** `agent-governance-family/repo-pdr-swarm-router`
- **Relationship:** exact
- **Guidance:** This skill was integrated into `agent-governance-family` in v0.15.0. Use `/repo-pdr-swarm-router` in Claude Code sessions when `agent-governance-family` is loaded. The SKILL.md and the `parse_repo_pdr.py` script are both present. No behavioral difference intended.

---

### `queue-dispatcher`
- **Plugin equivalent:** `agent-governance-family/delegate` + `agent-governance-family/parallel-plan`
- **Relationship:** partial
- **Guidance:** `queue-dispatcher` selects, routes, and operationalizes the next work item from an existing queue. In the plugin ecosystem, `delegate` assigns a known task to the right agent or family, and `parallel-plan` coordinates concurrent dispatch. For queue management and next-item selection logic, use `repo-pdr-swarm-router` upstream to build the queue, then `delegate` to dispatch.

---

### `chromatic-systems-auditor`
- **Plugin equivalent:** `qa-eval-family/failure-analysis` + `observability-family/health-report` + `security-family/threat-model`
- **Relationship:** partial
- **Guidance:** `chromatic-systems-auditor` does cross-system governance review: contradictions, evidence gaps, alignment drift, and risk. In the plugin ecosystem, this audit is split by domain. Use `failure-analysis` for execution issues, `health-report` for system status, and `threat-model` for risk. For contradiction detection specifically (a gap in the plugin families), use `context-family/source-of-truth-audit` as the closest proxy.

---

### `fusion-computer`
- **Plugin equivalent:** `rpi/implement` + `qa-eval-family/eval-suite` + `release-family/deploy-checklist`
- **Relationship:** partial
- **Guidance:** `fusion-computer` is an artifact factory — it produces validated reusable components, templates, manifests, and deployable packages. In the plugin ecosystem, `rpi/implement` drives the build, `eval-suite` validates correctness, and `deploy-checklist` gates deployment. For packaging artifacts specifically, `toolchain-family/harvest` collects and organizes produced outputs.

---

### `repo-tree-architect`
- **Plugin equivalent:** None
- **Relationship:** gap
- **Guidance:** This skill audits and redesigns repo trees, root hygiene, scattered files, and folder structure. No equivalent exists in the plugin families. When working in Claude Code, use `toolchain-family/system-audit` for broad health checks and `docs-family/doc-audit` for documentation structure, but neither covers repo-tree redesign. **Candidate for a new skill in `toolchain-family`** (PDR-003 backlog).

---

### `tree-repo-auditor`
- **Plugin equivalent:** None
- **Relationship:** gap
- **Guidance:** This skill enforces numbered folder and subfolder naming standards. No equivalent in the plugin families. Use `toolchain-family/system-audit` as a partial substitute. **Candidate for a new skill in `toolchain-family`** (PDR-003 backlog).

---

### `skill-agent-utilization-auditor`
- **Plugin equivalent:** `toolchain-family/system-audit`
- **Relationship:** partial
- **Guidance:** `skill-agent-utilization-auditor` audits skill usage patterns, inactive agents, redundant skills, and log analysis. In the plugin ecosystem, `system-audit` covers general health; for usage analytics specifically, use the `context-usage.jsonl` and `skill-invocation.jsonl` logs (see `observability-family/context-monitor`). Full utilization audit is a PDR-002 Phase D item (FOUND-008).

---

### `github-repo-scout`
- **Plugin equivalent:** `data-research-family/source-scan` + `data-research-family/benchmark-compare`
- **Relationship:** partial
- **Guidance:** `github-repo-scout` specifically finds external GitHub repos and templates to evaluate before building. In the plugin ecosystem, `source-scan` finds authoritative sources broadly, and `benchmark-compare` evaluates build-vs-borrow options. For GitHub-specific discovery, combine these with explicit build-vs-borrow framing.

---

### `inventory-matrix-manager`
- **Plugin equivalent:** `context-family/context-map` + `toolchain-family/harvest`
- **Relationship:** partial
- **Guidance:** `inventory-matrix-manager` manages inventories of files, assets, prompts, workflows, models, and registries. In the plugin ecosystem, `context-map` audits the current project state, and `harvest` gathers data from repos. For frontend asset inventory specifically, use `frontend-family/webpage-asset-extract`.

---

### `cognitive-stack-architect`
- **Plugin equivalent:** `product-family/prioritize` + `rpi/discovery`
- **Relationship:** partial
- **Guidance:** `cognitive-stack-architect` organizes scattered nonlinear thinking into structured decisions, priorities, and handoffs — specifically useful when the project is ambiguous or overloaded. In the plugin ecosystem, `rpi/discovery` maps unknowns before planning, and `product-family/prioritize` creates a structured ranking. Neither fully replicates the "triage scattered context" framing. **Candidate for a new skill in `context-family`** (PDR-003 backlog) or `product-family`.

---

### `llm-ide-handoff-packager`
- **Plugin equivalent:** `toolchain-family/llm-ide-handoff-packager`
- **Relationship:** exact
- **Guidance:** Integrated into `toolchain-family` in v0.15.0. Use `/llm-ide-handoff-packager` in Claude Code sessions. Behavior matches the spec from `chromatic-skill-utilization-roadmap-pdr`.

---

### `chromatic-memory-registrar`
- **Plugin equivalent:** `context-family/chromatic-memory-registrar`
- **Relationship:** exact
- **Guidance:** Integrated into `context-family` in v0.15.0. Use `/chromatic-memory-registrar` in Claude Code sessions. Behavior matches the spec.

---

### `github-org-governance-manager`
- **Plugin equivalent:** `agent-governance-family/github-org-governance-manager`
- **Relationship:** exact
- **Guidance:** Integrated into `agent-governance-family` in v0.15.0. Use `/github-org-governance-manager` in Claude Code sessions.

---

## Summary

| Poly-Chromatic skill | Status | Plugin equivalent |
|---|---|---|
| `project-level-operator` | partial | `rpi/discovery` + `product-family/mvp-plan` + `agent-governance/parallel-plan` |
| `repo-pdr-swarm-router` | **exact** | `agent-governance-family/repo-pdr-swarm-router` |
| `queue-dispatcher` | partial | `agent-governance/delegate` + `agent-governance/parallel-plan` |
| `chromatic-systems-auditor` | partial | `qa-eval/failure-analysis` + `observability/health-report` + `security/threat-model` |
| `fusion-computer` | partial | `rpi/implement` + `qa-eval/eval-suite` + `release/deploy-checklist` |
| `repo-tree-architect` | **gap** | None — PDR-003 candidate |
| `tree-repo-auditor` | **gap** | None — PDR-003 candidate |
| `skill-agent-utilization-auditor` | partial | `toolchain/system-audit` |
| `github-repo-scout` | partial | `data-research/source-scan` + `data-research/benchmark-compare` |
| `inventory-matrix-manager` | partial | `context/context-map` + `toolchain/harvest` |
| `cognitive-stack-architect` | partial | `rpi/discovery` + `product/prioritize` — PDR-003 candidate |
| `llm-ide-handoff-packager` | **exact** | `toolchain-family/llm-ide-handoff-packager` |
| `chromatic-memory-registrar` | **exact** | `context-family/chromatic-memory-registrar` |
| `github-org-governance-manager` | **exact** | `agent-governance-family/github-org-governance-manager` |

**4 exact matches · 7 partial matches · 3 gaps**

Gaps (`repo-tree-architect`, `tree-repo-auditor`, `cognitive-stack-architect`) are tracked in PDR-003.
