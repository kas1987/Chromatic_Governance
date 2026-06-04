# Chromatic Router Map

## Routing Precedence
1. User-specified router
2. Project-specific router file
3. Repo governance file
4. Chromatic default router below
5. Assistant inference, clearly marked as inferred

## Default Agent Roles

### sentinel
Owns implementation safety: code review, test gaps, CI, security, failure modes, regression risk.

### auditor
Owns governance: evidence, contradiction tracking, acceptance gates, policy adherence, audit reports.

### chainbreaker
Owns unblock logic: ambiguous specs, circular dependencies, brittle plans, missing decisions, sequencing failures.

### quartermaster
Owns inventory: manifests, assets, dependencies, package completeness, environment readiness.

### cartographer
Owns repo structure: tree maps, numbered folder standards, root hygiene, file placement, architectural maps.

### financier
Owns cost/control: token budget, cloud spend, build-versus-borrow analysis, resource allocation, waste reduction.

### archivist
Owns memory: changelogs, decision registers, repo learning logs, versioning, handoff persistence.

### janitor
Owns cleanup: duplicate removal, stale files, naming repair, scattered file reduction, hygiene tasks.

## Conflict Routing
- contradiction in requirements: auditor
- missing source file or dependency: quartermaster
- repo tree placement issue: cartographer
- implementation defect risk: sentinel
- blocked sequencing: chainbreaker
- runaway cost/scope: financier
- lost context or stale memory: archivist
- clutter or duplicated artifacts: janitor
