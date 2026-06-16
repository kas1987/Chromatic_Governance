"""Tests for log_resolution.main() — end-to-end argparse integration.

The existing test_dispatch.py tests replicate log_resolution logic manually.
These tests call main() directly to pin the argparse contract and edge cases.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import log_resolution as lr


def _run(monkeypatch, argv: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", ["log_resolution.py"] + argv)
    return lr.main()


def _base_args(tmp_path: Path) -> list[str]:
    return [
        "--finding", "RF-001",
        "--task", "NW-001",
        "--agent", "Sentinel",
        "--queue", str(tmp_path / "queue.json"),
        "--log", str(tmp_path / "resolution.jsonl"),
    ]


class TestResolvedStatus:
    def test_writes_jsonl_record(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-001", "status": "in-progress"}]}) + "\n")
        _run(monkeypatch, _base_args(tmp_path) + ["--status", "resolved", "--summary", "Fixed it"])
        record = json.loads((tmp_path / "resolution.jsonl").read_text())
        assert record["finding_id"] == "RF-001"
        assert record["status"] == "resolved"
        assert record["summary"] == "Fixed it"
        assert record["agent"] == "Sentinel"

    def test_updates_queue_item_to_done(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-001", "status": "in-progress"}]}) + "\n")
        _run(monkeypatch, _base_args(tmp_path))
        data = json.loads(queue.read_text())
        assert data["items"][0]["status"] == "done"
        assert "resolved_at" in data["items"][0]

    def test_validation_and_files_stored_in_record(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": []}) + "\n")
        _run(monkeypatch, [
            "--finding", "RF-002", "--task", "NW-002", "--agent", "Auditor",
            "--validation", "pytest tests/", "mypy src/",
            "--files", "src/main.py", "src/util.py",
            "--queue", str(queue),
            "--log", str(tmp_path / "r.jsonl"),
        ])
        record = json.loads((tmp_path / "r.jsonl").read_text())
        assert record["validation"] == ["pytest tests/", "mypy src/"]
        assert record["files_changed"] == ["src/main.py", "src/util.py"]

    def test_resolved_at_timestamp_present_and_utc(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": []}) + "\n")
        _run(monkeypatch, _base_args(tmp_path))
        record = json.loads((tmp_path / "resolution.jsonl").read_text())
        assert "resolved_at" in record
        assert record["resolved_at"].endswith("Z")

    def test_returns_zero(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": []}) + "\n")
        rc = _run(monkeypatch, _base_args(tmp_path))
        assert rc == 0


class TestBlockedAndClarificationStatus:
    def test_blocked_status_sets_queue_blocked(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-001", "status": "in-progress"}]}) + "\n")
        _run(monkeypatch, _base_args(tmp_path) + ["--status", "blocked"])
        data = json.loads(queue.read_text())
        assert data["items"][0]["status"] == "blocked"

    def test_needs_clarification_status_preserved(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-001", "status": "in-progress"}]}) + "\n")
        _run(monkeypatch, _base_args(tmp_path) + ["--status", "needs-clarification"])
        data = json.loads(queue.read_text())
        assert data["items"][0]["status"] == "needs-clarification"

    def test_blocked_record_written_to_log(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": []}) + "\n")
        _run(monkeypatch, _base_args(tmp_path) + ["--status", "blocked"])
        record = json.loads((tmp_path / "resolution.jsonl").read_text())
        assert record["status"] == "blocked"


class TestEdgeCases:
    def test_task_not_in_queue_leaves_queue_unchanged(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        original = {"items": [{"id": "NW-999", "status": "in-progress"}]}
        queue.write_text(json.dumps(original) + "\n")
        _run(monkeypatch, [
            "--finding", "RF-X", "--task", "NW-NOT-HERE", "--agent", "A",
            "--queue", str(queue),
            "--log", str(tmp_path / "r.jsonl"),
        ])
        data = json.loads(queue.read_text())
        assert data["items"][0]["status"] == "in-progress"

    def test_missing_queue_file_no_error(self, tmp_path, monkeypatch):
        rc = _run(monkeypatch, [
            "--finding", "RF-X", "--task", "NW-001", "--agent", "A",
            "--queue", str(tmp_path / "nonexistent.json"),
            "--log", str(tmp_path / "r.jsonl"),
        ])
        assert rc == 0
        assert (tmp_path / "r.jsonl").exists()

    def test_empty_queue_file_no_error(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text("")
        rc = _run(monkeypatch, [
            "--finding", "RF-X", "--task", "NW-001", "--agent", "A",
            "--queue", str(queue),
            "--log", str(tmp_path / "r.jsonl"),
        ])
        assert rc == 0

    def test_creates_nested_log_parent_dirs(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": []}) + "\n")
        log = tmp_path / "nested" / "deep" / "r.jsonl"
        rc = _run(monkeypatch, [
            "--finding", "RF-X", "--task", "NW-001", "--agent", "A",
            "--queue", str(queue),
            "--log", str(log),
        ])
        assert rc == 0
        assert log.exists()

    def test_multiple_resolutions_append_to_log(self, tmp_path, monkeypatch):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": []}) + "\n")
        log = tmp_path / "r.jsonl"
        for finding in ("RF-001", "RF-002", "RF-003"):
            _run(monkeypatch, [
                "--finding", finding, "--task", "NW-XXX", "--agent", "A",
                "--queue", str(queue),
                "--log", str(log),
            ])
        lines = [l for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 3
