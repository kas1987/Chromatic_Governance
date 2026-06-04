# PDR-002: Chromatic Skill Ecosystem — Technical Foundation

## Status
Draft v1.0

## Date
2026-06-04

## Owner
Kris Sayresmith / Poly-Chromatic

## Supersedes
PDR-001 Phase 0 (skill inventory and governance baseline — complete)

## Reference
`SWOT.md` (full analysis backing this PDR)

---

## Executive Summary

The skill ecosystem is documentation-first and mechanism-second. 118 skills are well-designed and well-governed on paper. The critical gap is that the on-demand loading model exists only as guidance — not as tooling. Without a dynamic serving mechanism, agents load everything at startup or load nothing. Without CI validation, governance degrades silently. Without invocation telemetry, utilization decisions are guesswork. This PDR defines five technical foundations that convert the documented ecosystem into an operating one.

---

## Background

v0.15.0 delivers:
- 118 skills across 13 families
- A 7-tier taxonomy with trigger conditions and anti-overlap rules
- On-demand loading guidance in `AGENT_GUIDE.md`
- Context monitoring via `context-monitor` skill + `context-usage.jsonl`
- Durable memory via `chromatic-memory-registrar`
- Cross-LLM handoffs via `llm-ide-handoff-packager`
- PDR routing via `repo-pdr-swarm-router`

What v0.15.0 does not deliver:
- A mechanism to load skills dynamically (W1)
- A CI check that skills meet the governance standard (W6)
- Automatic telemetry without agent discipline (W3, W4)
- Reconciliation of the parallel Poly-Chromatic operating-skill world (W8)
- Integration between the broker policy engine and plugin family access (W9)

---

## Problem Statement

The ecosystem makes correct recommendations but cannot enforce them. An agent told to "load only what you need" has no technical path to do so mid-session. An agent told to invoke `context-monitor` before loading a third family may simply forget. Skills added without a PDR are undetectable until a human reviews a PR. Usage data — essential for keep/retire/improve decisions — does not exist. Two partially-overlapping skill inventories give agents conflicting trigger maps.

These gaps mean the ecosystem's value is bounded by human discipline rather than by tooling.

---

## Goals

1. Build the MCP skill server so on-demand loading is a tool call, not an aspiration.
2. Wire automatic context telemetry into session lifecycle hooks.
3. Add CI validation so governance compliance is checked on every PR.
4. Fix the `parse_repo_pdr.py` orphan and integrate it into the plugin.
5. Reconcile the two skill worlds so agents have one consistent trigger map.
6. Update all stale documentation to v15.
7. Define the broker × plugin permission mapping so the two governance planes are coherent.

---

## Non-Goals

- This PDR does not redesign the skill taxonomy or family structure.
- This PDR does not publish to a plugin marketplace (that is Phase 5 of PDR-001 roadmap).
- This PDR does not implement context budget forecasting (O9 in SWOT — deferred to PDR-003).
- This PDR does not add bus-factor mitigation or second-operator onboarding (organizational concern, not technical).

---

## Design Decisions

### Decision 1: MCP server as the on-demand loading mechanism

Build a lightweight MCP server (`chromatic-skills-mcp`) that:
- Exposes a `list_skills(family?)` tool returning skill names and descriptions
- Exposes a `get_skill(skill_name)` tool returning full SKILL.md content
- Exposes a `search_skills(query)` tool returning the top 3 matching skills from the taxonomy trigger map

This converts skill loading from a pre-context file read into a tool call. An agent loads only what it needs, exactly when it needs it, and the taxonomy drives discovery rather than the agent guessing family membership.

**Rationale:** Every other mechanism (documentation, AGENT_GUIDE, manual discipline) has failed to achieve true lazy loading. The MCP boundary is the correct technical solution. The `plugin.json` format can remain as a backup for environments where MCP is unavailable.

### Decision 2: Stop hook for passive context telemetry

Add a `Stop` lifecycle hook to the global `settings.json` (or per-session) that writes a `context-usage.jsonl` snapshot entry whenever a session ends. The entry records: timestamp, model, session ID, estimated tokens used, loaded families, and session duration.

