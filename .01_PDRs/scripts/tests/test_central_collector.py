"""Tests for scripts/central_collector.py.

Covers:
- Database initialization and schema
- Ingest from JSONL files (success, malformed JSON, dedup/idempotency)
- Query with filters (status, repo, finding_type, confidence)
- Summary generation (counting by repo, status, type)
- Empty database case
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict

import pytest

import sys
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from central_collector import (
    compute_content_hash,
    generate_summary,
    ingest_finding,
    ingest_jsonl,
    init_db,
    query_findings,
)


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    """Path to a temporary SQLite database."""
    return tmp_path / "test.db"


@pytest.fixture()
def tmp_jsonl(tmp_path: Path) -> Path:
    """Path to a temporary JSONL file."""
    return tmp_path / "findings.jsonl"


def _make_finding(
    *,
    finding_id: str = "RF-TEST-001",
    repo: str = "owner/repo",
    pr_number: int = 42,
    status: str = "open",
    confidence: int = 85,
    finding_type: str = "bug_fix",
    body: str = "Test finding",
    path: str = "src/foo.py",
    line: int = 10,
) -> Dict[str, Any]:
    """Factory function for test findings."""
    return {
        "finding_id": finding_id,
        "source": "github_pr_review_comment",
        "repo": repo,
        "pr_number": pr_number,
        "review_id": 123,
        "comment_id": 456,
        "author": "test-user",
        "created_at": "2026-06-04T00:00:00Z",
        "commit_sha": "abc123def456",
        "path": path,
        "line": line,
        "body": body,
        "finding_type": finding_type,
        "severity": "medium",
        "risk_level": "low",
        "status": status,
        "dedupe_key": f"{repo}#{pr_number}:{path}:{line}:{finding_id}",
        "confidence_score": confidence,
        "suggested_agent": "Sentinel",
        "acceptance_checks": ["Run tests"],
        "links": {"pr": f"https://github.com/{repo}/pull/{pr_number}"},
    }


# ============================================================================
# Test: Database Initialization
# ============================================================================


def test_init_db_creates_table(tmp_db: Path) -> None:
    """Test that init_db creates the findings table."""
    conn = init_db(tmp_db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='findings'")
    assert cursor.fetchone() is not None

    cursor.execute("PRAGMA table_info(findings)")
    columns = {row[1] for row in cursor.fetchall()}
    expected = {"finding_id", "repo", "pr_number", "status", "confidence", "finding_type", "ingested_at", "raw_json"}
    assert columns == expected

    conn.close()


def test_init_db_idempotent(tmp_db: Path) -> None:
    """Test that calling init_db multiple times does not fail."""
    conn1 = init_db(tmp_db)
    conn1.close()

    conn2 = init_db(tmp_db)
    cursor = conn2.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 0

    conn2.close()


# ============================================================================
# Test: Single Finding Ingestion
# ============================================================================


def test_ingest_finding_success(tmp_db: Path) -> None:
    """Test successful ingestion of a single finding."""
    conn = init_db(tmp_db)
    finding = _make_finding()

    result = ingest_finding(conn, finding)
    assert result is True

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings WHERE finding_id = ?", (finding["finding_id"],))
    assert cursor.fetchone()[0] == 1

    conn.close()


def test_ingest_finding_upsert(tmp_db: Path) -> None:
    """Test that re-ingesting the same finding_id updates the record."""
    conn = init_db(tmp_db)
    finding1 = _make_finding(status="open", confidence=80)

    ingest_finding(conn, finding1)

    cursor = conn.cursor()
    cursor.execute("SELECT confidence FROM findings WHERE finding_id = ?", (finding1["finding_id"],))
    assert cursor.fetchone()[0] == 80

    finding2 = _make_finding(status="resolved", confidence=90)
    ingest_finding(conn, finding2)

    cursor.execute("SELECT status, confidence FROM findings WHERE finding_id = ?", (finding2["finding_id"],))
    row = cursor.fetchone()
    assert row[0] == "resolved"
    assert row[1] == 90

    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 1

    conn.close()


def test_ingest_finding_without_id_no_hash(tmp_db: Path) -> None:
    """Test that finding without finding_id is skipped if upsert_by_hash=False."""
    conn = init_db(tmp_db)
    finding = _make_finding()
    del finding["finding_id"]

    result = ingest_finding(conn, finding, upsert_by_hash=False)
    assert result is False

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 0

    conn.close()


def test_ingest_finding_without_id_with_hash(tmp_db: Path) -> None:
    """Test that finding without finding_id generates ID from hash if upsert_by_hash=True."""
    conn = init_db(tmp_db)
    finding = _make_finding()
    del finding["finding_id"]

    result = ingest_finding(conn, finding, upsert_by_hash=True)
    assert result is True

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 1

    conn.close()


# ============================================================================
# Test: JSONL Ingestion
# ============================================================================


def test_ingest_jsonl_success(tmp_db: Path, tmp_jsonl: Path) -> None:
    """Test successful ingestion from a JSONL file."""
    findings = [_make_finding(finding_id=f"RF-{i:03d}", pr_number=10 + i) for i in range(3)]

    with tmp_jsonl.open("w", encoding="utf-8") as f:
        for finding in findings:
            f.write(json.dumps(finding) + "\n")

    conn = init_db(tmp_db)
    inserted, skipped = ingest_jsonl(conn, tmp_jsonl)

    assert inserted == 3
    assert skipped == 0

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 3

    conn.close()


def test_ingest_jsonl_with_empty_lines(tmp_db: Path, tmp_jsonl: Path) -> None:
    """Test that empty lines in JSONL are skipped gracefully."""
    findings = [
        _make_finding(finding_id="RF-001"),
        "",
        _make_finding(finding_id="RF-002"),
        "   ",
        _make_finding(finding_id="RF-003"),
    ]

    with tmp_jsonl.open("w", encoding="utf-8") as f:
        for finding in findings:
            if isinstance(finding, dict):
                f.write(json.dumps(finding) + "\n")
            else:
                f.write(finding + "\n")

    conn = init_db(tmp_db)
    inserted, skipped = ingest_jsonl(conn, tmp_jsonl)

    assert inserted == 3
    assert skipped == 0

    conn.close()


def test_ingest_jsonl_with_malformed_json(tmp_db: Path, tmp_jsonl: Path) -> None:
    """Test that malformed JSON lines are skipped."""
    with tmp_jsonl.open("w", encoding="utf-8") as f:
        f.write(json.dumps(_make_finding(finding_id="RF-001")) + "\n")
        f.write("{invalid json\n")
        f.write(json.dumps(_make_finding(finding_id="RF-002")) + "\n")

    conn = init_db(tmp_db)
    inserted, skipped = ingest_jsonl(conn, tmp_jsonl)

    assert inserted == 2
    assert skipped == 1

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 2

    conn.close()


def test_ingest_jsonl_nonexistent_file(tmp_db: Path) -> None:
    """Test that ingest_jsonl handles nonexistent file gracefully."""
    conn = init_db(tmp_db)
    fake_path = Path("/nonexistent/path/findings.jsonl")

    inserted, skipped = ingest_jsonl(conn, fake_path)

    assert inserted == 0
    assert skipped == 0

    conn.close()


def test_ingest_jsonl_dedup_idempotency(tmp_db: Path, tmp_jsonl: Path) -> None:
    """Test that ingesting the same JSONL twice is idempotent."""
    finding = _make_finding(finding_id="RF-001")

    with tmp_jsonl.open("w", encoding="utf-8") as f:
        f.write(json.dumps(finding) + "\n")

    conn = init_db(tmp_db)

    inserted1, _ = ingest_jsonl(conn, tmp_jsonl)
    assert inserted1 == 1

    inserted2, _ = ingest_jsonl(conn, tmp_jsonl)
    assert inserted2 == 1

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM findings")
    assert cursor.fetchone()[0] == 1

    conn.close()


# ============================================================================
# Test: Query Filtering
# ============================================================================


def test_query_findings_all(tmp_db: Path) -> None:
    """Test querying all findings without filters."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", repo="owner/repo1", status="open"),
        _make_finding(finding_id="RF-002", repo="owner/repo2", status="resolved"),
        _make_finding(finding_id="RF-003", repo="owner/repo1", status="escalated"),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    results = query_findings(conn)
    assert len(results) == 3

    conn.close()


