# Claude Code Plugin Families Scaffold

Generated: 2026-06-03
Polished: 2026-06-03

This repository contains scoped Claude Code plugin-family packs. Each plugin is intended to be loaded only when its scope is relevant, avoiding one giant always-on toolkit.

## Included plugin families

- `rpi` - Full research, planning, implementation, review, and iteration lifecycle for scoped delivery work.
- `toolchain-family` - Infrastructure and authoring utilities for agent workspaces, handoffs, audits, harvesting, and repo operations.
- `context-family` - Context, memory, decision log, source-of-truth, and session handoff controls.
- `security-family` - Security, trust-boundary, secrets, prompt-injection, and permission review controls for agentic development.
- `architecture-family` - Design governance for architecture, interfaces, module boundaries, ADRs, migrations, and technical debt.
- `qa-eval-family` - Testing, acceptance criteria, regression harnesses, LLM/agent evals, golden cases, and failure analysis.
- `release-family` - Release planning, changelogs, versioning, rollout, deployment checks, rollback, and post-release monitoring.
- `observability-family` - Logs, metrics, tracing, incident summaries, RCA, SLO checks, alert tuning, and health reports.
- `agent-governance-family` - Multi-agent delegation, authority maps, conflict resolution, review chains, parallel planning, and escalation policy.
- `docs-family` - Documentation operations for README, API docs, runbooks, dev guides, troubleshooting, diagrams, and doc audits.
- `product-family` - Requirements, user stories, MVP planning, prioritization, UX critique, and feedback-to-backlog conversion.
- `data-research-family` - Evidence gathering, source scans, benchmarks, documentation digests, API change watches, and citation audits.
- `frontend-family` - Frontend/UI-UX delivery, webpage asset extraction, CSS/Tailwind/component systems, dashboards, local apps, external UI platforms, and Blender/3D assets.

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

The v14 pass completes the major scaffold-to-core transition:

- 13 plugin families
- 113 implemented skill entrypoints
- family-level agents, policies, hooks, references, and selected utility scripts
- root scope matrix, plugin index, final PDR, and ecosystem handoff guide

Run validation before installing or distributing:

```bash
./scripts/validate-scaffold.sh .
./toolchain-family/scripts/plugin-structure-audit.sh .
```

## Operating principle

Use the smallest plugin set that covers the mission. Add MCP access only when a scoped plugin genuinely needs external system capability.
