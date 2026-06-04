"""Tests for findings_db.py — PDR-004 Phase 5 SQLite aggregator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import findings_db as fdb


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _finding(
    id_: str,
    *,
    repo: str = "owner/repo",
    finding_type: str = "bug",
    status: str = "open",
    severity: str = "medium",
    confidence: int = 75,
) -> dict:
    return {
        "finding_id": id_,
        "repo": repo,
        "pr_number": 1,
        "event_type": "pull_request_review_comment",
        "finding_type": finding_type,
        "severity": severity,
        "confidence_score": confidence,
        "risk_level": "low",
        "status": status,
        "suggested_agent": "Sentinel",
        "body": f"Issue in {id_}",
        "path": "src/main.py",
        "author": "reviewer",
        "source_url": f"https://github.com/owner/repo/pull/1#comment-{id_}",
    }


def _write_jsonl(path: Path, findings: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for item in findings:
            f.write(json.dumps(item) + "\n")


# ---------------------------------------------------------------------------
# open_db / schema
# ---------------------------------------------------------------------------

class TestOpenDb:
    def test_creates_db_file(self, tmp_path):
        conn = fdb.open_db(tmp_path / "test.db")
        conn.close()
        assert (tmp_path / "test.db").exists()

    def test_creates_parent_dirs(self, tmp_path):
        conn = fdb.open_db(tmp_path / "sub" / "dir" / "test.db")
        conn.close()
        assert (tmp_path / "sub" / "dir" / "test.db").exists()

    def test_findings_table_exists(self, tmp_path):
        conn = fdb.open_db(tmp_path / "test.db")
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "findings" in tables
        conn.close()

    def test_idempotent_on_second_open(self, tmp_path):
        path = tmp_path / "test.db"
        conn = fdb.open_db(path)
        conn.close()
        conn2 = fdb.open_db(path)
        conn2.close()


# ---------------------------------------------------------------------------
# ingest_jsonl
# ---------------------------------------------------------------------------

class TestIngestJsonl:
    def test_ingests_all_records(self, tmp_path):
        jsonl = tmp_path / "f.jsonl"
        _write_jsonl(jsonl, [_finding("F-001"), _finding("F-002"), _finding("F-003")])
        conn = fdb.open_db(tmp_path / "db.sqlite")
        count = fdb.ingest_jsonl(conn, jsonl)
        assert count == 3
        conn.close()

    def test_missing_file_returns_zero(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        count = fdb.ingest_jsonl(conn, tmp_path / "nope.jsonl")
        assert count == 0
        conn.close()

    def test_upsert_updates_existing(self, tmp_path):
        jsonl = tmp_path / "f.jsonl"
        _write_jsonl(jsonl, [_finding("F-001", status="open")])
        conn = fdb.open_db(tmp_path / "db.sqlite")
        fdb.ingest_jsonl(conn, jsonl)

        jsonl2 = tmp_path / "f2.jsonl"
        _write_jsonl(jsonl2, [_finding("F-001", status="resolved")])
        fdb.ingest_jsonl(conn, jsonl2)

        row = conn.execute("SELECT status FROM findings WHERE finding_id = 'F-001'").fetchone()
        assert row["status"] == "resolved"
        conn.close()

    def test_skips_blank_lines(self, tmp_path):
        jsonl = tmp_path / "f.jsonl"
        jsonl.write_text(json.dumps(_finding("F-A")) + "\n\n\n" + json.dumps(_finding("F-B")) + "\n")
        conn = fdb.open_db(tmp_path / "db.sqlite")
        count = fdb.ingest_jsonl(conn, jsonl)
        assert count == 2
        conn.close()

    def test_skips_invalid_json(self, tmp_path):
        jsonl = tmp_path / "f.jsonl"
        jsonl.write_text("NOT JSON\n" + json.dumps(_finding("F-OK")) + "\n")
        conn = fdb.open_db(tmp_path / "db.sqlite")
        count = fdb.ingest_jsonl(conn, jsonl)
        assert count == 1
        conn.close()

    def test_skips_missing_finding_id(self, tmp_path):
        jsonl = tmp_path / "f.jsonl"
        jsonl.write_text(json.dumps({"repo": "a/b"}) + "\n")
        conn = fdb.open_db(tmp_path / "db.sqlite")
        count = fdb.ingest_jsonl(conn, jsonl)
        assert count == 0
        conn.close()

    def test_raw_json_stored(self, tmp_path):
        finding = _finding("F-RAW")
        finding["custom_field"] = "custom_value"
        jsonl = tmp_path / "f.jsonl"
        _write_jsonl(jsonl, [finding])
        conn = fdb.open_db(tmp_path / "db.sqlite")
        fdb.ingest_jsonl(conn, jsonl)
        row = conn.execute("SELECT raw_json FROM findings WHERE finding_id = 'F-RAW'").fetchone()
        raw = json.loads(row["raw_json"])
        assert raw["custom_field"] == "custom_value"
        conn.close()


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

class TestReport:
    def _seed(self, conn, findings):
        for f in findings:
            row = fdb._finding_to_row(f)
            conn.execute(fdb.UPSERT_SQL, row)
        conn.commit()

    def test_total_count(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [_finding(f"F-{i:03d}") for i in range(5)])
        r = fdb.report(conn)
        assert r["total"] == 5
        conn.close()

    def test_by_repo(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-A", repo="org/alpha"),
            _finding("F-B", repo="org/alpha"),
            _finding("F-C", repo="org/beta"),
        ])
        r = fdb.report(conn)
        assert r["by_repo"]["org/alpha"] == 2
        assert r["by_repo"]["org/beta"] == 1
        conn.close()

    def test_by_type(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-1", finding_type="bug"),
            _finding("F-2", finding_type="bug"),
            _finding("F-3", finding_type="security"),
        ])
        r = fdb.report(conn)
        assert r["by_type"]["bug"] == 2
        assert r["by_type"]["security"] == 1
        conn.close()

    def test_by_status(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-1", status="open"),
            _finding("F-2", status="resolved"),
            _finding("F-3", status="open"),
        ])
        r = fdb.report(conn)
        assert r["by_status"]["open"] == 2
        assert r["by_status"]["resolved"] == 1
        conn.close()

    def test_empty_db_total_zero(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        r = fdb.report(conn)
        assert r["total"] == 0
        conn.close()


# ---------------------------------------------------------------------------
# query_findings
# ---------------------------------------------------------------------------

class TestQueryFindings:
    def _seed(self, conn, findings):
        for f in findings:
            row = fdb._finding_to_row(f)
            conn.execute(fdb.UPSERT_SQL, row)
        conn.commit()

    def test_no_filter_returns_all(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [_finding(f"F-{i:02d}") for i in range(3)])
        rows = fdb.query_findings(conn)
        assert len(rows) == 3
        conn.close()

    def test_filter_by_repo(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-A", repo="org/alpha"),
            _finding("F-B", repo="org/beta"),
        ])
        rows = fdb.query_findings(conn, repo="org/alpha")
        assert len(rows) == 1
        assert rows[0]["finding_id"] == "F-A"
        conn.close()

    def test_filter_by_status(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-1", status="open"),
            _finding("F-2", status="resolved"),
            _finding("F-3", status="open"),
        ])
        rows = fdb.query_findings(conn, status="open")
        assert len(rows) == 2
        conn.close()

    def test_filter_by_type(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-1", finding_type="bug"),
            _finding("F-2", finding_type="security"),
        ])
        rows = fdb.query_findings(conn, finding_type="security")
        assert len(rows) == 1
        assert rows[0]["finding_id"] == "F-2"
        conn.close()

    def test_filter_by_min_confidence(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-LO", confidence=30),
            _finding("F-HI", confidence=85),
        ])
        rows = fdb.query_findings(conn, min_confidence=75)
        assert len(rows) == 1
        assert rows[0]["finding_id"] == "F-HI"
        conn.close()

    def test_limit_respected(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [_finding(f"F-{i:03d}") for i in range(10)])
        rows = fdb.query_findings(conn, limit=3)
        assert len(rows) == 3
        conn.close()

    def test_filter_by_severity(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-H", severity="high"),
            _finding("F-M", severity="medium"),
        ])
        rows = fdb.query_findings(conn, severity="high")
        assert len(rows) == 1
        assert rows[0]["finding_id"] == "F-H"
        conn.close()

    def test_combined_filters(self, tmp_path):
        conn = fdb.open_db(tmp_path / "db.sqlite")
        self._seed(conn, [
            _finding("F-1", repo="a/b", status="open", finding_type="bug"),
            _finding("F-2", repo="a/b", status="resolved", finding_type="bug"),
            _finding("F-3", repo="a/c", status="open", finding_type="bug"),
        ])
        rows = fdb.query_findings(conn, repo="a/b", status="open")
        assert len(rows) == 1
        assert rows[0]["finding_id"] == "F-1"
        conn.close()


# ---------------------------------------------------------------------------
# utc_now
# ---------------------------------------------------------------------------

class TestUtcNow:
    def test_format(self):
        ts = fdb.utc_now()
        assert "T" in ts
        assert ts.endswith("Z")
