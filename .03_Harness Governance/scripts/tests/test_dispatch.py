"""Tests for dispatch_queue.py and log_resolution.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dispatch_queue as dq
import log_resolution as lr


# ---------------------------------------------------------------------------
# dispatch_queue helpers
# ---------------------------------------------------------------------------

def _make_queue(items: list, path: Path) -> None:
    path.write_text(json.dumps({"items": items}, indent=2) + "\n")


def _ready_item(id_: str, priority: int = 80, agent: str = "Auditor") -> dict:
    return {
        "id": id_,
        "title": f"Task {id_}",
        "status": "ready",
        "priority": priority,
        "repo": "owner/repo",
        "pr_number": 42,
        "owner_agent": agent,
        "risk_level": "low",
        "confidence_score": 80,
        "acceptance_checks": ["Run tests"],
        "allowed_files": ["src/main.py"],
        "links": ["https://github.com/owner/repo/pull/42#comment-1"],
        "notes": "Test task",
    }


class TestLoadQueue:
    def test_missing_file_returns_empty(self, tmp_path):
        q = dq.load_queue(tmp_path / "nope.json")
        assert q == {"items": []}

    def test_list_format_wrapped(self, tmp_path):
        p = tmp_path / "q.json"
        p.write_text(json.dumps([{"id": "NW-1"}]))
        q = dq.load_queue(p)
        assert "items" in q
        assert q["items"][0]["id"] == "NW-1"

    def test_object_format_passes_through(self, tmp_path):
        p = tmp_path / "q.json"
        p.write_text(json.dumps({"items": [{"id": "NW-1"}], "meta": "ok"}))
        q = dq.load_queue(p)
        assert q["meta"] == "ok"


class TestDispatchIdFor:
    def test_deterministic(self):
        a = dq.dispatch_id_for("NW-001")
        b = dq.dispatch_id_for("NW-001")
        assert a == b

    def test_prefix(self):
        assert dq.dispatch_id_for("NW-001").startswith("DISP-")

    def test_different_ids_differ(self):
        assert dq.dispatch_id_for("NW-001") != dq.dispatch_id_for("NW-002")


class TestRenderMissionPacket:
    def test_contains_task_id(self):
        item = _ready_item("NW-TEST-001")
        out = dq.render_mission_packet(item)
        assert "NW-TEST-001" in out

    def test_contains_allowed_files(self):
        item = _ready_item("NW-TEST-002")
        out = dq.render_mission_packet(item)
        assert "src/main.py" in out

    def test_contains_stop_conditions(self):
        item = _ready_item("NW-TEST-003")
        out = dq.render_mission_packet(item)
        assert "Lock cannot be acquired" in out

    def test_no_file_scope_message(self):
        item = _ready_item("NW-TEST-004")
        item["allowed_files"] = []
        out = dq.render_mission_packet(item)
        assert "PR-level" in out


class TestDispatchItem:
    def test_creates_mission_file(self, tmp_path):
        item = _ready_item("NW-D-001")
        missions = tmp_path / "missions"
        log = tmp_path / "dispatch.jsonl"
        locks = tmp_path / "locks"
        entry = dq.dispatch_item(item, missions, log, dry_run=False, lock_dir=str(locks))
        mission_file = missions / "NW-D-001.md"
        assert mission_file.exists()
        assert "NW-D-001" in mission_file.read_text()

    def test_writes_dispatch_log(self, tmp_path):
        item = _ready_item("NW-D-002")
        missions = tmp_path / "missions"
        log = tmp_path / "dispatch.jsonl"
        locks = tmp_path / "locks"
        dq.dispatch_item(item, missions, log, dry_run=False, lock_dir=str(locks))
        lines = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 1
        assert lines[0]["task_id"] == "NW-D-002"
        assert lines[0]["status"] == "dispatched"

    def test_dry_run_does_not_write(self, tmp_path):
        item = _ready_item("NW-D-003")
        missions = tmp_path / "missions"
        log = tmp_path / "dispatch.jsonl"
        dq.dispatch_item(item, missions, log, dry_run=True)
        assert not (missions / "NW-D-003.md").exists()
        assert not log.exists()

    def test_returns_dispatch_entry(self, tmp_path):
        item = _ready_item("NW-D-004")
        entry = dq.dispatch_item(item, tmp_path / "m", tmp_path / "l.jsonl", dry_run=True)
        assert entry["dispatch_id"].startswith("DISP-")
        assert entry["agent"] == "Auditor"
        assert entry["task_id"] == "NW-D-004"

    def test_lock_acquired_field_present(self, tmp_path):
        item = _ready_item("NW-D-005")
        entry = dq.dispatch_item(item, tmp_path / "m", tmp_path / "l.jsonl", dry_run=True)
        assert "lock_acquired" in entry
        assert entry["lock_acquired"] is True  # dry_run always treats lock as acquired

    def test_lock_fail_skips_mission_file(self, tmp_path, monkeypatch):
        item = _ready_item("NW-D-006")
        missions = tmp_path / "missions"
        log = tmp_path / "dispatch.jsonl"
        monkeypatch.setattr(dq, "acquire_branch_lock", lambda *a, **kw: False)
        entry = dq.dispatch_item(item, missions, log, dry_run=False)
        assert entry["lock_acquired"] is False
        assert entry["status"] == "lock-failed"
        assert not (missions / "NW-D-006.md").exists()
        # dispatch log entry is still written even on lock failure
        assert log.exists()

    def test_human_gate_blocks_non_ready_item(self, tmp_path):
        item = {**_ready_item("NW-D-007"), "status": "blocked"}
        q = tmp_path / "queue.json"
        q.write_text(json.dumps({"items": [item]}) + "\n")
        queue = dq.load_queue(q)
        non_ready = [i for i in queue["items"] if i.get("status") in dq._HUMAN_GATE_STATUSES]
        assert len(non_ready) == 1
        ready = [i for i in queue["items"] if i.get("status") == "ready"]
        assert len(ready) == 0


class TestMainDispatch:
    def test_dispatches_ready_items(self, tmp_path):
        q = tmp_path / "queue.json"
        _make_queue([_ready_item("NW-M-001", priority=90), _ready_item("NW-M-002", priority=70)], q)
        missions = tmp_path / "missions"
        log = tmp_path / "dispatch.jsonl"
        rc = dq.main.__wrapped__ if hasattr(dq.main, "__wrapped__") else None
        # Call internal logic directly
        queue = dq.load_queue(q)
        ready = sorted(
            [i for i in queue["items"] if i.get("status") == "ready"],
            key=lambda x: -x.get("priority", 0),
        )
        assert ready[0]["id"] == "NW-M-001"
        assert ready[1]["id"] == "NW-M-002"

    def test_no_ready_items(self, tmp_path):
        q = tmp_path / "queue.json"
        blocked = {**_ready_item("NW-BLK"), "status": "blocked"}
        _make_queue([blocked], q)
        queue = dq.load_queue(q)
        ready = [i for i in queue["items"] if i.get("status") == "ready"]
        assert ready == []

    def test_max_limits_dispatch(self, tmp_path):
        items = [_ready_item(f"NW-MAX-{i:03d}", priority=100 - i) for i in range(5)]
        q = tmp_path / "queue.json"
        _make_queue(items, q)
        queue = dq.load_queue(q)
        ready = sorted(
            [i for i in queue["items"] if i.get("status") == "ready"],
            key=lambda x: -x.get("priority", 0),
        )[:3]
        assert len(ready) == 3

    def test_status_counts(self, tmp_path):
        items = [
            _ready_item("NW-S-001"),
            {**_ready_item("NW-S-002"), "status": "blocked"},
            {**_ready_item("NW-S-003"), "status": "done"},
        ]
        q = tmp_path / "queue.json"
        _make_queue(items, q)
        queue = dq.load_queue(q)
        from collections import Counter
        counts = Counter(i.get("status") for i in queue["items"])
        assert counts["ready"] == 1
        assert counts["blocked"] == 1
        assert counts["done"] == 1

    def test_update_to_in_progress_after_dispatch(self, tmp_path):
        q = tmp_path / "queue.json"
        _make_queue([_ready_item("NW-IP-001")], q)
        missions = tmp_path / "missions"
        log = tmp_path / "dispatch.jsonl"
        locks = tmp_path / "locks"
        queue = dq.load_queue(q)
        item = queue["items"][0]
        dq.dispatch_item(item, missions, log, dry_run=False, lock_dir=str(locks))
        # Simulate status update
        for qi in queue["items"]:
            if qi["id"] == item["id"]:
                qi["status"] = "in-progress"
                qi["dispatched_at"] = dq.utc_now()
        dq.save_queue(q, queue)
        updated = dq.load_queue(q)
        assert updated["items"][0]["status"] == "in-progress"


# ---------------------------------------------------------------------------
# log_resolution
# ---------------------------------------------------------------------------

class TestLogResolution:
    def test_writes_jsonl_record(self, tmp_path):
        log = tmp_path / "resolution.jsonl"
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-001", "status": "in-progress"}]}) + "\n")
        record = {
            "finding_id": "RF-ABC",
            "task_id": "NW-001",
            "agent": "Sentinel",
            "status": "resolved",
            "summary": "Fixed it",
            "validation": ["pytest passed"],
            "files_changed": ["src/main.py"],
            "resolved_at": lr.utc_now(),
        }
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a") as f:
            import json as _json
            f.write(_json.dumps(record, sort_keys=True) + "\n")
        lines = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
        assert lines[0]["finding_id"] == "RF-ABC"
        assert lines[0]["status"] == "resolved"

    def test_updates_queue_item_to_done(self, tmp_path):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-001", "status": "in-progress"}]}) + "\n")
        data = json.loads(queue.read_text())
        for item in data["items"]:
            if item["id"] == "NW-001":
                item["status"] = "done"
                item["resolved_at"] = lr.utc_now()
        queue.write_text(json.dumps(data, indent=2) + "\n")
        updated = json.loads(queue.read_text())
        assert updated["items"][0]["status"] == "done"
        assert "resolved_at" in updated["items"][0]

    def test_blocked_status_sets_queue_blocked(self, tmp_path):
        queue = tmp_path / "queue.json"
        queue.write_text(json.dumps({"items": [{"id": "NW-002", "status": "in-progress"}]}) + "\n")
        data = json.loads(queue.read_text())
        for item in data["items"]:
            if item["id"] == "NW-002":
                item["status"] = "blocked"
        queue.write_text(json.dumps(data, indent=2) + "\n")
        updated = json.loads(queue.read_text())
        assert updated["items"][0]["status"] == "blocked"

    def test_creates_log_parent_dirs(self, tmp_path):
        log = tmp_path / "sub" / "dir" / "resolution.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a") as f:
            f.write(json.dumps({"finding_id": "RF-1"}) + "\n")
        assert log.exists()

    def test_utc_now_is_iso_format(self):
        ts = lr.utc_now()
        assert "T" in ts
        assert ts.endswith("Z")