**Rationale:** Telemetry that requires agent action will be inconsistently captured. Passive hooks are always-on. This is the minimal viable implementation of session-level context analytics.

### Decision 3: GitHub Actions CI for skill governance validation

Add `.github/workflows/skill-governance.yml` that on every PR touching `.02_Plugins/**`:
1. Runs `validate-scaffold.sh` on all 13 families
2. Checks every SKILL.md for required frontmatter fields (`name`, `description`)
3. Checks for required section headers (Core procedure, Output format, Guardrails)
4. Checks that no two skills share an identical `name` field
5. Fails the PR if any check fails

**Rationale:** Enforcement without tooling is aspiration. CI is the correct gate.

### Decision 4: Reconcile Poly-Chromatic operating skills via a bridge map

Produce a `SKILL_BRIDGE.md` that maps each Poly-Chromatic operating skill to its nearest plugin-family equivalent, states the relationship (equivalent / partial overlap / gap), and documents when to use each. Do not merge or retire operating skills from their existing context — they live in a different system (ChatGPT tools) and serve a different activation mechanism.

**Rationale:** The two systems were built in parallel and are not in conflict — they are in different planes. The confusion is not structural; it is documentation. A bridge map resolves it without a migration.

### Decision 5: Broker × plugin permission mapping

Add a `plugin-access-policy.md` to `.03_Harness Governance/governance/` that maps each broker permission profile to allowed plugin families:

- `read_only` → context-family, data-research-family, docs-family, observability-family
- `issue_triage` → + product-family, agent-governance-family
- `patch_standard` → + rpi, architecture-family, qa-eval-family, release-family, toolchain-family
- `cleanup_limited` → rpi, docs-family, toolchain-family, context-family

**Rationale:** The broker grants action authority; the plugin families grant skill access. Mapping them makes the governance planes coherent without requiring code integration — the policy document is the integration point.

---

## Work Queue

| ID | Priority | Status | Task | Inputs | Output | Stop condition |
|---|---:|---|---|---|---|---|
| FOUND-001 | P0 | done | Integrate `parse_repo_pdr.py` into `agent-governance-family/scripts/` and update router SKILL.md reference | `repo-pdr-swarm-router.zip` extracted scripts | Committed script + updated SKILL.md | Stop if script has undocumented external dependencies |
| FOUND-002 | P0 | done | Update `README.md` and `SCOPE_MATRIX.md` to v15 (118 skills, 5 new skills, new docs) | Current file content | Updated files committed | Stop if scope of changes is unclear |
| FOUND-003 | P1 | ready | Build `chromatic-skills-mcp` server: `list_skills`, `get_skill`, `search_skills` tools | SKILL_TAXONOMY.md; all SKILL.md files; MCP SDK docs | Working MCP server in `.02_Plugins/mcp/` with tests | Stop if MCP SDK API is unclear or unavailable |
| FOUND-004 | P1 | ready | Add `Stop` hook to write context-usage snapshot | `context-monitor` SKILL.md; Claude Code hook docs | `settings.json` hook entry + hook script in `.agents/hooks/` | Stop if hook format is incompatible with current Claude Code version |
| FOUND-005 | P1 | ready | Add `.github/workflows/skill-governance.yml` CI check | `validate-scaffold.sh`; governance standard; all SKILL.md files | Passing CI workflow | Stop if `validate-scaffold.sh` produces false positives |
| FOUND-006 | P1 | ready | Write `SKILL_BRIDGE.md` mapping Poly-Chromatic operating skills to plugin families | `current-skill-inventory.md` from PDR-001; SKILL_TAXONOMY.md | `SKILL_BRIDGE.md` in `.02_Plugins/` | Stop if operating-skill sources are inaccessible |
| FOUND-007 | P2 | ready | Write `plugin-access-policy.md` mapping broker profiles to plugin families | `permission_profiles.yaml`; PLUGIN_INDEX.md | Policy doc in `.03_Harness Governance/governance/` | Stop if profile semantics are ambiguous |
| FOUND-008 | P2 | ready | Add `skill-invocation.jsonl` logging to the MCP server (FOUND-003 dependency) | FOUND-003 output | Invocation log spec + MCP server update | Blocked until FOUND-003 is done |
| FOUND-009 | P2 | ready | Add skill-level `version` field to frontmatter standard and backfill all 118 skills | Governance standard; all SKILL.md files | Updated governance standard + backfilled frontmatter | Stop if automated backfill script produces incorrect diffs |
| FOUND-010 | P3 | ready | Build `search_skills` CLI wrapper (bash or Python) for environments without MCP | SKILL_TAXONOMY.md | `scripts/search-skills.sh` or `scripts/search_skills.py` | Stop if the taxonomy trigger map is insufficient for keyword search |

