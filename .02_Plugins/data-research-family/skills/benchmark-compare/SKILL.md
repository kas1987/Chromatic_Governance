---
name: benchmark-compare
description: compare tools, models, frameworks, vendors, libraries, databases, APIs, or architectures using benchmark data and qualitative evidence. use when the user asks which option is better, faster, safer, cheaper, more maintainable, or more suitable for a defined context.
---

# Benchmark Compare

## Mission

Compare options using fit-for-purpose criteria rather than generic leaderboard thinking.

## Inputs to collect

- User question, claim, decision, or comparison target
- Required timeframe and freshness requirements
- Required source types or excluded sources
- Decision context and downstream consumer
- Known constraints, versions, geography, platform, or workload
- Existing notes, links, files, or citations

## Procedure

1. Define the decision context and workload.
2. List candidate options and required constraints.
3. Select benchmark dimensions: performance, latency, cost, reliability, security, ecosystem, maintainability, licensing, and integration fit.
4. Separate official benchmarks, third-party benchmarks, user reports, and synthetic tests.
5. Normalize comparisons where possible and flag non-comparable metrics.
6. Score options with explicit weighting.
7. Recommend winner, runner-up, and avoid conditions.

## Guardrails

- Do not rely on a single benchmark.
- Do not compare incompatible versions or workloads without warning.
- Treat synthetic benchmarks as directional only.
- Flag marketing benchmarks and benchmark-gaming risk.

## Expected output

- Decision context
- Candidate table
- Benchmark evidence
- Weighted scorecard
- Tradeoffs
- Recommendation
- Validation plan

## Reference loading

Load only when useful:

- `../../references/benchmark-comparison-template.md`
- `../../references/research-operating-model.md`
- `../../references/confidence-scale.md`
