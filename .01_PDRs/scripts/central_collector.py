#!/usr/bin/env python3
"""SQLite-backed central findings collector for cross-repo review findings."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with findings schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            finding_id TEXT PRIMARY KEY,
            repo TEXT NOT NULL,
            pr_number TEXT,
            status TEXT NOT NULL,
            confidence REAL,
            finding_type TEXT,
            ingested_at TEXT NOT NULL,
            raw_json TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def compute_content_hash(record: Dict[str, Any]) -> str:
    """Compute SHA1 hash of finding content for dedup."""
    content = json.dumps(
        {
            "repo": record.get("repo"),
            "pr_number": record.get("pr_number"),
            "body": record.get("body"),
            "path": record.get("path"),
            "line": record.get("line"),
        },
        sort_keys=True,
    )
    return hashlib.sha1(content.encode("utf-8")).hexdigest()


def ingest_finding(
    conn: sqlite3.Connection,
    record: Dict[str, Any],
    upsert_by_hash: bool = False,
) -> bool:
    """Ingest a single finding into the database.

    Returns True if inserted/updated, False if duplicate.
    Uses finding_id as primary key if present, else uses content hash.
    """
    cursor = conn.cursor()

    finding_id = record.get("finding_id")
    if not finding_id:
        if not upsert_by_hash:
            return False
        finding_id = f"RF-{compute_content_hash(record)[:12].upper()}"

    repo = record.get("repo", "unknown")
    pr_number = str(record.get("pr_number")) if record.get("pr_number") else None
    status = record.get("status", "open")
    confidence = record.get("confidence_score")
    finding_type = record.get("finding_type")
    raw_json = json.dumps(record, sort_keys=True)
    ingested_at = utc_now()

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO findings
            (finding_id, repo, pr_number, status, confidence, finding_type, ingested_at, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (finding_id, repo, pr_number, status, confidence, finding_type, ingested_at, raw_json))
        conn.commit()
        return True
    except sqlite3.Error:
        return False


def ingest_jsonl(
    conn: sqlite3.Connection,
    jsonl_path: Path,
    upsert_by_hash: bool = False,
) -> tuple[int, int]:
    """Ingest a JSONL file into the database.

    Returns (inserted_count, skipped_count).
    Wraps json.loads in try/except per governance rules.
    """
    if not jsonl_path.exists():
        return 0, 0

    inserted = 0
    skipped = 0

    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue

        if ingest_finding(conn, record, upsert_by_hash):
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped


def query_findings(
    conn: sqlite3.Connection,
    status: Optional[str] = None,
    repo: Optional[str] = None,
    finding_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Query findings with optional filters.

    Returns list of findings as dicts.
    """
    cursor = conn.cursor()

    where_clauses = []
    params = []

    if status:
        where_clauses.append("status = ?")
        params.append(status)
    if repo:
        where_clauses.append("repo = ?")
        params.append(repo)
    if finding_type:
        where_clauses.append("finding_type = ?")
        params.append(finding_type)
    if min_confidence is not None:
        where_clauses.append("confidence >= ?")
        params.append(min_confidence)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    cursor.execute(f"""
        SELECT finding_id, repo, pr_number, status, confidence, finding_type, ingested_at, raw_json
        FROM findings
        WHERE {where_sql}
        ORDER BY ingested_at DESC
    """, params)

    rows = cursor.fetchall()
    results = []

    for row in rows:
        raw_json = row[7]
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            parsed = {"error": "Failed to parse raw_json"}

        results.append({
            "finding_id": row[0],
            "repo": row[1],
            "pr_number": row[2],
            "status": row[3],
            "confidence": row[4],
            "finding_type": row[5],
            "ingested_at": row[6],
            "data": parsed,
        })

    return results


