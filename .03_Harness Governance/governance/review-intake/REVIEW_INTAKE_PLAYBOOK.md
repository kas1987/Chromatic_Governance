# Review Intake Playbook

## Purpose

Convert GitHub PR review events into normalized, auditable review findings.

## Inputs

- GitHub webhook or GitHub Actions event payload
- Repository full name
- Pull request number, when available
- Review/comment/check metadata

## Outputs

- `.agents/review-intake/review-findings.jsonl`
- `.agents/review-intake/next-work.queue.json`
- `.agents/review-intake/review-intake.state.json`

## Operating loop

```
Receive Event → Normalize → Classify → Score → Dedupe → Queue → Log State
```

## Rules

1. Do not patch code during passive intake.
2. Do not create queue items for successful checks or approved reviews.
3. Every actionable item must get a dedupe key.
4. Low-confidence findings must be blocked or review-required.
5. Security and architecture findings need stronger gates (< 90 → needs-human-decision).

## Stop conditions

- Payload cannot be parsed.
- Repo or PR cannot be identified.
- Finding lacks body/evidence.
- Queue file is malformed.
