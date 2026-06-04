# Chromatic Review Intake PDR Bundle

This package scaffolds a GitHub review-intake loop for Chromatic Harness.

It converts GitHub PR reviews, review comments, issue comments, and CI/check failures into normalized review findings, then creates confidence-scored Next Work items that agents/subagents can safely pick up.

## Core loop

```text
GitHub Event -> Review Finding -> Confidence Gate -> Next Work Queue -> Agent Dispatch -> Patch -> Validate -> PR Resolution -> Learning Log
```

## Drop-in files

- `.github/workflows/review-intake.yml` - GitHub Action event intake
- `scripts/review_intake.py` - event parser and queue writer
- `scripts/classify_review_finding.py` - finding classifier and confidence scoring
- `scripts/update_next_work_queue.py` - deterministic queue update helper
- `scripts/post_review_resolution.py` - PR resolution comment helper template
- `scripts/lock_pr_branch.py` - file-based PR mutation lock
- `schemas/*.schema.json` - contracts for findings, queue items, dispatches, locks
- `00_PLANNING/*.json*` - seed queue, finding log, state, risk register
- `03_PLAYBOOKS/*.md` - operating playbooks
- `04_HANDOFFS/*.md` - agent mission packets
- `05_DOCS/REVIEW_INTAKE_PDR.md` - main PDR

## Recommended first run

```bash
python scripts/review_intake.py \
  --event-name pull_request_review_comment \
  --event-path sample-event.json \
  --findings 00_PLANNING/review-findings.jsonl \
  --queue 00_PLANNING/next-work.queue.json
```

## Governance stance

Agents do not randomly scrape PRs. GitHub emits events, the harness normalizes them, confidence gates them, and the dispatcher assigns scoped work.
