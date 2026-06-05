"""Tests for pre_tool_guard.py — check_command() and main() integration."""
from __future__ import annotations

import io
import json
import sys

import pytest

import pre_tool_guard as ptg


class TestCheckCommand:
    def test_safe_git_status_allowed(self):
        blocked, reason = ptg.check_command("git status")
        assert blocked is False
        assert reason == ""

    def test_force_push_long_flag_blocked(self):
        blocked, _ = ptg.check_command("git push --force origin feature-branch")
        assert blocked is True

    def test_force_push_short_flag_blocked(self):
        blocked, _ = ptg.check_command("git push -f origin feature-branch")
        assert blocked is True

    def test_reset_hard_blocked(self):
        blocked, _ = ptg.check_command("git reset --hard HEAD~1")
        assert blocked is True

    def test_force_branch_delete_blocked(self):
        blocked, _ = ptg.check_command("git branch -D old-feature")
        assert blocked is True

    def test_push_no_verify_blocked(self):
        blocked, _ = ptg.check_command("git push --no-verify")
        assert blocked is True

    def test_commit_no_verify_blocked(self):
        blocked, _ = ptg.check_command("git commit --no-verify -m 'skip'")
        assert blocked is True

    def test_drop_table_blocked(self):
        blocked, _ = ptg.check_command("DROP TABLE users;")
        assert blocked is True

    def test_drop_table_case_insensitive(self):
        blocked, _ = ptg.check_command("drop table users")
        assert blocked is True

    def test_push_to_main_blocked(self):
        blocked, _ = ptg.check_command("git push origin main")
        assert blocked is True

    def test_push_to_master_blocked(self):
        blocked, _ = ptg.check_command("git push origin master")
        assert blocked is True

    def test_push_to_feature_branch_allowed(self):
        blocked, _ = ptg.check_command("git push origin feature/my-work")
        assert blocked is False

    def test_rm_root_path_blocked(self):
        blocked, _ = ptg.check_command("rm -rf /some/path")
        assert blocked is True

    def test_blocked_reason_is_non_empty(self):
        _, reason = ptg.check_command("git push --force")
        assert len(reason) > 0

    def test_safe_pytest_command_allowed(self):
        blocked, _ = ptg.check_command("pytest tests/ -v")
        assert blocked is False

    def test_safe_pip_install_allowed(self):
        blocked, _ = ptg.check_command("pip install -r requirements.txt")
        assert blocked is False


class TestMain:
    def _run(self, monkeypatch, payload: dict | None, *, env: dict | None = None) -> int:
        stdin_str = json.dumps(payload) if payload is not None else ""
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_str))
        monkeypatch.setattr(ptg, "_audit_log", lambda entry: None)
        if env:
            for k, v in env.items():
                monkeypatch.setenv(k, v)
        return ptg.main()

    def test_non_shell_tool_allowed(self, monkeypatch):
        rc = self._run(monkeypatch, {"tool_name": "Read", "tool_input": {"file_path": "/foo"}})
        assert rc == 0

    def test_blocked_command_returns_2(self, monkeypatch):
        rc = self._run(monkeypatch, {
            "tool_name": "Bash",
            "tool_input": {"command": "git push --force origin main"},
        })
        assert rc == 2

    def test_blocked_reason_printed_to_stderr(self, monkeypatch, capsys):
        self._run(monkeypatch, {
            "tool_name": "Bash",
            "tool_input": {"command": "git reset --hard HEAD"},
        })
        assert "BLOCKED" in capsys.readouterr().err

    def test_safe_command_returns_0(self, monkeypatch):
        rc = self._run(monkeypatch, {
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/"},
        })
        assert rc == 0

    def test_empty_stdin_returns_0(self, monkeypatch):
        rc = self._run(monkeypatch, None)
        assert rc == 0

    def test_invalid_json_returns_0(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO("not valid json {{{"))
        monkeypatch.setattr(ptg, "_audit_log", lambda entry: None)
        assert ptg.main() == 0

    def test_empty_command_allowed(self, monkeypatch):
        rc = self._run(monkeypatch, {"tool_name": "Bash", "tool_input": {"command": ""}})
        assert rc == 0

    def test_shell_tool_aliases_inspected(self, monkeypatch):
        for tool in ("computer", "execute_bash", "shell", "run_bash", "bash"):
            rc = self._run(monkeypatch, {
                "tool_name": tool,
                "tool_input": {"command": "git push --force"},
            })
            assert rc == 2, f"Tool alias {tool!r} should be blocked"

    def test_agent_id_from_env_does_not_crash(self, monkeypatch):
        rc = self._run(monkeypatch, {
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
        }, env={"CHROMATIC_AGENT_ID": "Sentinel"})
        assert rc == 0

    def test_cmd_key_in_tool_input_also_inspected(self, monkeypatch):
        rc = self._run(monkeypatch, {
            "tool_name": "Bash",
            "tool_input": {"cmd": "git push --force"},
        })
        assert rc == 2
