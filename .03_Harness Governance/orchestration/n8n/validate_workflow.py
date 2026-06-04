#!/usr/bin/env python3
"""Validate n8n workflow JSON and required environment wiring for Chromatic intake."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

REQUIRED_NODE_NAMES = {
    "Webhook Trigger",
    "Validate Secret",
    "Normalize Event",
    "Deduplicate",
    "Dedupe Gate",
    "Execute Intake",
    "Refresh Registry",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate n8n workflow scaffold for Chromatic ZIP intake")
    parser.add_argument(
        "--workflow",
        default=".03_Harness Governance/orchestration/n8n/pdr-zip-intake-phase1.workflow.json",
        help="Path to workflow JSON",
    )
    parser.add_argument(
        "--require-env",
        default="CHROMATIC_WEBHOOK_SECRET",
        help="Comma-separated env vars that must be set",
    )
    args = parser.parse_args()

    workflow_path = Path(args.workflow)
    if not workflow_path.exists():
        print(json.dumps({"ok": False, "error": f"workflow not found: {workflow_path}"}, indent=2))
        return 1

    try:
        data = json.loads(workflow_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"invalid json: {exc}"}, indent=2))
        return 1

    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    node_names = {n.get("name") for n in nodes if isinstance(n, dict)}
    missing_nodes = sorted(REQUIRED_NODE_NAMES - node_names)

    required_env = [e.strip() for e in args.require_env.split(",") if e.strip()]
    missing_env = [e for e in required_env if not os.environ.get(e)]

    result = {
        "ok": not missing_nodes and not missing_env,
        "workflow": str(workflow_path),
        "node_count": len(nodes),
        "missing_nodes": missing_nodes,
        "missing_env": missing_env,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
