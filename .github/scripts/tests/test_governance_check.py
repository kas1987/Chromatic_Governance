"""Tests for governance_check.py — required-file detection and exit behaviour."""
import os
import pytest
from pathlib import Path

import governance_check

REQUIRED = governance_check.REQUIRED_FILES


class TestCheckRequiredFiles:
    def test_all_files_present_returns_empty_list(self, tmp_path):
        for f in REQUIRED:
            (tmp_path / f).write_text("content")
        assert governance_check.check_required_files(tmp_path) == []

    def test_missing_file_is_returned(self, tmp_path):
        for f in REQUIRED:
            (tmp_path / f).write_text("content")
        target = REQUIRED[0]
        (tmp_path / target).unlink()
        missing = governance_check.check_required_files(tmp_path)
        assert target in missing

    def test_all_files_missing_returns_all(self, tmp_path):
        missing = governance_check.check_required_files(tmp_path)
        assert set(missing) == set(REQUIRED)

    def test_only_missing_files_reported(self, tmp_path):
        for f in REQUIRED[1:]:
            (tmp_path / f).write_text("content")
        missing = governance_check.check_required_files(tmp_path)
        assert missing == [REQUIRED[0]]


class TestMain:
    def test_passes_when_all_files_present(self, tmp_path, monkeypatch, capsys):
        for f in REQUIRED:
            (tmp_path / f).write_text("content")
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        governance_check.main()  # must not raise
        assert "PASSED" in capsys.readouterr().out

    def test_fails_when_file_missing(self, tmp_path, monkeypatch, capsys):
        for f in REQUIRED[1:]:
            (tmp_path / f).write_text("content")
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        with pytest.raises(SystemExit) as exc:
            governance_check.main()
        assert exc.value.code == 1

    def test_missing_file_name_in_output(self, tmp_path, monkeypatch, capsys):
        for f in REQUIRED[1:]:
            (tmp_path / f).write_text("content")
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        with pytest.raises(SystemExit):
            governance_check.main()
        assert REQUIRED[0] in capsys.readouterr().out

    def test_github_workspace_env_var_used(self, tmp_path, monkeypatch):
        """GITHUB_WORKSPACE should be the root, not the cwd."""
        for f in REQUIRED:
            (tmp_path / f).write_text("content")
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        # cwd is intentionally different — the env var must win
        governance_check.main()  # must not raise

    def test_falls_back_to_dot_when_no_env_var(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)
        monkeypatch.chdir(tmp_path)
        # All files absent → fails, but the important thing is it doesn't crash
        with pytest.raises(SystemExit) as exc:
            governance_check.main()
        assert exc.value.code == 1
