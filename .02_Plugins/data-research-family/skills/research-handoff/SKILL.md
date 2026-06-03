---
name: research-handoff
description: package completed research into implementation-ready handoff notes for product, architecture, security, QA/eval, docs, release, or RPI agents. use when the user wants research converted into decisions, backlog, requirements, implementation guidance, or next-agent instructions.
---

# Research Handoff

## Mission

Convert evidence into a clean handoff that downstream agents can act on without redoing research.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. Identify the downstream owner or plugin family.
2. State the question researched and final conclusion.
3. Separate evidence, assumptions, decisions, risks, and open questions.
4. Include source list with quality notes.
5. Translate findings into actionable requirements, constraints, tests, docs updates, or design implications.
6. Define what the next agent should not redo.
7. End with acceptance criteria for the next step.

## Guardrails

- Do not bury uncertainty in prose.
- Do not hand off raw source dumps without conclusions.
- Do not instruct downstream agents to change code unless scope and risk are clear.
- Preserve citations and source-quality labels.

## Expected output

- Destination family/agent
- Conclusion
- Evidence summary
- Actionable constraints
- Risks/open questions
- Do-not-redo notes
- Next acceptance criteria

## Reference loading

Load only when useful:

- `../../references/research-handoff-template.md`
- `../../references/evidence-brief-template.md`
- `../../references/change-impact-matrix.md`
