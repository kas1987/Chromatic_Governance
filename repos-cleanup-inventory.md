# C:\Repos Cleanup Inventory

**Date:** 2026-06-03  
**Purpose:** Decide what to mine, archive, or ignore before removing local clones from the laptop.  
**Rule:** Do not delete anything with dirty git state, missing remote, local secrets, or unclear backup status until it is explicitly backed up or exported.

**2026-06-03 update:** User reported deleting `kas1987` and item 1. Current filesystem check confirms `C:\Repos\kas1987` and `C:\Repos\DarkFactory` are gone, but `C:\Repos\3D_Meta` is still visible from this session and should be rechecked before counting the space recovered.

---

## Summary

| Path | Size MB | Git state | Recommendation | Why |
|---|---:|---|---|---|
| `C:\Repos\3D_Meta` | 1519.9 | clean, remote present | User says deleted; recheck | Still visible in the latest tool check, despite user report. If it remains, it is low relevance to routing governance. |
| `C:\Repos\9router` | 1093.8 | clean, remote present | Mined; safe to delete local clone | Useful routing reference for provider executors, fallback tiers, request translation, quota tracking. Key patterns are captured in `cross-provider-model-routing.md`. |
| `C:\Repos\agentops` | 66.5 | dirty, remote present | Archive local additions before deleting | Untracked files are small and useful: setup doctor, env loader, DarkFactory retro, Howie+ design pattern. |
| `C:\Repos\claude-octopus` | 33.5 | clean, remote present | Mined; safe to delete local clone | Useful multi-provider council, consensus-gate, and workflow reference. Key patterns captured below. |
| `C:\Repos\Consolidated` | 14427.5 | not a git repo | Split child-by-child before deleting | Largest disk target; contains archived/canonical project folders, including Prism and OpenClaw. |
| `C:\Repos\DarkFactory` | 39.2 | deleted | No further action | Earlier check found `.env` with `OPENAI_API_KEY`; latest filesystem check confirms folder is gone. |
| `C:\Repos\fusion-computer` | 1.3 | clean, remote present | Keep or archive carefully | Canonical template and standards repo for autonomy systems. |
| `C:\Repos\kas1987` | 574.2 | deleted | No further action | User deleted it; latest filesystem check confirms it is gone. |
| `C:\Repos\oh-my-pi` | 347.8 | clean, remote present | Mined; safe to delete local clone | Strong reference for agent tool surfaces, LSP/DAP integration, edit reliability, memory, subagents, and review UX. Key patterns captured below. |
| `C:\Repos\Poly-Chromatic` | 2018.9 | dirty, remote present | Do not delete yet | Organization meta repo with dirty nested repos: `chromatic-inbox-harness` and `prism-autonomy-harness`. |
| `C:\Repos\Understand-Anything` | 540.7 | clean, remote present | Mined; safe to delete local clone | Useful reference for knowledge graphs, onboarding maps, diff impact, and codebase understanding UX. Key patterns captured below. |

---

## One-by-One Notes

### 1. `C:\Repos\3D_Meta`

- Appears to be the source-of-truth repository for the MetaChromatic 3D visual system.
- Status file says `ACTIVE_NICHE`, Tier 5, active development.
- Relevance to current governance/routing work: low.
- Deletion posture: user reported deleting item 1, but `Test-Path C:\Repos\3D_Meta` still returned true in this session. Recheck after Explorer/terminal refresh; if it remains, it can be removed only if the remote and any large assets are backed up.

### 2. `C:\Repos\9router`

- Local AI API proxy and dashboard with provider executors, fallback tiers, token saving, quota tracking, and API-shape translation.
- Relevance to current governance/routing work: indirect but useful.
- Mined into `cross-provider-model-routing.md` as an external reference.
- Concrete patterns captured:
  - `BaseExecutor` separation of `buildUrl`, `buildHeaders`, `transformRequest`, `refreshCredentials`, retry, and fallback URL walking.
  - `getExecutor(provider)` registry with specialized executors plus default fallback.
  - OpenAI-compatible and Anthropic-compatible endpoint/header normalization.
  - Provider-specific credential metadata such as `providerSpecificData.baseUrl`, account IDs, and local host resolution.
  - RTK-style token saving before provider format translation, especially for bulky `tool_result` content.
  - Subscription to cheap to free fallback tiers and quota tracking as an accounting pattern, not as governance policy.
