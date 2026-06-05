# Session Retrospective — Governance Audit, Routing Floor, Front-end Design Lane

**Date:** 2026-06-05
**PRs merged:** Chromatic_Governance #14 (audit), #16 (frontend lane); chromatic-wiki #29 (canonical routing)
**Epics closed:** none bead-tracked — work was ad-hoc audit + remediation

## What shipped

- **Repo/router/PDR/CI audit** (#14): four remediation tracks — router truth-up (wired
  `model-router.sh` as a real PreToolUse:Agent advisory hook with a `--hook` mode),
  file-safety (atomic temp+fsync+replace writes, guarded loads, SQLite WAL+timeout,
  fixed a cp1252 Windows crash), CI hardening (author-association gate on auto-push,
  inputs out of `run:` into `env:`, SHA-pinned actions, `permissions`/`concurrency`/
  `timeout` across 8 workflows), and hook robustness (`py -3` + `$CLAUDE_PROJECT_DIR`
  anchoring; validator derives interpreter from settings).
- **Routing floor raised** (#29 + global config): C1→Haiku (non-code only), **C2→Sonnet**
  (was Haiku — code review/edits need extended thinking), C3→Sonnet, C4→Opus; a
  **code floor** so code-touching work never routes to 3B–14B open models. Applied to
  `~/.claude/CLAUDE.md`, the `feedback-agent-model-routing` memory, the canonical
  `subagent-token-efficiency.md` + `multi-router-matrix.yaml`, then federated.
- **Front-end design lane** (#16): `frontend-experience-architect` agent given
  frontmatter (`model: opus`, `effort: medium`) + a design→impl routing table;
  `frontend-design`/`frontend-visual-triage` intents + `code_floor` in the canonical
  matrix; `visual-design` skill registered (`PLUGIN_INDEX.md` 10→11, `SKILL_TAXONOMY.md`).

## Learnings

### 1. A PreToolUse hook cannot change a subagent's model — only inject advisory context
`model-router.sh` was documented for months as "wired into settings.json to select the
model," but (a) it wasn't in settings.json and (b) the mechanism is impossible — a
PreToolUse hook can allow/deny/annotate, not swap the Agent's model. The fix was to set
`model:` explicitly per C-level on the Agent call and reframe the hook as advisory.
**Action:** never rely on a hook to downgrade/upgrade a subagent model; set `model:` at the call site.

### 2. Hooks wired with cwd-relative paths silently break when a shell's cwd moves
Settings had `python3 .agents/hooks/...`. A `cd` into a subdirectory in one Bash call
made every subsequent hook resolve against the wrong dir and fail (including the safety
guard) — and the failure persisted for the whole session because hook config is loaded
once. **Action:** anchor hook commands to `$CLAUDE_PROJECT_DIR` (cwd-independent), and on
Windows prefer `py -3` over `python3`.

### 3. The Edit tool rewrote a `.sh` file with CRLF, breaking bash
After a large Edit, `model-router.sh` had 218 CRLF pairs → `$'\r': command not found`,
`set: pipefail: invalid option`. **Action:** after editing shell scripts on Windows,
normalize to LF and add `*.sh eol=lf` to `.gitattributes`.

### 4. Edit the canonical governance source, never the federated copy
`federate-governance.sh` does `cp -f canonical → ~/.claude, ~/.agents, harness`. A direct
edit to `~/.claude/governance/subagent-token-efficiency.md` would have been overwritten on
the next federate. **Action:** edit `chromatic-wiki/03_GOVERNANCE/*` first, then federate.

### 5. The canonical routing matrix was never valid YAML — yet consumers tolerated it
`multi-router-matrix.yaml` had a list+key mix under `rudalo_providers` and a `medium:{`
missing-space in `effort_level_routing`. Nothing strict-parsed the whole file, so it went
unnoticed. Strict validation during federation exposed it. **Action:** validate config
with a real parser before propagating; lenient consumers hide structural bugs.

### 6. Stale `GH_TOKEN` env var shadows valid keyring auth
`gh` failed 401 because settings.json's `GH_TOKEN` is expired; clearing the env var
per-call (`export GH_TOKEN=''`) let `gh` fall back to the working keyring login.

### 7. Adding a skill trips two CI gates
A new `SKILL.md` must include validator-required sections (`## Core procedure`,
`## Output format`, `## Guardrails` — regex-matched aliases allowed), and the MCP server
test hard-codes the total skill count (123→124). Both block merge.

## Follow-up

- **Dependabot opened 9 PRs (#4–#12)** to bump the actions just SHA-pinned in #14 — review/group.
- **Stale `GH_TOKEN`** in settings.json — refresh or remove so `gh` stops erroring by default.
- **Harness gen probe-chains** (`code-small-edit`, etc.) still start on local coder models;
  the `code_floor` was applied to the Claude-agent tiers, not the gen `/api/delegate` chains — revisit if those route unreviewed code.
- Pre-existing `in_progress` beads (mc-22w, mc-6a5, mc-a2u …) are harness items, untouched here.
