# PDR Intake Rules

## Artifact Classes
Classify each file as one primary class and optional secondary classes.

Primary classes:
- source-of-truth: canonical project rules, architecture, router, governance, repo tree standard
- requirement: functional or non-functional requirement
- design-record: PDR, ADR, design note, decision memo, architecture narrative
- implementation-target: code file, scaffold, script, config, CI, tests
- queue-source: backlog, checklist, roadmap, issue list, TODO pack
- evidence: logs, test output, screenshots, audit reports, measurements
- memory: learning log, changelog, repo memory, notes
- bridge: Claude, Cursor, Codex, agents, README, prompt, or adapter file
- asset: image, template, sample data, non-reasoning support file
- unknown: insufficient evidence

## Extraction Targets
Extract:
- explicit decisions
- implied decisions
- unresolved questions
- hard constraints
- soft preferences
- agent roles
- tasks
- dependencies
- risks
- acceptance criteria
- stop conditions
- source-of-truth claims
- contradictions

## Intake Discipline
Do not summarize first. Inventory first. A summary without inventory causes governance drift.

Use path evidence for every meaningful finding. When citations are available, cite the file or line. When citations are unavailable, list the path and inspected section.

## PDR Decomposition
Break large PDRs into these sections:
1. purpose and scope
2. repo/system touched
3. decisions already locked
4. proposed work
5. open questions
6. implementation surfaces
7. governance requirements
8. risks and assumptions
9. dispatch candidates
10. validation requirements
