# PDR - Plugin Design Review

PDR meaning in this pack: Plugin Design Review. Use this before installing, publishing, or giving agents broad access to these plugin families.

## Decision summary

Status: scaffold ready for skill-body implementation.

Decision: use multiple scoped plugin families instead of one universal plugin. Plugins define mission scope; skills define repeatable workflows; agents provide bounded reasoning roles; hooks enforce lifecycle checks; MCP remains optional for external-system access.

## Review checklist

### 1. Structure

- [ ] `.claude-plugin/plugin.json` exists for each plugin.
- [ ] Component directories are at plugin root, not inside `.claude-plugin/`.
- [ ] No empty placeholder directory is required for runtime operation.
- [ ] Paths are relative or use `${CLAUDE_PLUGIN_ROOT}`.
- [ ] No secrets, tokens, `.env`, or machine-specific absolute paths are included.

### 2. Scope discipline

- [ ] Each plugin has a clear mission boundary.
- [ ] No plugin duplicates another plugin's core authority.
- [ ] Skills are not overloaded with unrelated responsibilities.
- [ ] Read-only families stay read-only by default unless explicitly escalated.

### 3. Agent authority

- [ ] Each agent has a narrow description and bounded tool policy.
- [ ] High-risk agents avoid broad write/edit access by default.
- [ ] Multi-agent workflows define a review chain before parallel execution.
- [ ] Worktree isolation is used when concurrent code changes are expected.

### 4. Hooks

- [ ] Hooks are advisory or blocking only where justified.
- [ ] Hook scripts are deterministic, fast, and fail safely.
- [ ] Hooks do not leak secrets or send data externally without explicit config.
- [ ] Hooks that run shell commands are reviewed before enabling.

### 5. MCP boundary

- [ ] MCP servers are not bundled unless the plugin truly needs live external access.
- [ ] MCP credentials are requested via user config, not hardcoded.
- [ ] Plugins remain useful without MCP where possible.

### 6. Quality gates

- [ ] `qa-eval-family` defines acceptance gates before implementation work.
- [ ] `security-family` runs on any plugin that touches commands, hooks, MCP, or external data.
- [ ] `context-family` checks that persistent project context is current and non-contradictory.
- [ ] `release-family` controls deployment, rollback, and post-release monitoring.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Plugin bloat | Agents inherit irrelevant instructions and authority | Load by mission scope only |
| Duplicate skills | Conflicting behavior and confusing triggers | Use `PLUGIN_INDEX.md` and deduplicate during skill-writing |
| Unsafe hooks | Shell commands execute too broadly | Keep hooks minimal; review scripts before enablement |
| MCP overuse | External access expands attack surface | Treat MCP as optional capability, not default |
| Weak context | Agents build from stale assumptions | Use `context-family` as a recurring gate |

## Next work package

1. Fill each placeholder `SKILL.md` with trigger conditions, procedure, inputs, outputs, and guardrails.
2. Replace advisory shell scripts with real checks only where useful.
3. Run `claude plugin validate ./<plugin>` on each plugin.
4. Decide which plugins should be default-enabled versus opt-in.
5. Add marketplace metadata only after the local developer workflow is stable.

---

## PDR Update - Context Family Core v0.2.0

### Status

Completed first real skill implementation pass for `context-family`.

### Implemented

- Replaced placeholder skill procedures for all 8 context-family skills.
- Built 3 deep core skills:
  - `session-brief`
  - `decision-log`
  - `handoff-pack`
- Built 5 support skills:
  - `context-map`
  - `source-of-truth-audit`
  - `context-prune`
  - `memory-sync`
  - `onboarding-brief`
- Added context references:
  - `context-state-schema.md`
  - `session-brief-template.md`
  - `decision-log-template.md`
  - `handoff-template.md`
  - `source-of-truth-rules.md`

### Design decision

Context-family should act as the continuity and source-of-truth control plane for the broader plugin ecosystem. It should be loaded early for multi-agent work, refactors, release preparation, security review, and any workflow likely to span sessions.

### Next recommended family

Build `security-family` next because it establishes permission, threat-model, and prompt-injection guardrails before expanding automation depth.

---

## PDR Update — v3 security core implementation

