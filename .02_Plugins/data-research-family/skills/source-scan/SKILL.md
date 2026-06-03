---
name: source-scan
description: gather and rank relevant sources for a question, claim, technology choice, market topic, or implementation decision. use when the user asks to find sources, survey evidence, collect references, compare source quality, or prepare research inputs without changing implementation files.
---

# Source Scan

## Mission

Find the strongest available sources and classify them by authority, recency, relevance, and use case.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. Define the research question and decision it supports.
2. List required source types: official docs, papers, standards, filings, benchmarks, reputable analysis, or community signals.
3. Search broadly first, then narrow to authoritative sources.
4. Classify each source as primary, secondary, tertiary, anecdotal, or vendor/marketing.
5. Record publication date, version, author/publisher, and freshness risk.
6. Summarize only what each source directly supports.
7. Produce a ranked source table and a short research gap list.

## Guardrails

- Do not treat vendor claims as neutral evidence.
- Do not use stale sources for current software, pricing, law, security, or API behavior unless marked historical.
- Separate facts from interpretation.
- Do not modify code, config, or product scope unless another family explicitly takes over.

## Expected output

- Research question
- Source ranking
- Source quality notes
- Key supported findings
- Conflicts or gaps
- Recommended next research or handoff

## Reference loading

Load only when useful:

- `../../references/source-ranking-model.md`
- `../../references/research-operating-model.md`
- `../../references/evidence-brief-template.md`
