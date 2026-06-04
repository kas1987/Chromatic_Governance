"""
registry_router.py — Phase 2 Registry-Aware Routing for PDR-005

Reads intake_events.jsonl for pending events.
For each event, loads PDR_REGISTRY.json and looks up each detected PDR ID.

Routing rules:
  - PDR status "Completed"  → archive
  - PDR status "In-Process" → dispatch
  - PDR status "Backlog" or not found → triage

Appends routing decisions to .agents/intake/routing-decisions.jsonl.
Updates the event status from "pending" to "routed" in events.jsonl.

Usage:
    python registry_router.py [--once] [--dry-run]
"""

import os
import re
import json
import datetime
import time
import argparse

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDR_ROOT = os.path.dirname(SCRIPT_DIR)
AGENTS_INTAKE_DIR = os.path.join(PDR_ROOT, ".agents", "intake")
EVENTS_JSONL = os.path.join(AGENTS_INTAKE_DIR, "events.jsonl")
ROUTING_JSONL = os.path.join(AGENTS_INTAKE_DIR, "routing-decisions.jsonl")
REGISTRY_JSON = os.path.join(PDR_ROOT, "PDR_REGISTRY.json")

POLL_INTERVAL_SECONDS = 10


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def load_registry(registry_path: str) -> dict:
    """Load PDR_REGISTRY.json; return empty dict on failure."""
    try:
        with open(registry_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[registry_router] WARNING: Could not load registry: {exc}")
        return {}


def build_pdr_status_map(registry: dict) -> dict:
    """Return {pdr_id: status} mapping from registry pdrs list."""
    mapping = {}
    for pdr in registry.get("pdrs", []):
        pdr_id = pdr.get("id", "").upper()
        status = pdr.get("status", "")
        if pdr_id:
            mapping[pdr_id] = status
    return mapping


def decide_route(pdr_status: str) -> str:
    """Apply routing rules; return decision string."""
    if pdr_status == "Completed":
        return "archive"
    if pdr_status == "In-Process":
        return "dispatch"
    # "Backlog", "Pre-flight", "Reviewed", "Archived", or not found → triage
    return "triage"


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------

def load_events(events_path: str) -> list:
    """Load all events from JSONL; skip malformed lines."""
    events = []
    if not os.path.exists(events_path):
        return events
    with open(events_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def rewrite_events(events_path: str, events: list) -> None:
    """Overwrite events JSONL with the updated events list."""
    os.makedirs(os.path.dirname(events_path), exist_ok=True)
    with open(events_path, "w", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev) + "\n")


def append_routing_decision(routing_path: str, decision: dict) -> None:
    os.makedirs(os.path.dirname(routing_path), exist_ok=True)
    with open(routing_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(decision) + "\n")


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def route_pending_events(
    events_path: str,
    routing_path: str,
    registry_path: str,
    dry_run: bool = False,
) -> int:
    """
    Process all pending events.
    Returns the count of events routed this pass.
    """
    events = load_events(events_path)
    pending = [ev for ev in events if ev.get("status") == "pending"]

    if not pending:
        return 0

    registry = load_registry(registry_path)
    pdr_status_map = build_pdr_status_map(registry)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    routed_count = 0

    for event in events:
        if event.get("status") != "pending":
            continue

        zip_filename = event.get("zip_filename", "")
        detected_ids = event.get("detected_pdr_ids", [])

        # detected_pdr_ids may have been serialised as a JSON string in older events
        if isinstance(detected_ids, str):
            try:
                detected_ids = json.loads(detected_ids)
            except json.JSONDecodeError:
                detected_ids = []

        if not detected_ids:
            # No PDR IDs detected — route the ZIP itself to triage
            decision = {
                "timestamp": timestamp,
                "zip_filename": zip_filename,
                "pdr_id": None,
                "pdr_status": None,
                "decision": "triage",
                "reason": "No PDR IDs detected in ZIP",
            }
            if not dry_run:
                append_routing_decision(routing_path, decision)
            print(
                f"[registry_router] ROUTED  {zip_filename} | PDR: (none) | "
                f"status: (none) → decision: triage"
            )
        else:
            for pdr_id in detected_ids:
                pdr_id_upper = pdr_id.upper()
                pdr_status = pdr_status_map.get(pdr_id_upper, "")
                route = decide_route(pdr_status)
                reason = (
                    f"PDR {pdr_id_upper} has status '{pdr_status}'"
                    if pdr_status
                    else f"PDR {pdr_id_upper} not found in registry"
                )
                decision = {
                    "timestamp": timestamp,
                    "zip_filename": zip_filename,
                    "pdr_id": pdr_id_upper,
                    "pdr_status": pdr_status or None,
                    "decision": route,
                    "reason": reason,
                }
                if not dry_run:
                    append_routing_decision(routing_path, decision)
                print(
                    f"[registry_router] ROUTED  {zip_filename} | PDR: {pdr_id_upper} | "
                    f"status: {pdr_status or '(not found)'} → decision: {route}"
                )

        if not dry_run:
            event["status"] = "routed"
        routed_count += 1

    if not dry_run and routed_count > 0:
        rewrite_events(events_path, events)
        print(f"[registry_router] Updated {routed_count} event(s) to status=routed in events.jsonl")

    return routed_count


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PDR-005 Phase 2 Registry-Aware Router")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process pending events once and exit; default polls continuously.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print routing decisions without writing any files.",
    )
    parser.add_argument("--events-jsonl", default=EVENTS_JSONL)
    parser.add_argument("--routing-jsonl", default=ROUTING_JSONL)
    parser.add_argument("--registry-json", default=REGISTRY_JSON)
    args = parser.parse_args()

    if args.once:
        count = route_pending_events(
            args.events_jsonl,
            args.routing_jsonl,
            args.registry_json,
            dry_run=args.dry_run,
        )
        print(f"[registry_router] Done. Routed {count} event(s).")
        return

    print(f"[registry_router] Polling every {POLL_INTERVAL_SECONDS}s. Ctrl-C to stop.")
    try:
        while True:
            route_pending_events(
                args.events_jsonl,
                args.routing_jsonl,
                args.registry_json,
                dry_run=args.dry_run,
            )
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[registry_router] Stopped.")


if __name__ == "__main__":
    main()
