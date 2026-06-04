"""
intake_event_bridge.py — Phase 1 Intake Event Bridge for PDR-005

Watches .01_Backlog for new .zip files using os.listdir polling (stdlib only).
For each new ZIP:
  - Extracts PDR IDs from filename and top-level .md files inside the ZIP
  - Writes intake event to .agents/intake/events.jsonl
  - Writes same event to SQLite at intake.db (table: intake_events)
  - Prints a summary line per event processed

Usage:
    python intake_event_bridge.py [--once]

    --once    Process current state and exit (for testing / CI); default is loop.
"""

import os
import re
import json
import sqlite3
import zipfile
import datetime
import time
import argparse
import sys

# ---------------------------------------------------------------------------
# Path constants — all relative so they survive repo moves
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDR_ROOT = os.path.dirname(SCRIPT_DIR)               # .01_PDRs/
BACKLOG_DIR = os.path.join(PDR_ROOT, ".01_Backlog")
AGENTS_INTAKE_DIR = os.path.join(PDR_ROOT, ".agents", "intake")
EVENTS_JSONL = os.path.join(AGENTS_INTAKE_DIR, "events.jsonl")
SQLITE_DB = os.path.join(PDR_ROOT, "intake.db")

PDR_ID_PATTERN = re.compile(r"PDR-\d{3}", re.IGNORECASE)
POLL_INTERVAL_SECONDS = 5


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def ensure_db(db_path: str) -> sqlite3.Connection:
    """Open (or create) the SQLite DB and ensure the intake_events table exists."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS intake_events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT    NOT NULL,
            zip_filename    TEXT    NOT NULL,
            detected_pdr_ids TEXT   NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'pending',
            UNIQUE(zip_filename)
        )
    """)
    conn.commit()
    return conn


def already_recorded(conn: sqlite3.Connection, zip_filename: str) -> bool:
    """Return True if this ZIP has already been written to the DB."""
    row = conn.execute(
        "SELECT 1 FROM intake_events WHERE zip_filename = ?", (zip_filename,)
    ).fetchone()
    return row is not None


def insert_event(conn: sqlite3.Connection, event: dict) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO intake_events (timestamp, zip_filename, detected_pdr_ids, status)
        VALUES (:timestamp, :zip_filename, :detected_pdr_ids, :status)
        """,
        {
            **event,
            "detected_pdr_ids": json.dumps(event["detected_pdr_ids"]),
        },
    )
    conn.commit()


def update_status_in_db(conn: sqlite3.Connection, zip_filename: str, new_status: str) -> None:
    conn.execute(
        "UPDATE intake_events SET status = ? WHERE zip_filename = ?",
        (new_status, zip_filename),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------

def load_recorded_zips_from_jsonl(jsonl_path: str) -> set:
    """Return set of zip_filenames already in the JSONL."""
    seen = set()
    if not os.path.exists(jsonl_path):
        return seen
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                seen.add(rec.get("zip_filename", ""))
            except json.JSONDecodeError:
                pass
    return seen


def append_event_jsonl(jsonl_path: str, event: dict) -> None:
    os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
    with open(jsonl_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def update_status_in_jsonl(jsonl_path: str, zip_filename: str, new_status: str) -> None:
    """Rewrite events.jsonl updating the status for the given zip_filename."""
    if not os.path.exists(jsonl_path):
        return
    lines = []
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("zip_filename") == zip_filename:
                    rec["status"] = new_status
                lines.append(json.dumps(rec))
            except json.JSONDecodeError:
                lines.append(line)
    with open(jsonl_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# PDR ID extraction
# ---------------------------------------------------------------------------

def extract_pdr_ids(zip_path: str) -> list:
    """
    Scan the ZIP filename and top-level .md files inside the archive for PDR-NNN patterns.
    Returns a sorted, deduplicated list of matched IDs (upper-cased).
    """
    ids = set()

    # 1. Filename itself
    basename = os.path.basename(zip_path)
    for m in PDR_ID_PATTERN.findall(basename):
        ids.add(m.upper())

    # 2. Top-level .md files inside the ZIP
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                # Top-level only: no directory separator in the name (or exactly one level)
                parts = name.split("/")
                if len(parts) <= 2 and name.endswith(".md"):
                    try:
                        content = zf.read(name).decode("utf-8", errors="replace")
                        for m in PDR_ID_PATTERN.findall(content):
                            ids.add(m.upper())
                    except Exception:
                        pass
    except (zipfile.BadZipFile, OSError):
        pass  # Corrupt or partial ZIP — proceed with filename matches only

    return sorted(ids)


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process_zip(zip_path: str, conn: sqlite3.Connection) -> dict:
    """Process a single ZIP, persist event, return the event dict."""
    zip_filename = os.path.basename(zip_path)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    detected_ids = extract_pdr_ids(zip_path)

    event = {
        "timestamp": timestamp,
        "zip_filename": zip_filename,
        "detected_pdr_ids": detected_ids,
        "status": "pending",
    }

    append_event_jsonl(EVENTS_JSONL, event)
    insert_event(conn, event)

    id_str = ", ".join(detected_ids) if detected_ids else "(none)"
    print(f"[intake_event_bridge] PROCESSED  {zip_filename} | PDR IDs: {id_str} | status: pending")
    return event


def scan_and_process(conn: sqlite3.Connection, seen: set) -> set:
    """
    Scan BACKLOG_DIR for .zip files not yet in `seen`.
    Process new ones, update `seen`, and return the updated set.
    """
    try:
        entries = os.listdir(BACKLOG_DIR)
    except FileNotFoundError:
        print(f"[intake_event_bridge] WARNING: Backlog dir not found: {BACKLOG_DIR}")
        return seen

    for entry in entries:
        if not entry.lower().endswith(".zip"):
            continue
        if entry in seen:
            continue
        full_path = os.path.join(BACKLOG_DIR, entry)
        if not os.path.isfile(full_path):
            continue
        process_zip(full_path, conn)
        seen.add(entry)

    return seen


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Declare globals first — must come before any use of these names in the function
    global BACKLOG_DIR, EVENTS_JSONL, SQLITE_DB, AGENTS_INTAKE_DIR

    parser = argparse.ArgumentParser(description="PDR-005 Phase 1 Intake Event Bridge")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Scan once and exit (for CI / test use); default polls continuously.",
    )
    parser.add_argument(
        "--backlog-dir",
        default=BACKLOG_DIR,
        help="Override the backlog directory to watch (useful for tests).",
    )
    parser.add_argument(
        "--events-jsonl",
        default=EVENTS_JSONL,
        help="Override the events JSONL output path.",
    )
    parser.add_argument(
        "--sqlite-db",
        default=SQLITE_DB,
        help="Override the SQLite DB path.",
    )
    args = parser.parse_args()

    # Apply overrides (used by tests and CLI)
    BACKLOG_DIR = args.backlog_dir
    EVENTS_JSONL = args.events_jsonl
    SQLITE_DB = args.sqlite_db
    AGENTS_INTAKE_DIR = os.path.dirname(EVENTS_JSONL)

    os.makedirs(AGENTS_INTAKE_DIR, exist_ok=True)

    conn = ensure_db(SQLITE_DB)
    seen = load_recorded_zips_from_jsonl(EVENTS_JSONL)

    if args.once:
        scan_and_process(conn, seen)
        conn.close()
        return

    print(f"[intake_event_bridge] Watching {BACKLOG_DIR} every {POLL_INTERVAL_SECONDS}s. Ctrl-C to stop.")
    try:
        while True:
            seen = scan_and_process(conn, seen)
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[intake_event_bridge] Stopped.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
