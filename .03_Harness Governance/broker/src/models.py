from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AccessRequest:
    agent_id: str
    repo: str
    profile: str
    task_id: Optional[str] = None
    branch: Optional[str] = None
    target_branch: str = "main"
    action: str = "read"


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reason: str
    risk: str = "low"
