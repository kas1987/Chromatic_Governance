"""Tests for PolicyEngine.decide() and path classification helpers."""
import pytest
from pathlib import Path

from models import AccessRequest
from policy_engine import PolicyEngine

# Self-contained test config (see tests/fixtures/config/). Decoupled from the
# production config/ dir so the suite is not affected by prod config drift.
CONFIG = Path(__file__).resolve().parent / "fixtures" / "config"


@pytest.fixture()
def engine():
    return PolicyEngine(CONFIG)


# ---------------------------------------------------------------------------
# Happy-path cases
# ---------------------------------------------------------------------------

class TestAllowed:
    def test_read_only_read(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert decision.allowed
        assert decision.reason == "allowed"
        assert decision.risk == "low"

    def test_patch_with_task_id_and_valid_branch(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="code_sentinel",
            repo="example-org/example-repo",
            profile="patch_standard",
            action="patch",
            task_id="GOV-002",
            branch="agent/codesentinel/my-fix",
        ))
        assert decision.allowed

    def test_auditor_read_only(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="auditor",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert decision.allowed

    def test_auditor_issue_triage(self, engine):
        """auditor is explicitly allowed the issue_triage profile."""
        decision = engine.decide(AccessRequest(
            agent_id="auditor",
            repo="example-org/example-repo",
            profile="issue_triage",
            action="read",
        ))
        assert decision.allowed


# ---------------------------------------------------------------------------
# Denial cases — agent-level checks
# ---------------------------------------------------------------------------

class TestDeniedAgent:
    def test_unknown_agent(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="ghost_agent",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "unknown_agent"

    def test_inactive_agent(self, engine):
        """janitor is defined in config but status=inactive."""
        decision = engine.decide(AccessRequest(
            agent_id="janitor",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "agent_not_active"


# ---------------------------------------------------------------------------
# Denial cases — repo-level checks
# ---------------------------------------------------------------------------

class TestDeniedRepo:
    def test_unknown_repo(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/nonexistent-repo",
            profile="read_only",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "unknown_repo"

    def test_repo_not_active(self, engine):
        """A repo present in config but with status != active should be denied."""
        engine.repos["example-org/example-repo"]["status"] = "inactive"
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "repo_not_active"

    def test_repo_not_allowed_for_agent(self, engine):
        """An agent whose allowed_repos doesn't include the target repo is denied."""
        engine.agents["repo_scout"]["allowed_repos"] = []
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "repo_not_allowed_for_agent"

    def test_agent_not_allowed_for_repo(self, engine):
        """A repo's allowed_agents list not containing the requesting agent is denied."""
        engine.repos["example-org/example-repo"]["allowed_agents"] = []
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="read_only",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "agent_not_allowed_for_repo"


# ---------------------------------------------------------------------------
# Denial cases — profile-level checks
# ---------------------------------------------------------------------------

class TestDeniedProfile:
    def test_unknown_profile(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="super_admin",
            action="read",
        ))
        assert not decision.allowed
        assert decision.reason == "unknown_profile"

    def test_profile_not_allowed_for_agent(self, engine):
        """repo_scout only has read_only; requesting patch_standard is denied."""
        decision = engine.decide(AccessRequest(
            agent_id="repo_scout",
            repo="example-org/example-repo",
            profile="patch_standard",
            action="patch",
            task_id="GOV-001",
            branch="agent/reposcout/test",
        ))
        assert not decision.allowed
        assert decision.reason == "profile_not_allowed_for_agent"

    def test_profile_does_not_allow_file_writes(self, engine):
        """issue_triage has may_write_files=false; a patch action must be denied."""
        decision = engine.decide(AccessRequest(
            agent_id="auditor",
            repo="example-org/example-repo",
            profile="issue_triage",
            action="patch",
            task_id="GOV-010",
            branch="agent/auditor/my-branch",
        ))
        assert not decision.allowed
        assert decision.reason == "profile_does_not_allow_file_writes"


# ---------------------------------------------------------------------------
# Denial cases — write-action checks
# ---------------------------------------------------------------------------

class TestDeniedWriteRules:
    def test_task_id_required_missing(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="code_sentinel",
            repo="example-org/example-repo",
            profile="patch_standard",
            action="patch",
            branch="agent/codesentinel/test",
        ))
        assert not decision.allowed
        assert decision.reason == "task_id_required_for_write"

    def test_invalid_branch_prefix(self, engine):
        decision = engine.decide(AccessRequest(
            agent_id="code_sentinel",
            repo="example-org/example-repo",
            profile="patch_standard",
            action="patch",
            task_id="GOV-003",
            branch="badprefix/my-fix",
        ))
        assert not decision.allowed
        assert decision.reason == "invalid_branch_prefix"

    def test_direct_protected_branch_write_denied(self, engine):
        """code_sentinel has deny_direct_main_push=true; writing without a branch
        while targeting main should be denied."""
        decision = engine.decide(AccessRequest(
            agent_id="code_sentinel",
            repo="example-org/example-repo",
            profile="patch_standard",
            action="patch",
            task_id="GOV-004",
            branch=None,
            target_branch="main",
        ))
        assert not decision.allowed
        assert decision.reason == "direct_protected_branch_write_denied"


# ---------------------------------------------------------------------------
# Path classification helpers
# ---------------------------------------------------------------------------

class TestPathClassification:
    @pytest.mark.parametrize("path,expected", [
        (".github/workflows/ci.yml", True),
        ("security/threat-model.md", True),
        ("config/agents.yaml", True),
        ("Dockerfile", True),
        ("deploy.pem", True),
        ("README.md", False),
        ("src/main.py", False),
    ])
    def test_path_is_high_risk(self, engine, path, expected):
        assert engine.path_is_high_risk("example-org/example-repo", path) == expected

    @pytest.mark.parametrize("path,expected", [
        ("secrets/prod.env", True),
        ("private_keys/deploy.key", True),
        (".git/config", True),
        ("README.md", False),
        ("src/main.py", False),
    ])
    def test_path_is_blocked(self, engine, path, expected):
        assert engine.path_is_blocked("example-org/example-repo", path) == expected

    def test_path_classification_unknown_repo_returns_false(self, engine):
        assert not engine.path_is_high_risk("unknown/repo", ".github/workflows/ci.yml")
        assert not engine.path_is_blocked("unknown/repo", "secrets/prod.env")