- Deletion posture: safe to delete the local clone after confirming no new uncommitted files; it is remote-backed and the useful patterns have been captured.

### 3. `C:\Repos\agentops`

- Agent workflow, context orchestration, multi-model validation, hooks, and knowledge flywheel system.
- Relevance to governance work: high for workflow patterns, validation gates, and session lifecycle ideas.
- Dirty state:
  - `agentops-doctor.sh`
  - `agentops-env.sh`
  - `docs/retros/`
  - `patterns/`
- Untracked content reviewed:
  - `agentops-doctor.sh` checks local Node/npm/Go/ao availability, AgentOps hooks, and skill inventory.
  - `agentops-env.sh` loads NVM, local Go paths, and `AO_SOURCE_DIR` defaults for AgentOps sessions.
  - `docs/retros/2026-02-24-dark-factory.md` records the Dark Factory learning database retro.
  - `patterns/design/howie-plus.md` captures the validated Howie+ visual design pattern from Dark Factory.
- Deletion posture: archive or commit those four local additions before deleting the clone. After that, the remote-backed clone itself is replaceable.

### 4. `C:\Repos\claude-octopus`

- Multi-provider Claude-native orchestration with consensus gates, provider-aware workflows, and council/debate patterns.
- Relevance to governance work: high as a reference for multi-model review and escalation patterns.
- Mined patterns to keep:
  - Use a four-phase lifecycle for serious work: Discover, Define, Develop, Deliver.
  - Treat multi-model consensus as a gate that surfaces disagreement, not an automatic override of minority views.
  - Fail loud when provider dispatch or provider preflight fails; do not silently degrade to one model while claiming multi-model validation.
  - Show provider participation/cost context before or during multi-provider runs so users know which external systems were used.
  - Keep provider addition opt-in; ordinary work can stay Claude/native, while higher-stakes work escalates to councils, debate, review, or security flows.
  - Track provider health and command availability with setup/doctor checks.
- Deletion posture: mined enough for local cleanup; remote-backed fork exists.

### 5. `C:\Repos\Consolidated`

- Not a git repo; contains multiple project/archive folders.
- Largest disk consumer in `C:\Repos`.
- Child-by-child classification:
  - `.07_Job` — 5723.5 MB, git repo with no remote configured, has `.beads/dolt-server.lock`; do not delete until backed up/exported.
  - `.02_Mod` — 5251.4 MB, clean git repo with GitHub remote `kas1987/Mod`; likely delete-safe if remote and large assets are confirmed sufficient.
  - `OpenClaw` — 1543.4 MB, clean external clone with upstream remote; can be deleted locally after mining any needed security/channel-routing notes.
  - `.04_Prism` — 1284.3 MB, dirty repo with GitHub remote and many agent-observability/monitoring changes; do not delete until local changes are backed up or committed.
  - `.00_Command Center` — 271.4 MB, clean repo with GitHub remote; likely delete-safe after confirming `.venv` can be regenerated.
  - `.01_Image Org` — 249.7 MB, clean repo but remote is local path `C:\.01_Image Org`; do not delete until that local-path remote is verified as the canonical copy.
  - `001_SaaS` — 93.1 MB, clean repo with GitHub remote, but contains `.env`, `.env.production`, DB files, and API/secret-key settings; export secrets/data before deletion.
  - `.03_MC_Newsletter` — 10.7 MB, clean repo with GitHub remote; likely delete-safe.
- Deletion posture: not safe as one bulk delete target.

### 6. `C:\Repos\DarkFactory`

- Small Node/Express/OpenAI/SQLite prototype with local HTML surfaces and Playwright artifacts.
- Earlier check found `.env` with key name `OPENAI_API_KEY` and no configured remote.
- Latest filesystem check reports `C:\Repos\DarkFactory` no longer exists.
- Relevance to governance work: low unless it contains unique dark-factory workflow prototypes.
- Deletion posture: deleted by user; no further local action available from this path.

### 7. `C:\Repos\fusion-computer`

- Canonical template and standards repository for local-first autonomy systems.
- Status says `ACTIVE` and canonical; role is artifact factory, manifest standards, validation, and handoff templates.
- Relevance to governance work: high for standards, templates, and reusable scaffolds.
- Deletion posture: keep or archive carefully; do not treat as disposable.

