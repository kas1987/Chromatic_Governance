#!/usr/bin/env python3
"""
review_dispatch_graph.py

Phase-1 LangGraph-style dispatcher scaffold for Chromatic review-intake queue items.
This script runs in simulation mode without LangGraph, and can build a real LangGraph
state graph when the `langgraph` package is installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOCK_SCRIPT = Path(".03_Harness Governance/scripts/lock_pr_branch.py")
QUEUE_PATH = Path(".agents/review-intake/next-work.queue.json")
MISSIONS_DIR = Path(".agents/review-intake/missions")
DISPATCH_LOG = Path(".agents/review-intake/logs/agent-dispatch-log.jsonl")

_STOP_CONDITIONS = [
    "Lock cannot be acquired for this PR branch.",
    "Fix requires files outside the allowed_files list.",
    "Reviewer intent is unclear; request clarification before patching.",
    "Security or architecture finding with confidence < 90 requires human decision.",
    "Tests fail outside touched file scope.",
]


@dataclass
class DispatchState:
    queue_id: str
    repo: str
    pr_number: int
    branch: str
    confidence: float
    status: str = "queued"
    attempt: int = 1
    trace_id: str = ""
    state_path: list[str] = field(default_factory=list)
    error: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_queue(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"items": []}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {"items": []}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"items": []}
    if isinstance(data, list):
        return {"items": data}
    data.setdefault("items", [])
    return data


def save_queue(path: Path, queue: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dispatch_id_for(task_id: str) -> str:
    return f"DISP-{hashlib.sha1(task_id.encode()).hexdigest()[:10].upper()}"


def render_mission_packet(item: dict[str, Any]) -> str:
    acceptance = "\n".join(f"- {c}" for c in (item.get("acceptance_checks") or [])) or "- Review manually"
    links = "\n".join(f"- {lnk}" for lnk in (item.get("links") or [])) or "- (no direct links)"
    allowed = "\n".join(f"- {f}" for f in (item.get("allowed_files") or [])) or "- (PR-level scope)"
    stops = "\n".join(f"- {s}" for s in _STOP_CONDITIONS)
    return f"""# Mission Packet - {item.get('id', 'unknown')}\n\n## Task ID\n{item.get('id', '')}\n\n## Objective\n{item.get('title', 'Address review finding')}\n\n## Source\n{links}\n\n## Owner Agent\n{item.get('owner_agent', 'Auditor')}\n\n## Allowed Files\n{allowed}\n\n## Risk Level\n{item.get('risk_level', 'medium')}\n\n## Confidence\n{item.get('confidence_score', 0)}/100\n\n## Acceptance Checks\n{acceptance}\n\n## Stop Conditions\n{stops}\n\n## Notes\n{item.get('notes', '')}\n"""


def write_dispatch_artifacts(item: dict[str, Any], trace: dict[str, Any], missions_dir: Path, dispatch_log: Path) -> dict[str, Any]:
    missions_dir.mkdir(parents=True, exist_ok=True)
    dispatch_log.parent.mkdir(parents=True, exist_ok=True)

    mission_path = missions_dir / f"{item.get('id', 'unknown')}.md"
    mission_path.write_text(render_mission_packet(item), encoding="utf-8")

    entry = {
        "dispatch_id": dispatch_id_for(item.get("id", "unknown")),
        "task_id": item.get("id"),
        "agent": item.get("owner_agent", "Auditor"),
        "status": "dispatched",
        "repo": item.get("repo", "unknown"),
        "pr_number": item.get("pr_number"),
        "started_at": utc_now(),
        "completed_at": None,
        "validation_summary": None,
        "links": item.get("links", []),
        "mission_packet": str(mission_path),
        "trace_id": trace.get("trace_id"),
    }
    with dispatch_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def select_ready_item(queue: dict[str, Any], queue_id: str | None) -> dict[str, Any] | None:
    items = queue.get("items", [])
    if queue_id:
        return next((i for i in items if i.get("id") == queue_id), None)
    ready = [i for i in items if i.get("status") == "ready"]
    ready.sort(key=lambda x: x.get("priority", 0), reverse=True)
    return ready[0] if ready else None


def transition(state: DispatchState, status: str) -> None:
    state.status = status
    state.state_path.append(status)


