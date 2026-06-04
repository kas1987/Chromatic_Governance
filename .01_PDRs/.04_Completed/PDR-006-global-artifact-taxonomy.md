# PDR-006: Global Artifact Taxonomy

## Status
In-Process v1.0 — All acceptance criteria verified 2026-06-04

## Date
2026-06-04

## Owner
Kris Sayresmith / Poly-Chromatic

---

## Executive Summary

The PDR registry tracks PDRs and artifact backlog entries as two flat lists with no relationships between them. As the artifact inventory grows across initiatives, operators and agents have no unified way to understand arrival order, dependencies, complexity, hierarchy, or what to work on next. This PDR defines a typed node/edge taxonomy backed by human-editable JSON and a SQLite query layer.

---

## Problem Statement

- No global sequence: arrival order of artifacts is unrecorded
- No dependency graph: agents cannot determine what is blocked or unblocked
- No hierarchy: companion artifacts, parent/child groupings, and initiative roll-ups are implicit
- No complexity/priority signal: agents have no computed score to rank work
- Duplicate and implementation signals live in `zip_intake.db` but not the main registry
- Two separate flat lists (`pdrs`, `artifact_backlog`) with no cross-references

---

## Files

| File | Purpose |
|------|---------|
| `ARTIFACT_TAXONOMY.json` | Human-editable node registry — source of truth |
| `TAXONOMY_EDGES.json` | Human-editable edge registry — all relationships |
| `taxonomy.db` | SQLite queryable backend — sync target, never edited directly |
| `taxonomy_sync.py` | Sync script: JSON → SQLite, computes `priority_score` and `is_blocked` |

---

## Node Types

| Type | Examples |
|------|---------|
| `initiative` | "Chromatic Harness v2" — top-level grouping, optional stubs |
| `epic` | "Agent Pipeline Foundations" — groups of related PDRs |
| `pdr` | PDR-001 through PDR-006 |
| `artifact` | ZIPs, extracted bundles, spec docs |

### Fields on every node

| Field | Type | Notes |
|-------|------|-------|
| `seq` | int | Global monotonic counter, immutable after assignment |
| `id` | string | Stable ID (PDR-002, ART-HERMES_HARNESS_PIPELINE_SCAFFOLD_V1) |
| `type` | enum | initiative \| epic \| pdr \| artifact |
| `title` | string | Human-readable name |
| `description` | string | One-line summary |
| `version` | string\|null | Explicit version (v1, v14-gold) |
| `stage` | enum | Backlog \| Pre-flight \| In-Process \| Completed \| Reviewed \| Archived |
| `mission_level` | enum\|null | M1 \| M2 \| M3 \| M4 |
| `source` | enum | gpt_drop \| agent_generated \| human_authored \| external |
| `owner` | string | Human owner |
| `assigned_agent_family` | string\|null | Agent family responsible for execution |
| `registered_at` | ISO-8601 | Immutable |
| `updated_at` | ISO-8601 | Updated on any field change |
| `last_activity_at` | ISO-8601 | Updated on stage transitions only |
| `priority_score` | float | Computed — see formula below |
| `is_blocked` | bool | Computed — true if any `depends_on` target is not terminal |
| `duplicate_status` | enum | unique \| possible_redundant \| redundant \| duplicate \| unknown |
| `duplicate_confidence` | int 0–100 | Confidence in duplicate_status |
| `implementation_signal` | enum | not_implemented \| preflight_ready \| in_progress \| implemented \| unknown |
| `related_prs` | string[] | GitHub PR references |
| `related_issues` | string[] | GitHub issue references |
| `tags` | string[] | Free-form labels |
| `notes` | string\|null | Freeform context |

### PDR-only fields
`file_path`, `extracted_path`, `completion_percentage`, `acceptance_criteria[]`

### Artifact-only fields
`artifact_type` (zip \| doc \| schema \| bundle \| extracted), `zip_path`, `extracted_path`, `extraction_status` (not_extracted \| extracted \| failed)

### Initiative/epic-only fields
`target_quarter` (nullable stub, e.g. "Q3-2026")

