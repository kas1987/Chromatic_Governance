# SWOT Analysis — Chromatic Skill Ecosystem

**Version:** 0.16.0  
**Date:** 2026-06-16  
**Scope:** Skill taxonomy, plugin families, loading model, governance infrastructure, broker policy engine, PDR process  
**Supersedes:** 0.15.0 (2026-06-04)

> **What changed since v0.15:** PDR-002 (skill-ecosystem technical foundation) landed its core deliverables — an MCP skill server, a wired `Stop` hook for context snapshots, and a CI frontmatter gate — converting three former "aspirational" weaknesses (W1/W2/W3, W6) into working mechanisms. PDR-007 closed the broker test gap: the 23 red `policy_engine` tests are green via self-contained fixtures (56 broker + 208 scripts tests passing). The README skill count was reconciled to 118. Net: the ecosystem is materially stronger on the *implementation* axis. The newly-exposed risk is **governance integrity** — the PDR registry over-claims completion relative to what is verifiably on disk (see W11, T9).

---

## Strengths

### S1 — Clear, governed taxonomy
118 skills are organized into operational tiers with explicit trigger conditions, output contracts, and anti-overlap rules. `SKILL_TAXONOMY.md` lets any agent find the right skill without guessing.

### S2 — On-demand loading is now technically real, not just documented
The on-demand philosophy is no longer aspirational: an MCP skill server (`.02_Plugins/mcp/chromatic_skills_server.py`) exposes `list_skills` / `get_skill` / `search_skills`, so skill content can be fetched as a tool call rather than pre-loaded into context. `AGENT_GUIDE.md` documents the model. (Caveat: this serves skills on demand but does not yet *replace* session-start family loading — see W1.)

### S3 — Strong family isolation
Each of the 13 families has a bounded domain and its own `plugin.json`, agents, hooks, policies, and references. Families compose without stepping on each other.

### S4 — Production-grade, now-verified broker governance
The `.03_Harness Governance` broker has a working YAML-driven policy engine, permission profiles, JSONL audit logging with secret filtering, and CI. As of PDR-007 the test suite is **green and honest**: 56 broker tests (incl. the previously-failing 23 `policy_engine` cases) + 208 scripts tests pass, against self-contained `tests/fixtures/config/` rather than production config. No assertions were weakened to get there. This is the strongest, best-tested part of the repo.

### S5 — PDR-driven development with traceable decisions
Every major design choice has a PDR record with a registry, status workflow, and physical folder lifecycle. The process produces real artifacts (PDR-002's MCP server, PDR-007's test fixes).

### S6 — Cross-LLM portability designed in from the start
`llm-ide-handoff-packager` provides a universal handoff contract with a `handoff_target` field; skills emit structured markdown/YAML consumable by Cursor, Codex, Gemini, GitHub Issues, or local LLMs.

### S7 — Passive context telemetry now exists
`context-monitor` provides threshold-based guidance and — via the now-wired `Stop` hook (`context_snapshot.py` in `.claude/settings.json`) — writes a `context-usage.jsonl` snapshot at session end **automatically**, with no agent action required.

### S8 — Skill governance is now CI-enforced
The formal approval test (7 questions) plus `skill-governance.yml` → `validate_skills.py` gate every PR: a `SKILL.md` missing `name`/`description` frontmatter fails CI. Sprawl prevention is now mechanical, not just policy.

### S9 — Broker↔plugin mapping documented
`plugin-access-policy.md` maps all four broker permission profiles (`read_only`, `issue_triage`, `patch_standard`, `cleanup_limited`) to plugin-family access — the first concrete bridge between the two governance planes (partial; see W9).

---

## Weaknesses

### W1 — On-demand loading still co-exists with eager session-start loading (partial)
The MCP server (S2) serves skills on request, but plugin families listed in `settings.json` are still loaded eagerly at session start. The on-demand path exists but does not yet *displace* the eager path — both run. The win is real but incomplete.

### W2 — ~~MCP boundary aspirational~~ → RESOLVED (PDR-002)
A real MCP skill server now serves SKILL.md content on demand. Retained here only to mark the v0.15 weakness as closed.

### W3 — ~~Context-monitor advisory only~~ → RESOLVED (PDR-002)
The `Stop` hook now writes snapshots automatically. Closed.

### W4 — Skill invocation is still not tracked
`context-usage.jsonl` logs token snapshots but not *which* skills were invoked, in what order, or with what outcome. `skill-agent-utilization-auditor` still depends on a log that isn't being written.

