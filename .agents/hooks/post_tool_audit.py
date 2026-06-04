#!/usr/bin/env python3
"""
post_tool_audit.py

PostToolUse hook for Chromatic multi-agent swarm.

Appends a lightweight audit record to .agents/logs/tool-audit.jsonl after
every tool invocation. Provides inter-agent observability and session replay.

Claude Code passes JSON on stdin after each tool call:

  {
    "tool_name": "...",
    "tool_input": {...},
    "tool_response": {...},
    "session_id": "...",
    ...
  }

Exit code is always 0 — this hook never blocks execution.

Environment:
  CHROMATIC_AGENT_ID  — set by each swarm agent for audit attribution
  AGENT_ID            — fallback agent identity env var
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Tools whose full response is too noisy — truncate it
_LARGE_RESPONSE_TOOLS: frozenset[str] = frozenset(
    {"Read", "Bash", "computer", "execute_bash", "shell", "grep_search", "semantic_search"}
)
_RESPONSE_MAX_CHARS = 400

# Tools to skip entirely (too frequent / no audit value)
_SKIP_TOOLS: frozenset[str] = frozenset()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _summarize(tool_name: str, value: object) -> str:
    """Serialise value to string, truncating for noisy tools."""
    text = json.dumps(value) if not isinstance(value, str) else value
    if tool_name in _LARGE_RESPONSE_TOOLS and len(text) > _RESPONSE_MAX_CHARS:
        return text[:_RESPONSE_MAX_CHARS] + "…[truncated]"
    return text


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
        return 0  # parse failure — do nothing, never block

    tool_name: str = payload.get("tool_name", "unknown")

    if tool_name in _SKIP_TOOLS:
        return 0

    tool_input: dict = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response")
    session_id: str = payload.get("session_id", "unknown")
    agent_id: str = (
        os.environ.get("CHROMATIC_AGENT_ID")
        or os.environ.get("AGENT_ID")
        or "unknown"
    )

    entry = {
        "ts": _utc(),
        "session_id": session_id,
        "agent_id": agent_id,
        "tool": tool_name,
        "input_preview": _summarize(tool_name, tool_input)[:300],
        "response_preview": _summarize(tool_name, tool_response),
    }

    try:
        log_path = (
            Path(__file__).resolve().parents[2] / ".agents" / "logs" / "tool-audit.jsonl"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception:
        pass  # never block on logging failure

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
