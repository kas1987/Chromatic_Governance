"""Integration tests for request_access() — verifies decision + audit log together."""
import pytest
from pathlib import Path
from unittest.mock import patch

import main as access_main
from models import AccessRequest

# Self-contained test config (see tests/fixtures/config/). Decoupled from the
# production config/ dir so the suite is not affected by prod config drift.
CONFIG = str(Path(__file__).resolve().parent / "fixtures" / "config")


@pytest.fixture(autouse=True)
def patch_log_path(tmp_path):
    """Redirect AuditLog to a temp file so tests don't write to the repo."""
    with patch("main.AuditLog") as MockLog:
        instance = MockLog.return_value
        written = []
        instance.write.side_effect = written.append
        yield written


class TestRequestAccess:
    def test_allowed_request_returns_allowed_decision(self):
        req = AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        )
        decision = access_main.request_access(req, config_root=CONFIG)
        assert decision.allowed

    def test_denied_request_returns_denied_decision(self):
        req = AccessRequest(
            agent_id="ghost_agent",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        )
        decision = access_main.request_access(req, config_root=CONFIG)
        assert not decision.allowed

    def test_audit_log_called_on_allowed(self, patch_log_path):
        req = AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        )
        access_main.request_access(req, config_root=CONFIG)
        assert len(patch_log_path) == 1
        event = patch_log_path[0]
        assert event["agent_id"] == "repo_scout"
        assert event["allowed"] is True

    def test_audit_log_called_on_denied(self, patch_log_path):
        req = AccessRequest(
            agent_id="ghost_agent",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        )
        access_main.request_access(req, config_root=CONFIG)
        assert len(patch_log_path) == 1
        event = patch_log_path[0]
        assert event["agent_id"] == "ghost_agent"
        assert event["allowed"] is False
        assert event["reason"] == "unknown_agent"

    def test_logged_event_contains_all_request_fields(self, patch_log_path):
        req = AccessRequest(
            agent_id="code_sentinel",
            repo="example-org/example-repo",
            profile="patch_standard",
            action="patch",
            task_id="GOV-099",
            branch="agent/codesentinel/feature",
            target_branch="main",
        )
        access_main.request_access(req, config_root=CONFIG)
        event = patch_log_path[0]
        assert event["task_id"] == "GOV-099"
        assert event["branch"] == "agent/codesentinel/feature"
        assert event["target_branch"] == "main"
