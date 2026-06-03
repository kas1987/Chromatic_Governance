# Source Ranking Model

| Rank | Source type | Default trust | Use case |
|---|---:|---:|---|
| S | Official primary source | Very high | API behavior, release notes, standards, filings |
| A | Primary empirical source | High | Benchmarks, papers, telemetry, incident reports |
| B | Reputable secondary analysis | Medium-high | Context, synthesis, expert interpretation |
| C | Community signal | Medium-low | Common problems, adoption signal, edge cases |
| D | Vendor/marketing source | Low-neutral | Positioning, claimed features, pricing pages |

## Score each source

- Authority: 1-5
- Relevance: 1-5
- Recency: 1-5
- Specificity: 1-5
- Bias risk: low, medium, high
- Actionability: 1-5

## Freshness risk

Mark high freshness risk for software APIs, models, pricing, regulations, security advisories, market share, vendor features, and current role/title claims.
