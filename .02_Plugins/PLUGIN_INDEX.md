# Plugin Index

| Plugin | Skills | Primary purpose |
|---|---:|---|
| `rpi` | 16 | Full research, planning, implementation, review, and iteration lifecycle for scoped delivery work. |
| `toolchain-family` | 8 | Infrastructure and authoring utilities: agent workspaces, handoffs, harvesting, repo operations, and LLM/IDE handoff packaging. |
| `context-family` | 9 | Context, memory, decision log, source-of-truth, session handoff, and durable memory registration. |
| `security-family` | 8 | Security, trust-boundary, secrets, prompt-injection, and permission review controls for agentic development. |
| `architecture-family` | 8 | Design governance for architecture, interfaces, module boundaries, ADRs, migrations, and technical debt. |
| `qa-eval-family` | 8 | Testing, acceptance criteria, regression harnesses, LLM/agent evals, golden cases, and failure analysis. |
| `release-family` | 8 | Release planning, changelogs, versioning, rollout, deployment checks, rollback, and post-release monitoring. |
| `observability-family` | 9 | Logs, metrics, tracing, incident summaries, RCA, SLO checks, alert tuning, health reports, and context/token usage monitoring. |
| `agent-governance-family` | 10 | Multi-agent delegation, authority maps, conflict resolution, review chains, parallel planning, escalation, PDR routing, and org governance. |
| `docs-family` | 8 | Documentation operations for README, API docs, runbooks, dev guides, troubleshooting, diagrams, and doc audits. |
| `product-family` | 8 | Requirements, user stories, MVP planning, prioritization, UX critique, and feedback-to-backlog conversion. |
| `data-research-family` | 8 | Evidence gathering, source scans, benchmarks, documentation digests, API change watches, and citation audits. |
| `frontend-family` | 10 | Frontend/UI-UX delivery, asset extraction, CSS/Tailwind/component systems, dashboards, local apps, and 3D assets. |

**Total: 118 skills across 13 families** (v0.15.0)

---

## On-demand loading guidance

**Do not load all families at session start.** Load only what the current task requires. Add families as triggers appear.

### Recommended loading by mission type

| Mission | Load these families |
|---|---|
| Feature delivery | `rpi` + `context-family` |
| Security review or risky tool use | `security-family` + `agent-governance-family` |
| Architecture or API change | `architecture-family` + `qa-eval-family` |
| Release / ship | `release-family` + `qa-eval-family` |
| UI / frontend work | `frontend-family` + `toolchain-family` |
| Multi-agent coordination or PDR routing | `agent-governance-family` + `context-family` |
| Research or evidence gathering | `data-research-family` + `docs-family` |
| Docs update | `docs-family` |
| Observability / incident | `observability-family` |
| Product planning | `product-family` + `data-research-family` |
| Cross-LLM / IDE handoffs | `toolchain-family` + `context-family` |
| GitHub org governance | `agent-governance-family` + `security-family` |
| Context budget / token monitoring | `observability-family` |

### Lazy loading rules

1. Start with the minimum required for the first task step.
2. Add families as the task evolves — do not pre-load "just in case."
3. Monitor context usage with `/context-monitor` before loading a third or subsequent family.
4. Subagents receive only the family or skill they need for their bounded task — not the full ecosystem.
5. When context is `orange` or above, stop loading new families and use `/handoff` or `/context-prune`.

---

## Skill quick-reference

### agent-governance-family
| Skill | Trigger |
|---|---|
| `agent-roster` | Define agent roles and responsibilities |
| `delegate` | Assign work to the right agent or family |
| `conflict-resolve` | Handle multi-agent disputes |
| `review-chain` | Define approval sequences |
| `authority-map` | Clarify decision authority |
| `parallel-plan` | Coordinate concurrent agent work |
| `agent-retrospective` | Post-work team review |
| `escalation` | Escalate when human approval needed |
| `repo-pdr-swarm-router` | Ingest PDR packages and route to agents |
| `github-org-governance-manager` | Plan GitHub org/repo governance and migrations |

### toolchain-family
| Skill | Trigger |
|---|---|
| `handoff` | Session continuation handoff |
| `harvest-insights` | Extract insights from logs |
| `harvest` | Harvest data from repos |
| `plugin` | Create or validate a plugin |
| `status` | Repo status report |
| `system-audit` | System health audit |
| `using-git-worktrees` | Git worktree guidance |
| `llm-ide-handoff-packager` | Convert outputs to Cursor/Codex/Claude/Gemini/Issue handoffs |

### context-family
| Skill | Trigger |
|---|---|
| `context-map` | Audit current project state |
| `context-prune` | Remove stale context |
| `decision-log` | Record decisions with evidence |
| `handoff-pack` | Prepare multi-session handoff |
| `memory-sync` | Sync context into durable files |
| `onboarding-brief` | Quick project onboarding |
| `session-brief` | Compact session summary |
| `source-of-truth-audit` | Verify authoritative sources |
| `chromatic-memory-registrar` | Register durable decisions, state, and changelogs |

### observability-family
| Skill | Trigger |
|---|---|
| `alert-tuning` | Configure alerts |
| `health-report` | System health summaries |
| `incident-brief` | Incident post-mortems |
| `logs-triage` | Log analysis workflow |
| `metrics-review` | Metrics interpretation |
| `root-cause` | Root cause analysis |
| `slo-check` | SLO monitoring |
| `trace-map` | Distributed trace analysis |
| `context-monitor` | Track token/context usage by model and session |

### rpi
`discovery` · `plan` · `crank` · `swarm` · `implement` · `council` · `quick-execute` · `vibe` · `validation` · `pre-mortem` · `post-mortem` · `test` · `review` · `refactor` · `bug-hunt` · `handoff-ready`

### security-family
`dependency-risk` · `hardening-pass` · `permissions-plan` · `prompt-injection-review` · `sandbox-check` · `secrets-audit` · `security-pr` · `threat-model`

### architecture-family
`adr-create` · `architecture-review` · `design-doc` · `interface-contracts` · `module-boundaries` · `migration-plan` · `scalability-review` · `technical-debt-map`

### qa-eval-family
`acceptance-criteria` · `chaos-test` · `coverage-review` · `eval-suite` · `failure-analysis` · `golden-cases` · `regression-harness` · `test-plan`

### release-family
`changelog` · `deploy-checklist` · `migration-check` · `post-release-monitor` · `release-notes` · `release-plan` · `rollback-plan` · `version-bump`

### docs-family
`api-docs` · `dev-guide` · `diagram-plan` · `doc-audit` · `doc-sync` · `readme-refresh` · `runbook` · `troubleshooting`

### product-family
`feedback-loop` · `mvp-plan` · `prioritize` · `requirements` · `roadmap` · `scope-cut` · `user-story` · `ux-critique`

### data-research-family
`api-change-watch` · `benchmark-compare` · `citation-audit` · `docs-digest` · `evidence-brief` · `market-scan` · `research-handoff` · `source-scan`

### frontend-family
`blender-3d-assets` · `component-library` · `css-library` · `external-ui-platforms` · `interactive-gui` · `local-apps` · `quick-dashboard` · `tailwind-system` · `ui-best-practices` · `webpage-asset-extract`
