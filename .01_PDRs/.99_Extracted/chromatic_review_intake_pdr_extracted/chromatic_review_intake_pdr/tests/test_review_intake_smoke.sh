#!/usr/bin/env bash
set -euo pipefail
TMP_DIR="$(mktemp -d)"
cp -R . "$TMP_DIR/pkg"
cd "$TMP_DIR/pkg"
python scripts/review_intake.py \
  --event-name pull_request_review_comment \
  --event-path tests/sample_pull_request_review_comment_event.json \
  --findings "$TMP_DIR/review-findings.jsonl" \
  --queue "$TMP_DIR/next-work.queue.json" \
  --state "$TMP_DIR/review-intake.state.json"
test -s "$TMP_DIR/review-findings.jsonl"
python -m json.tool "$TMP_DIR/next-work.queue.json" >/dev/null
python -m json.tool "$TMP_DIR/review-intake.state.json" >/dev/null
echo "review intake smoke test passed"
