"""
governance_check.py
Runs governance health checks on the Chromatic_Governance repo.
Flags missing docs, stale registry, absent hook infrastructure, and posts
a GitHub issue summary when run in CI.
"""
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Required governance documents
# ---------------------------------------------------------------------------
REQUIRED_DOCS = [
    "README.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "cross-provider-model-routing.md",
    "model-effort-routing.md",
    "repos-cleanup-inventory.md",
]

# ---------------------------------------------------------------------------
# Required agent hook infrastructure
# ---------------------------------------------------------------------------
REQUIRED_HOOKS = [
    ".agents/hooks/context_snapshot.py",
    ".agents/hooks/pre_tool_guard.py",
    ".agents/hooks/post_tool_audit.py",
    ".agents/hooks/subagent_stop.py",
    ".claude/settings.json",
]

# ---------------------------------------------------------------------------
# Required review-intake infrastructure
# ---------------------------------------------------------------------------
REQUIRED_INTAKE = [
    ".agents/review-intake/next-work.queue.json",
    ".agents/review-intake/review-intake.state.json",
]

# ---------------------------------------------------------------------------
# Required taxonomy / PDR registry
# ---------------------------------------------------------------------------
REQUIRED_REGISTRY = [
    "taxonomy.json",
    ".01_PDRs/ARTIFACT_TAXONOMY.json",
]


def check_required_files(root: Path, files: list[str], label: str) -> list[str]:
    missing = [f for f in files if not (root / f).exists()]
    return [f"[{label}] Missing: {f}" for f in missing]


def check_settings_hooks(root: Path) -> list[str]:
    """Verify settings.json wires the expected hook events."""
    issues = []
    settings_path = root / ".claude" / "settings.json"
    if not settings_path.exists():
        return ["[hooks] .claude/settings.json not found"]
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"[hooks] .claude/settings.json is not valid JSON: {exc}"]

    hooks = data.get("hooks") or {}
    for expected in ("PreToolUse", "PostToolUse", "Stop", "SubagentStop"):
        if expected not in hooks or not hooks[expected]:
            issues.append(f"[hooks] settings.json missing '{expected}' hook entry")
    return issues


def check_taxonomy_json(root: Path) -> list[str]:
    """Verify taxonomy.json is valid and non-empty."""
    issues = []
    path = root / "taxonomy.json"
    if not path.exists():
        return ["[taxonomy] taxonomy.json not found"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        node_count = data.get("metadata", {}).get("node_count", 0)
        if node_count == 0:
            issues.append("[taxonomy] taxonomy.json has 0 nodes — sync may be stale")
    except (json.JSONDecodeError, OSError) as exc:
        issues.append(f"[taxonomy] taxonomy.json is not valid JSON: {exc}")
    return issues


def check_pdr_registry(root: Path) -> list[str]:
    """Verify ARTIFACT_TAXONOMY.json is valid JSON."""
    issues = []
    path = root / ".01_PDRs" / "ARTIFACT_TAXONOMY.json"
    if not path.exists():
        return ["[pdr] ARTIFACT_TAXONOMY.json not found"]
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        issues.append(f"[pdr] ARTIFACT_TAXONOMY.json is not valid JSON: {exc}")
    return issues


def main() -> int:
    root = Path(os.environ.get("GITHUB_WORKSPACE", "."))
    issues: list[str] = []

    issues += check_required_files(root, REQUIRED_DOCS, "docs")
    issues += check_required_files(root, REQUIRED_HOOKS, "hooks")
    issues += check_required_files(root, REQUIRED_INTAKE, "intake")
    issues += check_required_files(root, REQUIRED_REGISTRY, "registry")
    issues += check_settings_hooks(root)
    issues += check_taxonomy_json(root)
    issues += check_pdr_registry(root)

    if issues:
        print("Governance check FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(f"Governance check PASSED ({len(REQUIRED_DOCS + REQUIRED_HOOKS + REQUIRED_INTAKE + REQUIRED_REGISTRY)} files verified, hooks wired, taxonomy valid).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
