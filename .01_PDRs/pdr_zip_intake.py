#!/usr/bin/env python3
"""
Automated ZIP intake scanner for .01_PDRs.

Behavior:
- Detects root-level ZIP artifacts under .01_PDRs.
- Performs lightweight review checks (hash, size, ZIP integrity, file count).
- Stores state/history in SQLite (.01_PDRs/.intake/zip_intake.db).
- Appends event logs to JSONL (.01_PDRs/.intake/zip_intake-log.jsonl).
- Correlates ZIPs with PDR_REGISTRY.json pipeline status and extracted path.
"""

import argparse
import hashlib
import json
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_registry(registry_path: Path) -> dict[str, Any]:
    if not registry_path.exists():
        return {"pdrs": [], "artifact_backlog": []}

    try:
        with registry_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        # Keep scanner resilient if registry is partially written by another process.
        return {"pdrs": [], "artifact_backlog": []}

    if not isinstance(data, dict):
        return {"pdrs": [], "artifact_backlog": []}

    data.setdefault("pdrs", [])
    data.setdefault("artifact_backlog", [])
    return data


def normalize_rel(path_str: str | None) -> str:
    if not path_str:
        return ""
    return path_str.replace("\\", "/")


def pipeline_lookup(registry: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Build ZIP -> pipeline metadata lookup from artifact_backlog and pdrs."""
    lookup: dict[str, dict[str, str]] = {}

    for artifact in registry.get("artifact_backlog", []):
        if not isinstance(artifact, dict):
            continue
        zip_path = normalize_rel(artifact.get("zip_path"))
        if not zip_path:
            continue
        zip_name = Path(zip_path).name
        lookup[zip_name] = {
            "pipeline_status": str(artifact.get("status", "Backlog")),
            "linked_pdr_id": str(artifact.get("linked_pdr_id", "")),
            "extracted_path": normalize_rel(artifact.get("extracted_path", "")),
        }

    for pdr in registry.get("pdrs", []):
        if not isinstance(pdr, dict):
            continue
        zip_path = normalize_rel(pdr.get("zip_path"))
        if not zip_path:
            continue
        zip_name = Path(zip_path).name
        lookup[zip_name] = {
            "pipeline_status": str(pdr.get("status", "Backlog")),
            "linked_pdr_id": str(pdr.get("id", "")),
            "extracted_path": normalize_rel(pdr.get("extracted_path", "")),
        }

    return lookup


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS zip_records (
            zip_name TEXT PRIMARY KEY,
            zip_rel_path TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            lifecycle_state TEXT NOT NULL,
            pipeline_status TEXT NOT NULL,
            linked_pdr_id TEXT,
            extracted_path TEXT,
            review_result TEXT NOT NULL,
            review_notes TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS intake_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_ts TEXT NOT NULL,
            zip_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            details_json TEXT
        )
        """
    )
    conn.commit()


