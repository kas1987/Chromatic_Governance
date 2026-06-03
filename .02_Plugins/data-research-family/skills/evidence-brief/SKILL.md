---
name: evidence-brief
description: turn collected sources, citations, notes, logs, studies, documents, or search findings into a decision-ready evidence brief. use when the user asks for evidence-based support, cited recommendations, factual grounding, or a compact research summary.
---

# Evidence Brief

## Mission

Convert research into a concise, decision-ready brief with clear evidence quality and uncertainty labels.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. State the decision, claim, or question being supported.
2. Group evidence by theme rather than by source order.
3. Identify strongest facts, weakest assumptions, and direct contradictions.
4. Quantify where possible with absolute numbers and percentages.
5. Rate confidence for each major conclusion.
6. Explain what would change the recommendation.
7. End with next actions and handoff target.

## Guardrails

- Do not overstate confidence.
- Do not hide conflicting evidence.
- Do not cite a source for claims it does not directly support.
- Avoid long quotations; summarize with attribution.

## Expected output

- One-paragraph narrative
- Executive summary with numbers where available
- Evidence table
- Confidence and uncertainty
- Risks and counterpoints
- Recommendation or next action

## Reference loading

Load only when useful:

- `../../references/evidence-brief-template.md`
- `../../references/confidence-scale.md`
- `../../references/citation-quality-rules.md`
