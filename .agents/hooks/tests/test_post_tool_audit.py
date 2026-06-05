"""Tests for post_tool_audit.py.

Log path is redirected by monkeypatching the module's __file__ attribute so
that Path(__file__).resolve().parents[2] resolves to tmp_path.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

import post_tool_audit as pta


def _fake_file(tmp_path: Path) -> Path:
    """Return a fake __file__ path whose parents[2] == tmp_path."""
    f = tmp_path / ".agents" / "hooks" / "post_tool_audit.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    return f


def _run(monkeypatch, tmp_path: Path, payload: dict | None) -> int:
    stdin_str = json.dumps(payload) if payload is not None else ""
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_str))
    monkeypatch.setattr(pta, "__file__", str(_fake_file(tmp_path)))
    return pta.main()


class TestSummarize:
    def test_short_response_unchanged(self):
        assert pta._summarize("Write", "short") == "short"

    def test_large_response_for_large_tool_truncated(self):
        big = "x" * 1000
        out = pta._summarize("Read", big)
        assert len(out) < len(big)
        assert "truncated" in out

    def test_large_response_for_non_large_tool_not_truncated(self):
        big = "x" * 1000
        assert pta._summarize("Write", big) == big

    def test_dict_value_serialized_to_string(self):
        out = pta._summarize("SomeTool", {"key": "val"})
        assert "key" in out
        assert "val" in out

    def test_exactly_at_limit_not_truncated(self):
        at_limit = "x" * pta._RESPONSE_MAX_CHARS
        out = pta._summarize("Read", at_limit)
        assert "truncated" not in out


class TestMain:
    def test_writes_audit_record(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "session_id": "sess-1",
        })
        log = tmp_path / ".agents" / "logs" / "tool-audit.jsonl"
        assert log.exists()
        entry = json.loads(log.read_text())
        assert entry["tool"] == "Bash"
        assert entry["session_id"] == "sess-1"

    def test_always_returns_0(self, tmp_path, monkeypatch):
        rc = _run(monkeypatch, tmp_path, {"tool_name": "Read"})
        assert rc == 0

    def test_invalid_json_returns_0(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO("not json {{"))
        assert pta.main() == 0

    def test_record_contains_ts_and_agent_id(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {"tool_name": "Write"})
        log = tmp_path / ".agents" / "logs" / "tool-audit.jsonl"
        entry = json.loads(log.read_text())
        assert "ts" in entry
        assert "T" in entry["ts"]
        assert "agent_id" in entry

    def test_response_preview_truncated_for_large_tools(self, tmp_path, monkeypatch):
        big_response = "z" * 2000
        _run(monkeypatch, tmp_path, {
            "tool_name": "Read",
            "tool_response": big_response,
        })
        log = tmp_path / ".agents" / "logs" / "tool-audit.jsonl"
        entry = json.loads(log.read_text())
        assert "truncated" in entry["response_preview"]

    def test_multiple_calls_appended(self, tmp_path, monkeypatch):
        for tool in ("Read", "Write", "Bash"):
            _run(monkeypatch, tmp_path, {"tool_name": tool})
        log = tmp_path / ".agents" / "logs" / "tool-audit.jsonl"
        lines = [l for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 3

    def test_agent_id_from_chromatic_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CHROMATIC_AGENT_ID", "Sentinel")
        _run(monkeypatch, tmp_path, {"tool_name": "Bash"})
        log = tmp_path / ".agents" / "logs" / "tool-audit.jsonl"
        entry = json.loads(log.read_text())
        assert entry["agent_id"] == "Sentinel"