### 8. `C:\Repos\kas1987`

- Non-git container folder with nested `3D_Meta` and `fusion-computer` mirrors.
- Relevance to governance work: likely duplicate storage.
- Deletion posture: deleted by user; latest filesystem check confirms the folder is gone.

### 9. `C:\Repos\oh-my-pi`

- Agent tool surface with IDE wiring, LSP/DAP, strong edit tools, subagents, review, memory, and internal URL schemes.
- Relevance to governance/harness work: high as a reference for tool-surface design and agent ergonomics.
- Mined patterns to keep:
  - Treat LSP and DAP as first-class agent tools, especially rename, references, diagnostics, code actions, breakpoints, stack frames, and variable inspection.
  - Prefer edit tools with content anchors, hash/stale-file checks, preview/accept flows, and measured first-attempt edit success.
  - Keep read/search/browser/GitHub/PR/issue surfaces filesystem-shaped where possible so the model learns one interface.
  - Use typed subagent outputs and schema validation instead of parsing freeform prose from worker agents.
  - Hide rarely used tools but keep them searchable/discoverable by intent when needed.
  - Track provider quality with benchmarks and per-model prompt tuning before adding models to default routes.
  - Preserve project memory as scoped facts rather than dumping every session into global context.
- Deletion posture: mined enough for local cleanup; remote-backed upstream exists.

### 10. `C:\Repos\Poly-Chromatic`

- Organization-level repo containing multiple Chromatic projects and nested repos.
- Dirty state:
  - top-level reports `chromatic-inbox-harness` modified and `prism-autonomy-harness` modified
  - nested `chromatic-inbox-harness` has untracked `10_RUNTIME/`
  - nested `prism-autonomy-harness` has deleted GitHub workflows, modified queue/bridge/registry/docs, and many untracked automation/runtime files
- Relevance to governance work: high, but broad and risky to delete.
- Deletion posture: do not delete until nested dirty state is resolved and backed up.

### 11. `C:\Repos\Understand-Anything`

- Codebase and knowledge-base graphing plugin with interactive dashboard, guided tours, domain graph, diff impact, and onboarding views.
- Relevance to governance work: useful for codebase maps, impact analysis, and onboarding documentation patterns.
- Mined patterns to keep:
  - Generate durable `.understand-anything/knowledge-graph.json` style artifacts so teammates can reuse analysis without rerunning the full pipeline.
  - Keep intermediate analysis on disk rather than in chat context; make it disposable and excluded from commits unless explicitly needed.
  - Combine deterministic static parsing with LLM summaries, tags, architectural layers, business-domain mapping, and guided tours.
  - Support incremental updates from changed-file fingerprints instead of rebuilding every graph from scratch.
  - Include diff impact analysis so code review can see likely affected domains before merge.
  - Design graphs to teach, not impress: structural graph, domain view, semantic search, guided tours, and persona-adaptive detail.
  - Keep dashboard/core boundaries browser-safe through subpath exports or equivalent module boundaries.
- Deletion posture: mined enough for local cleanup; remote-backed upstream exists.

---

## Loose Files

| Path | Recommendation |
|---|---|
| `C:\Repos\tmp_cc_triage.ps1` | Archive with Command-Center triage reports or delete after confirming reports are saved elsewhere. |
| `C:\Repos\cc_issues_pages.json` | Generated GitHub issue export; archive with reports or delete if regenerated output exists. |

---

## Deletion Order

1. Recheck `3D_Meta`; user reported deleting it, but it is still visible from this session's filesystem check.
2. Delete `9router` locally if desired; the useful routing patterns have been mined and it is remote-backed.
3. Delete other clean external clones if desired: `claude-octopus`, `oh-my-pi`, `Understand-Anything`; the useful patterns have now been mined.
4. Archive/commit `agentops` local additions, then the clone can be removed if desired.
5. Do not delete `Poly-Chromatic` until nested dirty repos are backed up or committed.
6. Handle `Consolidated` child-by-child: likely delete-safe children are `.02_Mod`, `.00_Command Center`, `.03_MC_Newsletter`, and `OpenClaw`; backup-first children are `.07_Job`, `.04_Prism`, `.01_Image Org`, and `001_SaaS`.
7. `DarkFactory` is already gone; if its secrets were real, rotate the `OPENAI_API_KEY` that was present there.