---

## Phased delivery

### Phase A — Immediate fixes (no new builds, one session)
FOUND-001, FOUND-002. These are corrections to existing work. They should be done before any new features.

### Phase B — Infrastructure (2–3 sessions)
FOUND-003 (MCP server), FOUND-004 (Stop hook), FOUND-005 (CI). These are the three highest-leverage technical investments. Each is independently deliverable.

### Phase B exit criteria
- An agent can call `get_skill("context-monitor")` via MCP and receive full SKILL.md content.
- Every Claude Code session end writes a JSONL snapshot without agent action.
- A PR adding a SKILL.md without required frontmatter fails CI automatically.

### Phase C — Governance coherence (1–2 sessions)
FOUND-006 (bridge map), FOUND-007 (broker × plugin policy). These close the two-world ambiguity and the disconnected governance planes.

### Phase D — Telemetry and polish (ongoing)
FOUND-008 (invocation logging), FOUND-009 (skill versioning), FOUND-010 (CLI search). These improve observability and completeness but do not block operation.

---

## Risks

| Risk | Severity | Mitigation |
|---|---:|---|
| MCP SDK API changes before FOUND-003 is complete | High | Pin the SDK version; build against a stable release |
| Claude Code hook format doesn't support Stop hooks in all environments | Medium | Make the hook optional; document manual fallback |
| CI false positives on validate-scaffold.sh block PRs unfairly | Medium | Audit the script for false positives before wiring to CI; add a bypass label |
| SKILL_BRIDGE.md is ignored if it's just documentation | Low | Link it from AGENT_GUIDE.md and SKILL_TAXONOMY.md so it's in the navigation path |
| FOUND-009 backfill creates 118 noisy commits | Medium | Use a single commit with a bulk-update script; version them as `patch` |
| Two-operator confusion if broker × plugin policy contradicts existing YAML config | Low | Policy doc is additive documentation — it does not modify `permission_profiles.yaml` |

---

## Acceptance criteria

This PDR is complete when:

- [x] `parse_repo_pdr.py` is in `agent-governance-family/scripts/` and the SKILL.md reference is live
- [x] README.md and SCOPE_MATRIX.md say 118 skills and reference v15 additions
- [ ] `chromatic-skills-mcp` server passes: `list_skills()`, `get_skill("context-monitor")`, `search_skills("track token usage")`
- [ ] A session end event writes a well-formed JSONL entry to `.agents/logs/context-usage.jsonl` automatically
- [ ] A PR adding a SKILL.md without `name` frontmatter fails the skill-governance CI check
- [ ] `SKILL_BRIDGE.md` maps all 12 Poly-Chromatic operating skills with relationship and guidance
- [ ] `plugin-access-policy.md` maps all 4 broker profiles to allowed families with rationale
- [ ] All items above are committed, pushed, and referenced from `AGENT_GUIDE.md`

---

## Next action

Phase A (FOUND-001, FOUND-002) is complete as of 2026-06-04. Both corrections are done:
- `parse_repo_pdr.py` integrated (canonical ZIP version, SHA256: `817354BCA5391F18E2148683B27907645BB84307DFF926FF4C60EA7961446DA7`)
- README.md and SCOPE_MATRIX.md already reflected v0.15.0 / 118 skills / 13 families

Open FOUND-003 as a separate session with `llm-ide-handoff-packager` output targeting Claude Code / Python MCP SDK.
