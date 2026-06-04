"""Tests for validate_artifact.py — required-file and manifest-key checks."""
import json
import pytest
from pathlib import Path

import validate_artifact

HARNESS_ROOT = Path(__file__).resolve().parents[3]


def _make_valid_manifest():
    return {
        "name": "test-artifact",
        "version": "0.1.0",
        "purpose": "testing",
        "contents": [],
        "validation": "passed",
    }


def _scaffold_valid_root(tmp_path: Path) -> Path:
    """Create the minimal directory tree that validate_artifact expects."""
    required_files = [
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
    ]
    for rel in required_files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("placeholder")
    manifest = tmp_path / "artifact_manifest.json"
    manifest.write_text(json.dumps(_make_valid_manifest()))
    return tmp_path


class TestValidArtifact:
    def test_all_files_present_returns_zero(self, tmp_path, monkeypatch):
        root = _scaffold_valid_root(tmp_path)
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        assert validate_artifact.main() == 0

    def test_passing_message_printed(self, tmp_path, monkeypatch, capsys):
        root = _scaffold_valid_root(tmp_path)
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        validate_artifact.main()
        assert "passed" in capsys.readouterr().out


class TestMissingFiles:
    def test_missing_readme_returns_one(self, tmp_path, monkeypatch):
        root = _scaffold_valid_root(tmp_path)
        (root / "README.md").unlink()
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        assert validate_artifact.main() == 1

    def test_missing_file_is_reported(self, tmp_path, monkeypatch, capsys):
        root = _scaffold_valid_root(tmp_path)
        (root / "security" / "threat-model.md").unlink()
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        validate_artifact.main()
        assert "security/threat-model.md" in capsys.readouterr().out

    def test_multiple_missing_files_all_reported(self, tmp_path, monkeypatch, capsys):
        root = _scaffold_valid_root(tmp_path)
        (root / "README.md").unlink()
        (root / "operations" / "runbook.md").unlink()
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        validate_artifact.main()
        out = capsys.readouterr().out
        assert "README.md" in out
        assert "operations/runbook.md" in out


class TestManifestValidation:
    @pytest.mark.parametrize("missing_key", [
        "name", "version", "purpose", "contents", "validation"
    ])
    def test_missing_manifest_key_returns_one(self, tmp_path, monkeypatch, missing_key):
        root = _scaffold_valid_root(tmp_path)
        manifest = _make_valid_manifest()
        del manifest[missing_key]
        (root / "artifact_manifest.json").write_text(json.dumps(manifest))
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        assert validate_artifact.main() == 1

    @pytest.mark.parametrize("missing_key", [
        "name", "version", "purpose", "contents", "validation"
    ])
    def test_missing_manifest_key_is_reported(self, tmp_path, monkeypatch, capsys, missing_key):
        root = _scaffold_valid_root(tmp_path)
        manifest = _make_valid_manifest()
        del manifest[missing_key]
        (root / "artifact_manifest.json").write_text(json.dumps(manifest))
        monkeypatch.setattr(validate_artifact, "ROOT", root)
        validate_artifact.main()
        assert missing_key in capsys.readouterr().out
