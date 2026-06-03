import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "broker" / "src"))

from models import AccessRequest
from policy_engine import PolicyEngine


def assert_allowed(decision):
    assert decision.allowed, decision


def assert_denied(decision):
    assert not decision.allowed, decision


def run_tests():
    engine = PolicyEngine(ROOT / "config")

    assert_allowed(engine.decide(AccessRequest(
        agent_id="repo_scout",
        repo="example-org/example-repo",
        profile="read_only",
        action="read",
    )))

    assert_denied(engine.decide(AccessRequest(
        agent_id="repo_scout",
        repo="example-org/example-repo",
        profile="patch_standard",
        action="patch",
        task_id="GOV-001",
        branch="agent/reposcout/test",
    )))

    assert_denied(engine.decide(AccessRequest(
        agent_id="code_sentinel",
        repo="example-org/example-repo",
        profile="patch_standard",
        action="patch",
        branch="agent/codesentinel/test",
    )))

    assert_allowed(engine.decide(AccessRequest(
        agent_id="code_sentinel",
        repo="example-org/example-repo",
        profile="patch_standard",
        action="patch",
        task_id="GOV-002",
        branch="agent/codesentinel/test",
    )))

    assert_denied(engine.decide(AccessRequest(
        agent_id="code_sentinel",
        repo="example-org/example-repo",
        profile="patch_standard",
        action="patch",
        task_id="GOV-003",
        branch="badprefix/test",
    )))

    assert engine.path_is_high_risk("example-org/example-repo", ".github/workflows/ci.yml")
    assert engine.path_is_blocked("example-org/example-repo", "secrets/prod.env")
    print("policy_engine tests passed")


if __name__ == "__main__":
    run_tests()