def test_query_findings_by_status(tmp_db: Path) -> None:
    """Test filtering findings by status."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", status="open"),
        _make_finding(finding_id="RF-002", status="resolved"),
        _make_finding(finding_id="RF-003", status="open"),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    results = query_findings(conn, status="open")
    assert len(results) == 2
    assert all(r["status"] == "open" for r in results)

    conn.close()


def test_query_findings_by_repo(tmp_db: Path) -> None:
    """Test filtering findings by repository."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", repo="owner/repo1"),
        _make_finding(finding_id="RF-002", repo="owner/repo2"),
        _make_finding(finding_id="RF-003", repo="owner/repo1"),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    results = query_findings(conn, repo="owner/repo1")
    assert len(results) == 2
    assert all(r["repo"] == "owner/repo1" for r in results)

    conn.close()


def test_query_findings_by_finding_type(tmp_db: Path) -> None:
    """Test filtering findings by type."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", finding_type="bug_fix"),
        _make_finding(finding_id="RF-002", finding_type="security"),
        _make_finding(finding_id="RF-003", finding_type="bug_fix"),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    results = query_findings(conn, finding_type="bug_fix")
    assert len(results) == 2
    assert all(r["finding_type"] == "bug_fix" for r in results)

    conn.close()


def test_query_findings_by_min_confidence(tmp_db: Path) -> None:
    """Test filtering findings by minimum confidence."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", confidence=70),
        _make_finding(finding_id="RF-002", confidence=85),
        _make_finding(finding_id="RF-003", confidence=95),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    results = query_findings(conn, min_confidence=85.0)
    assert len(results) == 2
    assert all(r["confidence"] >= 85.0 for r in results)

    conn.close()


