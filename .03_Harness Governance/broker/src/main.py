from pathlib import Path

from models import AccessRequest
from policy_engine import PolicyEngine
from audit_log import AuditLog


def request_access(req: AccessRequest, config_root: str = "config"):
    engine = PolicyEngine(config_root)
    decision = engine.decide(req)
    AuditLog("logs/access_events.jsonl").write({
        "agent_id": req.agent_id,
        "repo": req.repo,
        "profile": req.profile,
        "task_id": req.task_id,
        "branch": req.branch,
        "target_branch": req.target_branch,
        "action": req.action,
        "allowed": decision.allowed,
        "reason": decision.reason,
        "risk": decision.risk,
    })
    return decision


if __name__ == "__main__":
    request = AccessRequest(
        agent_id="repo_scout",
        repo="example-org/example-repo",
        profile="read_only",
        action="read",
    )
    print(request_access(request, config_root=str(Path(__file__).resolve().parents[2] / "config")))
