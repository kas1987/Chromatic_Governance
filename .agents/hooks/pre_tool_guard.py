#!/usr/bin/env python3
"""
pre_tool_guard.py

PreToolUse hook for Chromatic multi-agent swarm.

Blocks destructive commands and protected-branch pushes before execution.
Claude Code passes JSON on stdin when a tool is about to be invoked:

  {
    "tool_name": "Bash",
    "tool_input": {"command": "..."},
    "session_id": "...",
    ...
  }

Exit codes:
  0 — allow the tool call to proceed
  2 — block the tool call (message printed to stderr, shown to model)
  1 — internal error (non-blocking, logged)

Environment:
  CHROMATIC_AGENT_ID  — set by each swarm agent for audit attribution
  AGENT_ID            — fallback agent identity env var
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROTECTED_BRANCHES: frozenset[str] = frozenset({"main", "master", "Main"})

# (compiled_pattern, human-readable reason)
DESTRUCTIVE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\bgit\s+push\b.*--force\b"),
        "git push --force is blocked — use a PR instead",
    ),
    (
        re.compile(r"\bgit\s+push\b.*\s+-f\b"),
        "git push -f is blocked — use a PR instead",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        "git reset --hard must be run manually with explicit approval",
    ),
    (
        re.compile(r"\bgit\s+branch\s+-D\b"),
        "Force branch delete (-D) must be run manually with explicit approval",
    ),
    (
        re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)?(-[a-zA-Z]*f[a-zA-Z]*\s+)?/"),
        "rm on root paths is blocked",
    ),
    (
        re.compile(r"\bdrop\s+table\b", re.IGNORECASE),
        "DROP TABLE must be run manually",
    ),
    (
        re.compile(r"\bgit\s+push\b.*--no-verify\b"),
        "git push --no-verify bypasses safety hooks and is blocked",
    ),
    (
        re.compile(r"\bgit\s+commit\b.*--no-verify\b"),
        "git commit --no-verify bypasses safety hooks and is blocked",
    ),
]

# Pattern for detecting pushes to protected branches
_PROTECTED_PUSH_RE = re.compile(
    r"\bgit\s+push\b[^\|&;]*\b("
    + "|".join(re.escape(b) for b in PROTECTED_BRANCHES)
    + r")\b"
)

# Tools whose shell commands should be inspected
_SHELL_TOOLS: frozenset[str] = frozenset(
    {"Bash", "computer", "execute_bash", "shell", "run_bash", "bash"}
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _audit_log(entry: dict) -> None:
    """Append a guard event to tool-guard.jsonl (best-effort, never raises)."""
    try:
        log_path = (
            Path(__file__).resolve().parents[2] / ".agents" / "logs" / "tool-guard.jsonl"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception:
        pass


def check_command(command: str) -> tuple[bool, str]:
    """Return (blocked: bool, reason: str).

    blocked=True means the tool call should be rejected.
    """
    # Direct push to a protected branch
    if _PROTECTED_PUSH_RE.search(command):
        branches = ", ".join(sorted(PROTECTED_BRANCHES))
        return True, (
            f"Direct push to a protected branch ({branches}) is blocked. "
            "Use a session branch and open a PR."
        )

    for pattern, reason in DESTRUCTIVE_PATTERNS:
        if pattern.search(command):
            return True, reason

    return False, ""


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
        # Parse failure — allow through; logging only
        _audit_log({"ts": _utc(), "error": "stdin parse failure", "blocked": False})
        return 0

    tool_name: str = payload.get("tool_name", "")
    tool_input: dict = payload.get("tool_input") or {}
    session_id: str = payload.get("session_id", "unknown")
    agent_id: str = (
        os.environ.get("CHROMATIC_AGENT_ID")
        or os.environ.get("AGENT_ID")
        or "unknown"
    )

    # Only inspect shell/command tools
    if tool_name not in _SHELL_TOOLS:
        return 0

    command: str = (
        tool_input.get("command", "")
        or tool_input.get("cmd", "")
        or ""
    )
    if not command:
        return 0

    blocked, reason = check_command(command)

    _audit_log(
        {
            "ts": _utc(),
            "session_id": session_id,
            "agent_id": agent_id,
            "tool": tool_name,
            "command_preview": command[:300],
            "blocked": blocked,
            "reason": reason or None,
        }
    )

    if blocked:
        # Exit 2 signals Claude Code to block this tool call and show the reason
        print(f"[pre_tool_guard] BLOCKED: {reason}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
