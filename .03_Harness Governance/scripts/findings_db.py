#!/usr/bin/env python3
"""PDR-004 Phase 5 — SQLite multi-repo findings aggregator.

Provides three CLI modes:
  --ingest   Read a JSONL findings file and upsert into the DB
  --report   Print a summary report (counts by repo/type/status)
  --query    Return JSON rows matching optional filter flags

Schema mirrors review_finding.schema.json; each row is one finding.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB = Path(".agents/review-intake/findings.db")


# ---------------------------------------------------------------------------
# Schema / DB helpers
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS findings (
    finding_id       TEXT PRIMARY KEY,
    repo             TEXT NOT NULL DEFAULT '',
    pr_number        INTEGER,
    event_type       TEXT,
    finding_type     TEXT,
    severity         TEXT,
    confidence_score INTEGER,
    risk_level       TEXT,
    status           TEXT NOT NULL DEFAULT 'open',
    suggested_agent  TEXT,
    body             TEXT,
    path             TEXT,
    author           TEXT,
    source_url       TEXT,
    ingested_at      TEXT NOT NULL,
    raw_json         TEXT
);

CREATE INDEX IF NOT EXISTS idx_findings_repo   ON findings (repo);
CREATE INDEX IF NOT EXISTS idx_findings_type   ON findings (finding_type);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings (status);
"""


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    conn.commit()
    return conn


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

def _finding_to_row(finding: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "finding_id":       finding.get("finding_id", ""),
        "repo":             finding.get("repo", ""),
        "pr_number":        finding.get("pr_number"),
        "event_type":       finding.get("event_type"),
        "finding_type":     finding.get("finding_type"),
        "severity":         finding.get("severity"),
        "confidence_score": finding.get("confidence_score"),
        "risk_level":       finding.get("risk_level"),
        "status":           finding.get("status", "open"),
        "suggested_agent":  finding.get("suggested_agent"),
        "body":             finding.get("body"),
        "path":             finding.get("path"),
        "author":           finding.get("author"),
        "source_url":       finding.get("source_url"),
        "ingested_at":      utc_now(),
        "raw_json":         json.dumps(finding),
    }


UPSERT_SQL = """
INSERT INTO findings (
    finding_id, repo, pr_number, event_type, finding_type, severity,
    confidence_score, risk_level, status, suggested_agent, body, path,
    author, source_url, ingested_at, raw_json
) VALUES (
    :finding_id, :repo, :pr_number, :event_type, :finding_type, :severity,
    :confidence_score, :risk_level, :status, :suggested_agent, :body, :path,
    :author, :source_url, :ingested_at, :raw_json
)
ON CONFLICT(finding_id) DO UPDATE SET
    repo             = excluded.repo,
    pr_number        = excluded.pr_number,
    event_type       = excluded.event_type,
    finding_type     = excluded.finding_type,
    severity         = excluded.severity,
    confidence_score = excluded.confidence_score,
    risk_level       = excluded.risk_level,
    status           = excluded.status,
    suggested_agent  = excluded.suggested_agent,
    body             = excluded.body,
    path             = excluded.path,
    author           = excluded.author,
    source_url       = excluded.source_url,
    ingested_at      = excluded.ingested_at,
    raw_json         = excluded.raw_json
"""


def ingest_jsonl(conn: sqlite3.Connection, jsonl_path: Path) -> int:
    if not jsonl_path.exists():
        return 0
    count = 0
    with jsonl_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                finding = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not finding.get("finding_id"):
                continue
            row = _finding_to_row(finding)
            conn.execute(UPSERT_SQL, row)
            count += 1
    conn.commit()
    return count


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def report(conn: sqlite3.Connection) -> Dict[str, Any]:
    total = conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]

    by_repo = {
        r["repo"]: r["cnt"]
        for r in conn.execute(
            "SELECT repo, COUNT(*) as cnt FROM findings GROUP BY repo ORDER BY cnt DESC"
        ).fetchall()
    }
    by_type = {
        r["finding_type"] or "unknown": r["cnt"]
        for r in conn.execute(
            "SELECT finding_type, COUNT(*) as cnt FROM findings GROUP BY finding_type ORDER BY cnt DESC"
        ).fetchall()
    }
    by_status = {
        r["status"]: r["cnt"]
        for r in conn.execute(
            "SELECT status, COUNT(*) as cnt FROM findings GROUP BY status ORDER BY cnt DESC"
        ).fetchall()
    }
    by_severity = {
        r["severity"] or "unknown": r["cnt"]
        for r in conn.execute(
            "SELECT severity, COUNT(*) as cnt FROM findings GROUP BY severity ORDER BY cnt DESC"
        ).fetchall()
    }

    return {
        "total": total,
        "by_repo": by_repo,
        "by_type": by_type,
        "by_status": by_status,
        "by_severity": by_severity,
    }


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def query_findings(
    conn: sqlite3.Connection,
    *,
    repo: Optional[str] = None,
    finding_type: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    min_confidence: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    clauses: List[str] = []
    params: List[Any] = []

    if repo:
        clauses.append("repo = ?")
        params.append(repo)
    if finding_type:
        clauses.append("finding_type = ?")
        params.append(finding_type)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if severity:
        clauses.append("severity = ?")
        params.append(severity)
    if min_confidence is not None:
        clauses.append("confidence_score >= ?")
        params.append(min_confidence)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM findings {where} ORDER BY confidence_score DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Chromatic multi-repo findings aggregator (Phase 5)")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite database file")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ingest", metavar="JSONL", help="Ingest findings from a JSONL file")
    mode.add_argument("--report", action="store_true", help="Print summary report as JSON")
    mode.add_argument("--query", action="store_true", help="Query findings as JSON")

    # Query filters
    parser.add_argument("--repo", help="Filter by repository (owner/repo)")
    parser.add_argument("--type", dest="finding_type", help="Filter by finding_type")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--severity", help="Filter by severity")
    parser.add_argument("--min-confidence", type=int, help="Minimum confidence_score")
    parser.add_argument("--limit", type=int, default=100, help="Max rows returned by --query")

    args = parser.parse_args()
    db_path = Path(args.db)
    conn = open_db(db_path)

    if args.ingest:
        count = ingest_jsonl(conn, Path(args.ingest))
        print(json.dumps({"ingested": count, "db": str(db_path)}))

    elif args.report:
        result = report(conn)
        print(json.dumps(result, indent=2))

    elif args.query:
        rows = query_findings(
            conn,
            repo=args.repo,
            finding_type=args.finding_type,
            status=args.status,
            severity=args.severity,
            min_confidence=args.min_confidence,
            limit=args.limit,
        )
        print(json.dumps(rows, indent=2))

    conn.close()


if __name__ == "__main__":
    main()
