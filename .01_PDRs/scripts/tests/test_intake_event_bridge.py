"""
test_intake_event_bridge.py — Unit tests for intake_event_bridge.py (Phase 1, PDR-005)

Run with:
    python -m pytest scripts/tests/test_intake_event_bridge.py -v
or from repo root:
    python -m pytest .01_PDRs/scripts/tests/test_intake_event_bridge.py -v
"""

import os
import sys
import json
import sqlite3
import zipfile
import tempfile

import pytest

# Make the scripts package importable when running from any working directory
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import intake_event_bridge as bridge


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_zip(directory: str, name: str, md_content: str = "") -> str:
    """Create a minimal ZIP file inside *directory* and return its full path."""
    zip_path = os.path.join(directory, name)
    with zipfile.ZipFile(zip_path, "w") as zf:
        if md_content:
            zf.writestr("README.md", md_content)
    return zip_path


# ---------------------------------------------------------------------------
# Test 1: extract_pdr_ids — IDs found in filename and .md content
# ---------------------------------------------------------------------------

class TestExtractPdrIds:
    def test_ids_from_filename_and_md(self, tmp_path):
        """PDR IDs should be found both in the ZIP filename and inside a top-level .md."""
        zip_path = make_zip(
            str(tmp_path),
            "PDR-005-intake.zip",
            md_content="This file relates to PDR-005 and PDR-002.\n",
        )
        ids = bridge.extract_pdr_ids(zip_path)
        assert "PDR-005" in ids
        assert "PDR-002" in ids
        # Deduplicated — PDR-005 appears in name AND md but should appear once
        assert ids.count("PDR-005") == 1

    def test_no_pdr_ids_returns_empty(self, tmp_path):
        """A ZIP with no PDR patterns returns an empty list."""
        zip_path = make_zip(str(tmp_path), "random-artifact.zip", md_content="No references here.")
        ids = bridge.extract_pdr_ids(zip_path)
        assert ids == []

    def test_ids_case_normalised_to_upper(self, tmp_path):
        """IDs found as 'pdr-003' should be normalised to 'PDR-003'."""
        zip_path = make_zip(str(tmp_path), "artifact.zip", md_content="See pdr-003 for details.")
        ids = bridge.extract_pdr_ids(zip_path)
        assert "PDR-003" in ids


# ---------------------------------------------------------------------------
# Test 2: process_zip — event written to JSONL and SQLite
# ---------------------------------------------------------------------------

class TestProcessZip:
    def test_event_written_to_jsonl_and_sqlite(self, tmp_path):
        """process_zip should persist one pending event to both JSONL and SQLite."""
        # Create a ZIP with a known PDR ID
        zip_path = make_zip(str(tmp_path), "PDR-005-test.zip")

        events_jsonl = str(tmp_path / "events.jsonl")
        sqlite_db = str(tmp_path / "intake.db")

        # Override module-level globals for this test
        bridge.EVENTS_JSONL = events_jsonl
        bridge.AGENTS_INTAKE_DIR = str(tmp_path)

        conn = bridge.ensure_db(sqlite_db)
        event = bridge.process_zip(zip_path, conn)
        conn.close()

        # --- JSONL check ---
        assert os.path.exists(events_jsonl), "events.jsonl was not created"
        with open(events_jsonl, "r") as fh:
            records = [json.loads(line) for line in fh if line.strip()]
        assert len(records) == 1
        rec = records[0]
        assert rec["zip_filename"] == "PDR-005-test.zip"
        assert rec["status"] == "pending"
        assert "PDR-005" in rec["detected_pdr_ids"]

        # --- SQLite check ---
        conn2 = sqlite3.connect(sqlite_db)
        row = conn2.execute(
            "SELECT zip_filename, status FROM intake_events WHERE zip_filename = ?",
            ("PDR-005-test.zip",),
        ).fetchone()
        conn2.close()
        assert row is not None, "Row not found in SQLite"
        assert row[0] == "PDR-005-test.zip"
        assert row[1] == "pending"


# ---------------------------------------------------------------------------
# Test 3: scan_and_process — idempotency (same ZIP not double-processed)
# ---------------------------------------------------------------------------

class TestScanAndProcess:
    def test_no_duplicate_events_on_rescan(self, tmp_path):
        """Rescanning a directory should not produce duplicate events for the same ZIP."""
        backlog_dir = str(tmp_path / "backlog")
        os.makedirs(backlog_dir)
        make_zip(backlog_dir, "PDR-004-artifact.zip")

        events_jsonl = str(tmp_path / "events.jsonl")
        sqlite_db = str(tmp_path / "intake.db")

        bridge.BACKLOG_DIR = backlog_dir
        bridge.EVENTS_JSONL = events_jsonl
        bridge.AGENTS_INTAKE_DIR = str(tmp_path)

        conn = bridge.ensure_db(sqlite_db)
        seen: set = set()

        # First scan — should process 1 ZIP
        seen = bridge.scan_and_process(conn, seen)
        assert "PDR-004-artifact.zip" in seen

        # Second scan — same ZIP, should not produce another event
        seen = bridge.scan_and_process(conn, seen)
        conn.close()

        with open(events_jsonl, "r") as fh:
            records = [json.loads(line) for line in fh if line.strip()]
        assert len(records) == 1, "Duplicate event written on rescan"