### W5 — `parse_repo_pdr.py` orphan — status unconfirmed
`repo-pdr-swarm-router`'s SKILL.md references `scripts/parse_repo_pdr.py`, historically only present in the extracted zip. Not re-verified in this pass — treat as open until confirmed copied into the family `scripts/`.

### W6 — ~~No CI governance validation~~ → RESOLVED (PDR-002)
`skill-governance.yml` + `validate_skills.py` now gate SKILL.md frontmatter. Closed. (Section-completeness and trigger-uniqueness checks remain a future hardening — see O4.)

### W7 — Source-of-truth drift, reduced but not eliminated
README skill count reconciled to 118 in this pass. `SCOPE_MATRIX.md` and other docs were not re-audited; multiple count/version statements may still disagree until a single generated source-of-truth exists.

### W8 — Two parallel skill worlds still unreconciled
The `chromatic-skill-utilization-roadmap-pdr` operating stack (`project-level-operator`, `cognitive-stack-architect`, `chromatic-systems-auditor`, `queue-dispatcher`, `fusion-computer`) is not in the plugin families and carries a different taxonomy/trigger/output model. An agent that knows both faces conflicting guidance.

### W9 — Broker↔plugin integration documented, not enforced (partial)
`plugin-access-policy.md` (S9) describes the profile→family mapping, but nothing *enforces* it at runtime: an agent can still be granted a broker profile while loading unrelated families, or vice versa. The planes now reference each other on paper but don't gate each other in execution.

### W10 — No skill-level versioning
The ecosystem has a version; individual skills don't. A trigger or output-contract change leaves no changelog trail.

### W11 — PDR registry over-claims completion vs. on-disk reality (NEW — governance integrity)
The 2026-06-16 hygiene sweep verified acceptance criteria against disk and found gaps the registry hides:
- **PDR-004 (review-intake):** registry says `Completed / Phase 5 / 100%`, but only Phases 1–2 are verified, Phase 3 is partially wired (no `review-resolution-log.jsonl`, no end-to-end agent patching), **Phase 4 (learning loop) is entirely unimplemented**, and Phase 5 has no GitHub App/webhook or cross-fork dedup. The `.md` now reflects this honestly; the registry entry was left at 100% (out of sweep scope) — so registry and `.md` now disagree.
- **PDR-002:** registry says 100%, but its own acceptance criterion "referenced from `AGENT_GUIDE.md`" is unmet — `SKILL_BRIDGE.md` and `plugin-access-policy.md` are not linked from `AGENT_GUIDE.md`.

This is the highest-priority weakness in v0.16: completion claims that can't be reproduced from artifacts erode trust in every other "Completed" status. **Reconciled in this PR:** PDR-004 downgraded to `In-Process` / Phase 3 / 45% with a transition documenting the verified vs. unimplemented work (Phases 4–5 deferred to a follow-up PDR), and PDR-002's `AGENT_GUIDE.md` references added so its last criterion is genuinely met. The structural fix (keeping every "Completed" verifiable) remains an ongoing discipline — see O3.

---

## Opportunities

### O1 — Close the eager-load path
Make the MCP server the primary loading mechanism by trimming the eager family list in `settings.json` to a minimal core and resolving the rest on demand. Converts W1 from "partial" to "done" and delivers the real context-budget win.

### O2 — Skill invocation log + analytics
Add `skill-invocation.jsonl` (`{ts, model, session, skill, family, trigger_text, outcome}`) alongside `context-usage.jsonl`; after 30+ entries run `/skill-agent-utilization-auditor` to surface hot/cold/overlapping skills. Closes W4.

### O3 — Reconcile the registry to disk (governance integrity)
Either (a) downgrade PDR-004's registry completion to honest reality and re-scope Phases 4–5 into a follow-up PDR, or (b) if Phases 4–5 were intentionally descoped, record that decision explicitly. Add the two missing `AGENT_GUIDE.md` references to fully close PDR-002. Directly addresses W11/T9.

### O4 — Harden the CI skill gate
Extend `validate_skills.py` beyond frontmatter to required sections (Core procedure, Output format, Guardrails) and trigger-uniqueness against the taxonomy.

### O5 — Skill discovery surface
The MCP `search_skills` tool exists; expose it as a one-line CLI/grep wrapper for non-MCP clients so discovery works everywhere.

