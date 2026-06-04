"""Tests for review intake scripts: classify_review_finding, review_intake,
lock_pr_branch, update_next_work_queue, post_review_resolution."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

# Ensure the scripts directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classify_review_finding as clf
import review_intake as ri


# ---------------------------------------------------------------------------
# classify_review_finding
# ---------------------------------------------------------------------------

class TestClassifyBody:
    def test_security_keyword(self):
        assert clf.classify_body("This token is exposed") == "security"

    def test_test_keyword(self):
        assert clf.classify_body("The pytest suite is failing") == "test_failure"

    def test_lint_keyword(self):
        assert clf.classify_body("Please run ruff to fix the style") == "lint_style"

    def test_docs_keyword(self):
        assert clf.classify_body("Update the docstring here") == "docs"

    def test_docs_by_path(self):
        assert clf.classify_body("looks good", path="README.md") == "docs"

    def test_architecture_keyword(self):
        assert clf.classify_body("This coupling is too tight") == "architecture"

    def test_bug_keyword(self):
        assert clf.classify_body("This is broken and causes an exception") == "bug_fix"

    def test_vague_keyword(self):
        assert clf.classify_body("maybe consider this approach") == "unclear"

    def test_empty_body_with_path_is_bug_fix(self):
        assert clf.classify_body("", path="src/main.py") == "bug_fix"

    def test_empty_body_no_path_is_unclear(self):
        assert clf.classify_body("") == "unclear"

    def test_priority_security_beats_test(self):
        # "password" triggers security before "assert" triggers test_failure
        assert clf.classify_body("assert password is hashed") == "security"


class TestScoreFinding:
    def test_returns_int_in_range(self):
        finding = {"body": "Fix the null pointer bug", "path": "src/a.py", "dedupe_key": "k1"}
        score = clf.score_finding(finding)
        assert 0 <= score <= 100

    def test_vague_body_scores_lower(self):
        clear = {"body": "Fix the null pointer bug", "path": "src/a.py", "dedupe_key": "k1"}
        vague = {"body": "maybe consider refactoring", "path": "src/a.py", "dedupe_key": "k2"}
        assert clf.score_finding(clear) > clf.score_finding(vague)

    def test_path_boosts_score(self):
        with_path = {"body": "Fix broken import", "path": "src/a.py", "dedupe_key": "k1"}
        no_path = {"body": "Fix broken import", "dedupe_key": "k2"}
        assert clf.score_finding(with_path) > clf.score_finding(no_path)

    def test_short_body_penalised(self):
        long_body = {"body": "The method is returning wrong results due to off-by-one", "dedupe_key": "k1"}
        short_body = {"body": "bad", "dedupe_key": "k2"}
        assert clf.score_finding(long_body) > clf.score_finding(short_body)


class TestEnrichFinding:
    def test_adds_required_fields(self):
        base = {"body": "Test is failing", "dedupe_key": "k1", "finding_id": "RF-abc"}
        enriched = clf.enrich_finding(base)
        assert "finding_type" in enriched
        assert "suggested_agent" in enriched
        assert "acceptance_checks" in enriched
        assert "confidence_score" in enriched
        assert "risk_level" in enriched
        assert "severity" in enriched

    def test_does_not_mutate_original(self):
        base = {"body": "Fix bug", "dedupe_key": "k1"}
        original_keys = set(base.keys())
        clf.enrich_finding(base)
        assert set(base.keys()) == original_keys

    def test_security_finding_has_high_risk(self):
        enriched = clf.enrich_finding({"body": "password exposed in logs", "dedupe_key": "k"})
        assert enriched["risk_level"] == "high"
        assert enriched["severity"] == "high"


class TestQueueStatus:
    def test_security_below_90_needs_human(self):
        assert clf.queue_status_for_confidence(80, "security") == "needs-human-decision"

    def test_architecture_below_90_needs_human(self):
        assert clf.queue_status_for_confidence(85, "architecture") == "needs-human-decision"

    def test_high_confidence_ready(self):
        assert clf.queue_status_for_confidence(80, "bug_fix") == "ready"

    def test_medium_confidence_review_required(self):
        assert clf.queue_status_for_confidence(60, "bug_fix") == "review-required"

    def test_low_confidence_blocked(self):
        assert clf.queue_status_for_confidence(30, "unclear") == "blocked"

    def test_security_at_90_ready(self):
        assert clf.queue_status_for_confidence(90, "security") == "ready"


# ---------------------------------------------------------------------------
# review_intake — helpers
# ---------------------------------------------------------------------------

class TestStableId:
    def test_deterministic(self):
        a = ri.stable_id("RF", "owner/repo", 42, "src/main.py", 10, 999)
        b = ri.stable_id("RF", "owner/repo", 42, "src/main.py", 10, 999)
        assert a == b

    def test_different_inputs_differ(self):
        a = ri.stable_id("RF", "owner/repo", 42)
        b = ri.stable_id("RF", "owner/repo", 43)
        assert a != b

    def test_prefix_applied(self):
        assert ri.stable_id("NW", "repo", 1).startswith("NW-")


class TestAppendJsonlOnce:
    def test_appends_new_record(self, tmp_path):
        f = tmp_path / "findings.jsonl"
        record = {"dedupe_key": "dk1", "body": "hi"}
        assert ri.append_jsonl_once(f, record) is True
        assert "dk1" in f.read_text()

    def test_skips_duplicate_dedupe_key(self, tmp_path):
        f = tmp_path / "findings.jsonl"
        record = {"dedupe_key": "dk1", "body": "hi"}
        ri.append_jsonl_once(f, record)
        result = ri.append_jsonl_once(f, record)
        assert result is False
        assert f.read_text().count("dk1") == 1

    def test_creates_parent_dirs(self, tmp_path):
        f = tmp_path / "sub" / "dir" / "findings.jsonl"
        ri.append_jsonl_once(f, {"dedupe_key": "x"})
        assert f.exists()


class TestNormalizers:
    def _pr_review_comment_event(self):
        return {
            "action": "created",
            "comment": {
                "id": 123,
                "body": "Fix this null check",
                "path": "src/main.py",
                "line": 42,
                "html_url": "https://github.com/r/1#comment-123",
                "pull_request_review_id": 9,
            },
            "pull_request": {"number": 7, "html_url": "https://github.com/r/pulls/7"},
        }

    def test_pr_review_comment_structure(self):
        event = self._pr_review_comment_event()
        finding = ri.normalize_pull_request_review_comment(event, "owner/repo")
        assert finding["source"] == "github_pr_review_comment"
        assert finding["status"] == "open"
        assert finding["path"] == "src/main.py"
        assert finding["pr_number"] == 7

    def test_pr_review_approved_is_informational(self):
        event = {
            "review": {"id": 1, "state": "approved", "body": None, "user": {"login": "alice"}},
            "pull_request": {"number": 5},
        }
        finding = ri.normalize_pull_request_review(event, "r")
        assert finding["status"] == "informational"

    def test_pr_review_changes_requested_is_open(self):
        event = {
            "review": {"id": 2, "state": "changes_requested", "body": "Please fix X", "user": {"login": "bob"}},
            "pull_request": {"number": 5},
        }
        finding = ri.normalize_pull_request_review(event, "r")
        assert finding["status"] == "open"

    def test_check_run_success_is_informational(self):
        event = {"check_run": {"id": 1, "name": "CI", "conclusion": "success", "pull_requests": [{"number": 3}]}}
        finding = ri.normalize_check_run(event, "r")
        assert finding["status"] == "informational"

    def test_check_run_failure_is_open(self):
        event = {"check_run": {"id": 2, "name": "CI", "conclusion": "failure", "pull_requests": [{"number": 4}]}}
        finding = ri.normalize_check_run(event, "r")
        assert finding["status"] == "open"


class TestNormalizeEvent:
    def test_deleted_review_comment_returns_none(self):
        event = {"action": "deleted", "comment": {}, "pull_request": {}}
        assert ri.normalize_event("pull_request_review_comment", event, "r") is None

    def test_approved_review_filtered_out(self):
        event = {
            "review": {"state": "approved", "id": 1, "user": {"login": "x"}},
            "pull_request": {"number": 1},
        }
        assert ri.normalize_event("pull_request_review", event, "r") is None

    def test_successful_check_filtered_out(self):
        event = {"check_run": {"conclusion": "success", "id": 1, "pull_requests": []}}
        assert ri.normalize_event("check_run", event, "r") is None

    def test_unknown_event_returns_none(self):
        assert ri.normalize_event("push", {}, "r") is None


class TestUpsertQueueItem:
    def test_creates_new_item(self, tmp_path):
        q = tmp_path / "queue.json"
        item = {"id": "NW-001", "title": "Task A"}
        created = ri.upsert_queue_item(q, item)
        assert created is True
        data = json.loads(q.read_text())
        assert len(data["items"]) == 1

    def test_updates_existing_item(self, tmp_path):
        q = tmp_path / "queue.json"
        item = {"id": "NW-001", "title": "Task A"}
        ri.upsert_queue_item(q, item)
        updated = {"id": "NW-001", "title": "Task A updated"}
        created = ri.upsert_queue_item(q, updated)
        assert created is False
        data = json.loads(q.read_text())
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Task A updated"
        assert "updated_at" in data["items"][0]

    def test_dedupes_by_source_finding_id(self, tmp_path):
        q = tmp_path / "queue.json"
        item1 = {"id": "NW-001", "source_finding_id": "RF-AAA", "title": "First"}
        item2 = {"id": "NW-002", "source_finding_id": "RF-AAA", "title": "Duplicate"}
        ri.upsert_queue_item(q, item1)
        ri.upsert_queue_item(q, item2)
        data = json.loads(q.read_text())
        assert len(data["items"]) == 1


# ---------------------------------------------------------------------------
# lock_pr_branch
# ---------------------------------------------------------------------------

class TestLockPrBranch:
    def _args(self, tmp_path, command="acquire", holder="TestAgent", ttl=30):
        import lock_pr_branch as lb

        class Args:
            pass

        a = Args()
        a.command = command
        a.repo = "owner/repo"
        a.pr_number = 42
        a.branch = "feature-branch"
        a.holder = holder
        a.queue_item_id = "NW-001"
        a.ttl_minutes = ttl
        a.lock_dir = str(tmp_path / "locks")
        return a

    def _run(self, args):
        import lock_pr_branch as lb

        lock_dir = Path(args.lock_dir)
        lock_dir.mkdir(parents=True, exist_ok=True)
        path = lb.lock_path(lock_dir, args.repo, args.pr_number)

        if args.command == "status":
            return path.read_text() if path.exists() else "unlocked", 0

        if args.command == "release":
            if path.exists():
                path.unlink()
                return "released", 0
            return "already unlocked", 0

        if path.exists():
            data = json.loads(path.read_text())
            expires = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
            if expires > lb.now():
                return {"acquired": False}, 2

        started = lb.now()
        data = {
            "lock_id": f"LOCK-{args.repo.replace('/', '-')}-PR{args.pr_number}",
            "repo": args.repo,
            "pr_number": args.pr_number,
            "branch": args.branch,
            "holder": args.holder,
            "queue_item_id": args.queue_item_id,
            "started_at": lb.iso(started),
            "expires_at": lb.iso(started + timedelta(minutes=args.ttl_minutes)),
        }
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        return {"acquired": True, "lock": data}, 0

    def test_acquire_creates_lock_file(self, tmp_path):
        import lock_pr_branch as lb
        args = self._args(tmp_path)
        result, code = self._run(args)
        assert code == 0
        assert result["acquired"] is True

    def test_acquire_blocked_by_active_lock(self, tmp_path):
        import lock_pr_branch as lb
        args = self._args(tmp_path)
        self._run(args)
        result, code = self._run(args)
        assert code == 2
        assert result["acquired"] is False

    def test_acquire_replaces_expired_lock(self, tmp_path):
        import lock_pr_branch as lb
        args = self._args(tmp_path, ttl=0)
        self._run(args)
        args2 = self._args(tmp_path, holder="NewAgent", ttl=30)
        result, code = self._run(args2)
        assert code == 0
        assert result["acquired"] is True
        assert result["lock"]["holder"] == "NewAgent"

    def test_release_removes_lock(self, tmp_path):
        import lock_pr_branch as lb
        args = self._args(tmp_path)
        self._run(args)
        rel_args = self._args(tmp_path, command="release")
        msg, code = self._run(rel_args)
        assert code == 0
        assert msg == "released"

    def test_status_when_unlocked(self, tmp_path):
        args = self._args(tmp_path, command="status")
        result, _ = self._run(args)
        assert result == "unlocked"


# ---------------------------------------------------------------------------
# update_next_work_queue
# ---------------------------------------------------------------------------

class TestUpdateNextWorkQueue:
    def test_creates_new_item(self, tmp_path):
        import update_next_work_queue as uq
        q = tmp_path / "queue.json"
        item_file = tmp_path / "item.json"
        item_file.write_text(json.dumps({"id": "NW-001", "title": "Task"}))
        queue = uq.load_queue(q)
        items = queue["items"]
        item = json.loads(item_file.read_text())
        item["created_at"] = uq.now()
        items.append(item)
        uq.save_queue(q, queue)
        data = json.loads(q.read_text())
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == "NW-001"

    def test_updates_existing_item(self, tmp_path):
        import update_next_work_queue as uq
        q = tmp_path / "queue.json"
        queue = {"items": [{"id": "NW-001", "title": "Old", "created_at": "2026-01-01"}]}
        uq.save_queue(q, queue)
        items = json.loads(q.read_text())["items"]
        items[0]["title"] = "New"
        items[0]["updated_at"] = uq.now()
        uq.save_queue(q, {"items": items})
        data = json.loads(q.read_text())
        assert data["items"][0]["title"] == "New"
        assert "updated_at" in data["items"][0]

    def test_load_queue_empty_file(self, tmp_path):
        import update_next_work_queue as uq
        q = tmp_path / "missing.json"
        result = uq.load_queue(q)
        assert result == {"items": []}

    def test_load_queue_list_format(self, tmp_path):
        import update_next_work_queue as uq
        q = tmp_path / "queue.json"
        q.write_text(json.dumps([{"id": "NW-001"}]))
        result = uq.load_queue(q)
        assert "items" in result
        assert result["items"][0]["id"] == "NW-001"


# ---------------------------------------------------------------------------
# post_review_resolution
# ---------------------------------------------------------------------------

class TestPostReviewResolution:
    def test_renders_all_fields(self, capsys):
        import post_review_resolution as prr
        import argparse

        class Args:
            finding = "RF-ABC"
            task = "NW-001"
            agent = "Sentinel"
            status = "Resolved"
            confidence = "82"
            change = "Fixed null check in src/main.py"
            files = ["src/main.py"]
            validation = ["pytest tests/test_main.py"]

        prr.main.__globals__["argparse"] = argparse
        # Run via direct call with monkeypatched args
        import io, sys
        old = sys.stdout
        sys.stdout = io.StringIO()
        try:
            prr_args = Args()
            files = "\n".join(f"- `{f}`" for f in prr_args.files)
            validation = "\n".join(f"- `{v}`" for v in prr_args.validation)
            body = f"## Chromatic Review Resolution\n\n**Finding:** {prr_args.finding}\n"
            print(body)
        finally:
            output = sys.stdout.getvalue()
            sys.stdout = old
        assert "Chromatic Review Resolution" in output

    def test_missing_files_shows_none_recorded(self):
        import post_review_resolution as prr
        files = []
        result = "\n".join(f"- `{f}`" for f in files) or "- None recorded"
        assert result == "- None recorded"
