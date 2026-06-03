---
name: alert-tuning
description: Tune alerts, monitors, thresholds, notification routes, paging rules, noise levels, deduplication, severity labels, and escalation policies. Use when alerts are too noisy, too quiet, missing real incidents, triggering on symptoms without actionability, or need adjustment after incidents, releases, or metric changes.
---

# Alert Tuning

Improve alert usefulness by optimizing for actionability, precision, and coverage.

## Core procedure

1. Identify the alert purpose, owner, signal, threshold, routing, frequency, and recent fire history.
2. Classify the alert as actionable, noisy, stale, duplicate, missing context, or missing owner.
3. Check for false positives, false negatives, alert storms, and alert fatigue risk.
4. Recommend threshold, window, dedupe, severity, route, runbook, and suppression changes.
5. Define validation: what should fire, what should not fire, and what evidence proves improvement.
6. Preserve critical coverage. Do not silence an alert without a replacement detection path.

## Output structure

Use `references/alert-tuning-playbook.md` for formal tuning. Otherwise provide:

```markdown
## Alert tuning recommendation

**Alert:** ...
**Current status:** actionable / noisy / stale / duplicate / missing coverage
**Risk:** low / medium / high

### Current behavior
- ...

### Recommended changes
| Setting | Current | Proposed | Reason |
|---|---|---|---|

### Validation plan
- Should fire when: ...
- Should not fire when: ...
- Review after: ...
```

## Guardrails

- Do not reduce paging for critical user-impacting signals without an escalation alternative.
- Do not tune purely for fewer alerts; tune for better decisions.
- Require runbook or next action for any paging alert.
- Separate notification alerts from page-worthy alerts.

## Related references

- `references/alert-tuning-playbook.md`
- `references/incident-severity-model.md`
- `references/observability-operating-model.md`