def append_jsonl(log_path: Path, payload: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def log_event(conn: sqlite3.Connection, log_path: Path, zip_name: str, event_type: str, details: dict[str, Any]) -> None:
    ts = utc_now()
    details_json = json.dumps(details, sort_keys=True)
    conn.execute(
        "INSERT INTO intake_events (event_ts, zip_name, event_type, details_json) VALUES (?, ?, ?, ?)",
        (ts, zip_name, event_type, details_json),
    )
    append_jsonl(
        log_path,
        {
            "event_ts": ts,
            "zip_name": zip_name,
            "event_type": event_type,
            "details": details,
        },
    )


def review_zip(zip_path: Path) -> tuple[str, str, int]:
    """Return (review_result, review_notes, file_count)."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad_member = zf.testzip()
            file_members = [n for n in zf.namelist() if not n.endswith("/")]
            file_count = len(file_members)
            if bad_member:
                return "fail", f"Corrupt member detected: {bad_member}", file_count
            if file_count == 0:
                return "warn", "ZIP is valid but contains no files", file_count
            root_names = {Path(name).parts[0] for name in file_members if Path(name).parts}
            if len(root_names) > 1:
                return "warn", "ZIP has multiple top-level roots", file_count
            return "pass", "ZIP integrity check passed", file_count
    except zipfile.BadZipFile:
        return "fail", "Invalid ZIP format", 0
    except OSError as exc:
        return "fail", f"I/O error during ZIP review: {exc}", 0


def scan_zip_intake(base_dir: Path, zip_name_filter: str | None = None) -> dict[str, int]:
    registry_path = base_dir / "PDR_REGISTRY.json"
    intake_dir = base_dir / ".intake"
    db_path = intake_dir / "zip_intake.db"
    log_path = intake_dir / "zip_intake-log.jsonl"

    intake_dir.mkdir(parents=True, exist_ok=True)
    registry = load_registry(registry_path)
    lookup = pipeline_lookup(registry)

    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)

        zips = sorted(base_dir.glob("*.zip"))
        if zip_name_filter:
            zips = [z for z in zips if z.name == zip_name_filter]

        seen_names: set[str] = set()
        counts = {
            "new": 0,
            "updated": 0,
            "current": 0,
            "historical": 0,
            "failed_review": 0,
            "total_scanned": 0,
        }

        for zip_path in zips:
            zip_name = zip_path.name
            seen_names.add(zip_name)
            counts["total_scanned"] += 1

            rel_zip = str(zip_path.relative_to(base_dir.parent)).replace("\\", "/")
            digest = sha256_file(zip_path)
            size_bytes = zip_path.stat().st_size
            review_result, review_notes, file_count = review_zip(zip_path)

            if review_result == "fail":
                counts["failed_review"] += 1

            pipeline_meta = lookup.get(
                zip_name,
                {
                    "pipeline_status": "Backlog",
                    "linked_pdr_id": "",
                    "extracted_path": f".01_PDRs/.99_Extracted/{zip_path.stem}",
                },
            )

            existing = conn.execute(
                "SELECT sha256, first_seen_at FROM zip_records WHERE zip_name = ?",
                (zip_name,),
            ).fetchone()

            if existing is None:
                event_type = "NEW"
                lifecycle_state = "new"
                first_seen = utc_now()
                counts["new"] += 1
            elif existing[0] != digest:
                event_type = "UPDATED"
                lifecycle_state = "updated"
                first_seen = existing[1]
                counts["updated"] += 1
            else:
                event_type = "CURRENT"
                lifecycle_state = "current"
                first_seen = existing[1]
                counts["current"] += 1

            conn.execute(
                """
                INSERT INTO zip_records (
                    zip_name, zip_rel_path, first_seen_at, last_seen_at, sha256, size_bytes,
                    lifecycle_state, pipeline_status, linked_pdr_id, extracted_path,
                    review_result, review_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(zip_name) DO UPDATE SET
                    zip_rel_path=excluded.zip_rel_path,
                    last_seen_at=excluded.last_seen_at,
                    sha256=excluded.sha256,
                    size_bytes=excluded.size_bytes,
                    lifecycle_state=excluded.lifecycle_state,
                    pipeline_status=excluded.pipeline_status,
                    linked_pdr_id=excluded.linked_pdr_id,
                    extracted_path=excluded.extracted_path,
                    review_result=excluded.review_result,
                    review_notes=excluded.review_notes
                """,
                (
                    zip_name,
                    rel_zip,
                    first_seen,
                    utc_now(),
                    digest,
                    size_bytes,
                    lifecycle_state,
                    pipeline_meta.get("pipeline_status", "Backlog"),
                    pipeline_meta.get("linked_pdr_id", ""),
                    pipeline_meta.get("extracted_path", ""),
                    review_result,
                    f"{review_notes}; file_count={file_count}",
                ),
            )

            log_event(
                conn,
                log_path,
                zip_name,
                event_type,
                {
                    "zip_rel_path": rel_zip,
                    "sha256": digest,
                    "size_bytes": size_bytes,
                    "pipeline_status": pipeline_meta.get("pipeline_status", "Backlog"),
                    "linked_pdr_id": pipeline_meta.get("linked_pdr_id", ""),
                    "extracted_path": pipeline_meta.get("extracted_path", ""),
                    "review_result": review_result,
                    "review_notes": review_notes,
                    "file_count": file_count,
                },
            )

        if not zip_name_filter:
            known_names = {
                row[0]
                for row in conn.execute("SELECT zip_name FROM zip_records").fetchall()
            }
            historical = sorted(known_names - seen_names)
            for zip_name in historical:
                conn.execute(
                    "UPDATE zip_records SET lifecycle_state = ?, last_seen_at = ? WHERE zip_name = ?",
                    ("historical", utc_now(), zip_name),
                )
                log_event(
                    conn,
                    log_path,
                    zip_name,
                    "HISTORICAL",
                    {"reason": "ZIP not present in current .01_PDRs root scan"},
                )
                counts["historical"] += 1

        conn.commit()
        return counts
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated ZIP intake review + tracking")
    parser.add_argument(
        "--base-dir",
        default=str(Path(__file__).parent),
        help="Path to .01_PDRs directory (default: current script directory)",
    )
    parser.add_argument(
        "--zip-name",
        default=None,
        help="Optional single ZIP filename to test intake against",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        raise SystemExit(f"Base dir not found: {base_dir}")

    counts = scan_zip_intake(base_dir=base_dir, zip_name_filter=args.zip_name)

    print("ZIP intake scan complete:")
    print(json.dumps(counts, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