def generate_summary(conn: sqlite3.Connection, summary_date: Optional[str] = None) -> Dict[str, Any]:
    """Generate daily summary counting open/resolved/escalated by repo.

    Summary structure:
    {
        "summary_date": "YYYY-MM-DD",
        "generated_at": "ISO8601Z",
        "by_repo": {
            "owner/repo": {
                "total": N,
                "by_status": {"open": N, "resolved": N, "escalated": N, ...},
                "by_type": {"security": N, "test_failure": N, ...}
            }
        }
    }
    """
    if not summary_date:
        summary_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT repo, status, finding_type, COUNT(*) as count
        FROM findings
        GROUP BY repo, status, finding_type
        ORDER BY repo, status, finding_type
    """)

    rows = cursor.fetchall()

    summary: Dict[str, Any] = {
        "summary_date": summary_date,
        "generated_at": utc_now(),
        "by_repo": {},
    }

    for repo, status, ftype, count in rows:
        if repo not in summary["by_repo"]:
            summary["by_repo"][repo] = {
                "total": 0,
                "by_status": {},
                "by_type": {},
            }

        summary["by_repo"][repo]["total"] += count
        summary["by_repo"][repo]["by_status"][status] = count
        summary["by_repo"][repo]["by_type"][ftype] = count

    return summary


def run_ingest(
    db_path: Path,
    findings_dir: Path,
    upsert_by_hash: bool = False,
) -> None:
    """CLI subcommand: ingest findings from a directory."""
    if not findings_dir.exists():
        print(f"Error: findings_dir {findings_dir} does not exist.")
        return

    conn = init_db(db_path)

    total_inserted = 0
    total_skipped = 0

    for jsonl_file in sorted(findings_dir.glob("**/*.jsonl")):
        inserted, skipped = ingest_jsonl(conn, jsonl_file, upsert_by_hash)
        total_inserted += inserted
        total_skipped += skipped
        if inserted > 0:
            print(f"Ingested {inserted} from {jsonl_file.name}")

    conn.close()

    print(f"Total inserted: {total_inserted}, skipped: {total_skipped}")


def run_query(
    db_path: Path,
    status: Optional[str] = None,
    repo: Optional[str] = None,
    finding_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
) -> None:
    """CLI subcommand: query findings with filters."""
    if not db_path.exists():
        print(f"Error: database {db_path} does not exist.")
        return

    conn = sqlite3.connect(str(db_path))

    results = query_findings(
        conn,
        status=status,
        repo=repo,
        finding_type=finding_type,
        min_confidence=min_confidence,
    )

    conn.close()

    print(f"Found {len(results)} findings")
    for r in results:
        print(json.dumps(r, indent=2))


def run_summary(
    db_path: Path,
    output_path: Optional[Path] = None,
) -> None:
    """CLI subcommand: generate and write daily summary."""
    if not db_path.exists():
        print(f"Error: database {db_path} does not exist.")
        return

    conn = sqlite3.connect(str(db_path))
    summary = generate_summary(conn)
    conn.close()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary written to {output_path}")
    else:
        print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SQLite-backed central findings collector for cross-repo review findings."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(".agents/review-intake/findings.db"),
        help="Path to SQLite database (default: .agents/review-intake/findings.db)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest findings from JSONL files")
    ingest_parser.add_argument(
        "--findings-dir",
        type=Path,
        required=True,
        help="Directory containing review-findings.jsonl files",
    )
    ingest_parser.add_argument(
        "--upsert-by-hash",
        action="store_true",
        help="Generate finding_id from content hash if not present",
    )

    query_parser = subparsers.add_parser("query", help="Query findings with filters")
    query_parser.add_argument("--status", type=str, help="Filter by status (e.g., open, resolved)")
    query_parser.add_argument("--repo", type=str, help="Filter by repository")
    query_parser.add_argument("--finding-type", type=str, help="Filter by finding type")
    query_parser.add_argument(
        "--min-confidence",
        type=float,
        help="Filter by minimum confidence score",
    )

    summary_parser = subparsers.add_parser("summary", help="Generate daily summary")
    summary_parser.add_argument(
        "--output",
        type=Path,
        help="Write summary to file (default: print to stdout)",
    )

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest(args.db, args.findings_dir, args.upsert_by_hash)
    elif args.command == "query":
        run_query(
            args.db,
            status=args.status,
            repo=args.repo,
            finding_type=args.finding_type,
            min_confidence=args.min_confidence,
        )
    elif args.command == "summary":
        run_summary(args.db, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