### Decision
Implemented `security-family` as the next high-leverage plugin family after `context-family`.

### Rationale
Context improves agent continuity; security constrains agent behavior before broader tool, MCP, hook, and automation access expands. This pass establishes least-privilege defaults, prompt-injection handling, secrets hygiene, dependency review, sandboxing, PR review, and hardening patterns.

### Files added / upgraded

- `security-family/skills/threat-model/SKILL.md`
- `security-family/skills/secrets-audit/SKILL.md`
- `security-family/skills/dependency-risk/SKILL.md`
- `security-family/skills/permissions-plan/SKILL.md`
- `security-family/skills/sandbox-check/SKILL.md`
- `security-family/skills/prompt-injection-review/SKILL.md`
- `security-family/skills/security-pr/SKILL.md`
- `security-family/skills/hardening-pass/SKILL.md`
- `security-family/references/security-review-checklist.md`
- `security-family/references/agent-permission-model.md`
- `security-family/references/secrets-patterns.md`
- `security-family/references/prompt-injection-patterns.md`
- `security-family/references/security-risk-register-template.md`
- `security-family/README.md`

### Security posture established

- Deny by default.
- Prefer read-only inspection before writes or execution.
- Require explicit approval for secrets, networked sensitive data, dependency installs, destructive commands, CI/CD changes, and deployment.
- Treat external content as data, not authority.
- Never print full secrets.

### Recommended next family

Build `qa-eval-family` next so implementation and security controls are backed by measurable pass/fail gates.


---

## PDR Update - v4 qa-eval core implementation

### Decision
Implemented `qa-eval-family` as the third high-leverage plugin family after `context-family` and `security-family`.

### Rationale
Context establishes continuity, security establishes boundaries, and QA/eval establishes measurable pass/fail gates. This creates a reliable control loop for agentic development: define scope, constrain risk, test outcomes, and preserve known-good behavior.

### Files added / upgraded

- `qa-eval-family/skills/acceptance-criteria/SKILL.md`
- `qa-eval-family/skills/test-plan/SKILL.md`
- `qa-eval-family/skills/regression-harness/SKILL.md`
- `qa-eval-family/skills/eval-suite/SKILL.md`
- `qa-eval-family/skills/golden-cases/SKILL.md`
- `qa-eval-family/skills/failure-analysis/SKILL.md`
- `qa-eval-family/skills/coverage-review/SKILL.md`
- `qa-eval-family/skills/chaos-test/SKILL.md`
- `qa-eval-family/references/qa-gate-model.md`
- `qa-eval-family/references/test-plan-template.md`
- `qa-eval-family/references/eval-suite-template.md`
- `qa-eval-family/references/regression-harness-template.md`
- `qa-eval-family/references/failure-analysis-template.md`
- `qa-eval-family/references/coverage-review-template.md`
- `qa-eval-family/references/golden-case-schema.md`
- `qa-eval-family/README.md`

### QA posture established

- Use explicit acceptance criteria before implementation when scope is ambiguous.
- Tie tests, evals, and regression harnesses to observable behavior.
- Use risk-based gate levels Q0-Q3.
- Treat LLM/agent behavior as testable through eval cases, golden cases, and failure triage.
- Separate pass, conditional pass, fail, and blocked results.

### Recommended next family

Build `architecture-family` next so larger implementation and refactor work has design governance before deeper toolchain automation.

## PDR Update - v5 architecture core implementation

### Change summary

Implemented `architecture-family` as the fourth high-leverage control layer after context, security, and QA/eval.

### Implemented skills

- `architecture-review`
- `design-doc`
- `adr-create`
- `interface-contracts`
- `module-boundaries`
- `migration-plan`
- `scalability-review`
- `technical-debt-map`

### Added references

- `architecture-family/references/architecture-review-checklist.md`
- `architecture-family/references/design-doc-template.md`
- `architecture-family/references/adr-template.md`
- `architecture-family/references/interface-contract-template.md`
- `architecture-family/references/module-boundary-rules.md`
- `architecture-family/references/migration-plan-template.md`
- `architecture-family/references/technical-debt-scoring.md`

### Design rationale

