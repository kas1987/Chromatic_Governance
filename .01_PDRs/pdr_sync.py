#!/usr/bin/env python3
"""
pdr_sync.py
Synchronizes PDR file locations with PDR_REGISTRY.json.
Enforces consistency: PDR file location must match registry status.
Generates audit trail of all transitions.
"""

import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class PDRTransition:
    pdr_id: str
    from_status: str
    to_status: str
    timestamp: str
    reason: str
    actor: str = "system-sync"


STATUS_ORDER = [
    "Backlog",
    "Pre-flight",
    "In-Process",
    "Completed",
    "Reviewed",
    "Archived",
]

STATUS_FOLDER_MAP = {
    "Backlog": ".01_Backlog",
    "Pre-flight": ".02_Pre-flight",
    "In-Process": ".03_In-Process",
    "Completed": ".04_Completed",
    "Reviewed": ".05_Reviewed",
    "Archived": ".00_Archived",
}

BACKLOG_ZIP_FOLDER = ".01_Backlog"

ACTIVE_STATUSES = {"Backlog", "Pre-flight", "In-Process", "Completed", "Reviewed"}


class PDRRegistry:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.base_dir = registry_path.parent
        self.data = self._load_registry()

    def _load_registry(self) -> dict:
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")
        with open(self.registry_path, "r") as f:
            return json.load(f)

    def _save_registry(self) -> None:
        self.data["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.registry_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def _sync_zip_backlog(self) -> None:
        """Track Backlog ZIP bundles and reconcile artifact entries by ZIP name."""
        artifacts = self.data.setdefault("artifact_backlog", [])
        tracked_by_name = {
            Path(str(a.get("zip_path", ""))).name: a
            for a in artifacts
            if isinstance(a, dict) and a.get("zip_path")
        }

        backlog_dir = self.base_dir / BACKLOG_ZIP_FOLDER
        backlog_dir.mkdir(parents=True, exist_ok=True)

        # Back-compat migration: if ZIPs are still in .01_PDRs root, move them to .01_Backlog.
        for root_zip in sorted(self.base_dir.glob("*.zip")):
            target = backlog_dir / root_zip.name
            if not target.exists():
                root_zip.rename(target)
                print(f"📦 Moved ZIP to backlog: {root_zip.name}")

        for zip_file in sorted(backlog_dir.glob("*.zip")):
            rel_zip = str(zip_file.relative_to(self.base_dir.parent))
            zip_name = zip_file.name

            if zip_name in tracked_by_name:
                tracked_by_name[zip_name]["zip_path"] = rel_zip
                tracked_by_name[zip_name]["status"] = "Backlog"
                continue

            artifact_id = f"ART-{zip_file.stem.upper().replace('-', '_')}"
            artifacts.append(
                {
                    "id": artifact_id,
                    "status": "Backlog",
                    "zip_path": rel_zip,
                    "extracted_path": f".01_PDRs/.99_Extracted/{zip_file.stem}",
                    "registered_at": datetime.now(timezone.utc).isoformat(),
                    "notes": "Auto-registered from root ZIP inventory. Keep intact until Pre-flight.",
                }
            )
            print(f"➕ Registered backlog artifact: {zip_file.name}")

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve registry paths consistently whether script is run from repo root or .01_PDRs."""
        raw = Path(path_str)
        if raw.is_absolute():
            return raw
        parts = raw.parts
        if parts and parts[0] == ".01_PDRs":
            return self.base_dir.parent / raw
        return self.base_dir / raw

    def sync_files(self) -> list[PDRTransition]:
        """
        Scan folders and ensure PDR file locations match registry status.
        Returns list of transitions performed.
        """
        transitions = []
        self._sync_zip_backlog()
        status_folders = {status: self.base_dir / folder for status, folder in STATUS_FOLDER_MAP.items()}

        # Map of PDR ID to its current file location
        pdr_files = {}
        for status, folder in status_folders.items():
            if folder.exists():
                for md_file in sorted(folder.glob("PDR-*.md")):
                    # Extract numeric part: PDR-002-xxx.md → PDR-002
                    parts = md_file.stem.split("-")
                    pdr_id = f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else md_file.stem
                    pdr_files[pdr_id] = (status, md_file)

        # Check registry entries against actual files
        for pdr in self.data.get("pdrs", []):
            pdr_id = pdr["id"]
            current_status = pdr["status"]
            current_file_path = self._resolve_path(pdr.get("file_path", ""))

            if pdr_id in pdr_files:
                actual_status, actual_file_path = pdr_files[pdr_id]

                # Mismatch: file location doesn't match registry status
                if actual_status != current_status:
                    print(
                        f"⚠️  Mismatch: {pdr_id} in {actual_status} but registry says {current_status}"
                    )
                    pdr["status"] = actual_status
                    pdr["file_path"] = str(actual_file_path.relative_to(self.base_dir.parent))
                    pdr["updated_at"] = datetime.now(timezone.utc).isoformat()

                    # Record transition
                    transition = PDRTransition(
                        pdr_id=pdr_id,
                        from_status=current_status,
                        to_status=actual_status,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        reason="File location corrected to match folder",
                    )
                    transitions.append(transition)
                    print(f"✅ Synced {pdr_id}: {current_status} → {actual_status}")
            else:
                print(f"❌ Missing file for {pdr_id}: {current_file_path}")

        # Check for orphaned files (files not in registry)
        for pdr_id, (status, file_path) in pdr_files.items():
            if not any(p["id"] == pdr_id for p in self.data.get("pdrs", [])):
                print(f"⚠️  Orphaned file: {file_path} (not in registry)")

        self._save_registry()
        return transitions

    def promote(self, pdr_id: str, to_status: str, reason: str = "") -> bool:
        """
        Transition a PDR to a new status and move its file.
        """
        pdr = next((p for p in self.data.get("pdrs", []) if p["id"] == pdr_id), None)
        if not pdr:
            print(f"❌ PDR not found: {pdr_id}")
            return False

        from_status = pdr["status"]
        workflow = self.data.get("status_workflow", {})

        # Check if transition is allowed
        allowed = workflow.get(from_status, {}).get("allowed_transitions", [])
        if to_status not in allowed:
            print(
                f"❌ Transition not allowed: {pdr_id} {from_status} → {to_status}"
            )
            return False

        if to_status not in STATUS_FOLDER_MAP:
            print(f"❌ Unknown target status: {to_status}")
            return False

        # ZIP lifecycle:
        # - keep zip intact in Backlog
        # - on Pre-flight, ensure extracted folder exists (auto-unpack when zip_path is configured)
        # - entering In-Process from Pre-flight requires extracted content
        zip_path = pdr.get("zip_path")
        extracted_path = pdr.get("extracted_path")

        if to_status == "Pre-flight" and zip_path and extracted_path:
            zip_abs = self._resolve_path(zip_path)
            extracted_abs = self._resolve_path(extracted_path)
            extracted_abs.mkdir(parents=True, exist_ok=True)
            if zip_abs.exists() and not any(extracted_abs.iterdir()):
                shutil.unpack_archive(str(zip_abs), str(extracted_abs))
                print(f"📦 Unpacked ZIP for Pre-flight: {zip_abs.name} -> {extracted_abs}")

        if from_status == "Pre-flight" and to_status == "In-Process" and extracted_path:
            extracted_abs = self._resolve_path(extracted_path)
            if not extracted_abs.exists() or not any(extracted_abs.iterdir()):
                print(
                    f"❌ Cannot enter In-Process: extracted bundle missing/empty at {extracted_abs}"
                )
                return False

        # Move file
        old_path = self._resolve_path(pdr.get("file_path", ""))
        new_path = self.base_dir / STATUS_FOLDER_MAP[to_status] / old_path.name

        if old_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)
            print(f"📁 Moved: {old_path.name} {old_path.parent.name} → {to_status}")
        else:
            print(f"⚠️  File not found, updating registry only: {old_path}")

        # Update registry
        pdr["status"] = to_status
        pdr["file_path"] = str(new_path.relative_to(self.base_dir.parent))
        pdr["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Extracted bundle lifecycle: keep while active, move to archive shelf when Archived.
        extracted_path = pdr.get("extracted_path")
        if to_status == "Archived" and extracted_path:
            source_extracted = self._resolve_path(extracted_path)
            if source_extracted.exists():
                archive_shelf = self.base_dir / STATUS_FOLDER_MAP["Archived"] / "_extracted"
                archive_shelf.mkdir(parents=True, exist_ok=True)
                target_extracted = archive_shelf / pdr_id
                if target_extracted.exists():
                    print(f"⚠️  Archive shelf exists for {pdr_id}, leaving extracted bundle in place")
                else:
                    source_extracted.rename(target_extracted)
                    pdr["archived_extracted_path"] = str(target_extracted.relative_to(self.base_dir.parent))
                    print(f"📦 Archived extracted bundle: {source_extracted.name} -> {target_extracted}")

        # Record transition
        pdr.setdefault("transitions", []).append(
            {
                "from": from_status,
                "to": to_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "user",
                "reason": reason,
            }
        )

        self._save_registry()
        print(f"✅ Promoted {pdr_id}: {from_status} → {to_status}")
        return True

    def report(self) -> str:
        """Generate a status report."""
        lines = ["# PDR Pipeline Status Report", ""]
        by_status = {}
        for pdr in self.data.get("pdrs", []):
            status = pdr["status"]
            by_status.setdefault(status, []).append(pdr)

        for status in STATUS_ORDER:
            pdrs = by_status.get(status, [])
            lines.append(f"## {status} ({len(pdrs)})")
            for pdr in pdrs:
                completion = pdr.get("completion_percentage", 0)
                lines.append(
                    f"- **{pdr['id']}** — {pdr['title']} ({completion}% complete)"
                )
            lines.append("")

        return "\n".join(lines)


def main():
    registry_path = Path(__file__).parent / "PDR_REGISTRY.json"

    if not registry_path.exists():
        print(f"Error: PDR_REGISTRY.json not found at {registry_path}")
        sys.exit(1)

    registry = PDRRegistry(registry_path)

    if len(sys.argv) < 2:
        print("Usage: python pdr_sync.py [sync|promote|report]")
        print("  sync        — sync files with registry")
        print("  promote PDR_ID TO_STATUS [reason]  — promote a PDR")
        print("  report      — show status report")
        sys.exit(1)

    command = sys.argv[1]

    if command == "sync":
        transitions = registry.sync_files()
        if transitions:
            print(f"\n{len(transitions)} transitions recorded")
        else:
            print("✅ All PDRs in sync")

    elif command == "promote":
        if len(sys.argv) < 4:
            print("Usage: python pdr_sync.py promote PDR_ID TO_STATUS [reason]")
            sys.exit(1)
        pdr_id = sys.argv[2]
        to_status = sys.argv[3]
        reason = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        registry.promote(pdr_id, to_status, reason)

    elif command == "report":
        print(registry.report())

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
