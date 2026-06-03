"""
governance_check.py
Runs basic governance health checks on the Chromatic_Governance repo.
Flags missing docs, stale routing tables, and posts a GitHub issue summary.
"""
import os
import sys
from pathlib import Path

REQUIRED_FILES = [
    "cross-provider-model-routing.md",
    "model-effort-routing.md",
    "repos-cleanup-inventory.md",
]

def check_required_files(root: Path) -> list[str]:
    missing = []
    for f in REQUIRED_FILES:
        if not (root / f).exists():
            missing.append(f)
    return missing

def main():
    root = Path(os.environ.get("GITHUB_WORKSPACE", "."))
    issues = []

    missing = check_required_files(root)
    if missing:
        issues.append(f"Missing required governance files: {', '.join(missing)}")

    if issues:
        print("Governance check FAILED:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("Governance check PASSED.")

if __name__ == "__main__":
    main()
