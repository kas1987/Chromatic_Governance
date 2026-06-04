#!/usr/bin/env python3
"""
context_snapshot.py

Writes a context-usage JSONL snapshot at Claude Code session end.
Configured as a Stop hook in .claude/settings.json.

Claude Code passes a JSON payload on stdin when the hook fires.
This script is resilient to missing or partial payload fields.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


_THRESHOLDS = [
    (0.90, "critical"),
    (0.80, "red"),
    (0.65, "orange"),
    (0.40, "yellow"),
    (0.00, "green"),
]


def _status(pct: float) -> str:
    for threshold, label in _THRESHOLDS:
        if pct >= threshold:
            return label
    return "green"


def main() -> None:
    # Read stop-event payload from stdin
    payload: dict = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            payload = json.loads(raw)
    except Exception:
        pass  # proceed with empty payload; log what we can

    # Session identity
    session_id = (
        payload.get("session_id")
        or os.environ.get("CLAUDE_SESSION_ID", "unknown")
    )
    model = (
        payload.get("model")
        or os.environ.get("CLAUDE_MODEL", "unknown")
    )

    # Token usage — Claude Code may provide this in the stop event payload
    usage = payload.get("usage", {})
    used_tokens = int(
        usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        or usage.get("total_tokens", 0)
    )
    limit_tokens = int(usage.get("context_limit", 200_000))

    if used_tokens == 0:
        pct_used = 0.0
        status = "unknown"
    else:
        pct_used = round(used_tokens / limit_tokens, 4)
        status = _status(pct_used)

    agent_id = (
        payload.get("agent_id")
        or os.environ.get("CHROMATIC_AGENT_ID")
        or os.environ.get("AGENT_ID")
        or "unknown"
    )
    task_id = os.environ.get("CHROMATIC_TASK_ID", "")

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "session": session_id,
        "agent_id": agent_id,
        "task_id": task_id or None,
        "used_tokens": used_tokens,
        "limit_tokens": limit_tokens,
        "pct_used": pct_used,
        "status": status,
        "loaded_families": payload.get("loaded_plugins", []),
        "note": "auto-captured via Stop hook",
    }

    # Log path: two dirs up from .agents/hooks/ → repo root / .agents / logs /
    repo_root = Path(__file__).resolve().parents[2]
    log_path = repo_root / ".agents" / "logs" / "context-usage.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
