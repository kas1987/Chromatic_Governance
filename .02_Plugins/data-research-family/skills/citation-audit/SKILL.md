---
name: citation-audit
description: audit claims, citations, references, footnotes, source links, evidence tables, or generated research for factual support and citation quality. use when the user asks to verify sources, check whether citations support claims, clean up references, or identify unsupported claims.
---

# Citation Audit

## Mission

Verify that claims are supported by the cited sources and that source quality is adequate.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. Extract each claim that needs support.
2. Map each claim to its cited source or mark uncited.
3. Check whether the source directly supports, partially supports, contradicts, or does not address the claim.
4. Assess source quality, date, authority, and conflict of interest.
5. Flag citation laundering, stale sources, broken links, and overbroad claims.
6. Propose corrected wording or stronger source needs.
7. Produce an audit table and unresolved issue list.

## Guardrails

- Do not validate a claim just because a citation exists.
- Do not use a source outside its scope.
- Do not silently fix unsupported claims; mark the change needed.
- For high-stakes topics, require primary or authoritative sources where possible.

## Expected output

- Claim inventory
- Citation support status
- Quality findings
- Unsupported/overstated claims
- Suggested fixes
- Source gaps

## Reference loading

Load only when useful:

- `../../references/citation-audit-template.md`
- `../../references/citation-quality-rules.md`
- `../../references/source-ranking-model.md`