Architecture-family now acts as the system-design gate between agent intent and implementation. It keeps agents from building quickly into unclear ownership, brittle interfaces, unsafe migrations, circular dependencies, or unbounded technical debt.

### Validation

The scaffold validator was rerun after implementation and passed across all plugin families.

---

## PDR Update — v6 release core implementation

### Decision
Implemented `release-family` as the next control-plane plugin after context, security, QA/eval, and architecture.

### Rationale
The prior families establish continuity, safety, measurable quality, and design control. Release-family turns completed work into controlled shipping decisions by requiring scope clarity, readiness gates, versioning discipline, migration checks, rollback planning, deployment checklists, and post-release monitoring.

### Files added / upgraded

- Replaced placeholder procedures for all 8 release-family skills:
  - `release-plan`
  - `changelog`
  - `version-bump`
  - `release-notes`
  - `migration-check`
  - `rollback-plan`
  - `deploy-checklist`
  - `post-release-monitor`
- Added release references:
  - `release-gate-model.md`
  - `release-plan-template.md`
  - `changelog-format.md`
  - `versioning-policy.md`
  - `release-notes-template.md`
  - `migration-check-template.md`
  - `rollback-plan-template.md`
  - `deploy-checklist-template.md`
  - `post-release-monitor-template.md`
- Updated `release-family/README.md` with operating rules and reference map.

### Governance rule
A release should not be treated as ready simply because implementation is complete. Readiness requires evidence across release scope, tests/evals, security, migration safety, observability, rollback/recovery, and communication.

### Next recommended family
Build `toolchain-family` next to improve repo utilities, status harvesting, handoffs, system audits, worktree usage, and skill authoring now that the major governance layers are in place.

## PDR Update - v7 toolchain core implementation

### Summary

Upgraded `toolchain-family` from placeholder procedures into a usable operational control layer for Claude Code plugin workspaces and IDE agent workflows.

### Implemented skills

- `handoff`
- `status`
- `harvest`
- `harvest-insights`
- `system-audit`
- `using-git-worktrees`
- `writing-skills`

### Added references

- `toolchain-family/references/toolchain-operating-model.md`
- `toolchain-family/references/handoff-template.md`
- `toolchain-family/references/status-report-template.md`
- `toolchain-family/references/harvest-checklist.md`
- `toolchain-family/references/system-audit-checklist.md`
- `toolchain-family/references/git-worktree-playbook.md`
- `toolchain-family/references/skill-authoring-standards.md`

### Added scripts

- `toolchain-family/scripts/repo-status-summary.sh`
- `toolchain-family/scripts/plugin-structure-audit.sh`

### Decision

Toolchain remains an operational layer, not an authority layer. It gathers evidence, audits structure, prepares handoffs, and supports safe worktree workflows. Security, architecture, QA/eval, and release approvals remain owned by their respective families.

### Validation

Scaffold validation and ZIP integrity checks were run after implementation.


## PDR Update - v8 observability core implementation

### Summary

Upgraded `observability-family` from placeholder procedures into a usable operational signal and incident analysis layer.

### Implemented skills

- `logs-triage`
- `metrics-review`
- `trace-map`
- `incident-brief`
- `root-cause`
- `slo-check`
- `alert-tuning`
- `health-report`

### Added references

- `observability-family/references/observability-operating-model.md`
- `observability-family/references/incident-severity-model.md`
- `observability-family/references/log-triage-template.md`
- `observability-family/references/metrics-review-template.md`
- `observability-family/references/incident-brief-template.md`
- `observability-family/references/root-cause-template.md`
- `observability-family/references/slo-review-template.md`
- `observability-family/references/alert-tuning-playbook.md`
- `observability-family/references/health-report-template.md`
- `observability-family/references/trace-map-template.md`
- `observability-family/references/release-health-signals.md`

### Decision

Observability-family is an evidence interpretation layer, not a remediation authority layer. It may diagnose, classify, summarize, and recommend. Release decisions remain with `release-family`; security exposure decisions remain with `security-family`; test/eval gaps remain with `qa-eval-family`; systemic design fixes remain with `architecture-family`.

### Validation

Scaffold validation and ZIP integrity checks were run after implementation.

## PDR Update — v9 agent-governance core implementation

### Scope completed

