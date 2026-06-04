"""
intake_metrics.py — Phase 4: Governance Metrics

Reads events.jsonl, routing-decisions.jsonl, and emissions.jsonl from the
intake agent directory. Computes weekly intake statistics, prints a summary
to stdout, and writes a dated JSON report.

Usage:
    python scripts/intake_metrics.py [--week-offset N]

    --week-offset N  (default 0) — 0 = current week, 1 = last week, etc.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # C:\.00_Governance
PDR_ROOT = REPO_ROOT / ".01_PDRs"
INTAKE_DIR = PDR_ROOT / ".agents" / "intake"

EVENTS_LOG = INTAKE_DIR / "events.jsonl"
ROUTING_DECISIONS = INTAKE_DIR / "routing-decisions.jsonl"
EMISSIONS_LOG = INTAKE_DIR / "emissions.jsonl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file, skipping malformed lines. Returns [] if missing."""
    if not path.exists():
        return []
    records: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                print(
                    f"  [WARN] Skipping malformed line {lineno} in {path.name}: {exc}",
                    file=sys.stderr,
                )
    return records


def _parse_ts(ts_str: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp string, returning None on failure."""
    if not ts_str:
        return None
    try:
        # Python 3.11+ handles Z suffix natively; for 3.10 and below replace it.
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _week_bounds(week_offset: int = 0) -> tuple[datetime, datetime]:
    """Return (start, end) UTC datetimes for the requested ISO week.

    week_offset=0 is the current week (Monday 00:00 UTC to Sunday 23:59:59 UTC).
    week_offset=1 is last week, etc.
    """
    today = datetime.now(timezone.utc)
    # Monday of the current week
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    monday -= timedelta(weeks=week_offset)
    sunday_end = monday + timedelta(weeks=1) - timedelta(microseconds=1)
    return monday, sunday_end


def _in_window(ts: datetime | None, start: datetime, end: datetime) -> bool:
    if ts is None:
        return False
    # Make naive timestamps UTC-aware for comparison
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return start <= ts <= end


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def compute_metrics(week_offset: int = 0) -> dict:
    week_start, week_end = _week_bounds(week_offset)
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    events = _load_jsonl(EVENTS_LOG)
    decisions = _load_jsonl(ROUTING_DECISIONS)
    emissions = _load_jsonl(EMISSIONS_LOG)

    # --- Events in window ---
    week_events = [
        e for e in events
        if _in_window(_parse_ts(e.get("timestamp")), week_start, week_end)
    ]
    total_processed = len(week_events)

    # Build set of zip_filenames that appear in decisions for this week
    week_decision_zips: set[str] = set()
    by_decision: dict[str, int] = {"archive": 0, "dispatch": 0, "triage": 0}

    week_decisions = [
        d for d in decisions
        if _in_window(_parse_ts(d.get("timestamp")), week_start, week_end)
    ]
    for d in week_decisions:
        decision_key = d.get("decision", "unknown")
        if decision_key in by_decision:
            by_decision[decision_key] += 1
        else:
            # Count unexpected decision values under their own key
            by_decision[decision_key] = by_decision.get(decision_key, 0) + 1
        zip_name = d.get("zip_filename") or d.get("zip_name", "")
        if zip_name:
            week_decision_zips.add(zip_name)

    routed = len(week_decisions)

    # --- Pending events (have an event record but no routing decision) ---
    event_zips = {
        e.get("zip_filename") or e.get("zip_name", "") for e in week_events
    }
    pending_zips = event_zips - week_decision_zips
    # Remove empty-string entries caused by missing fields
    pending_zips.discard("")
    pending = len(pending_zips)

    # --- Missions emitted this week ---
    missions_emitted = sum(
        1 for e in emissions
        if _in_window(_parse_ts(e.get("timestamp")), week_start, week_end)
    )

    return {
        "report_date": report_date,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_processed": total_processed,
        "routed": routed,
        "pending": pending,
        "by_decision": by_decision,
        "missions_emitted": missions_emitted,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(metrics: dict) -> None:
    sep = "-" * 50
    print(sep)
    print(f"  Intake Governance Metrics — {metrics['report_date']}")
    print(f"  Week: {metrics['week_start'][:10]} to {metrics['week_end'][:10]}")
    print(sep)
    print(f"  Total ZIPs processed this week : {metrics['total_processed']}")
    print(f"  Routed (have a decision)       : {metrics['routed']}")
    print(f"  Still pending (backlog)        : {metrics['pending']}")
    print()
    print("  Routing breakdown:")
    for decision, count in sorted(metrics["by_decision"].items()):
        print(f"    {decision:<12} : {count}")
    print()
    print(f"  Mission packets emitted        : {metrics['missions_emitted']}")
    print(sep)

    if metrics["pending"] > 0:
        print(
            f"  [FLAG] {metrics['pending']} ZIP event(s) are not yet routed — "
            "investigate routing-decisions.jsonl for gaps."
        )
        print(sep)


def write_report(metrics: dict) -> Path:
    report_path = INTAKE_DIR / f"metrics-{metrics['report_date']}.json"
    INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    # Build the canonical output shape required by the spec
    output = {
        "report_date": metrics["report_date"],
        "total_processed": metrics["total_processed"],
        "routed": metrics["routed"],
        "pending": metrics["pending"],
        "by_decision": metrics["by_decision"],
        "missions_emitted": metrics["missions_emitted"],
    }
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return report_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute intake governance metrics for a given week."
    )
    parser.add_argument(
        "--week-offset",
        type=int,
        default=0,
        metavar="N",
        help="0 = current week (default), 1 = last week, etc.",
    )
    args = parser.parse_args()

    print(f"intake_metrics — computing for week_offset={args.week_offset}")
    print(f"  events.jsonl          : {EVENTS_LOG}")
    print(f"  routing-decisions     : {ROUTING_DECISIONS}")
    print(f"  emissions.jsonl       : {EMISSIONS_LOG}")
    print()

    metrics = compute_metrics(week_offset=args.week_offset)
    print_report(metrics)

    report_path = write_report(metrics)
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
