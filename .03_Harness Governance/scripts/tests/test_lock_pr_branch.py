"""Tests for lock_pr_branch.py — acquire, release, status, TTL, lock path."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lock_pr_branch as lb


class TestLockPath:
    def test_slash_replaced_with_double_underscore(self):
        p = lb.lock_path(Path("/locks"), "owner/repo", 42)
        assert p.name == "owner__repo__pr42.lock.json"

    def test_lives_inside_lock_dir(self):
        p = lb.lock_path(Path("/my/locks"), "a/b", 1)
        assert p.parent == Path("/my/locks")

    def test_different_prs_produce_different_paths(self):
        p1 = lb.lock_path(Path("/locks"), "owner/repo", 1)
        p2 = lb.lock_path(Path("/locks"), "owner/repo", 2)
        assert p1 != p2


class TestAcquire:
    def test_creates_lock_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "10",
            "--lock-dir", str(tmp_path),
        ])
        rc = lb.main()
        assert rc == 0
        assert (tmp_path / "owner__repo__pr10.lock.json").exists()

    def test_lock_file_content_shape(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "10",
            "--holder", "tester", "--queue-item-id", "NW-001",
            "--lock-dir", str(tmp_path),
        ])
        lb.main()
        data = json.loads((tmp_path / "owner__repo__pr10.lock.json").read_text())
        assert data["repo"] == "owner/repo"
        assert data["pr_number"] == 10
        assert data["holder"] == "tester"
        assert data["queue_item_id"] == "NW-001"
        assert "expires_at" in data
        assert "started_at" in data

    def test_active_lock_blocks_second_acquire(self, tmp_path, monkeypatch):
        argv = [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "7",
            "--lock-dir", str(tmp_path),
        ]
        monkeypatch.setattr(sys, "argv", argv)
        assert lb.main() == 0
        monkeypatch.setattr(sys, "argv", argv)
        assert lb.main() == 2

    def test_expired_lock_is_reacquired(self, tmp_path, monkeypatch):
        lock_file = lb.lock_path(tmp_path, "owner/repo", 5)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        expired = datetime.now(timezone.utc) - timedelta(minutes=60)
        lock_file.write_text(json.dumps({
            "lock_id": "LOCK-owner-repo-PR5",
            "repo": "owner/repo", "pr_number": 5,
            "branch": "unknown", "holder": "old",
            "queue_item_id": "NW-OLD",
            "started_at": expired.isoformat().replace("+00:00", "Z"),
            "expires_at": expired.isoformat().replace("+00:00", "Z"),
        }))
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "5",
            "--lock-dir", str(tmp_path),
        ])
        assert lb.main() == 0

    def test_ttl_stored_in_lock_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "20",
            "--ttl-minutes", "15",
            "--lock-dir", str(tmp_path),
        ])
        lb.main()
        data = json.loads((tmp_path / "owner__repo__pr20.lock.json").read_text())
        started = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
        expires = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        assert abs((expires - started).total_seconds() - 15 * 60) < 5

    def test_lock_id_contains_repo_and_pr(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "acme/widget", "--pr-number", "99",
            "--lock-dir", str(tmp_path),
        ])
        lb.main()
        data = json.loads((tmp_path / "acme__widget__pr99.lock.json").read_text())
        assert "acme" in data["lock_id"]
        assert "99" in data["lock_id"]


class TestRelease:
    def test_removes_existing_lock_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "30",
            "--lock-dir", str(tmp_path),
        ])
        lb.main()
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "release",
            "--repo", "owner/repo", "--pr-number", "30",
            "--lock-dir", str(tmp_path),
        ])
        rc = lb.main()
        assert rc == 0
        assert not (tmp_path / "owner__repo__pr30.lock.json").exists()

    def test_release_when_no_lock_is_harmless(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "release",
            "--repo", "owner/repo", "--pr-number", "99",
            "--lock-dir", str(tmp_path),
        ])
        rc = lb.main()
        assert rc == 0
        assert "already unlocked" in capsys.readouterr().out

    def test_after_release_reacquire_succeeds(self, tmp_path, monkeypatch):
        argv_acquire = [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "40",
            "--lock-dir", str(tmp_path),
        ]
        argv_release = [
            "lock_pr_branch.py", "release",
            "--repo", "owner/repo", "--pr-number", "40",
            "--lock-dir", str(tmp_path),
        ]
        monkeypatch.setattr(sys, "argv", argv_acquire)
        lb.main()
        monkeypatch.setattr(sys, "argv", argv_release)
        lb.main()
        monkeypatch.setattr(sys, "argv", argv_acquire)
        assert lb.main() == 0


class TestStatus:
    def test_status_unlocked_prints_unlocked(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "status",
            "--repo", "owner/repo", "--pr-number", "50",
            "--lock-dir", str(tmp_path),
        ])
        rc = lb.main()
        assert rc == 0
        assert "unlocked" in capsys.readouterr().out

    def test_status_locked_prints_lock_json(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "acquire",
            "--repo", "owner/repo", "--pr-number", "60",
            "--lock-dir", str(tmp_path),
        ])
        lb.main()
        capsys.readouterr()
        monkeypatch.setattr(sys, "argv", [
            "lock_pr_branch.py", "status",
            "--repo", "owner/repo", "--pr-number", "60",
            "--lock-dir", str(tmp_path),
        ])
        lb.main()
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["repo"] == "owner/repo"
        assert data["pr_number"] == 60
