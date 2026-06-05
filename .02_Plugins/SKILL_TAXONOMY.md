# Chromatic Skill Taxonomy

**Version:** 0.16.0  
**Skills:** 123 across 13 families  
**Governance standard:** One skill, one primary trigger, one output contract.

---

## Taxonomy tiers

Skills are organized into four tiers by operational role.

### Tier 0 — Lifecycle orchestration
The full delivery loop. Load when you have a scoped task and need structured phases.

| Skill | Family | Primary trigger |
|---|---|---|
| `discovery` | rpi | "Research and plan this before we build" |
| `plan` | rpi | "Create a detailed execution plan" |
| `crank` | rpi | "Implement this in focused waves" |
| `swarm` | rpi | "Coordinate parallel execution across agents" |
| `implement` | rpi | "Build this feature or fix" |
| `council` | rpi | "We need a structured decision ceremony" |
| `quick-execute` | rpi | "Small task, skip full planning overhead" |
| `vibe` | rpi | "Validate quality mid-flight" |
| `validation` | rpi | "Post-implementation verification" |
| `pre-mortem` | rpi | "Identify risks before we start" |
| `post-mortem` | rpi | "Extract learnings after we finish" |
| `test` | rpi | "Drive from tests first" |
| `review` | rpi | "Code review gate" |
| `refactor` | rpi | "Structured refactoring" |
| `bug-hunt` | rpi | "Systematic defect detection" |
| `handoff-ready` | rpi | "Prepare for handoff to another agent or session" |

---

### Tier 1 — Routing and orchestration
Route work, govern agents, manage authority, and convert PDRs into executable queues.

| Skill | Family | Primary trigger |
|---|---|---|
| `repo-pdr-swarm-router` | agent-governance | "Here is a PDR/audit bundle — route it to agents" |
| `delegate` | agent-governance | "Assign this work to the right agent" |
| `parallel-plan` | agent-governance | "Coordinate concurrent agent work" |
| `review-chain` | agent-governance | "Define the approval sequence" |
| `authority-map` | agent-governance | "Clarify who decides what" |
| `agent-roster` | agent-governance | "Define agent roles for this project" |
| `conflict-resolve` | agent-governance | "Two agents disagree — resolve it" |
| `agent-retrospective` | agent-governance | "Post-work team review" |
| `escalation` | agent-governance | "This needs human approval" |
| `llm-ide-handoff-packager` | toolchain | "Convert outputs to Cursor/Codex/Claude/Gemini/Issue handoffs" |

---

### Tier 2 — Governance and safety
Apply before risky operations, structural changes, or permission-sensitive actions.

| Skill | Family | Primary trigger |
|---|---|---|
| `github-org-governance-manager` | agent-governance | "Plan/audit GitHub org/repo governance or migration" |
| `threat-model` | security | "Model threats for this system or change" |
| `security-pr` | security | "Security-focused PR review" |
| `permissions-plan` | security | "Design least-privilege permissions" |
| `secrets-audit` | security | "Audit secrets management" |
| `hardening-pass` | security | "Apply security hardening checklist" |
| `sandbox-check` | security | "Verify sandbox isolation" |
| `prompt-injection-review` | security | "Review prompt injection risks" |
| `dependency-risk` | security | "Audit dependency security" |
| `adr-create` | architecture | "Record an architecture decision" |
| `architecture-review` | architecture | "Gate review for a design or change" |
| `design-doc` | architecture | "Produce a system design document" |
| `interface-contracts` | architecture | "Define API or interface contracts" |
| `module-boundaries` | architecture | "Set module ownership rules" |
| `migration-plan` | architecture | "Plan a safe refactoring or migration" |
| `scalability-review` | architecture | "Assess performance at scale" |
| `technical-debt-map` | architecture | "Inventory and prioritize technical debt" |

---

### Tier 3 — Quality, testing, and evaluation
Apply before accepting behavior, agent outputs, or release candidates.

| Skill | Family | Primary trigger |
|---|---|---|
| `test-plan` | qa-eval | "Plan the test approach" |
| `acceptance-criteria` | qa-eval | "Define acceptance gates" |
| `regression-harness` | qa-eval | "Set up regression testing" |
| `eval-suite` | qa-eval | "Build LLM or agent evaluation suite" |
| `golden-cases` | qa-eval | "Capture known-good behavior examples" |
| `coverage-review` | qa-eval | "Analyze test coverage gaps" |
| `failure-analysis` | qa-eval | "Triage a failure" |
| `chaos-test` | qa-eval | "Chaos engineering" |

---

### Tier 4 — Release and operations
Apply when shipping, monitoring, or responding to incidents.

| Skill | Family | Primary trigger |
|---|---|---|
| `release-plan` | release | "Plan the release scope and sequence" |
| `deploy-checklist` | release | "Pre-deployment verification" |
| `changelog` | release | "Generate a changelog" |
| `release-notes` | release | "Author release notes" |
| `version-bump` | release | "Bump semantic version" |
| `migration-check` | release | "Migration safety gate" |
| `rollback-plan` | release | "Write rollback runbook" |
| `post-release-monitor` | release | "Monitor after release" |
| `health-report` | observability | "System health summary" |
| `logs-triage` | observability | "Analyze logs" |
| `metrics-review` | observability | "Interpret metrics" |
| `trace-map` | observability | "Map distributed traces" |
| `alert-tuning` | observability | "Configure alerts" |
| `slo-check` | observability | "Check SLO compliance" |
| `root-cause` | observability | "Root cause analysis" |
| `incident-brief` | observability | "Post-incident summary" |
| `context-monitor` | observability | "Track token/context usage; decide when to prune or hand off" |

