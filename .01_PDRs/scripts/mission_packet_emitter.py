"""
mission_packet_emitter.py — Phase 3: Human/Agent Handoff

Reads routing-decisions.jsonl, emits mission packets for dispatch decisions
that have not yet been emitted. Idempotent: skips any pdr_id+zip combo that
already has a mission file on disk.

Usage:
    python scripts/mission_packet_emitter.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path constants — all relative to the repo root so this script can be called
# from any working directory.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # C:\.00_Governance
PDR_ROOT = REPO_ROOT / ".01_PDRs"
INTAKE_DIR = PDR_ROOT / ".agents" / "intake"
MISSIONS_DIR = REPO_ROOT / ".agents" / "review-intake" / "missions"
ROUTING_DECISIONS = INTAKE_DIR / "routing-decisions.jsonl"
EMISSIONS_LOG = INTAKE_DIR / "emissions.jsonl"

PACKET_TEMPLATE = """\
---
mission_id: {mission_id}
pdr_id: {pdr_id}
source_zip: {zip_filename}
status: pending
created_at: {timestamp}
---
# Mission: Intake {pdr_id}

## Context
ZIP artifact received: {zip_filename}

## Required Actions
- [ ] Review ZIP contents against PDR-{pdr_num} acceptance criteria
- [ ] Update PDR_REGISTRY.json completion_percentage
- [ ] Move to appropriate pipeline stage
"""


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


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _already_emitted(
    emissions: list[dict], pdr_id: str, zip_filename: str
) -> bool:
    """Return True if an emission record exists for this pdr_id + zip combo."""
    for e in emissions:
        if e.get("pdr_id") == pdr_id and e.get("zip_filename") == zip_filename:
            return True
    return False


def _mission_file_exists(pdr_id: str, zip_filename: str) -> Path | None:
    """Return the first existing mission file that matches pdr_id + zip stem."""
    if not MISSIONS_DIR.exists():
        return None
    zip_stem = Path(zip_filename).stem
    for candidate in MISSIONS_DIR.glob(f"INTAKE-{pdr_id}-*.md"):
        # Read frontmatter to confirm zip match (cheap guard against stem collisions)
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if f"source_zip: {zip_filename}" in text:
            return candidate
    return None


def _pdr_num(pdr_id: str) -> str:
    """Extract the numeric portion from a PDR id like 'PDR-005' -> '005'."""
    parts = pdr_id.upper().split("-")
    return parts[1] if len(parts) >= 2 else pdr_id


def emit_missions(dry_run: bool = False) -> int:
    """Process routing-decisions.jsonl and emit pending mission packets.

    Returns the count of newly emitted packets.
    """
    decisions = _load_jsonl(ROUTING_DECISIONS)
    emissions = _load_jsonl(EMISSIONS_LOG)

    dispatch_decisions = [
        d for d in decisions if d.get("decision") == "dispatch"
    ]

    if not dispatch_decisions:
        print("No dispatch decisions found in routing-decisions.jsonl.")
        return 0

    MISSIONS_DIR.mkdir(parents=True, exist_ok=True)

    emitted_count = 0
    for record in dispatch_decisions:
        pdr_id: str = record.get("pdr_id", "UNKNOWN")
        zip_filename: str = record.get("zip_filename", record.get("zip_name", "unknown.zip"))

        # Idempotency check 1: emissions log
        if _already_emitted(emissions, pdr_id, zip_filename):
            print(f"  [SKIP] Already emitted for {pdr_id} / {zip_filename}")
            continue

        # Idempotency check 2: mission file on disk
        existing = _mission_file_exists(pdr_id, zip_filename)
        if existing:
            print(
                f"  [SKIP] Mission file already exists on disk: {existing.name}"
            )
            continue

        # Build mission id and packet
        now = datetime.now(timezone.utc)
        ts_short = now.strftime("%Y%m%dT%H%M%S")
        ts_full = now.isoformat()
        mission_id = f"INTAKE-{pdr_id}-{ts_short}"

        packet_content = PACKET_TEMPLATE.format(
            mission_id=mission_id,
            pdr_id=pdr_id,
            zip_filename=zip_filename,
            timestamp=ts_full,
            pdr_num=_pdr_num(pdr_id),
        )

        mission_path = MISSIONS_DIR / f"{mission_id}.md"

        if dry_run:
            print(f"  [DRY-RUN] Would write: {mission_path}")
            print(f"  [DRY-RUN] Would append emission to: {EMISSIONS_LOG}")
        else:
            mission_path.write_text(packet_content, encoding="utf-8")

            emit_record = {
                "timestamp": ts_full,
                "mission_id": mission_id,
                "pdr_id": pdr_id,
                "zip_filename": zip_filename,
            }
            _append_jsonl(EMISSIONS_LOG, emit_record)
            print(f"  [OK] Emitted mission packet: {mission_path.name}")

        emitted_count += 1

    return emitted_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit mission packets for dispatch routing decisions."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without writing any files.",
    )
    args = parser.parse_args()

    print(f"mission_packet_emitter — {'DRY RUN ' if args.dry_run else ''}starting")
    print(f"  Routing decisions : {ROUTING_DECISIONS}")
    print(f"  Missions dir      : {MISSIONS_DIR}")
    print(f"  Emissions log     : {EMISSIONS_LOG}")
    print()

    count = emit_missions(dry_run=args.dry_run)
    print(f"\nDone. Packets emitted this run: {count}")


if __name__ == "__main__":
    main()
