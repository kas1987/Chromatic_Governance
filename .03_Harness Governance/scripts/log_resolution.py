#!/usr/bin/env python3
"""
log_resolution.py — Record a review-finding resolution outcome.

Appends a JSONL entry to the resolution log and updates the queue item status.

Usage:
  python log_resolution.py \
    --finding RF-ABC123 --task NW-001 --agent Sentinel \
    --status resolved --summary "Fixed null pointer in process_data()" \
    --validation "pytest tests/test_process.py -v" \
    --files src/process.py
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description="Log a Chromatic review finding resolution.")
    parser.add_argument("--finding", required=True, help="finding_id (RF-...)")
    parser.add_argument("--task", required=True, help="Queue item ID (NW-...)")
    parser.add_argument("--agent", required=True, help="Agent that resolved the finding")
    parser.add_argument(
        "--status",
        choices=["resolved", "blocked", "needs-clarification"],
        default="resolved",
    )
    parser.add_argument("--summary", default="", help="Short description of the change made")
    parser.add_argument("--validation", nargs="*", default=[], help="Validation commands run")
    parser.add_argument("--files", nargs="*", default=[], help="Files changed")
    parser.add_argument("--queue", default=".agents/review-intake/next-work.queue.json")
    parser.add_argument("--log", default=".agents/review-intake/logs/review-resolution-log.jsonl")
    args = parser.parse_args()

    record = {
        "finding_id": args.finding,
        "task_id": args.task,
        "agent": args.agent,
        "status": args.status,
        "summary": args.summary,
        "validation": args.validation,
        "files_changed": args.files,
        "resolved_at": utc_now(),
    }

    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")

    queue_path = Path(args.queue)
    if queue_path.exists() and queue_path.read_text().strip():
        data = json.loads(queue_path.read_text())
        items = data.get("items", [])
        changed = False
        for item in items:
            if item.get("id") == args.task:
                item["status"] = "done" if args.status == "resolved" else args.status
                item["resolved_at"] = record["resolved_at"]
                changed = True
                break
        if changed:
            queue_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
