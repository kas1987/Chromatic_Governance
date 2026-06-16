"""End-to-end tests for dispatch_queue.main() and acquire_branch_lock().

The existing test_dispatch.py tests bypass main() by calling internal
helpers directly. These tests exercise the full argparse + dispatch path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dispatch_queue as dq


def _make_queue(items: list, path: Path) -> None:
    path.write_text(json.dumps({"items": items}, indent=2) + "\n")


def _ready_item(id_: str, priority: int = 80) -> dict:
    """pr_number=None avoids subprocess lock calls in main() tests."""
    return {
        "id": id_, "title": f"Task {id_}", "status": "ready",
        "priority": priority, "repo": "owner/repo", "pr_number": None,
        "owner_agent": "Auditor", "risk_level": "low", "confidence_score": 80,
        "acceptance_checks": ["Run tests"], "allowed_files": ["src/main.py"],
        "links": [], "notes": "",
    }


def _run(monkeypatch, tmp_path: Path, extra_argv: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", [
        "dispatch_queue.py",
        "--queue", str(tmp_path / "queue.json"),
        "--missions-dir", str(tmp_path / "missions"),
        "--dispatch-log", str(tmp_path / "dispatch.jsonl"),
        "--lock-dir", str(tmp_path / "locks"),
    ] + extra_argv)
    return dq.main()


class TestItemFlag:
    def test_item_not_found_returns_1(self, tmp_path, monkeypatch):
        _make_queue([_ready_item("NW-001")], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--item", "NW-NOTEXIST"])
        assert rc == 1

    def test_item_in_human_gate_blocked_without_force(self, tmp_path, monkeypatch):
        _make_queue([{**_ready_item("NW-BLK"), "status": "blocked"}], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--item", "NW-BLK"])
        assert rc == 1

    def test_item_in_dispatched_status_blocked_without_force(self, tmp_path, monkeypatch):
        _make_queue([{**_ready_item("NW-DISP"), "status": "dispatched"}], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--item", "NW-DISP"])
        assert rc == 1

    def test_item_with_force_dispatches_blocked_item(self, tmp_path, monkeypatch):
        _make_queue([{**_ready_item("NW-BLK2"), "status": "blocked"}], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--item", "NW-BLK2", "--force"])
        assert rc == 0
        assert (tmp_path / "missions" / "NW-BLK2.md").exists()

    def test_item_dispatches_ready_item(self, tmp_path, monkeypatch):
        _make_queue([_ready_item("NW-ONE")], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--item", "NW-ONE"])
        assert rc == 0
        assert (tmp_path / "missions" / "NW-ONE.md").exists()


class TestStatusFlag:
    def test_prints_json_counts_and_exits_0(self, tmp_path, monkeypatch, capsys):
        _make_queue([
            _ready_item("NW-S-001"),
            {**_ready_item("NW-S-002"), "status": "blocked"},
            {**_ready_item("NW-S-003"), "status": "done"},
        ], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--status"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["total"] == 3
        assert out["by_status"]["ready"] == 1
        assert out["by_status"]["blocked"] == 1
        assert out["by_status"]["done"] == 1

    def test_empty_queue_status_shows_zero_total(self, tmp_path, monkeypatch, capsys):
        _make_queue([], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--status"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["total"] == 0


class TestMaxFlag:
    def test_max_limits_dispatched_items(self, tmp_path, monkeypatch):
        items = [_ready_item(f"NW-MAX-{i:03d}", priority=100 - i) for i in range(5)]
        _make_queue(items, tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--max", "2"])
        assert rc == 0
        assert len(list((tmp_path / "missions").glob("*.md"))) == 2

    def test_max_0_dispatches_all(self, tmp_path, monkeypatch):
        items = [_ready_item(f"NW-ALL-{i:03d}") for i in range(3)]
        _make_queue(items, tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, ["--max", "0"])
        assert rc == 0
        assert len(list((tmp_path / "missions").glob("*.md"))) == 3


class TestQueuePersistence:
    def test_dispatched_items_become_in_progress(self, tmp_path, monkeypatch):
        _make_queue([_ready_item("NW-PERSIST")], tmp_path / "queue.json")
        _run(monkeypatch, tmp_path, [])
        data = json.loads((tmp_path / "queue.json").read_text())
        item = data["items"][0]
        assert item["status"] == "in-progress"
        assert "dispatched_at" in item
        assert "dispatch_id" in item

    def test_dry_run_leaves_queue_unchanged(self, tmp_path, monkeypatch):
        _make_queue([_ready_item("NW-DRY")], tmp_path / "queue.json")
        _run(monkeypatch, tmp_path, ["--dry-run"])
        data = json.loads((tmp_path / "queue.json").read_text())
        assert data["items"][0]["status"] == "ready"

    def test_dry_run_creates_no_mission_files(self, tmp_path, monkeypatch):
        _make_queue([_ready_item("NW-DRY2")], tmp_path / "queue.json")
        _run(monkeypatch, tmp_path, ["--dry-run"])
        assert not (tmp_path / "missions").exists()

    def test_no_ready_items_returns_0(self, tmp_path, monkeypatch):
        _make_queue([{**_ready_item("NW-BLK"), "status": "blocked"}], tmp_path / "queue.json")
        rc = _run(monkeypatch, tmp_path, [])
        assert rc == 0

    def test_priority_order_preserved_in_dispatch(self, tmp_path, monkeypatch):
        items = [
            _ready_item("NW-LOW", priority=10),
            _ready_item("NW-HIGH", priority=90),
            _ready_item("NW-MID", priority=50),
        ]
        _make_queue(items, tmp_path / "queue.json")
        _run(monkeypatch, tmp_path, ["--max", "1"])
        assert (tmp_path / "missions" / "NW-HIGH.md").exists()
        assert not (tmp_path / "missions" / "NW-LOW.md").exists()


class TestAcquireBranchLockIntegration:
    def test_success_creates_lock_file(self, tmp_path):
        item = {"id": "NW-001", "repo": "owner/repo", "pr_number": 42}
        lock_dir = str(tmp_path / "locks")
        result = dq.acquire_branch_lock(item, lock_dir, "test-holder")
        assert result is True
        assert (tmp_path / "locks" / "owner__repo__pr42.lock.json").exists()

    def test_no_pr_number_always_returns_true(self):
        item = {"id": "NW-001", "repo": "owner/repo"}  # no pr_number key
        result = dq.acquire_branch_lock(item, "/tmp/unused-locks", "test")
        assert result is True

    def test_pr_number_none_always_returns_true(self):
        item = {"id": "NW-001", "repo": "owner/repo", "pr_number": None}
        result = dq.acquire_branch_lock(item, "/tmp/unused-locks", "test")
        assert result is True

    def test_active_lock_returns_false(self, tmp_path):
        item = {"id": "NW-001", "repo": "owner/repo", "pr_number": 55}
        lock_dir = str(tmp_path / "locks")
        dq.acquire_branch_lock(item, lock_dir, "holder-1")
        result = dq.acquire_branch_lock(item, lock_dir, "holder-2")
        assert result is False

    def test_oserror_returns_false(self, tmp_path, monkeypatch):
        def raise_oserror(*args, **kwargs):
            raise OSError("binary not found")
        monkeypatch.setattr(dq.subprocess, "run", raise_oserror)
        item = {"id": "NW-001", "repo": "owner/repo", "pr_number": 77}
        result = dq.acquire_branch_lock(item, str(tmp_path), "test")
        assert result is False
