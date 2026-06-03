# Data Research Family

Data-research-family is the evidence layer for Claude Code / IDE agent workflows. It gathers, ranks, digests, audits, and packages evidence so downstream agents can make grounded decisions without bloating implementation context.

## Implemented skills

| Skill | Purpose |
|---|---|
| `source-scan` | Find and rank relevant sources by authority, recency, and decision fit. |
| `evidence-brief` | Convert research into a decision-ready evidence brief with confidence labels. |
| `benchmark-compare` | Compare tools, models, libraries, APIs, or vendors using fit-for-purpose criteria. |
| `market-scan` | Map competitor, vendor, product category, and commercial landscape signals. |
| `docs-digest` | Turn official docs, SDK docs, standards, and changelogs into actionable guidance. |
| `api-change-watch` | Review API, SDK, dependency, model, or platform changes for implementation impact. |
| `citation-audit` | Check whether citations actually support claims and identify weak or stale sources. |
| `research-handoff` | Package research into implementation-ready notes for downstream plugin families. |

## Operating sequence

1. Use `source-scan` to gather and rank sources.
2. Use `docs-digest`, `benchmark-compare`, `market-scan`, or `api-change-watch` for domain-specific analysis.
3. Use `citation-audit` when claims must be verified against sources.
4. Use `evidence-brief` to summarize decision-ready findings.
5. Use `research-handoff` to route conclusions to product, architecture, security, QA/eval, docs, release, or RPI.

## Guardrails

- Preserve a hard boundary between evidence and interpretation.
- Prefer primary sources for technical, legal, financial, medical, security, and current-product claims.
- Mark stale, vendor-biased, anecdotal, or non-comparable evidence.
- Do not modify implementation files by default.
- Do not let research tasks become unbounded browsing; define the decision being supported.
- Hand off executable work to the correct downstream family.

## References

- `references/research-operating-model.md`
- `references/source-ranking-model.md`
- `references/confidence-scale.md`
- `references/citation-quality-rules.md`
- `references/evidence-brief-template.md`
- `references/benchmark-comparison-template.md`
- `references/market-scan-template.md`
- `references/docs-digest-template.md`
- `references/api-change-watch-template.md`
- `references/citation-audit-template.md`
- `references/research-handoff-template.md`
- `references/change-impact-matrix.md`
