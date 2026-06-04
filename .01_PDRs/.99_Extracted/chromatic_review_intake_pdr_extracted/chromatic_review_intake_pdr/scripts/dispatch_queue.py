#!/usr/bin/env python3
"""Dispatch ready queue items to the correct agent with a bounded mission packet.

Implements the REVIEW_DISPATCH_PLAYBOOK routing rules and stop conditions.
Writes dispatch records to the agent-dispatch-log.jsonl and updates queue
item status to in-progress.

Usage:
    python scripts/dispatch_queue.py \\
        --queue 00_PLANNING/next-work.queue.json \\
        --dispatch-log 02_LOGS/agent-dispatch-log.jsonl \\
        [--item-id NW-REVIEW-INTAKE-001] \\
        [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Agent routing table — mirrors REVIEW_DISPATCH_PLAYBOOK §Agent Routing
# ---------------------------------------------------------------------------
AGENT_BY_FINDING_TYPE: dict[str, str] = {
    "security": "Sentinel",
    "test_failure": "Auditor",
    "lint_style": "Janitor",
    "docs": "Archivist",
    "architecture": "Archivist",
    "bug_fix": "Sentinel",
    "repo_hygiene": "Janitor",
    "unclear": "Auditor",
}

# Finding types that require a human gate before any code mutation
HUMAN_GATE_TYPES: frozenset[str] = frozenset({"security", "architecture"})

# Minimum confidence score for mutation work (REVIEW_DISPATCH_PLAYBOOK §Stop Conditions)
CONFIDENCE_MUTATION_THRESHOLD = 75

# Stop condition strings appended to blocked dispatch records
STOP_CONFIDENCE_LOW = "confidence_below_75_for_mutation"
STOP_EMPTY_FILES = "allowed_files_empty_for_code_mutation"
STOP_HUMAN_GATE = "human_gate_required"
STOP_ACTIVE_LOCK = "pr_branch_has_active_mutation_lock"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utc_now() -> str:
    """Return current UTC time as ISO-8601 string with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def dispatch_id(task_id: str, ts: str) -> str:
    """Generate a stable dispatch ID from task ID and timestamp."""
    raw = f"{task_id}|{ts}"
    digest = hashlib.sha1(raw.encode()).hexdigest()[:12].upper()
    return f"DISPATCH-{digest}"


def load_queue(path: Path) -> dict[str, Any]:
    """Load and normalise the next-work queue JSON.

    Returns ``{"items": [...]}`` regardless of whether the file stores a bare
    list or the wrapped object form.  Wraps ``json.loads`` in a try/except per
    coding standards (files may be partially written).
    """
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return {"items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Queue file is not valid JSON: {path}") from exc
    if isinstance(data, list):
        return {"items": data}
    data.setdefault("items", [])
    return data


def save_queue(path: Path, data: dict[str, Any]) -> None:
    """Write the queue object back to disk atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_dispatch_log(path: Path, record: dict[str, Any]) -> None:
    """Append one dispatch record to the JSONL dispatch log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def resolve_agent(item: dict[str, Any]) -> str:
    """Return the correct owner agent for a queue item.

    Uses ``owner_agent`` if already set and non-empty; otherwise falls back to
    the routing table keyed on ``finding_type``.
    """
    explicit = (item.get("owner_agent") or "").strip()
    if explicit:
        return explicit
    finding_type = (item.get("finding_type") or item.get("area") or "unclear").strip()
    return AGENT_BY_FINDING_TYPE.get(finding_type, "Auditor")


# ---------------------------------------------------------------------------
# Stop condition checks
# ---------------------------------------------------------------------------

def check_stop_conditions(item: dict[str, Any]) -> list[str]:
    """Return a list of triggered stop condition strings for *item*.

    An empty list means the item is clear for dispatch.
    """
    stops: list[str] = []

    confidence: int = int(item.get("confidence_score") or 0)
    finding_type: str = (item.get("finding_type") or "unclear").strip()
    allowed_files: list[str] = item.get("allowed_files") or []

    # Stop 1: confidence below 75 for mutation work
    if confidence < CONFIDENCE_MUTATION_THRESHOLD:
        stops.append(STOP_CONFIDENCE_LOW)

    # Stop 2: allowed_files empty for code mutation finding types
    mutation_types = {"bug_fix", "lint_style", "test_failure", "security", "repo_hygiene"}
    if finding_type in mutation_types and not allowed_files:
        stops.append(STOP_EMPTY_FILES)

    # Stop 3: human gate for security / architecture
    if finding_type in HUMAN_GATE_TYPES:
        stops.append(STOP_HUMAN_GATE)

    return stops