Upgraded `agent-governance-family` from placeholder scaffold to a usable governance control plane for multi-agent Claude Code / IDE workflows.

### Skills implemented

- `agent-roster`
- `delegate`
- `conflict-resolve`
- `review-chain`
- `authority-map`
- `parallel-plan`
- `agent-retrospective`
- `escalation`

### References added

- `agent-governance-family/references/governance-operating-model.md`
- `agent-governance-family/references/agent-roster-template.md`
- `agent-governance-family/references/delegation-matrix.md`
- `agent-governance-family/references/authority-model.md`
- `agent-governance-family/references/escalation-policy.md`
- `agent-governance-family/references/risk-tier-model.md`
- `agent-governance-family/references/review-chain-template.md`
- `agent-governance-family/references/conflict-resolution-record.md`
- `agent-governance-family/references/decision-rules.md`
- `agent-governance-family/references/parallel-execution-plan.md`
- `agent-governance-family/references/agent-retrospective-template.md`

### Design notes

This family now defines who acts, who reviews, what authority each actor has, how conflicts are resolved, how parallel lanes are bounded, and when humans must be pulled in. It complements `security-family` permissioning and `toolchain-family` operational inspection.

### Validation

Scaffold validation and plugin structure audit should pass after this update.



## PDR Update - v10 docs core implementation

### Scope completed

Upgraded `docs-family` from placeholder scaffold to a usable documentation operations layer for Claude Code / IDE agent workflows.

### Skills implemented

- `readme-refresh`
- `api-docs`
- `runbook`
- `dev-guide`
- `troubleshooting`
- `diagram-plan`
- `doc-audit`
- `doc-sync`

### References added

- `docs-family/references/documentation-operating-model.md`
- `docs-family/references/readme-template.md`
- `docs-family/references/api-docs-template.md`
- `docs-family/references/runbook-template.md`
- `docs-family/references/dev-guide-template.md`
- `docs-family/references/troubleshooting-template.md`
- `docs-family/references/diagram-plan-template.md`
- `docs-family/references/doc-audit-template.md`
- `docs-family/references/doc-sync-checklist.md`
- `docs-family/references/doc-quality-checklist.md`

### Design notes

Docs-family now acts as the durable knowledge publishing layer. It creates, refreshes, audits, and synchronizes documentation while preserving source-of-truth hierarchy and uncertainty labels. It complements `context-family` by turning session truth into maintained project documents, and complements `release-family` by keeping user-facing and operator-facing release documentation accurate.

### Validation

Scaffold validation and plugin structure audit checks were hardened to avoid shell validation stalls, then run with an equivalent Python validation pass. Docs drift quick check and ZIP integrity checks were run after this update.

## PDR Update - v11 product core implementation

### Summary

Implemented the product-family core so the plugin ecosystem now has a durable product/value control layer. This pass turns placeholder product skills into executable planning workflows for user stories, requirements, MVP scope, prioritization, roadmapping, UX critique, and feedback conversion.

### Files added or upgraded

- Implemented all 8 product-family skills:
  - `user-story`
  - `requirements`
  - `scope-cut`
  - `mvp-plan`
  - `prioritize`
  - `roadmap`
  - `ux-critique`
  - `feedback-loop`
- Added product references:
  - `product-operating-model.md`
  - `user-story-template.md`
  - `requirements-template.md`
  - `mvp-template.md`
  - `scope-cut-playbook.md`
  - `prioritization-models.md`
  - `roadmap-template.md`
  - `ux-critique-checklist.md`
  - `feedback-loop-template.md`
  - `product-risk-model.md`
- Updated `product-family/README.md`
- Updated `product-family/policies/policy.md`
- Updated `product-family/agents/product-strategist.md`
- Strengthened `product-family/scripts/product-scope.sh`

### Design rationale

Product-family now prevents agentic development from becoming pure implementation drift. It clarifies who the work is for, what outcome matters, what evidence exists, what should be cut, and what should be sequenced next.

### Recommended next family

Build `data-research-family` next to support evidence gathering, benchmark comparison, source scans, citation audits, and API change watching.

## PDR Update - v12 data-research core implementation

### Summary