def test_query_findings_combined_filters(tmp_db: Path) -> None:
    """Test querying with multiple filters combined."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", repo="owner/repo1", status="open", finding_type="bug_fix", confidence=80),
        _make_finding(finding_id="RF-002", repo="owner/repo1", status="resolved", finding_type="bug_fix", confidence=90),
        _make_finding(finding_id="RF-003", repo="owner/repo2", status="open", finding_type="security", confidence=95),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    results = query_findings(
        conn,
        repo="owner/repo1",
        status="open",
        finding_type="bug_fix",
        min_confidence=75.0,
    )

    assert len(results) == 1
    assert results[0]["finding_id"] == "RF-001"

    conn.close()


def test_query_findings_empty_db(tmp_db: Path) -> None:
    """Test querying an empty database."""
    conn = init_db(tmp_db)

    results = query_findings(conn)
    assert len(results) == 0

    results_filtered = query_findings(conn, status="open")
    assert len(results_filtered) == 0

    conn.close()


def test_query_findings_parses_raw_json(tmp_db: Path) -> None:
    """Test that query results include parsed JSON data."""
    conn = init_db(tmp_db)
    finding = _make_finding(finding_id="RF-001", body="Test body")

    ingest_finding(conn, finding)

    results = query_findings(conn)
    assert len(results) == 1
    assert results[0]["data"]["body"] == "Test body"
    assert results[0]["data"]["finding_id"] == "RF-001"

    conn.close()


# ============================================================================
# Test: Summary Generation
# ============================================================================


def test_generate_summary_empty_db(tmp_db: Path) -> None:
    """Test summary generation on an empty database."""
    conn = init_db(tmp_db)

    summary = generate_summary(conn)

    assert "summary_date" in summary
    assert "generated_at" in summary
    assert summary["by_repo"] == {}

    conn.close()


def test_generate_summary_single_repo(tmp_db: Path) -> None:
    """Test summary generation with findings from a single repo."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", repo="owner/repo", status="open", finding_type="bug_fix"),
        _make_finding(finding_id="RF-002", repo="owner/repo", status="open", finding_type="security"),
        _make_finding(finding_id="RF-003", repo="owner/repo", status="resolved", finding_type="bug_fix"),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    summary = generate_summary(conn)

    assert "owner/repo" in summary["by_repo"]
    repo_summary = summary["by_repo"]["owner/repo"]
    assert repo_summary["total"] == 3
    assert repo_summary["by_status"]["open"] == 2
    assert repo_summary["by_status"]["resolved"] == 1
    assert repo_summary["by_type"]["bug_fix"] == 2
    assert repo_summary["by_type"]["security"] == 1

    conn.close()


def test_generate_summary_multiple_repos(tmp_db: Path) -> None:
    """Test summary generation with findings from multiple repos."""
    conn = init_db(tmp_db)

    findings = [
        _make_finding(finding_id="RF-001", repo="owner/repo1", status="open", finding_type="bug_fix"),
        _make_finding(finding_id="RF-002", repo="owner/repo1", status="resolved", finding_type="bug_fix"),
        _make_finding(finding_id="RF-003", repo="owner/repo2", status="open", finding_type="security"),
        _make_finding(finding_id="RF-004", repo="owner/repo2", status="escalated", finding_type="security"),
    ]

    for finding in findings:
        ingest_finding(conn, finding)

    summary = generate_summary(conn)

    assert len(summary["by_repo"]) == 2
    assert summary["by_repo"]["owner/repo1"]["total"] == 2
    assert summary["by_repo"]["owner/repo2"]["total"] == 2

    conn.close()


def test_generate_summary_includes_timestamp(tmp_db: Path) -> None:
    """Test that summary includes generated_at timestamp."""
    conn = init_db(tmp_db)

    summary = generate_summary(conn)

    assert "generated_at" in summary
    assert summary["generated_at"].endswith("Z")

    conn.close()


def test_generate_summary_uses_custom_date(tmp_db: Path) -> None:
    """Test that summary uses provided date."""
    conn = init_db(tmp_db)

    custom_date = "2026-06-01"
    summary = generate_summary(conn, summary_date=custom_date)

    assert summary["summary_date"] == custom_date

    conn.close()


# ============================================================================
# Test: Content Hash (Dedup Helper)
# ============================================================================


def test_compute_content_hash_consistency(tmp_db: Path) -> None:
    """Test that identical findings produce the same hash."""
    finding1 = _make_finding(finding_id="RF-001")
    finding2 = _make_finding(finding_id="RF-002")

    del finding2["finding_id"]

    hash1 = compute_content_hash(finding1)
    hash2 = compute_content_hash(finding2)

    assert hash1 == hash2


def test_compute_content_hash_differs_by_content(tmp_db: Path) -> None:
    """Test that different content produces different hashes."""
    finding1 = _make_finding(body="test 1")
    finding2 = _make_finding(body="test 2")

    hash1 = compute_content_hash(finding1)
    hash2 = compute_content_hash(finding2)

    assert hash1 != hash2