---

## Edge Types

| Type | Meaning |
|------|---------|
| `depends_on` | from cannot start until to is in a terminal stage |
| `child_of` | from is a structural sub-component of to |
| `rolls_up_to` | from contributes progress toward to (epic/initiative) |
| `supersedes` | from replaces to |
| `companion_of` | peer relationship, no ordering implied |
| `implements` | artifact is the concrete realization of a PDR |

### Edge fields
`id`, `from_id`, `to_id`, `type`, `created_at`, `notes`

---

## Priority Score Formula

```
base          = stage_weight + mission_weight + dependency_bonus + age_bonus
priority_score = base × duplicate_multiplier × (0.2 if is_blocked else 1.0)
```

| Component | Values |
|-----------|--------|
| stage_weight | Pre-flight=40, Backlog=30, In-Process=20, Completed=10, Reviewed/Archived=0 |
| mission_weight | M4=30, M3=20, M2=10, M1=5, null=0 |
| dependency_bonus | no deps or all terminal=20, partial=10, all blocked=0 |
| age_bonus | +1 per 7 days since `registered_at`, cap 10 |
| duplicate_multiplier | unique=1.0, possible_redundant=0.7, redundant=0.3, duplicate=0.1, unknown=1.0 |
| blocked penalty | multiply final score by 0.2 if `is_blocked` |

Terminal stages for dependency resolution: Completed, Reviewed, Archived

---

## SQLite Schema

Two tables: `nodes` (all node fields) and `edges` (all edge fields).

Indexes: `nodes(stage)`, `nodes(type)`, `nodes(mission_level)`, `nodes(priority_score DESC)`,
`edges(from_id)`, `edges(to_id)`, `edges(type)`.

Common queries the schema enables:
- Unblocked Backlog artifacts ordered by priority
- All nodes PDR-X transitively depends on
- All companions/children of a given artifact
- Everything rolled up to an initiative

---

## Acceptance Criteria

- [x] `ARTIFACT_TAXONOMY.json` created with all current PDRs and artifacts (seq 1–11)
- [x] `TAXONOMY_EDGES.json` created with all known relationships
- [x] `taxonomy_sync.py` syncs JSON → SQLite, computes `priority_score` and `is_blocked`
- [x] Query: unblocked Backlog artifacts ordered by `priority_score` returns correct ranking
- [x] Query: transitive dependencies of PDR-005 resolves correctly through the edge graph
- [x] All existing `PDR_REGISTRY.json` entries remain valid (taxonomy is additive, not a replacement)
- [x] `taxonomy_sync.py` run confirms: JSON valid, DB written, top-5 priority printed

---

## Constraints

- `ARTIFACT_TAXONOMY.json` and `TAXONOMY_EDGES.json` are the source of truth — `taxonomy.db` is never edited directly
- `seq` values are immutable after assignment
- `priority_score` and `is_blocked` are always derived — never hand-edited
- `PDR_REGISTRY.json` remains the authoritative PDR pipeline store; the taxonomy is additive
- Initiative/epic hierarchy fields are nullable stubs until a second initiative is defined

---

## Verification Log

### 2026-06-04 — Initial sync verified

**Unblocked Backlog artifacts by priority** (`taxonomy_sync.py --query`):
```
ART-HERMES_HARNESS_PIPELINE_SCAFFOLD_V1    70.0
ART-HERMES_HARNESS_PDR_PACKAGE             70.0
ART-CHROMATIC_SKILL_UTILIZATION_ROADMAP_PDR  60.0
ART-REPO_PDR_SWARM_ROUTER                  60.0
ART-CHROMATIC_MISSION_PACKET_FRAMEWORK_V1  60.0
ART-CLAUDE_PLUGIN_FAMILIES_SCAFFOLD_V14_GOLD  21.0  (redundant×0.3 penalty)
```

**Transitive depends_on for PDR-005** (recursive CTE):
```
PDR-004  depth=1  In-Process  (terminates — PDR-004 has no further depends_on edges)
```

PDR-005 is blocked because PDR-004 is not in a terminal stage. Chain resolves correctly.
