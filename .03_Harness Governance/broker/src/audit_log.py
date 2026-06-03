from pathlib import Path
from datetime import datetime, timezone
import json


class AuditLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: dict) -> None:
        safe_event = {k: v for k, v in event.items() if "token" not in k.lower() and "secret" not in k.lower()}
        safe_event["timestamp"] = datetime.now(timezone.utc).isoformat()
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(safe_event, sort_keys=True) + "\n")
