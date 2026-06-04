# Claude Code Plugin Families Scaffold

Generated: 2026-06-03  
Updated: 2026-06-04 (v0.15.0)

This repository contains scoped Claude Code plugin-family packs. Each plugin is intended to be loaded only when its scope is relevant, avoiding one giant always-on toolkit.

## Included plugin families

- `rpi` — Full research, planning, implementation, review, and iteration lifecycle for scoped delivery work. (16 skills)
- `toolchain-family` — Infrastructure and authoring utilities: agent workspaces, handoffs, harvesting, repo operations, and LLM/IDE handoff packaging. (8 skills)
- `context-family` — Context, memory, decision log, source-of-truth, session handoff, and durable memory registration. (9 skills)
- `security-family` — Security, trust-boundary, secrets, prompt-injection, and permission review controls. (8 skills)
- `architecture-family` — Design governance for architecture, interfaces, module boundaries, ADRs, migrations, and technical debt. (8 skills)
- `qa-eval-family` — Testing, acceptance criteria, regression harnesses, LLM/agent evals, golden cases, and failure analysis. (8 skills)
- `release-family` — Release planning, changelogs, versioning, rollout, deployment checks, rollback, and post-release monitoring. (8 skills)
- `observability-family` — Logs, metrics, tracing, incidents, RCA, SLO checks, alert tuning, health reports, and context/token usage monitoring. (9 skills)
- `agent-governance-family` — Multi-agent delegation, authority maps, conflict resolution, review chains, PDR routing, and org governance. (10 skills)
- `docs-family` — Documentation operations for README, API docs, runbooks, dev guides, troubleshooting, diagrams, and audits. (8 skills)
- `product-family` — Requirements, user stories, MVP planning, prioritization, UX critique, and feedback-to-backlog conversion. (8 skills)
- `data-research-family` — Evidence gathering, source scans, benchmarks, documentation digests, API change watches, and citation audits. (8 skills)
- `frontend-family` — Frontend/UI-UX delivery, asset extraction, CSS/Tailwind/component systems, dashboards, local apps, and 3D assets. (10 skills)

## Structure rule

Each plugin keeps metadata in `.claude-plugin/plugin.json` and places components at plugin root level:

```text
plugin-name/
  .claude-plugin/plugin.json
  README.md
  LICENSE
  skills/<skill-name>/SKILL.md
  agents/<agent-name>.md
  hooks/hooks.json
  scripts/*
  policies/*.md
  references/*.md
```

## Suggested use

- Feature build: `rpi`, `architecture-family`, `qa-eval-family`, `context-family`
- Security review: `security-family`, `architecture-family`, `context-family`
- Release prep: `release-family`, `qa-eval-family`, `docs-family`, `observability-family`
- Multi-agent sprint: `agent-governance-family`, `rpi`, `toolchain-family`, `context-family`
- Frontend/UI build: `frontend-family`, `product-family`, `qa-eval-family`, `docs-family`
- Research task: `data-research-family`, `product-family`, `context-family`

## Current status

v0.15.0 — PDR skill integration + technical foundation:

- 13 plugin families
- **118 implemented skill entrypoints** (+5 from PDR zips)
- New: `repo-pdr-swarm-router`, `github-org-governance-manager`, `llm-ide-handoff-packager`, `chromatic-memory-registrar`, `context-monitor`
- New governance docs: `SKILL_TAXONOMY.md`, `AGENT_GUIDE.md`, `SWOT.md`
- Active PDR: `PDR-002-skill-ecosystem-technical-foundation.md` (MCP server, CI governance, telemetry)
- Context usage log: `.agents/logs/context-usage.jsonl`

See `PLUGIN_INDEX.md` for the full on-demand loading guide and skill quick-reference.

Run validation before installing or distributing:

```bash
./scripts/validate-scaffold.sh .
./toolchain-family/scripts/plugin-structure-audit.sh .
```

## Operating principle

Use the smallest plugin set that covers the mission. Add MCP access only when a scoped plugin genuinely needs external system capability.
