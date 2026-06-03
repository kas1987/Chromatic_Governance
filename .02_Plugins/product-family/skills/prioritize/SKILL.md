---
name: prioritize
description: rank features, bugs, roadmap items, backlog candidates, research findings, or agent tasks using impact, effort, confidence, risk, urgency, and strategic fit. use when deciding what to build first, cut, defer, sequence, or escalate.
---

# Prioritize

## Mission

Turn competing work into a ranked decision with visible tradeoffs and evidence strength.

## Inputs to collect

- List of candidate items
- User/business goals
- Constraints: time, team, budget, release window
- Evidence for each item
- Known effort, uncertainty, dependencies, and risks
- Required scoring model, if the user has one

## Procedure

1. Clarify the decision frame: now, next sprint, release, quarter, or roadmap.
2. Choose a scoring model:
   - RICE for product bets
   - impact/effort for fast triage
   - risk-adjusted priority for technical or safety-heavy work
   - MoSCoW for stakeholder alignment
3. Score each item using explicit assumptions.
4. Penalize hidden dependencies, high uncertainty, and unclear user value.
5. Identify quick wins, strategic bets, chores, and traps.
6. Recommend sequence, not just rank.
7. State what evidence would change the ranking.

## Guardrails

- Do not overfit fake precision. Use ranges when estimates are weak.
- Do not bury risk behind high impact.
- Do not rank items without exposing assumptions.
- Escalate security, compliance, data-loss, or revenue-impacting items when needed.

## Expected output

- Ranked list
- Scoring method
- Score table or concise rationale
- Recommended sequence
- Items to cut/defer
- Assumptions and sensitivity notes

## Reference loading

Load only when useful:

- `../../references/prioritization-models.md`
- `../../references/product-risk-model.md`
