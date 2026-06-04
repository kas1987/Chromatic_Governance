"""Tests for scripts/dispatch_queue.py.

Covers:
- Agent routing table (all finding types)
- Stop condition detection (confidence, allowed_files, human gate, lock)
- Dispatch record structure completeness
- Only 'ready' items are dispatched
- Queue status updated to in-progress after successful dispatch
- Dispatch log written on dispatch
- Dry-run skips all writes
- Mission packet field presence
- Blocked items: no mission packet, correct stop conditions
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add the scripts directory to the module search path for direct import
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from dispatch_queue import (  # noqa: E402
    AGENT_BY_FINDING_TYPE,
    CONFIDENCE_MUTATION_THRESHOLD,
    STOP_ACTIVE_LOCK,
    STOP_CONFIDENCE_LOW,
    STOP_EMPTY_FILES,
    STOP_HUMAN_GATE,
    build_mission_packet,
    check_stop_conditions,
    dispatch_item,
    load_queue,
    resolve_agent,
    run_dispatch,
    save_queue,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_queue(tmp_path: Path) -> Path:
    """Path to a temporary queue JSON file (initially empty)."""
    p = tmp_path / "next-work.queue.json"
    return p


@pytest.fixture()
def tmp_dispatch_log(tmp_path: Path) -> Path:
    """Path to a temporary dispatch log JSONL file."""
    return tmp_path / "agent-dispatch-log.jsonl"


@pytest.fixture()
def tmp_lock_dir(tmp_path: Path) -> Path:
    """Path to a temporary lock directory."""
    d = tmp_path / "locks"
    d.mkdir()
    return d


def _make_item(
    *,
    item_id: str = "NW-TEST-001",
    status: str = "ready",
    finding_type: str = "bug_fix",
    confidence: int = 85,
    allowed_files: list[str] | None = None,
    owner_agent: str = "",
    repo: str = "owner/repo",
    pr_number: int = 42,
) -> dict:
    return {
        "id": item_id,
        "title": f"Test item {item_id}",
        "status": status,
        "priority": confidence,
        "repo": repo,
        "area": "review-intake",
        "specialties": ["testing"],
        "owner_agent": owner_agent,
        "depends_on": [],
        "blocked_by": [],
        "risk_level": "low",
        "confidence_score": confidence,
        "acceptance_checks": ["Run targeted tests"],
        "links": ["https://github.com/owner/repo/pull/42"],
        "finding_type": finding_type,
        "source_finding_id": "RF-AABBCCDDEE00",
        "allowed_files": allowed_files if allowed_files is not None else ["src/foo.py"],
        "pr_number": pr_number,
        "notes": "Test note.",
    }


# ---------------------------------------------------------------------------
# Agent routing table
# ---------------------------------------------------------------------------

class TestAgentRouting:
    """Routing table covers all finding types defined in the playbook."""

    @pytest.mark.parametrize("finding_type,expected_agent", [
        ("security", "Sentinel"),
        ("test_failure", "Auditor"),
        ("lint_style", "Janitor"),
        ("docs", "Archivist"),
        ("architecture", "Archivist"),
        ("bug_fix", "Sentinel"),
        ("repo_hygiene", "Janitor"),
        ("unclear", "Auditor"),
    ])
    def test_routing_table_covers_all_types(self, finding_type: str, expected_agent: str) -> None:
        assert AGENT_BY_FINDING_TYPE[finding_type] == expected_agent

    def test_resolve_agent_uses_routing_table(self) -> None:
        item = _make_item(finding_type="lint_style", owner_agent="")
        assert resolve_agent(item) == "Janitor"

    def test_resolve_agent_respects_explicit_owner(self) -> None:
        """An explicit owner_agent on the item overrides the routing table."""
        item = _make_item(finding_type="lint_style", owner_agent="SpecialBot")
        assert resolve_agent(item) == "SpecialBot"

    def test_resolve_agent_unknown_type_defaults_to_auditor(self) -> None:
        item = _make_item(finding_type="completely_unknown_xyz", owner_agent="")
        assert resolve_agent(item) == "Auditor"


# ---------------------------------------------------------------------------
# Stop conditions
# ---------------------------------------------------------------------------

class TestStopConditions:
    def test_clear_item_has_no_stops(self) -> None:
        item = _make_item(finding_type="bug_fix", confidence=85, allowed_files=["src/foo.py"])
        assert check_stop_conditions(item) == []

    def test_low_confidence_triggers_stop(self) -> None:
        item = _make_item(confidence=CONFIDENCE_MUTATION_THRESHOLD - 1)
        stops = check_stop_conditions(item)
        assert STOP_CONFIDENCE_LOW in stops

    def test_confidence_at_threshold_is_clear(self) -> None:
        item = _make_item(confidence=CONFIDENCE_MUTATION_THRESHOLD, allowed_files=["src/x.py"])
        stops = check_stop_conditions(item)
        assert STOP_CONFIDENCE_LOW not in stops

    def test_empty_allowed_files_triggers_stop_for_mutation_type(self) -> None:
        item = _make_item(finding_type="bug_fix", confidence=90, allowed_files=[])
        stops = check_stop_conditions(item)
        assert STOP_EMPTY_FILES in stops

    def test_empty_allowed_files_no_stop_for_docs(self) -> None:
        """docs findings are not mutation work; empty allowed_files is OK."""
        item = _make_item(finding_type="docs", confidence=90, allowed_files=[])
        stops = check_stop_conditions(item)
        assert STOP_EMPTY_FILES not in stops

    def test_security_triggers_human_gate(self) -> None:
        item = _make_item(finding_type="security", confidence=90, allowed_files=["src/auth.py"])
        stops = check_stop_conditions(item)
        assert STOP_HUMAN_GATE in stops

    def test_architecture_triggers_human_gate(self) -> None:
        item = _make_item(finding_type="architecture", confidence=90, allowed_files=[])
        stops = check_stop_conditions(item)
        assert STOP_HUMAN_GATE in stops

    def test_bug_fix_does_not_trigger_human_gate(self) -> None:
        item = _make_item(finding_type="bug_fix", confidence=90, allowed_files=["src/foo.py"])
        stops = check_stop_conditions(item)
        assert STOP_HUMAN_GATE not in stops

    def test_multiple_stops_can_coexist(self) -> None:
        """Low confidence + security = both stops triggered."""
        item = _make_item(finding_type="security", confidence=50, allowed_files=["src/auth.py"])
        stops = check_stop_conditions(item)
        assert STOP_CONFIDENCE_LOW in stops
        assert STOP_HUMAN_GATE in stops


# ---------------------------------------------------------------------------
# dispatch_item: structure and side-effects
# ---------------------------------------------------------------------------

class TestDispatchItem:
    def test_dispatched_record_has_required_fields(self, tmp_path: Path) -> None:
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item()
        rec = dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=True)

        required = {
            "dispatch_id", "task_id", "source_finding_id", "agent", "status",
            "repo", "started_at", "links", "stop_conditions_triggered",
            "risk_level", "confidence_score",
        }
        for field in required:
            assert field in rec, f"Missing field: {field}"

    def test_dispatched_item_has_mission_packet(self, tmp_path: Path) -> None:
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item()
        rec = dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=True)
        assert rec["status"] == "dispatched"
        assert "mission_packet" in rec
        assert "Task ID" in rec["mission_packet"]
        assert "Allowed Files" in rec["mission_packet"]
        assert "Acceptance Checks" in rec["mission_packet"]
        assert "Stop Conditions" in rec["mission_packet"]

    def test_blocked_item_has_no_mission_packet(self, tmp_path: Path) -> None:
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item(finding_type="security", confidence=50, allowed_files=["src/a.py"])
        rec = dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=True)
        assert rec["status"] == "blocked"
        assert "mission_packet" not in rec

    def test_dispatch_log_written_when_not_dry_run(self, tmp_path: Path) -> None:
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item()
        dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=False)
        assert log.exists()
        lines = [l for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["task_id"] == item["id"]

    def test_dispatch_log_not_written_in_dry_run(self, tmp_path: Path) -> None:
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item()
        dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=True)
        assert not log.exists()

    def test_active_lock_triggers_stop(self, tmp_path: Path) -> None:
        from datetime import timedelta
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item(repo="owner/repo", pr_number=42)

        # Write an unexpired lock file
        from dispatch_queue import utc_now
        from datetime import datetime, timezone
        now_dt = datetime.now(timezone.utc)
        expires = (now_dt + timedelta(minutes=30)).isoformat().replace("+00:00", "Z")
        lock_data = {
            "lock_id": "LOCK-owner-repo-PR42",
            "repo": "owner/repo",
            "pr_number": 42,
            "expires_at": expires,
        }
        lock_file = lock_dir / "owner__repo__pr42.lock.json"
        lock_file.write_text(json.dumps(lock_data))

        rec = dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=True)
        assert rec["status"] == "blocked"
        assert STOP_ACTIVE_LOCK in rec["stop_conditions_triggered"]

    def test_expired_lock_does_not_block(self, tmp_path: Path) -> None:
        from datetime import timedelta, datetime, timezone
        lock_dir = tmp_path / "locks"
        lock_dir.mkdir()
        log = tmp_path / "dispatch.jsonl"
        item = _make_item(repo="owner/repo", pr_number=42)

        # Write an expired lock file
        expired = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        lock_data = {
            "lock_id": "LOCK-owner-repo-PR42",
            "repo": "owner/repo",
            "pr_number": 42,
            "expires_at": expired,
        }
        lock_file = lock_dir / "owner__repo__pr42.lock.json"
        lock_file.write_text(json.dumps(lock_data))

        rec = dispatch_item(item, lock_dir=lock_dir, dispatch_log=log, dry_run=True)
        assert STOP_ACTIVE_LOCK not in rec["stop_conditions_triggered"]


# ---------------------------------------------------------------------------
# run_dispatch: queue filtering and status mutation
# ---------------------------------------------------------------------------

class TestRunDispatch:
    def test_only_ready_items_dispatched(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        items = [
            _make_item(item_id="NW-001", status="ready"),
            _make_item(item_id="NW-002", status="blocked"),
            _make_item(item_id="NW-003", status="done"),
            _make_item(item_id="NW-004", status="needs-human-decision"),
        ]
        save_queue(q_path, {"items": items})

        records = run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
            dry_run=True,
        )
        assert len(records) == 1
        assert records[0]["task_id"] == "NW-001"

    def test_item_id_filter_targets_single_item(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        items = [
            _make_item(item_id="NW-001", status="ready"),
            _make_item(item_id="NW-002", status="ready"),
        ]
        save_queue(q_path, {"items": items})

        records = run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
            item_id="NW-002",
            dry_run=True,
        )
        assert len(records) == 1
        assert records[0]["task_id"] == "NW-002"

    def test_queue_item_status_updated_to_in_progress(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        item = _make_item(item_id="NW-001", status="ready")
        save_queue(q_path, {"items": [item]})

        run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
            dry_run=False,
        )

        updated = load_queue(q_path)
        assert updated["items"][0]["status"] == "in-progress"
        assert "dispatched_at" in updated["items"][0]
        assert "dispatch_id" in updated["items"][0]

    def test_blocked_item_status_not_changed(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        # security + low confidence: will be blocked
        item = _make_item(
            item_id="NW-001", status="ready",
            finding_type="security", confidence=50, allowed_files=["src/auth.py"]
        )
        save_queue(q_path, {"items": [item]})

        run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
            dry_run=False,
        )

        updated = load_queue(q_path)
        assert updated["items"][0]["status"] == "ready"

    def test_empty_queue_returns_empty_list(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        save_queue(q_path, {"items": []})

        records = run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
        )
        assert records == []

    def test_nonexistent_queue_returns_empty_list(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "does_not_exist.json"
        records = run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
        )
        assert records == []

    def test_dispatch_log_has_one_record_per_dispatched_item(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        items = [
            _make_item(item_id="NW-001", status="ready"),
            _make_item(item_id="NW-002", status="ready"),
        ]
        save_queue(q_path, {"items": items})

        run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
            dry_run=False,
        )

        lines = [ln for ln in tmp_dispatch_log.read_text().splitlines() if ln.strip()]
        assert len(lines) == 2
        ids = {json.loads(ln)["task_id"] for ln in lines}
        assert ids == {"NW-001", "NW-002"}

    def test_dry_run_does_not_mutate_queue_or_log(
        self, tmp_path: Path, tmp_dispatch_log: Path, tmp_lock_dir: Path
    ) -> None:
        q_path = tmp_path / "queue.json"
        item = _make_item(item_id="NW-001", status="ready")
        save_queue(q_path, {"items": [item]})

        run_dispatch(
            queue_path=q_path,
            dispatch_log=tmp_dispatch_log,
            lock_dir=tmp_lock_dir,
            dry_run=True,
        )

        assert not tmp_dispatch_log.exists()
        still_ready = load_queue(q_path)["items"][0]["status"]
        assert still_ready == "ready"


# ---------------------------------------------------------------------------
# Mission packet content
# ---------------------------------------------------------------------------

class TestMissionPacket:
    def test_packet_contains_task_id(self) -> None:
        item = _make_item(item_id="NW-PACKET-001")
        packet = build_mission_packet(item, "Sentinel")
        assert "NW-PACKET-001" in packet

    def test_packet_contains_agent(self) -> None:
        item = _make_item()
        packet = build_mission_packet(item, "Archivist")
        assert "Archivist" in packet

    def test_packet_contains_allowed_files(self) -> None:
        item = _make_item(allowed_files=["src/bar.py", "src/baz.py"])
        packet = build_mission_packet(item, "Sentinel")
        assert "src/bar.py" in packet
        assert "src/baz.py" in packet

    def test_packet_contains_forbidden_files_note(self) -> None:
        item = _make_item()
        packet = build_mission_packet(item, "Sentinel")
        assert "Forbidden Files" in packet

    def test_packet_contains_confidence(self) -> None:
        item = _make_item(confidence=88)
        packet = build_mission_packet(item, "Auditor")
        assert "88/100" in packet

    def test_packet_required_output_section_present(self) -> None:
        item = _make_item()
        packet = build_mission_packet(item, "Sentinel")
        assert "Required Output" in packet
        assert "Patch or explanation" in packet


# ---------------------------------------------------------------------------
# load_queue robustness
# ---------------------------------------------------------------------------

class TestLoadQueue:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        q = load_queue(tmp_path / "missing.json")
        assert q == {"items": []}

    def test_bare_list_normalised(self, tmp_path: Path) -> None:
        p = tmp_path / "q.json"
        p.write_text(json.dumps([{"id": "NW-X", "status": "ready"}]))
        q = load_queue(p)
        assert "items" in q
        assert q["items"][0]["id"] == "NW-X"

    def test_invalid_json_raises_value_error(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("{ not valid json }")
        with pytest.raises(ValueError, match="not valid JSON"):
            load_queue(p)
