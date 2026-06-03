# Technical Debt Scoring

Score each debt item from 1 to 5.

## Impact

| Score | Meaning |
|---|---|
| 1 | Annoying but low consequence |
| 2 | Slows occasional work |
| 3 | Repeated friction or moderate defect risk |
| 4 | Blocks important work or creates high defect risk |
| 5 | Security, data, release, or major maintainability risk |

## Effort

| Score | Meaning |
|---|---|
| 1 | Less than 1 hour |
| 2 | Half day |
| 3 | 1-2 days |
| 4 | Several days or cross-module |
| 5 | Multi-stage project or migration |

## Priority rule

Prioritize high impact with low or medium effort first. High impact and high effort items should become design docs or migration plans, not casual cleanup tasks.

## Register format

```markdown
| ID | Debt item | Type | Evidence | Impact | Effort | Priority | Recommended action |
|---|---|---|---:|---:|---:|---|---|
```