### O6 — Reconcile the two skill worlds
Map the roadmap-PDR operating stack to nearest plugin-family equivalents — absorb, retire, or formally bridge with a "when each system applies" document. Closes W8.

### O7 — Confirm/repair `parse_repo_pdr.py`
Verify whether the script is in the family `scripts/`; copy it from the extracted zip and fix the SKILL.md reference if not. Closes W5.

### O8 — Enforce broker × plugin mapping at runtime
Turn `plugin-access-policy.md` from documentation into a check: at load time, validate the loaded family set against the agent's broker profile. Closes W9.

### O9 — Generated single source of truth for counts/versions
Generate skill counts and family lists into README/SCOPE_MATRIX from the taxonomy so they cannot drift. Closes W7 permanently.

### O10 — Marketplace publication
With CI green (S8) and the MCP server live (S2), individual families are closer to marketplace-ready. Gate on W11 resolution first — don't publish over-claimed statuses.

---

## Threats

### T1 — Claude Code plugin format instability
The `plugin.json` schema and family-activation model may change as Claude Code matures; a format change could invalidate all 13 manifests at once. No version pin or compatibility layer.

### T2 — On-demand discipline still partly manual
With W1 only partially closed, the context-saving model still depends on agents preferring the MCP path over eager-loaded families. Under time pressure, agents default to what's already loaded.

### T3 — Sprawl pressure persists despite the gate
CI now blocks malformed SKILL.md (mitigates the old form of this threat), but a well-formed-but-redundant skill still passes. Trigger-uniqueness enforcement (O4) is the remaining gap.

### T4 — Cross-LLM portability gap
Handoff documents are correctly formatted, but Cursor/Codex/Gemini don't natively consume them; portability still depends on copy-paste at the receiving end.

### T5 — Single-operator bus factor
One owner/maintainer, no backup, no documented onboarding for a second maintainer.

### T6 — Two-governance-plane confusion at runtime
The broker (policy engine) and plugin skill governance still don't gate each other in execution (W9); contradictory behavior remains possible.

### T7 — Context-window inflation erodes the value proposition
As context windows grow (1M+ now common), the per-family loading discipline becomes easier to ignore, weakening the incentive to maintain the on-demand pattern.

### T8 — JSONL logs are runtime artifacts, not source-controlled
`.agents/logs/*.jsonl` is gitignored with no cross-machine/session aggregation; analytics stay local and ephemeral until a pipeline exists.

### T9 — False-green completion claims (NEW)
W11 elevated to a threat because it compounds: if "Completed" in the registry doesn't mean "verifiable on disk," then SWOT strengths, PDR closures, and any downstream automation that trusts the registry inherit the inaccuracy. Reconciling registry↔disk (O3) and keeping acceptance criteria verifiable is the structural fix.

---

## Summary matrix

|   | Helpful | Harmful |
|---|---|---|
| **Internal** | S1–S9: governed taxonomy, *verified* broker tests, real MCP server + Stop hook + CI gate, broker↔plugin mapping | W1, W4, W5, W7–W11: partial lazy-load, no invocation log, two skill worlds, mapping not enforced, **registry over-claims completion** |
| **External** | O1–O10: close eager-load, registry reconciliation, harden CI, marketplace | T1–T9: format instability, manual discipline, bus factor, context inflation, **false-green completion** |

---

## Highest-priority actions derived from this SWOT

| Priority | Action | SWOT driver |
|---|---:|---|
| P0 | ~~Reconcile PDR registry to on-disk reality~~ DONE 2026-06-16: PDR-004 downgraded; PDR-002 refs closed. Remaining: re-scope deferred PDR-004 Phases 4–5 into a follow-up PDR | W11, T9, O3 |
| P0 | Close the eager-load path so MCP server is the primary loader | W1, T2, O1 |
| P1 | Confirm/repair `parse_repo_pdr.py` orphan | W5, O7 |
| P1 | Harden CI gate (sections + trigger uniqueness) | T3, O4 |
| P1 | Reconcile the two skill worlds | W8, O6 |
| P1 | Generated single source of truth for counts/versions | W7, O9 |
| P2 | Add skill invocation logging + analytics | W4, O2 |
| P2 | Enforce broker × plugin mapping at runtime | W9, T6, O8 |
| P2 | Add skill-level versioning | W10 |
| P3 | Expose `search_skills` as a non-MCP discovery surface | O5 |
| P3 | Bus-factor mitigation / second-maintainer onboarding | T5 |