Implemented the data-research-family core so the plugin ecosystem now has a durable evidence layer for source scans, evidence briefs, benchmark comparisons, market scans, documentation digestion, API change watching, citation audits, and research handoffs.

### Files added or upgraded

- Implemented all 8 data-research-family skills:
  - `source-scan`
  - `evidence-brief`
  - `benchmark-compare`
  - `market-scan`
  - `docs-digest`
  - `api-change-watch`
  - `citation-audit`
  - `research-handoff`
- Added data-research references:
  - `research-operating-model.md`
  - `source-ranking-model.md`
  - `confidence-scale.md`
  - `citation-quality-rules.md`
  - `evidence-brief-template.md`
  - `benchmark-comparison-template.md`
  - `market-scan-template.md`
  - `docs-digest-template.md`
  - `api-change-watch-template.md`
  - `citation-audit-template.md`
  - `research-handoff-template.md`
  - `change-impact-matrix.md`
- Updated `data-research-family/README.md`
- Updated `data-research-family/policies/policy.md`
- Updated `data-research-family/agents/research-analyst.md`
- Strengthened `data-research-family/scripts/research-scope.sh`

### Design rationale

Data-research-family now protects the system from weak evidence, stale claims, vendor bias, citation laundering, and unbounded research loops. It acts as the upstream evidence supplier for product, architecture, security, QA/eval, docs, release, and RPI workflows.

### Recommended next family

With data-research complete, the remaining major gap is finishing any final placeholder family pass and then running a full ecosystem polish/PDR pass across all plugin families.



## PDR Update - v13 frontend family implementation

Added `frontend-family` as the thirteenth plugin family. This family covers webpage asset extraction, CSS library governance, Tailwind systems, component libraries, UI/UX best practices, quick dashboards, interactive GUI planning, local app patterns, external UI platform selection, and Blender/3D asset pipelines.

### Implemented skills

- `webpage-asset-extract`
- `css-library`
- `tailwind-system`
- `component-library`
- `ui-best-practices`
- `quick-dashboard`
- `interactive-gui`
- `local-apps`
- `external-ui-platforms`
- `blender-3d-assets`

### Added references and scripts

Added frontend operating references, asset extraction playbooks, CSS/Tailwind/component standards, dashboard and GUI platform selection guidance, local app patterns, and Blender/3D asset pipeline rules. Added `asset_inventory.py` for local HTML/CSS asset manifest generation and `frontend-scope-check.sh` for advisory scope checks.


---

# PDR Update - v14 ecosystem polish and RPI completion

## Summary

Completed the full ecosystem polish pass after adding `frontend-family`. This pass found that `rpi` still contained placeholder skill procedures, so the RPI lifecycle family was upgraded into a usable execution core rather than leaving the primary delivery family as an intent marker.

## Changes completed

- Implemented all 16 `rpi` skills:
  - `discovery`
  - `plan`
  - `crank`
  - `swarm`
  - `implement`
  - `council`
  - `quick-execute`
  - `vibe`
  - `validation`
  - `pre-mortem`
  - `post-mortem`
  - `test`
  - `review`
  - `refactor`
  - `bug-hunt`
  - `handoff-ready`
- Added RPI references:
  - `rpi/references/rpi-operating-model.md`
  - `rpi/references/delivery-checklist.md`
  - `rpi/references/review-rubric.md`
- Updated root `README.md` to reflect the actual v14 status rather than earlier placeholder language.
- Normalized `PLUGIN_INDEX.md` so `frontend-family` is included in the main table.
- Expanded `SCOPE_MATRIX.md` with frontend, incident, docs, and ecosystem-maintenance scopes.
- Added `FAMILY_DEPENDENCY_MAP.md`.
- Added `FINAL_HANDOFF.md`.
- Re-ran scaffold validation and plugin-structure audit across all 13 families.

## Final ecosystem status

| Metric | Count |
|---|---:|
| Plugin families | 13 |
| Implemented skill entrypoints | 113 |
| Root ecosystem docs | 6 |
| Major validation scripts | 3 |

## PDR judgement

The scaffold has crossed from placeholder pack to usable operating ecosystem. Next work should be real-world calibration: run 2-3 practical workflows per family, record friction, and tighten the SKILL.md files based on observed behavior.
