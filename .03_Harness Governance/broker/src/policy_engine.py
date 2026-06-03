from pathlib import Path
from typing import Any, Dict
import fnmatch
import yaml

from models import AccessRequest, AccessDecision


class PolicyEngine:
    def __init__(self, config_root: str | Path):
        self.config_root = Path(config_root)
        self.agents = self._load_yaml("agents.yaml").get("agents", {})
        self.repos = self._load_yaml("repos.yaml").get("repos", {})
        self.profiles = self._load_yaml("permission_profiles.yaml").get("profiles", {})

    def _load_yaml(self, name: str) -> Dict[str, Any]:
        path = self.config_root / name
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def decide(self, req: AccessRequest) -> AccessDecision:
        agent = self.agents.get(req.agent_id)
        if not agent:
            return AccessDecision(False, "unknown_agent", "medium")
        if agent.get("status") != "active":
            return AccessDecision(False, "agent_not_active", "medium")

        repo = self.repos.get(req.repo)
        if not repo:
            return AccessDecision(False, "unknown_repo", "medium")
        if repo.get("status") != "active":
            return AccessDecision(False, "repo_not_active", "medium")

        if req.repo not in agent.get("allowed_repos", []):
            return AccessDecision(False, "repo_not_allowed_for_agent", "high")
        if req.agent_id not in repo.get("allowed_agents", []):
            return AccessDecision(False, "agent_not_allowed_for_repo", "high")

        profile = self.profiles.get(req.profile)
        if not profile:
            return AccessDecision(False, "unknown_profile", "medium")
        if req.profile not in agent.get("allowed_profiles", []):
            return AccessDecision(False, "profile_not_allowed_for_agent", "high")

        is_write = req.action in {"write", "commit", "branch", "pr", "patch"}
        if is_write:
            if not profile.get("may_write_files", False) and req.action in {"write", "commit", "patch"}:
                return AccessDecision(False, "profile_does_not_allow_file_writes", "high")
            if profile.get("require_task_id", False) or agent.get("require_task_id_for_write", False):
                if not req.task_id:
                    return AccessDecision(False, "task_id_required_for_write", "medium")
            if agent.get("deny_direct_main_push", False) and req.target_branch in repo.get("protected_branches", []):
                if req.action in {"write", "commit", "patch"} and not req.branch:
                    return AccessDecision(False, "direct_protected_branch_write_denied", "high")
            branch_prefix = agent.get("branch_prefix")
            if branch_prefix and req.branch and not req.branch.startswith(branch_prefix):
                return AccessDecision(False, "invalid_branch_prefix", "medium")

        return AccessDecision(True, "allowed", "low")

    def path_is_blocked(self, repo_name: str, file_path: str) -> bool:
        repo = self.repos.get(repo_name, {})
        for pattern in repo.get("blocked_paths", []):
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def path_is_high_risk(self, repo_name: str, file_path: str) -> bool:
        repo = self.repos.get(repo_name, {})
        for pattern in repo.get("high_risk_paths", []):
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False
