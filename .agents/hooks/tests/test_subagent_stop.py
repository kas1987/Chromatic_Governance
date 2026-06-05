"""Tests for subagent_stop.py.

Queue and log paths are redirected by monkeypatching __file__ so that
Path(__file__).resolve().parents[2] resolves to tmp_path.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

import subagent_stop as ss


def _fake_file(tmp_path: Path) -> Path:
    f = tmp_path / ".agents" / "hooks" / "subagent_stop.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    return f


def _make_queue(tmp_path: Path, items: list) -> Path:
    path = tmp_path / ".agents" / "review-intake" / "next-work.queue.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"items": items}))
    return path


def _run(monkeypatch, tmp_path: Path, payload: dict | None, env: dict | None = None) -> int:
    stdin_str = json.dumps(payload) if payload is not None else ""
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_str))
    monkeypatch.setattr(ss, "__file__", str(_fake_file(tmp_path)))
    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)
    monkeypatch.delenv("CHROMATIC_TASK_ID", raising=False)
    monkeypatch.delenv("CHROMATIC_AGENT_ID", raising=False)
    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)
    return ss.main()


def _read_log(tmp_path: Path) -> dict:
    return json.loads(
        (tmp_path / ".agents" / "logs" / "subagent-completions.jsonl").read_text()
    )


class TestLoadJson:
    def test_returns_none_for_missing_file(self, tmp_path):
        assert ss._load_json(tmp_path / "nonexistent.json") is None

    def test_returns_none_for_malformed_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json {{{{")
        assert ss._load_json(bad) is None

    def test_returns_parsed_dict(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text(json.dumps({"key": "value"}))
        assert ss._load_json(f) == {"key": "value"}


class TestUpdateQueueItem:
    def test_advances_in_progress_to_needs_review(self, tmp_path, monkeypatch):
        _make_queue(tmp_path, [{"id": "NW-001", "status": "in-progress"}])
        monkeypatch.setattr(ss, "__file__", str(_fake_file(tmp_path)))
        result = ss._update_queue_item("NW-001", "sess-abc")
        assert result is True
        data = json.loads(
            (tmp_path / ".agents" / "review-intake" / "next-work.queue.json").read_text()
        )
        item = data["items"][0]
        assert item["status"] == "needs-review"
        assert "subagent_completed_at" in item
        assert item["subagent_session_id"] == "sess-abc"

    def test_does_not_modify_non_matching_item(self, tmp_path, monkeypatch):
        _make_queue(tmp_path, [{"id": "NW-999", "status": "in-progress"}])
        monkeypatch.setattr(ss, "__file__", str(_fake_file(tmp_path)))
        result = ss._update_queue_item("NW-NOT-HERE", "sess-xyz")
        assert result is False
        data = json.loads(
            (tmp_path / ".agents" / "review-intake" / "next-work.queue.json").read_text()
        )
        assert data["items"][0]["status"] == "in-progress"

    def test_only_advances_in_progress_not_other_statuses(self, tmp_path, monkeypatch):
        _make_queue(tmp_path, [{"id": "NW-001", "status": "done"}])
        monkeypatch.setattr(ss, "__file__", str(_fake_file(tmp_path)))
        result = ss._update_queue_item("NW-001", "sess-abc")
        assert result is False

    def test_returns_false_when_queue_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ss, "__file__", str(_fake_file(tmp_path)))
        result = ss._update_queue_item("NW-001", "sess-abc")
        assert result is False


class TestMain:
    def test_writes_completion_record(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "session_id": "sess-xyz",
            "model": "claude-sonnet-4-6",
            "usage": {"input_tokens": 100, "output_tokens": 50},
        })
        entry = _read_log(tmp_path)
        assert entry["event"] == "subagent_stop"
        assert entry["session_id"] == "sess-xyz"
        assert entry["tokens_used"] == 150

    def test_always_returns_0(self, tmp_path, monkeypatch):
        rc = _run(monkeypatch, tmp_path, {"session_id": "s"})
        assert rc == 0

    def test_invalid_json_returns_0(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO("bad json {{"))
        assert ss.main() == 0

    def test_task_id_env_var_advances_queue(self, tmp_path, monkeypatch):
        _make_queue(tmp_path, [{"id": "NW-TASK", "status": "in-progress"}])
        _run(monkeypatch, tmp_path, {"session_id": "s"}, env={"CHROMATIC_TASK_ID": "NW-TASK"})
        entry = _read_log(tmp_path)
        assert entry["queue_item_advanced"] is True

    def test_without_task_id_queue_not_advanced(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {"session_id": "s"})
        entry = _read_log(tmp_path)
        assert entry["queue_item_advanced"] is False
        assert entry["task_id"] is None

    def test_total_tokens_field_used_as_fallback(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {
            "usage": {"total_tokens": 9000},
        })
        assert _read_log(tmp_path)["tokens_used"] == 9000

    def test_multiple_completions_appended(self, tmp_path, monkeypatch):
        for i in range(3):
            _run(monkeypatch, tmp_path, {"session_id": f"sess-{i}"})
        log = tmp_path / ".agents" / "logs" / "subagent-completions.jsonl"
        lines = [l for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 3

    def test_agent_id_recorded(self, tmp_path, monkeypatch):
        _run(monkeypatch, tmp_path, {}, env={"CHROMATIC_AGENT_ID": "Cartographer"})
        assert _read_log(tmp_path)["agent_id"] == "Cartographer"
