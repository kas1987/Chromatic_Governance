#!/usr/bin/env python3
"""Import n8n workflow JSON and validate required environment wiring."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import error, request

REQUIRED_WORKFLOW_NODES = {
    "Webhook Trigger",
    "Validate Secret",
    "Normalize Event",
    "Deduplicate",
    "Dedupe Gate",
    "Execute Intake",
    "Refresh Registry",
}


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_workflow_structure(path: Path) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"workflow file not found: {path}"]
    try:
        data = read_json(path)
    except json.JSONDecodeError as exc:
        return False, [f"invalid workflow JSON: {exc}"]

    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    names = {node.get("name") for node in nodes if isinstance(node, dict)}
    missing = sorted(REQUIRED_WORKFLOW_NODES - names)
    if missing:
        return False, [f"missing workflow nodes: {', '.join(missing)}"]
    return True, []


def validate_env_vars(required: list[str]) -> tuple[bool, list[str]]:
    missing = [name for name in required if not os.environ.get(name)]
    return (not missing, missing)


def import_workflow(*, base_url: str, api_key: str, workflow: dict) -> tuple[bool, str]:
    endpoint = base_url.rstrip("/") + "/api/v1/workflows"
    payload = json.dumps(workflow).encode("utf-8")
    req = request.Request(endpoint, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-N8N-API-KEY", api_key)

    try:
        with request.urlopen(req, timeout=30) as resp:  # noqa: S310 - explicit n8n endpoint
            body = resp.read().decode("utf-8", errors="replace")
            return True, body
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else str(exc)
        return False, f"HTTP {exc.code}: {detail}"
    except error.URLError as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and import n8n workflow scaffold")
    parser.add_argument(
        "--workflow",
        default=".03_Harness Governance/orchestration/n8n/pdr-zip-intake-phase1.workflow.json",
        help="Path to workflow JSON",
    )
    parser.add_argument(
        "--required-env",
        default="CHROMATIC_WEBHOOK_SECRET",
        help="Comma-separated env vars required for workflow runtime",
    )
    parser.add_argument(
        "--import-workflow",
        action="store_true",
        help="When set, import workflow to n8n via REST API",
    )
    parser.add_argument(
        "--n8n-url",
        default=os.environ.get("N8N_BASE_URL", ""),
        help="n8n base URL (or set N8N_BASE_URL)",
    )
    parser.add_argument(
        "--n8n-api-key",
        default=os.environ.get("N8N_API_KEY", ""),
        help="n8n API key (or set N8N_API_KEY)",
    )
    args = parser.parse_args()

    workflow_path = Path(args.workflow)
    required_env = [name.strip() for name in args.required_env.split(",") if name.strip()]

    workflow_ok, workflow_errors = validate_workflow_structure(workflow_path)
    env_ok, missing_env = validate_env_vars(required_env)

    result: dict[str, object] = {
        "workflow": str(workflow_path),
        "workflow_ok": workflow_ok,
        "env_ok": env_ok,
        "missing_runtime_env": missing_env,
        "import_requested": bool(args.import_workflow),
    }

    if workflow_errors:
        result["workflow_errors"] = workflow_errors

    if not workflow_ok or not env_ok:
        print(json.dumps(result, indent=2))
        return 2

    if not args.import_workflow:
        result["import_status"] = "skipped"
        print(json.dumps(result, indent=2))
        return 0

    missing_import_env: list[str] = []
    if not args.n8n_url:
        missing_import_env.append("N8N_BASE_URL or --n8n-url")
    if not args.n8n_api_key:
        missing_import_env.append("N8N_API_KEY or --n8n-api-key")

    if missing_import_env:
        result["import_status"] = "blocked"
        result["missing_import_env"] = missing_import_env
        print(json.dumps(result, indent=2))
        return 2

    workflow_json = read_json(workflow_path)
    ok, detail = import_workflow(base_url=args.n8n_url, api_key=args.n8n_api_key, workflow=workflow_json)
    result["import_status"] = "success" if ok else "failed"
    result["import_detail"] = detail
    print(json.dumps(result, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
