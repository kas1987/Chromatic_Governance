from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "pdr/PDR-github-agent-access-broker.md",
    "governance/best-practices.md",
    "governance/agent-permission-matrix.md",
    "governance/risk-register.md",
    "config/agents.yaml",
    "config/repos.yaml",
    "config/permission_profiles.yaml",
    "broker/src/policy_engine.py",
    "broker/tests/test_policy_engine.py",
    "security/threat-model.md",
    "operations/runbook.md",
    "artifact_manifest.json",
]


def main():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        print("Missing required files:")
        for p in missing:
            print(f"- {p}")
        return 1

    manifest = json.loads((ROOT / "artifact_manifest.json").read_text(encoding="utf-8"))
    for key in ["name", "version", "purpose", "contents", "validation"]:
        if key not in manifest:
            print(f"Manifest missing key: {key}")
            return 1

    print("artifact validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
