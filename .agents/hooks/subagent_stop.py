#!/usr/bin/env python3
"""
subagent_stop.py

SubagentStop hook for Chromatic multi-agent swarm.

Fires when a subagent session ends. Writes a completion record to
.agents/logs/subagent-completions.jsonl so the orchestrating agent and
queue dispatcher can detect finished work without polling.

Claude Code passes JSON on stdin when a subagent stops:

  {
    "session_id": "...",
    "model": "...",
    "usage": {...},
    ...
  }

Additionally updates any queue item with a matching dispatch trace_id
from "in-progress" to "needs-review" to signal the dispatcher.

Exit code is always 0 — this hook never blocks execution.

Environment:
  CHROMATIC_AGENT_ID    — identity of the subagent that just stopped
  AGENT_ID              — fallback agent identity
  CHROMATIC_TASK_ID     — queue task ID being worked by this subagent
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict | None:
    """Load JSON from path. Returns None on any error (partial writes, etc.)."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _update_queue_item(task_id: str, session_id: str) -> bool:
    """If a queue item matches task_id, advance it to needs-review.

    Returns True if an item was updated.
    """
    queue_path = (
        Path(__file__).resolve().parents[2]
        / ".agents"
        / "review-intake"
        / "next-work.queue.json"
    )
    data = _load_json(queue_path)
    if not data:
        return False

    items: list[dict] = data.get("items") or []
    updated = False
    for item in items:
        if item.get("id") == task_id and item.get("status") == "in-progress":
            item["status"] = "needs-review"
            item["subagent_completed_at"] = _utc()
            item["subagent_session_id"] = session_id
            updated = True
            break

    if updated:
        try:
            queue_path.write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass

    return updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    payload: dict = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            payload = json.loads(raw)
    except Exception:
        return 0

    session_id: str = payload.get("session_id", "unknown")
    model: str = payload.get("model", "unknown")
    usage: dict = payload.get("usage") or {}

    agent_id: str = (
        os.environ.get("CHROMATIC_AGENT_ID")
        or os.environ.get("AGENT_ID")
        or "unknown"
    )
    task_id: str = os.environ.get("CHROMATIC_TASK_ID", "")

    entry = {
        "ts": _utc(),
        "event": "subagent_stop",
        "session_id": session_id,
        "agent_id": agent_id,
        "task_id": task_id or None,
        "model": model,
        "tokens_used": int(
            usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            or usage.get("total_tokens", 0)
        ),
        "queue_item_advanced": False,
    }

    # Try to advance the queue item if we know the task ID
    if task_id:
        entry["queue_item_advanced"] = _update_queue_item(task_id, session_id)

    try:
        log_path = (
            Path(__file__).resolve().parents[2]
            / ".agents"
            / "logs"
            / "subagent-completions.jsonl"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
