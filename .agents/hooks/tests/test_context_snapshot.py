"""Tests for context_snapshot.py.

Log path is redirected by monkeypatching __file__ so that
Path(__file__).resolve().parents[2] resolves to tmp_path.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

import context_snapshot as cs


def _fake_file(tmp_path: Path) -> Path:
    f = tmp_path / ".agents" / "hooks" / "context_snapshot.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    return f


def _run(monkeypatch, tmp_path: Path, payload: dict | None) -> None:
    stdin_str = json.dumps(payload) if payload is not None else ""
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_str))
    monkeypatch.setattr(cs, "__file__", str(_fake_file(tmp_path)))
    cs.main()


def _read_log(tmp_path: Path) -> dict:
    return json.loads((tmp_path / ".agents" / "logs" / "context-usage.jsonl").read_text())


class TestStatus:
    @pytest.mark.parametrize("pct,expected", [
        (0.95, "critical"),
        (0.90, "critical"),
        (0.85, "red"),
        (0.80, "red"),
        (0.70, "orange"),
        (0.65, "orange"),
        (0.50, "yellow"),
        (0.40, "yellow"),
        (0.20, "green"),
        (0.00, "green"),
    ])
    def test_threshold_boundaries(self, pct, expected):
        assert cs._status(pct) == expected


class TestMain:
    def test_writes_snapshot_record(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "session_id": "sess-abc",
            "model": "claude-opus-4-8",
            "usage": {"input_tokens": 5000, "output_tokens": 3000, "context_limit": 200000},
        })
        entry = _read_log(tmp_path)
        assert entry["session"] == "sess-abc"
        assert entry["model"] == "claude-opus-4-8"
        assert entry["used_tokens"] == 8000
        assert entry["pct_used"] == round(8000 / 200000, 4)

    def test_zero_tokens_status_unknown(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {})
        entry = _read_log(tmp_path)
        assert entry["status"] == "unknown"
        assert entry["used_tokens"] == 0
        assert entry["pct_used"] == 0.0

    def test_high_usage_status_critical(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "usage": {"input_tokens": 180000, "output_tokens": 0, "context_limit": 200000},
        })
        assert _read_log(tmp_path)["status"] == "critical"

    def test_low_usage_status_green(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "usage": {"input_tokens": 10000, "output_tokens": 0, "context_limit": 200000},
        })
        assert _read_log(tmp_path)["status"] == "green"

    def test_invalid_json_proceeds_gracefully(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO("not json {{"))
        monkeypatch.setattr(cs, "__file__", str(_fake_file(tmp_path)))
        cs.main()  # must not raise
        log = tmp_path / ".agents" / "logs" / "context-usage.jsonl"
        assert log.exists()

    def test_agent_id_from_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CHROMATIC_AGENT_ID", "Auditor")
        _run(monkeypatch, tmp_path, {})
        assert _read_log(tmp_path)["agent_id"] == "Auditor"

    def test_task_id_from_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CHROMATIC_TASK_ID", "NW-007")
        _run(monkeypatch, tmp_path, {})
        assert _read_log(tmp_path)["task_id"] == "NW-007"

    def test_no_task_id_stores_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CHROMATIC_TASK_ID", raising=False)
        _run(monkeypatch, tmp_path, {})
        assert _read_log(tmp_path)["task_id"] is None

    def test_total_tokens_field_used_as_fallback(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "usage": {"total_tokens": 4000, "context_limit": 200000},
        })
        assert _read_log(tmp_path)["used_tokens"] == 4000

    def test_multiple_snapshots_appended(self, tmp_path, monkeypatch):
        for _ in range(3):
            _run(monkeypatch, tmp_path, {})
        log = tmp_path / ".agents" / "logs" / "context-usage.jsonl"
        lines = [l for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 3