def check_lock(item: dict[str, Any], lock_dir: Path) -> bool:
    """Return True if an active (non-expired) lock exists for this item's PR."""
    pr_number = item.get("pr_number") or item.get("links") and None
    repo = (item.get("repo") or "").replace("/", "__")
    if not pr_number or not repo:
        return False
    lock_file = lock_dir / f"{repo}__pr{pr_number}.lock.json"
    if not lock_file.exists():
        return False
    try:
        data = json.loads(lock_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    expires_raw: str = data.get("expires_at") or ""
    if not expires_raw:
        return False
    expires = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
    return expires > datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Mission packet builder
# ---------------------------------------------------------------------------

def build_mission_packet(item: dict[str, Any], agent: str) -> str:
    """Render a mission packet string from a queue item.

    Format mirrors ``templates/agent_mission_packet.md``.
    """
    task_id: str = item.get("id") or "UNKNOWN"
    objective: str = item.get("title") or "Address review finding."
    links: list[str] = item.get("links") or []
    source_links: str = "\n".join(f"- {lnk}" for lnk in links) or "- (no source links recorded)"
    allowed_files: list[str] = item.get("allowed_files") or []
    allowed_str: str = "\n".join(f"- {f}" for f in allowed_files) or "- (none — read-only investigation only)"
    forbidden_str: str = "- All files not listed in Allowed Files above"
    risk_level: str = item.get("risk_level") or "unknown"
    confidence: int = int(item.get("confidence_score") or 0)
    checks: list[str] = item.get("acceptance_checks") or ["Review manually"]
    checks_str: str = "\n".join(f"- {c}" for c in checks)
    notes: str = item.get("notes") or ""
    stop_lines = "\n".join(
        f"- {s}" for s in [
            f"Confidence below {CONFIDENCE_MUTATION_THRESHOLD} for mutation work.",
            "Allowed files are empty for code mutation.",
            "Human gate required.",
            "PR branch already has an active mutation lock.",
        ]
    )

    return f"""# Mission Packet

## Task ID
{task_id}

## Objective
{objective}

## Source
{source_links}

## Allowed Files
{allowed_str}

## Forbidden Files
{forbidden_str}

## Risk Level
{risk_level}

## Confidence
{confidence}/100

## Acceptance Checks
{checks_str}

## Stop Conditions
{stop_lines}

## Required Output
- Patch or explanation of why patch is blocked
- Validation evidence
- PR resolution comment
- Queue status update

## Agent
{agent}

## Notes
{notes}
"""


# ---------------------------------------------------------------------------
# Core dispatch logic
# ---------------------------------------------------------------------------

def dispatch_item(
    item: dict[str, Any],
    *,
    lock_dir: Path,
    dispatch_log: Path,
    dry_run: bool,
) -> dict[str, Any]:
    """Evaluate and dispatch a single queue item.

    Returns a dispatch record dict describing the outcome.
    """
    ts = utc_now()
    d_id = dispatch_id(item.get("id", ""), ts)
    agent = resolve_agent(item)

    # Check active lock
    lock_active = check_lock(item, lock_dir)
    stops = check_stop_conditions(item)
    if lock_active:
        stops.insert(0, STOP_ACTIVE_LOCK)

    dispatched = not stops
    record: dict[str, Any] = {
        "dispatch_id": d_id,
        "task_id": item.get("id"),
        "source_finding_id": item.get("source_finding_id"),
        "agent": agent,
        "status": "dispatched" if dispatched else "blocked",
        "repo": item.get("repo"),
        "pr_number": item.get("pr_number"),
        "started_at": ts,
        "completed_at": None,
        "validation_summary": None,
        "links": item.get("links") or [],
        "stop_conditions_triggered": stops,
        "risk_level": item.get("risk_level"),
        "confidence_score": item.get("confidence_score"),
    }

    if dispatched:
        packet = build_mission_packet(item, agent)
        record["mission_packet"] = packet

    if not dry_run:
        append_dispatch_log(dispatch_log, record)

    return record


def run_dispatch(
    queue_path: Path,
    dispatch_log: Path,
    lock_dir: Path,
    *,
    item_id: str | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Load the queue, filter ready items, dispatch each one.

    Returns a list of dispatch records (one per item attempted).

    Args:
        queue_path: Path to next-work.queue.json.
        dispatch_log: Path to agent-dispatch-log.jsonl.
        lock_dir: Directory containing PR branch lock files.
        item_id: If set, dispatch only the item with this ID.
        dry_run: If True, skip writing to disk.
    """
    queue = load_queue(queue_path)
    items: list[dict[str, Any]] = queue.get("items") or []

    # Filter: only dispatch 'ready' items (Dispatch Rule from playbook)
    candidates = [i for i in items if i.get("status") == "ready"]
    if item_id:
        candidates = [i for i in candidates if i.get("id") == item_id]

    if not candidates:
        return []

    records: list[dict[str, Any]] = []
    for item in candidates:
        record = dispatch_item(item, lock_dir=lock_dir, dispatch_log=dispatch_log, dry_run=dry_run)
        records.append(record)

        # Update queue item status to in-progress when dispatch succeeded
        if record["status"] == "dispatched" and not dry_run:
            for q_item in items:
                if q_item.get("id") == item.get("id"):
                    q_item["status"] = "in-progress"
                    q_item["dispatched_at"] = record["started_at"]
                    q_item["dispatch_id"] = record["dispatch_id"]
                    break
            save_queue(queue_path, queue)

    return records


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI entry point for dispatch_queue.py."""
    parser = argparse.ArgumentParser(
        description="Dispatch ready queue items to Chromatic agents."
    )
    parser.add_argument(
        "--queue",
        default="00_PLANNING/next-work.queue.json",
        help="Path to next-work.queue.json",
    )
    parser.add_argument(
        "--dispatch-log",
        default="02_LOGS/agent-dispatch-log.jsonl",
        help="Path to agent-dispatch-log.jsonl",
    )
    parser.add_argument(
        "--lock-dir",
        default="00_PLANNING/locks",
        help="Directory containing PR branch lock files",
    )
    parser.add_argument(
        "--item-id",
        default=None,
        help="Dispatch only the queue item with this ID",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print dispatch records without writing to disk",
    )
    args = parser.parse_args()

    records = run_dispatch(
        queue_path=Path(args.queue),
        dispatch_log=Path(args.dispatch_log),
        lock_dir=Path(args.lock_dir),
        item_id=args.item_id,
        dry_run=args.dry_run,
    )

    if not records:
        print("No ready items to dispatch.")
        return 0

    for rec in records:
        print(json.dumps(rec, indent=2))

    dispatched = sum(1 for r in records if r["status"] == "dispatched")
    blocked = len(records) - dispatched
    print(f"\nSummary: {dispatched} dispatched, {blocked} blocked.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
