# SWOT Analysis — Chromatic Skill Ecosystem

**Version:** 0.15.0  
**Date:** 2026-06-04  
**Scope:** Skill taxonomy, plugin families, loading model, governance infrastructure  

---

## Strengths

### S1 — Clear, governed taxonomy
118 skills are organized into 7 operational tiers with explicit trigger conditions, output contracts, and anti-overlap rules. The `SKILL_TAXONOMY.md` makes it straightforward for any agent to find the right skill for a task without guessing.

### S2 — On-demand loading philosophy is architecturally sound
The design principle — load only what the current task requires, add families as triggers appear — is the correct approach for preserving context budget across long sessions and multi-agent work. `AGENT_GUIDE.md` documents the model clearly.

### S3 — Strong family isolation
Each of the 13 families has a clear domain, bounded scope, and its own `plugin.json`, agents, hooks, policies, and references. Families compose without stepping on each other.

### S4 — Production-grade governance infrastructure
The `.03_Harness Governance` broker has a working policy engine with 72 tests at 95% coverage, YAML-driven permission profiles, JSONL audit logging with secret filtering, and a CI workflow. This is the strongest part of the repo.

### S5 — PDR-driven development with traceable decisions
Every major design choice has a PDR record. The skill-utilization-roadmap PDR identified missing skills; those skills are now built. The process works.

### S6 — Cross-LLM portability designed in from the start
`llm-ide-handoff-packager` provides a universal handoff contract with a `handoff_target` field. Skills produce structured markdown/YAML outputs that can be consumed by Cursor, Codex, Gemini, GitHub Issues, or local LLMs.

### S7 — Context monitoring now exists
`context-monitor` provides threshold-based guidance (`green/yellow/orange/red/critical`) and writes JSONL snapshots to `.agents/logs/context-usage.jsonl`, creating a feedback loop for usage patterns.

### S8 — Skill governance standard prevents sprawl
The formal approval test (7 questions before creating a skill) and the requirement for a PDR and trigger map create friction that filters noise.

---

## Weaknesses

### W1 — No actual lazy-loading mechanism (critical)
`PLUGIN_INDEX.md` says "load only what you need" and `AGENT_GUIDE.md` references `/plugin load <family>`, but no such command exists in Claude Code. Plugin families listed in `settings.json` are loaded at session start — all of them, every time. The on-demand model is documented but not enforced or technically implemented.

### W2 — MCP boundary is aspirational, not implemented
The design says "MCP optional for external-system access." There is no MCP server that serves skills on demand. Skills are static SKILL.md files that require the family to already be loaded. There is no dynamic skill discovery or serve-on-request mechanism.

### W3 — Context-monitor is advisory only
`context-monitor` documents thresholds and a JSONL log format, but nothing invokes it automatically. If an agent doesn't call it proactively, there's no protection against context overflow. The hook infrastructure exists (`.claude-plugin/hooks.json`) but no `Stop` hook writes a snapshot at session end.

### W4 — Skill invocation is not tracked
`context-usage.jsonl` logs token snapshots but does not record which skills were invoked, in what order, or with what outcome. The `skill-agent-utilization-auditor` skill is documented but its trigger depends on logs that don't yet exist.

### W5 — `parse_repo_pdr.py` is orphaned
`repo-pdr-swarm-router`'s SKILL.md references `scripts/parse_repo_pdr.py`. That script lives in the extracted zip (`repo-pdr-swarm-router.zip`) but was never copied into the plugin family's `scripts/` directory. The reference in the skill is broken.

### W6 — No CI validation for SKILL.md governance compliance
`validate-scaffold.sh` and `plugin-structure-audit.sh` exist but are not wired into any CI workflow for the `.02_Plugins` directory. Skills can be added that violate the governance standard with no automated detection.

### W7 — README.md and SCOPE_MATRIX.md still say v14 / 113 skills
Neither root document was updated after the v15 additions. The ecosystem has two sources of truth claiming different skill counts.

### W8 — Two parallel skill worlds are not reconciled
The `chromatic-skill-utilization-roadmap-pdr` describes a separate operating stack (`project-level-operator`, `cognitive-stack-architect`, `chromatic-systems-auditor`, `queue-dispatcher`, `fusion-computer`, etc.) that is not in the plugin families. These skills have different taxonomy, trigger maps, and output contracts. An agent that knows both systems faces conflicting guidance.

### W9 — Broker and plugin systems are disconnected
`.03_Harness Governance` controls agent access via a policy engine. `.02_Plugins` controls skill content. There is no integration: an agent could be granted broker access but have no relevant skills loaded, or have skills loaded but be denied by the broker. The two governance planes don't talk.

### W10 — No skill-level versioning
The ecosystem has a version (0.15.0), but individual skills have no version. A skill can be changed without any changelog, making it impossible to know when a breaking change to a trigger or output contract occurred.

---

## Opportunities

### O1 — MCP skill server: the missing loading mechanism
An MCP server that serves SKILL.md content on request would implement the on-demand model technically rather than aspirationally. A client calls `get_skill("context-monitor")` and receives the SKILL.md. Skill loading becomes a tool call, not a pre-context file load. This is the single highest-leverage build.

### O2 — Skill invocation log + analytics
Add a `skill-invocation.jsonl` log alongside `context-usage.jsonl`. Each log entry: `{ts, model, session, skill, family, trigger_text, outcome}`. After 30+ entries, run `/skill-agent-utilization-auditor` to surface which skills are hot, which are cold, which need improvement, and which overlap in practice.

