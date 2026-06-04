#!/usr/bin/env python3
"""
dispatch_queue.py — Pick ready items from the Chromatic Next Work Queue
and emit agent mission packets.

Usage:
  python dispatch_queue.py                    # dispatch all ready items
  python dispatch_queue.py --dry-run          # preview without mutating
  python dispatch_queue.py --item NW-001      # dispatch specific item
  python dispatch_queue.py --status           # print queue summary and exit
  python dispatch_queue.py --max 3            # dispatch at most 3 items
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_STOP_CONDITIONS = [
    "Lock cannot be acquired for this PR branch.",
    "Fix requires files outside the allowed_files list.",
    "Reviewer intent is unclear — ask for clarification before patching.",
    "Security or architecture finding with confidence < 90 requires human decision.",
    "Tests fail outside the touched file scope.",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def dispatch_id_for(task_id: str) -> str:
    return f"DISP-{hashlib.sha1(task_id.encode()).hexdigest()[:10].upper()}"


def load_queue(path: Path) -> Dict[str, Any]:
    if not path.exists() or not path.read_text().strip():
        return {"items": []}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[dispatch_queue] WARNING: could not parse queue ({exc}); treating as empty.")
        return {"items": []}
    if isinstance(data, list):
        return {"items": data}
    data.setdefault("items", [])
    return data


def save_queue(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def render_mission_packet(item: Dict[str, Any]) -> str:
    acceptance = "\n".join(f"- {c}" for c in (item.get("acceptance_checks") or []))
    allowed = "\n".join(f"- `{f}`" for f in (item.get("allowed_files") or [])) or "- (PR-level — no specific file scope)"
    stops = "\n".join(f"- {s}" for s in _STOP_CONDITIONS)
    links = "\n".join(f"- {lnk}" for lnk in (item.get("links") or [])) or "- (no direct links)"
    return f"""# Mission Packet — {item['id']}

## Task ID
{item['id']}

## Objective
{item.get('title', 'Address review finding')}

## Source
{links}

## Owner Agent
{item.get('owner_agent', 'Auditor')}

## Allowed Files
{allowed}

## Forbidden Files
- All files not listed in Allowed Files above
- `.env`, secrets, CI scripts, unless explicitly listed
- Files outside the repo root

## Risk Level
{item.get('risk_level', 'medium')}

## Confidence
{item.get('confidence_score', 0)}/100

## Acceptance Checks
{acceptance}

## Stop Conditions
{stops}

## Required Output
- Patch or documented explanation of why patch is blocked
- Validation evidence (test run output, lint output)
- Resolution comment (pipe `post_review_resolution.py` into `gh pr comment`)
- Queue status update (`log_resolution.py --task {item['id']} --status resolved`)