---

### Tier 5 — Context, memory, and continuity
Apply to preserve state, prevent context loss, and enable clean session hand-offs.

| Skill | Family | Primary trigger |
|---|---|---|
| `chromatic-memory-registrar` | context | "Save durable decisions, project state, and changelogs after major events" |
| `cognitive-stack-architect` | context | "Too many threads; triage scattered thinking into a prioritised decision stack" |
| `memory-sync` | context | "Sync context into durable repo files" |
| `decision-log` | context | "Record decisions with evidence" |
| `source-of-truth-audit` | context | "Verify authoritative sources" |
| `handoff-pack` | context | "Prepare a multi-session handoff pack" |
| `context-map` | context | "Audit current project state" |
| `context-prune` | context | "Remove stale context from the session" |
| `session-brief` | context | "Compact summary of the current session" |
| `onboarding-brief` | context | "Quick onboarding for a new agent or contributor" |
| `handoff` | toolchain | "Create structured handoff for session continuation" |

---

### Tier 6 — Research, docs, product, and frontend
Load on demand when the task domain is clear.

| Skill | Family | Primary trigger |
|---|---|---|
| `source-scan` | data-research | "Find authoritative sources" |
| `evidence-brief` | data-research | "Compile supporting evidence" |
| `docs-digest` | data-research | "Summarize documentation" |
| `benchmark-compare` | data-research | "Compare products or approaches" |
| `api-change-watch` | data-research | "Track API updates" |
| `market-scan` | data-research | "Market opportunity research" |
| `citation-audit` | data-research | "Verify evidence quality" |
| `research-handoff` | data-research | "Package research findings" |
| `readme-refresh` | docs | "Update README" |
| `api-docs` | docs | "Generate API documentation" |
| `dev-guide` | docs | "Write developer guide" |
| `runbook` | docs | "Write operational runbook" |
| `troubleshooting` | docs | "Write troubleshooting guide" |
| `doc-audit` | docs | "Check documentation completeness" |
| `doc-sync` | docs | "Sync docs with code" |
| `diagram-plan` | docs | "Plan architecture diagrams" |
| `requirements` | product | "Gather requirements" |
| `user-story` | product | "Write user stories" |
| `mvp-plan` | product | "Define MVP scope" |
| `roadmap` | product | "Build product roadmap" |
| `prioritize` | product | "Prioritize features" |
| `scope-cut` | product | "Manage scope boundaries" |
| `feedback-loop` | product | "Convert feedback to backlog" |
| `ux-critique` | product | "UX review" |
| `component-library` | frontend | "Build component system" |
| `css-library` | frontend | "CSS architecture" |
| `tailwind-system` | frontend | "Tailwind configuration" |
| `ui-best-practices` | frontend | "UI/UX standards review" |
| `quick-dashboard` | frontend | "Scaffold a dashboard" |
| `interactive-gui` | frontend | "Interactive GUI planning" |
| `visual-design` | frontend | "Interactive visual design / live preview" |
| `local-apps` | frontend | "Local app patterns" |
| `external-ui-platforms` | frontend | "UI platform selection" |
| `webpage-asset-extract` | frontend | "Local asset inventory" |
| `blender-3d-assets` | frontend | "3D asset pipelines" |

---

### Tier 7 — Toolchain utilities
Support tools used during any tier. Load individually as needed.

| Skill | Family | Primary trigger |
|---|---|---|
| `repo-tree-architect` | toolchain | "Audit and redesign repo folder structure and root hygiene" |
| `status` | toolchain | "Repo status report" |
| `system-audit` | toolchain | "System health audit" |
| `harvest` | toolchain | "Harvest data from repos" |
| `harvest-insights` | toolchain | "Extract insights from logs" |
| `plugin` | toolchain | "Create or validate a plugin" |
| `tree-repo-auditor` | toolchain | "Enforce numbered folder naming standards" |
| `using-git-worktrees` | toolchain | "Git worktree guidance" |
| `writing-skills` | toolchain | "Skill authoring support" |

---

## Anti-overlap rules

| Do not confuse | These are distinct |
|---|---|
| `repo-pdr-swarm-router` vs `delegate` | Router decomposes PDR packages into work; delegate assigns a known task to an agent |
| `chromatic-memory-registrar` vs `memory-sync` | Registrar records durable project state after events; memory-sync syncs specific facts into repo files |
| `context-monitor` vs `context-prune` | Monitor reports usage and recommends action; prune removes stale content from the session |
| `handoff` vs `handoff-pack` | `handoff` (toolchain) is for session continuation; `handoff-pack` (context) is for multi-session or multi-agent packages |
| `llm-ide-handoff-packager` vs `handoff` | Packager converts governed work items into target-specific execution formats; handoff captures session state |
| `health-report` vs `context-monitor` | Health report covers system/service health; context-monitor covers token and context window usage |
| `github-org-governance-manager` vs `permissions-plan` | Org manager handles GitHub org/repo governance; permissions-plan designs least-privilege at code level |

---

## Skill governance rules

1. One skill, one primary trigger. Do not create a skill that covers two unrelated domains.
2. Every skill must produce a structured output with an explicit output contract.
3. Skills compose through files, queues, PDRs, and handoffs — not hidden shared state.
4. Add a reference or template to an existing skill before creating a new one.
5. Require a PDR and trigger map before adding a new skill to this taxonomy.
6. Review this taxonomy monthly or after major milestones using `skill-agent-utilization-auditor`.
