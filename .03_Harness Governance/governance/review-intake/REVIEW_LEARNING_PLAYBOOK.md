# Review Learning Playbook

## Purpose

Convert repeated reviewer feedback into durable harness rules, tests, docs, and repo standards.

## Learning sources

- `.agents/review-intake/review-findings.jsonl` — all findings to date
- `.agents/review-intake/logs/review-resolution-log.jsonl` — outcomes
- Recurring failed CI checks
- Repeated reviewer comments across PRs
- Blocked findings (confidence too low)

## Learning actions

| Pattern | Action |
|---|---|
| Repeated lint/style issue | Add formatter rule to project config |
| Repeated test failure | Add regression test template |
| Repeated architecture concern | Update `architecture-family` skill or ADR |
| Repeated repo hygiene issue | Update `tree-repo-auditor` rules |
| Repeated vague task | Improve `classify_review_finding.py` VAGUE regex |

## Review cadence

- Weekly during active PR cycles.
- Immediately after a severe collision, failed auto-patch, or security-gated finding.

## Analysis query

```bash
# Most common finding types this week
python -c "
import json, collections
from pathlib import Path
rows = [json.loads(l) for l in Path('.agents/review-intake/review-findings.jsonl').read_text().splitlines() if l.strip()]
types = collections.Counter(r.get('finding_type','?') for r in rows)
print(types.most_common())
"
```