def try_acquire_lock(state: DispatchState, holder: str = "langgraph-dispatcher") -> tuple[bool, str]:
    if not LOCK_SCRIPT.exists():
        return False, f"Lock script not found: {LOCK_SCRIPT}"

    cmd = [
        "python",
        str(LOCK_SCRIPT),
        "acquire",
        "--repo",
        state.repo,
        "--pr-number",
        str(state.pr_number),
        "--branch",
        state.branch,
        "--holder",
        holder,
        "--queue-item-id",
        state.queue_id,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode == 0:
        return True, proc.stdout.strip()
    return False, (proc.stderr or proc.stdout).strip()


def release_lock(state: DispatchState, holder: str = "langgraph-dispatcher") -> None:
    if not LOCK_SCRIPT.exists():
        return
    cmd = [
        "python",
        str(LOCK_SCRIPT),
        "release",
        "--repo",
        state.repo,
        "--pr-number",
        str(state.pr_number),
        "--branch",
        state.branch,
        "--holder",
        holder,
        "--queue-item-id",
        state.queue_id,
    ]
    subprocess.run(cmd, text=True, capture_output=True, check=False)


def run_simulation(item: dict[str, Any], confidence_threshold: float) -> dict[str, Any]:
    state = DispatchState(
        queue_id=item.get("id", ""),
        repo=item.get("repo", "kas1987/Chromatic_Governance"),
        pr_number=int(item.get("pr_number") or 1),
        branch=item.get("branch", "claude/test-coverage-analysis-XoxC1"),
        confidence=float(item.get("confidence_score", 0)) / 100.0,
        trace_id=f"trace-{item.get('id', 'unknown')}-{int(datetime.now().timestamp())}",
    )

    transition(state, "queued")

    if state.confidence < confidence_threshold:
        transition(state, "failed_terminal")
        state.error = "confidence below threshold; routed to manual review"
        return telemetry(state)

    transition(state, "lock_pending")
    acquired, lock_msg = try_acquire_lock(state)
    if not acquired:
        transition(state, "failed_retryable")
        state.error = f"lock_acquire_failed: {lock_msg}"
        return telemetry(state)

    try:
        transition(state, "locked")
        transition(state, "planning")
        transition(state, "executing")
        transition(state, "validating")
        transition(state, "resolving")
        transition(state, "completed")
        return telemetry(state)
    finally:
        release_lock(state)


def telemetry(state: DispatchState) -> dict[str, Any]:
    return {
        "trace_id": state.trace_id,
        "queue_id": state.queue_id,
        "branch": state.branch,
        "state_path": state.state_path,
        "attempt": state.attempt,
        "result": state.status,
        "failure_class": state.error or None,
        "completed_at": utc_now(),
    }


def apply_writeback(
    *,
    queue_path: Path,
    queue: dict[str, Any],
    item: dict[str, Any],
    trace: dict[str, Any],
    writeback: bool,
    missions_dir: Path,
    dispatch_log: Path,
) -> dict[str, Any] | None:
    if not writeback:
        return None

    dispatch_entry = write_dispatch_artifacts(item, trace, missions_dir, dispatch_log)
    result = str(trace.get("result", ""))
    failure_class = trace.get("failure_class")
    for queue_item in queue.get("items", []):
        if queue_item.get("id") == item.get("id"):
            if result == "completed":
                queue_item["status"] = "in-progress"
            elif result == "failed_retryable":
                queue_item["status"] = "review-required"
            elif result == "failed_terminal":
                queue_item["status"] = "needs-human-decision"
            queue_item["dispatched_at"] = dispatch_entry["started_at"]
            queue_item["dispatch_id"] = dispatch_entry["dispatch_id"]
            queue_item["trace_id"] = trace.get("trace_id")
            queue_item["last_dispatch_result"] = result
            queue_item["last_dispatch_error"] = failure_class
            queue_item["updated_at"] = utc_now()
            break
    save_queue(queue_path, queue)
    return dispatch_entry


def maybe_build_langgraph() -> str:
    try:
        from langgraph.graph import StateGraph  # noqa: F401
    except Exception:
        return "langgraph_not_installed"
    return "langgraph_available"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a LangGraph dispatcher simulation over review-intake queue items.")
    parser.add_argument("--queue", default=str(QUEUE_PATH), help="Path to next-work queue JSON")
    parser.add_argument("--queue-id", default="", help="Specific queue item ID to simulate")
    parser.add_argument("--confidence-threshold", type=float, default=0.75, help="Threshold for auto-dispatch")
    parser.add_argument("--check-langgraph", action="store_true", help="Only report whether langgraph is importable")
    parser.add_argument("--writeback", action="store_true", help="Write queue status, mission packet, and dispatch log")
    parser.add_argument("--missions-dir", default=str(MISSIONS_DIR), help="Mission packet output directory")
    parser.add_argument("--dispatch-log", default=str(DISPATCH_LOG), help="Dispatch log JSONL path")
    args = parser.parse_args()

    if args.check_langgraph:
        print(json.dumps({"langgraph": maybe_build_langgraph()}, indent=2))
        return 0

    queue_path = Path(args.queue)
    queue = load_queue(queue_path)
    item = select_ready_item(queue, args.queue_id or None)
    if not item:
        print(json.dumps({"result": "no_item", "message": "No matching ready queue item found."}, indent=2))
        return 0

    output = run_simulation(item, args.confidence_threshold)
    dispatch_entry = apply_writeback(
        queue_path=queue_path,
        queue=queue,
        item=item,
        trace=output,
        writeback=args.writeback and output.get("result") == "completed",
        missions_dir=Path(args.missions_dir),
        dispatch_log=Path(args.dispatch_log),
    )
    if args.writeback:
        output["writeback"] = "applied" if dispatch_entry else "skipped"
        output["dispatch_id"] = dispatch_entry.get("dispatch_id") if dispatch_entry else None
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