### O3 — Automatic context snapshot on session Stop hook
Wire `context-monitor` into the Claude Code `Stop` hook so every session end writes a context-usage JSONL entry automatically — no agent action required. This gives passive, consistent telemetry without overhead.

### O4 — CI governance validation for skills
A GitHub Actions workflow that runs `validate-scaffold.sh` and checks every SKILL.md for required frontmatter (`name`, `description`), required sections (Core procedure, Output format, Guardrails), and trigger uniqueness against the taxonomy. Blocks PRs that introduce non-compliant skills.

### O5 — Skill discovery tool
A lightweight skill search — given a task description string, return the top 3 matching skills from `SKILL_TAXONOMY.md` by keyword match against trigger conditions. Could be a simple Python script, a bash grep wrapper, or an MCP tool.

### O6 — Reconcile the two skill worlds
Map `project-level-operator`, `cognitive-stack-architect`, `chromatic-systems-auditor`, `queue-dispatcher`, and `fusion-computer` to their nearest plugin-family equivalents (or gaps). Either absorb them as skills, retire them as redundant, or create a formal bridge document explaining when each system applies.

### O7 — Integrate `parse_repo_pdr.py` into the plugin
Copy the script from the extracted zip into `agent-governance-family/scripts/parse_repo_pdr.py` and update the SKILL.md reference. This makes the router skill's optional automation actually available.

### O8 — Broker × plugin integration
Define how the broker's permission profiles map to plugin family access. A `read_only` profile agent should load only read-oriented families. A `patch_standard` agent should be allowed architecture and qa-eval families. This makes the governance planes coherent.

### O9 — Context budget forecasting
Before a session starts, estimate required context from the task description and planned family loads. Output: "this task will use approximately X% of context on model Y — consider Z instead." Prevents surprises before they happen.

### O10 — Publish to the Claude Code plugin marketplace
Once CI validation is green and the MCP server exists, the ecosystem is marketplace-ready. External teams can install individual families rather than the whole scaffold.

---

## Threats

### T1 — Claude Code plugin format instability
The `.claude-plugin/plugin.json` schema and how plugin families are activated is subject to change as Claude Code matures. A format change could invalidate all 13 plugin manifests simultaneously. There is no version pin or compatibility layer.

### T2 — "Load by mission" is unenforceable without tooling
Without W1 fixed (the lazy-loading mechanism), the on-demand model depends entirely on human or agent discipline. Under real time pressure, agents will default to loading everything or guessing, defeating the context savings.

### T3 — Skill sprawl without enforcement
The governance standard requires a PDR before creating a new skill, but nothing enforces this. A contributor can add a SKILL.md directly without review. Without CI validation (O4), the only check is human review of PRs.

### T4 — Cross-LLM portability gap
`llm-ide-handoff-packager` produces handoff documents in the correct format, but Cursor, Codex, and Gemini do not natively consume these files. The portability promise depends on human copy-paste or agent discipline at the receiving end — not on a technical integration.

### T5 — Single-operator bus factor
The ecosystem is owned and maintained by one person. No bus-factor mitigation, no backup owner, no documented onboarding path for a second maintainer. If the operator is unavailable, the system goes stale.

### T6 — Two-governance-plane confusion at runtime
An agent that knows both the broker governance (policy engine) and the plugin skill governance (SKILL.md) has two sets of rules that don't reference each other. This can produce contradictory behavior — the broker approves an action the skill's guardrails block, or vice versa.

### T7 — Context window inflation may erode the value proposition
As model context windows grow (Gemini already at 1M tokens, Claude approaching that range), the careful per-family loading model becomes less critical. Teams may simply load everything and ignore the on-demand guidance, leading to a degraded ecosystem with no incentive to maintain the on-demand pattern.

### T8 — JSONL logs are runtime artifacts, not source-controlled
`.agents/logs/*.jsonl` is gitignored. There is no mechanism to aggregate logs across machines, sessions, or operators. Usage analytics will be local and ephemeral unless an explicit aggregation pipeline is built.

---

## Summary matrix

|   | Helpful | Harmful |
|---|---|---|
| **Internal** | S1–S8: Strong taxonomy, governance, portability design, PDR process | W1–W10: No real lazy-load, no MCP server, orphaned scripts, two skill worlds, no CI |
| **External** | O1–O10: MCP server, analytics, CI gate, skill reconciliation, marketplace | T1–T8: Format instability, unenforceable discipline, bus factor, context inflation |

---

## Highest-priority actions derived from this SWOT

| Priority | Action | SWOT driver |
|---|---:|---|
| P0 | Build the MCP skill server (on-demand loading) | W1, T2, O1 |
| P0 | Fix `parse_repo_pdr.py` orphan in router skill | W5 |
| P1 | Add CI validation for SKILL.md governance | W6, T3, O4 |
| P1 | Add Stop hook for automatic context snapshots | W3, O3 |
| P1 | Update README and SCOPE_MATRIX to v15 | W7 |
| P1 | Reconcile two skill worlds / map Poly-Chromatic skills | W8, O6 |
| P2 | Add skill invocation logging | W4, O2 |
| P2 | Define broker × plugin permission mapping | W9, O8 |
| P2 | Add skill-level versioning | W10 |
| P3 | Skill discovery tool | O5 |
| P3 | Context budget forecasting | O9 |
