#!/usr/bin/env python3
"""
Local ZIP intake automation for GPT-delivered bundles.

Modes:
- once:   scan current .01_PDRs ZIPs through intake pipeline once
- watch:  keep watching .01_PDRs for dropped/updated ZIPs and intake immediately
- import: copy or move ZIPs from a source folder (e.g., Downloads) into .01_PDRs,
          then intake each imported ZIP
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from pdr_zip_intake import scan_zip_intake


BACKLOG_ZIP_FOLDER = ".01_Backlog"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_path(base_dir: Path) -> Path:
    return base_dir / ".intake" / "drop_watcher-state.json"


def load_state(base_dir: Path) -> dict[str, float]:
    path = state_path(base_dir)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return {k: float(v) for k, v in data.items()}
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return {}


def save_state(base_dir: Path, state: dict[str, float]) -> None:
    path = state_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)


def detect_changed_zips(base_dir: Path, previous: dict[str, float]) -> tuple[list[Path], dict[str, float]]:
    current: dict[str, float] = {}
    changed: list[Path] = []
    backlog_dir = base_dir / BACKLOG_ZIP_FOLDER
    backlog_dir.mkdir(parents=True, exist_ok=True)

    for zip_path in sorted(backlog_dir.glob("*.zip")):
        mtime = zip_path.stat().st_mtime
        current[zip_path.name] = mtime
        if previous.get(zip_path.name) != mtime:
            changed.append(zip_path)

    return changed, current


def intake_zip(base_dir: Path, zip_name: str) -> None:
    counts = scan_zip_intake(base_dir=base_dir, zip_name_filter=zip_name)
    print(f"[{utc_now()}] intaked {zip_name}: {counts}")


def run_once(base_dir: Path) -> None:
    counts = scan_zip_intake(base_dir=base_dir)
    print(f"[{utc_now()}] one-shot intake complete: {counts}")


def run_watch(base_dir: Path, interval: int) -> None:
    previous = load_state(base_dir)
    print(f"Watching {base_dir} for ZIP drops every {interval}s (Ctrl+C to stop)")

    try:
        while True:
            changed, current = detect_changed_zips(base_dir, previous)
            for zip_path in changed:
                intake_zip(base_dir, zip_path.name)
            if changed:
                save_state(base_dir, current)
            previous = current
            time.sleep(interval)
    except KeyboardInterrupt:
        save_state(base_dir, previous)
        print("Stopped watcher.")


def import_from_source(base_dir: Path, source_dir: Path, move: bool) -> None:
    if not source_dir.exists():
        raise SystemExit(f"Source folder does not exist: {source_dir}")

    imported = 0
    skipped = 0

    backlog_dir = base_dir / BACKLOG_ZIP_FOLDER
    backlog_dir.mkdir(parents=True, exist_ok=True)

    for src in sorted(source_dir.glob("*.zip")):
        dest = backlog_dir / src.name

        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            skipped += 1
            continue

        if dest.exists():
            stem = dest.stem
            suffix = dest.suffix
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            dest = base_dir / f"{stem}-{ts}{suffix}"

        if move:
            shutil.move(str(src), str(dest))
        else:
            shutil.copy2(src, dest)

        imported += 1
        intake_zip(base_dir, dest.name)

    print(
        f"Import complete from {source_dir}: imported={imported}, skipped={skipped}, mode={'move' if move else 'copy'}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Local ZIP drop automation for PDR intake")
    parser.add_argument(
        "mode",
        choices=["once", "watch", "import"],
        help="Run mode",
    )
    parser.add_argument(
        "--base-dir",
        default=str(Path(__file__).parent),
        help="Path to .01_PDRs (default: script directory)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Watch interval seconds (mode=watch)",
    )
    parser.add_argument(
        "--source-dir",
        default=str(Path.home() / "Downloads"),
        help="Source folder for import mode (default: ~/Downloads)",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move ZIPs from source instead of copying (mode=import)",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        raise SystemExit(f"Base dir not found: {base_dir}")

    if args.mode == "once":
        run_once(base_dir)
    elif args.mode == "watch":
        run_watch(base_dir, interval=args.interval)
    elif args.mode == "import":
        import_from_source(base_dir, Path(args.source_dir), move=args.move)


if __name__ == "__main__":
    main()
