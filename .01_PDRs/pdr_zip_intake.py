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
import os
import re
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKLOG_ZIP_FOLDER = ".01_Backlog"
DUPS_ZIP_FOLDER = ".01_Backlog/.99_Dups"
STRUCTURAL_ANCHORS = {
    "agent_guide.md",
    "package-index.json",
    "pdr.md",
    "plugin_index.md",
    "readme.md",
    "scope_matrix.md",
    "skill_bridge.md",
    "skill_taxonomy.md",
    "swot.md",
}


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


def pdr_registry_lookup(registry: dict[str, Any]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for pdr in registry.get("pdrs", []):
        if not isinstance(pdr, dict):
            continue
        pdr_id = str(pdr.get("id", "")).strip()
        if not pdr_id:
            continue
        lookup[pdr_id] = {
            "status": str(pdr.get("status", "Backlog")),
            "title": str(pdr.get("title", "")),
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
            detected_pdr_id TEXT,
            implementation_status TEXT,
            implementation_notes TEXT,
            duplicate_status TEXT,
            duplicate_confidence REAL,
            duplicate_notes TEXT,
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

    # Forward-compatible migrations for existing local DBs.
    existing_cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(zip_records)").fetchall()
    }
    for col_name, col_type in (
        ("detected_pdr_id", "TEXT"),
        ("implementation_status", "TEXT"),
        ("implementation_notes", "TEXT"),
        ("duplicate_status", "TEXT"),
        ("duplicate_confidence", "REAL"),
        ("duplicate_notes", "TEXT"),
    ):
        if col_name not in existing_cols:
            conn.execute(f"ALTER TABLE zip_records ADD COLUMN {col_name} {col_type}")
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


def detect_pdr_id_in_zip(zip_path: Path) -> tuple[str, str]:
    """Return (detected_pdr_id, detection_note)."""
    pattern = re.compile(r"PDR-\d{3,}", re.IGNORECASE)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            candidates = [
                n for n in zf.namelist()
                if not n.endswith("/") and n.lower().endswith((".md", ".txt", ".json"))
            ]
            for name in candidates:
                # Prioritize files that look like PDR docs.
                if "pdr" not in name.lower() and not name.lower().endswith("readme.md"):
                    continue
                with zf.open(name, "r") as handle:
                    content = handle.read(64 * 1024).decode("utf-8", errors="ignore")
                match = pattern.search(content)
                if match:
                    return match.group(0).upper(), f"Detected in {name}"

            # Fallback: detect from filenames themselves.
            for name in candidates:
                match = pattern.search(name)
                if match:
                    return match.group(0).upper(), f"Detected from filename {name}"
    except (zipfile.BadZipFile, OSError):
        pass
    return "", "No PDR ID detected in archive"


def zip_member_paths(zip_path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            return [
                normalize_rel(name).strip("/")
                for name in zf.namelist()
                if name and not name.endswith("/")
            ]
    except (zipfile.BadZipFile, OSError):
        return []


def repo_plugin_paths(base_dir: Path) -> set[str]:
    plugin_root = base_dir.parent / ".02_Plugins"
    if not plugin_root.exists():
        return set()

    repo_paths: set[str] = set()
    for file_path in plugin_root.rglob("*"):
        if file_path.is_file():
            repo_paths.add(normalize_rel(str(file_path.relative_to(plugin_root))).lower())
    return repo_paths


def normalize_zip_repo_candidates(member_path: str) -> set[str]:
    normalized = normalize_rel(member_path).strip("/").lower()
    if not normalized:
        return set()

    parts = [part for part in Path(normalized).parts if part not in {".", ""}]
    if not parts:
        return set()

    candidates = {"/".join(parts)}
    if len(parts) > 1:
        candidates.add("/".join(parts[1:]))

    if parts[0].startswith("claude_plugin") and len(parts) > 1:
        candidates.add("/".join(parts[1:]))

    if len(parts) > 2 and parts[1].endswith("-family"):
        candidates.add("/".join(parts[1:]))

    return {candidate for candidate in candidates if candidate}


def assess_duplicate_status(zip_path: Path, base_dir: Path) -> tuple[str, float, str]:
    dups_dir = base_dir / DUPS_ZIP_FOLDER
    current_digest = sha256_file(zip_path)
    if dups_dir.exists():
        for dup_zip in dups_dir.glob("*.zip"):
            if dup_zip.name == zip_path.name:
                continue
            try:
                if sha256_file(dup_zip) == current_digest:
                    return "duplicate", 1.0, f"SHA-256 matches archived duplicate {dup_zip.name}"
            except OSError:
                continue

    repo_paths = repo_plugin_paths(base_dir)
    if not repo_paths:
        return "unknown", 0.0, "No .02_Plugins tree found for redundancy comparison"

    members = zip_member_paths(zip_path)
    if not members:
        return "unknown", 0.0, "No readable file members found in ZIP"

    zip_candidates: set[str] = set()
    zip_basenames: set[str] = set()
    for member in members:
        zip_candidates.update(normalize_zip_repo_candidates(member))
        zip_basenames.add(Path(member).name.lower())

    repo_basenames = {Path(path).name.lower() for path in repo_paths}
    overlap = zip_candidates & repo_paths
    overlap_ratio = len(overlap) / max(len(zip_candidates), 1)
    anchor_hits = sorted((zip_basenames & repo_basenames) & STRUCTURAL_ANCHORS)
    matched_families = sorted({path.split("/", 1)[0] for path in overlap if "/" in path})

    if len(overlap) >= 40 and overlap_ratio >= 0.2:
        return (
            "redundant",
            0.97,
            f"Matched {len(overlap)} implemented plugin paths across families={','.join(matched_families[:6])}; anchors={','.join(anchor_hits[:6])}",
        )
    if len(overlap) >= 20 and len(anchor_hits) >= 4:
        return (
            "redundant",
            0.9,
            f"Strong scaffold overlap with implemented plugins: matched_paths={len(overlap)}; anchors={','.join(anchor_hits[:6])}",
        )
    if len(overlap) >= 8 and len(anchor_hits) >= 2:
        return (
            "possible_redundant",
            0.7,
            f"Partial overlap with implemented plugins: matched_paths={len(overlap)}; anchors={','.join(anchor_hits[:6])}",
        )
    return "unique", 0.1, f"Low overlap with implemented plugins: matched_paths={len(overlap)}"


def assess_implementation_status(
    zip_path: Path,
    detected_pdr_id: str,
    pipeline_meta: dict[str, str],
    registry_pdrs: dict[str, dict[str, str]],
    base_dir: Path,
) -> tuple[str, str]:
    """
    Determine whether the ZIP appears implemented in this local repo context.
    Statuses: not_implemented | preflight_ready | in_progress | implemented | unknown
    """
    extracted_path = pipeline_meta.get("extracted_path", "")
    extracted_abs = (base_dir.parent / extracted_path) if extracted_path.startswith(".01_PDRs/") else (base_dir / extracted_path)
    extracted_ready = extracted_abs.exists() and any(extracted_abs.iterdir()) if extracted_path else False

    linked_pdr_id = pipeline_meta.get("linked_pdr_id", "")
    pdr_id = linked_pdr_id or detected_pdr_id
    pipeline_status = pipeline_meta.get("pipeline_status", "Backlog")

    if pdr_id and pdr_id in registry_pdrs:
        pipeline_status = registry_pdrs[pdr_id].get("status", pipeline_status)

    if pipeline_status in {"Reviewed", "Archived", "Completed"}:
        return "implemented", f"Pipeline status={pipeline_status}; extracted_ready={extracted_ready}"
    if pipeline_status == "In-Process":
        return "in_progress", f"Pipeline status=In-Process; extracted_ready={extracted_ready}"
    if pipeline_status == "Pre-flight":
        return "preflight_ready", f"Pipeline status=Pre-flight; extracted_ready={extracted_ready}"
    if pipeline_status == "Backlog":
        return "not_implemented", f"Pipeline status=Backlog; extracted_ready={extracted_ready}"
    return "unknown", f"Pipeline status={pipeline_status}; extracted_ready={extracted_ready}"


def scan_zip_intake(base_dir: Path, zip_name_filter: str | None = None) -> dict[str, int]:
    registry_path = base_dir / "PDR_REGISTRY.json"
    intake_dir = base_dir / ".intake"
    db_path = intake_dir / "zip_intake.db"
    log_path = intake_dir / "zip_intake-log.jsonl"

    intake_dir.mkdir(parents=True, exist_ok=True)
    registry = load_registry(registry_path)
    lookup = pipeline_lookup(registry)
    registry_pdrs = pdr_registry_lookup(registry)

    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)

        zips = sorted((base_dir / BACKLOG_ZIP_FOLDER).glob("*.zip"))
        zips.extend(sorted((base_dir / DUPS_ZIP_FOLDER).glob("*.zip")))
        if zip_name_filter:
            zips = [z for z in zips if z.name == zip_name_filter]

        seen_names: set[str] = set()
        counts = {
            "new": 0,
            "updated": 0,
            "current": 0,
            "historical": 0,
            "duplicates": 0,
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
            detected_pdr_id, detection_note = detect_pdr_id_in_zip(zip_path)

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
            impl_status, impl_notes = assess_implementation_status(
                zip_path=zip_path,
                detected_pdr_id=detected_pdr_id,
                pipeline_meta=pipeline_meta,
                registry_pdrs=registry_pdrs,
                base_dir=base_dir,
            )
            duplicate_status, duplicate_confidence, duplicate_notes = assess_duplicate_status(
                zip_path=zip_path,
                base_dir=base_dir,
            )

            active_zip_path = zip_path
            if duplicate_status in {"duplicate", "redundant"} and duplicate_confidence >= 0.85:
                dups_dir = base_dir / DUPS_ZIP_FOLDER
                dups_dir.mkdir(parents=True, exist_ok=True)
                target_path = dups_dir / zip_name
                if zip_path.resolve() != target_path.resolve():
                    if target_path.exists():
                        target_path.unlink()
                    os.replace(zip_path, target_path)
                    active_zip_path = target_path
                counts["duplicates"] += 1

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

            rel_zip = str(active_zip_path.relative_to(base_dir.parent)).replace("\\", "/")

            conn.execute(
                """
                INSERT INTO zip_records (
                    zip_name, zip_rel_path, first_seen_at, last_seen_at, sha256, size_bytes,
                    lifecycle_state, pipeline_status, linked_pdr_id, extracted_path,
                    detected_pdr_id, implementation_status, implementation_notes,
                    duplicate_status, duplicate_confidence, duplicate_notes,
                    review_result, review_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(zip_name) DO UPDATE SET
                    zip_rel_path=excluded.zip_rel_path,
                    last_seen_at=excluded.last_seen_at,
                    sha256=excluded.sha256,
                    size_bytes=excluded.size_bytes,
                    lifecycle_state=excluded.lifecycle_state,
                    pipeline_status=excluded.pipeline_status,
                    linked_pdr_id=excluded.linked_pdr_id,
                    extracted_path=excluded.extracted_path,
                    detected_pdr_id=excluded.detected_pdr_id,
                    implementation_status=excluded.implementation_status,
                    implementation_notes=excluded.implementation_notes,
                    duplicate_status=excluded.duplicate_status,
                    duplicate_confidence=excluded.duplicate_confidence,
                    duplicate_notes=excluded.duplicate_notes,
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
                    detected_pdr_id,
                    impl_status,
                    impl_notes,
                    duplicate_status,
                    duplicate_confidence,
                    duplicate_notes,
                    review_result,
                    f"{review_notes}; file_count={file_count}; detection={detection_note}",
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
                    "detected_pdr_id": detected_pdr_id,
                    "implementation_status": impl_status,
                    "implementation_notes": impl_notes,
                    "duplicate_status": duplicate_status,
                    "duplicate_confidence": duplicate_confidence,
                    "duplicate_notes": duplicate_notes,
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
