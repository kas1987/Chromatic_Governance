# Plugin Index

| Plugin | Skills | Primary purpose |
|---|---:|---|
| `rpi` | 16 | Full research, planning, implementation, review, and iteration lifecycle for scoped delivery work. |
| `toolchain-family` | 7 | Infrastructure and authoring utilities for agent workspaces, handoffs, audits, harvesting, and repo operations. |
| `context-family` | 8 | Context, memory, decision log, source-of-truth, and session handoff controls. |
| `security-family` | 8 | Security, trust-boundary, secrets, prompt-injection, and permission review controls for agentic development. |
| `architecture-family` | 8 | Design governance for architecture, interfaces, module boundaries, ADRs, migrations, and technical debt. |
| `qa-eval-family` | 8 | Testing, acceptance criteria, regression harnesses, LLM/agent evals, golden cases, and failure analysis. |
| `release-family` | 8 | Release planning, changelogs, versioning, rollout, deployment checks, rollback, and post-release monitoring. |
| `observability-family` | 8 | Logs, metrics, tracing, incident summaries, RCA, SLO checks, alert tuning, and health reports. |
| `agent-governance-family` | 8 | Multi-agent delegation, authority maps, conflict resolution, review chains, parallel planning, and escalation policy. |
| `docs-family` | 8 | Documentation operations for README, API docs, runbooks, dev guides, troubleshooting, diagrams, and doc audits. |
| `product-family` | 8 | Requirements, user stories, MVP planning, prioritization, UX critique, and feedback-to-backlog conversion. |
| `data-research-family` | 8 | Evidence gathering, source scans, benchmarks, documentation digests, API change watches, and citation audits. |
| `frontend-family` | 10 | Frontend/UI-UX delivery, webpage asset extraction, CSS/Tailwind/component systems, dashboards, local apps, external UI platforms, and Blender/3D assets. |

## Family loading guidance

- Load `rpi` for the delivery loop.
- Add `context-family` when continuity, decisions, source-of-truth, or handoff quality matters.
- Add `security-family` before risky tool use, external content ingestion, credentials, or permission-sensitive changes.
- Add `qa-eval-family` before accepting complex behavior, agent workflows, or release candidates.
- Add `architecture-family` before structural changes, migrations, APIs, or module boundary decisions.
- Add `release-family` when shipping, publishing, versioning, or rollback is in scope.
- Add `frontend-family` when the work touches UI, UX, CSS, Tailwind, component systems, dashboards, local apps, external design/UI platforms, or 3D assets.
