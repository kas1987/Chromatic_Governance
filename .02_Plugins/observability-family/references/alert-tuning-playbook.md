# Alert Tuning Playbook

## Evaluation checklist

1. What user/system risk is the alert meant to detect?
2. Is the alert actionable by the routed owner?
3. Does the alert include enough context for first response?
4. How often did it fire in the review window?
5. How many fires were true positives, false positives, duplicates, or unknown?
6. What real incidents would not have been detected if this alert were disabled?

## Tuning levers

| Lever | Use when |
|---|---|
| Threshold | Alert fires too early/late |
| Window | Signal is too spiky or too slow |
| Dedupe | Repeated alerts describe the same issue |
| Severity | Page level does not match impact |
| Route | Wrong owner receives alert |
| Suppression | Known maintenance/release window causes noise |
| Runbook | Alert fires but responder lacks next steps |

## Paging rule

A page-worthy alert must have: clear user/system risk, owner, runbook or next action, and urgency that cannot wait for business hours.