## Notes
{item.get('notes', '')}
"""


def write_dispatch_log(log_path: Path, entry: Dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def acquire_branch_lock(item: Dict[str, Any], lock_dir: str, holder: str) -> bool:
    """Invoke lock_pr_branch.py acquire for the item's repo/PR. Returns True on success."""
    repo = item.get("repo", "unknown")
    pr_number = item.get("pr_number")
    if not pr_number:
        # No PR number — nothing to lock; allow dispatch to proceed.
        return True
    lock_script = Path(__file__).parent / "lock_pr_branch.py"
    cmd = [
        sys.executable, str(lock_script), "acquire",
        "--repo", str(repo),
        "--pr-number", str(pr_number),
        "--holder", holder,
        "--queue-item-id", item.get("id", "unknown"),
        "--lock-dir", lock_dir,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        # exit code 2 means an active lock exists
        print(f"[dispatch_queue] Lock denied for {repo}#{pr_number}: {result.stdout.strip() or result.stderr.strip()}")
        return False
    except OSError as exc:
        print(f"[dispatch_queue] Could not invoke lock_pr_branch.py: {exc}")
        return False


def dispatch_item(
    item: Dict[str, Any],
    missions_dir: Path,
    log_path: Path,
    dry_run: bool,
    lock_dir: str = ".agents/review-intake/locks",
    holder: str = "dispatch_queue",
) -> Dict[str, Any]:
    did = dispatch_id_for(item["id"])
    mission_path = missions_dir / f"{item['id']}.md"

    lock_acquired = dry_run or acquire_branch_lock(item, lock_dir, holder)

    entry = {
        "dispatch_id": did,
        "task_id": item["id"],
        "agent": item.get("owner_agent", "Auditor"),
        "status": "dispatched" if lock_acquired else "lock-failed",
        "repo": item.get("repo", "unknown"),
        "pr_number": item.get("pr_number"),
        "started_at": utc_now(),
        "completed_at": None,
        "validation_summary": None,
        "links": item.get("links", []),
        "mission_packet": str(mission_path),
        "lock_acquired": lock_acquired,
    }
    if not dry_run:
        if lock_acquired:
            missions_dir.mkdir(parents=True, exist_ok=True)
            mission_path.write_text(render_mission_packet(item))
        write_dispatch_log(log_path, entry)
    return entry


_HUMAN_GATE_STATUSES = {"review-required", "blocked", "needs-human-decision", "dispatched"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch ready Chromatic Next Work Queue items.")
    parser.add_argument("--queue", default=".agents/review-intake/next-work.queue.json")
    parser.add_argument("--missions-dir", default=".agents/review-intake/missions")
    parser.add_argument("--dispatch-log", default=".agents/review-intake/logs/agent-dispatch-log.jsonl")
    parser.add_argument("--lock-dir", default=".agents/review-intake/locks", help="Directory for PR branch locks")
    parser.add_argument("--holder", default="dispatch_queue", help="Lock holder name recorded in the lock file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--item", default=None, metavar="ID", help="Dispatch a specific queue item")
    parser.add_argument("--force", action="store_true", help="Allow dispatching non-ready items via --item (requires explicit human approval)")
    parser.add_argument("--status", action="store_true", help="Print queue summary and exit")
    parser.add_argument("--max", type=int, default=0, metavar="N", help="Dispatch at most N items (0=all)")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    queue = load_queue(queue_path)
    items = queue.get("items", [])

    if args.status:
        counts = Counter(i.get("status", "unknown") for i in items)
        print(json.dumps({"total": len(items), "by_status": dict(counts)}, indent=2))
        return 0

    skipped_human_gate = 0

    if args.item:
        candidates = [i for i in items if i.get("id") == args.item]
        if not candidates:
            print(f"Item {args.item!r} not found.")
            return 1
        item_status = candidates[0].get("status", "unknown")
        if item_status in _HUMAN_GATE_STATUSES and not args.force:
            print(
                f"Item {args.item!r} has status {item_status!r} and requires explicit human approval. "
                "Re-run with --force to override."
            )
            return 1
        ready_items = candidates
    else:
        all_non_ready = [i for i in items if i.get("status") in _HUMAN_GATE_STATUSES]
        skipped_human_gate = len(all_non_ready)
        ready_items = sorted(
            [i for i in items if i.get("status") == "ready"],
            key=lambda x: -x.get("priority", 0),
        )

    if skipped_human_gate:
        print(f"[dispatch_queue] Skipped {skipped_human_gate} item(s) requiring human approval (review-required/blocked/needs-human-decision/dispatched).")

    if not ready_items:
        print("No ready items to dispatch.")
        return 0

    if args.max > 0:
        ready_items = ready_items[: args.max]

    dispatched = []
    lock_failed = []
    for item in ready_items:
        entry = dispatch_item(
            item,
            Path(args.missions_dir),
            Path(args.dispatch_log),
            args.dry_run,
            lock_dir=args.lock_dir,
            holder=args.holder,
        )
        if not entry.get("lock_acquired", True):
            print(f"[dispatch_queue] Skipping {item['id']} — lock could not be acquired.")
            lock_failed.append(item["id"])
            continue
        dispatched.append(entry)
        if not args.dry_run:
            for qi in queue["items"]:
                if qi.get("id") == item["id"]:
                    qi["status"] = "in-progress"
                    qi["dispatched_at"] = entry["started_at"]
                    qi["dispatch_id"] = entry["dispatch_id"]
                    break
            save_queue(queue_path, queue)
        tag = "[DRY RUN] " if args.dry_run else ""
        print(f"{tag}Dispatched {item['id']} → {entry['agent']} (priority {item.get('priority', 0)})")

    print(json.dumps({
        "dispatched": len(dispatched),
        "lock_failed": len(lock_failed),
        "skipped_human_gate": skipped_human_gate,
        "dry_run": args.dry_run,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
