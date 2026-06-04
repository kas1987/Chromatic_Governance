#!/usr/bin/env python3
"""Parse a Repo PDR package into Chromatic Harness intake artifacts.

This script performs deterministic file inventory and lightweight extraction for
large markdown/text/json/yaml/code packages. It intentionally does not replace
human/LLM review; it creates structured seed artifacts for governed routing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

TEXT_EXTS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".ts",
    ".tsx", ".jsx", ".sh", ".ps1", ".ini", ".cfg", ".csv", ".sql"
}

ROLE_KEYWORDS = {
    "sentinel": ["test", "ci", "security", "bug", "failure", "lint", "coverage"],
    "auditor": ["governance", "audit", "evidence", "risk", "compliance", "acceptance"],
    "chainbreaker": ["blocked", "blocker", "dependency", "ambiguous", "unknown", "todo"],
    "quartermaster": ["inventory", "manifest", "asset", "package", "dependency"],
    "cartographer": ["tree", "folder", "path", "repo", "worktree", "structure"],
    "financier": ["cost", "budget", "token", "cloud", "spend", "efficient"],
    "archivist": ["memory", "changelog", "decision", "log", "version"],
    "janitor": ["cleanup", "duplicate", "stale", "root hygiene", "rename"],
}

CLASS_KEYWORDS = {
    "source-of-truth": ["source of truth", "governance", "router", "chromatic_trees", "standard"],
    "requirement": ["requirement", "must", "shall", "acceptance criteria"],
    "design-record": ["pdr", "adr", "design", "architecture", "decision"],
    "implementation-target": ["script", "function", "class", "config", "workflow", "ci"],
    "queue-source": ["todo", "backlog", "queue", "roadmap", "task"],
    "evidence": ["evidence", "test output", "log", "result", "screenshot"],
    "memory": ["memory", "learning", "learnings", "changelog"],
    "bridge": ["claude", "cursor", "codex", "agent", "agents"],
}

ACTION_PATTERNS = [
    re.compile(r"\b(?:todo|fixme|next|action|required|must|should)\b[:\-]?\s*(.+)", re.I),
    re.compile(r"^- \[ \] (.+)", re.I),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path, limit: int = 200000) -> str:
    try:
        data = path.read_bytes()[:limit]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def classify(path: Path, text: str) -> str:
    hay = f"{path.as_posix()}\n{text[:5000]}".lower()
    scores = {cls: sum(1 for kw in kws if kw in hay) for cls, kws in CLASS_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else ("implementation-target" if path.suffix in TEXT_EXTS else "asset")


def route(path: Path, text: str) -> str:
    hay = f"{path.as_posix()}\n{text[:5000]}".lower()
    scores = {role: sum(1 for kw in kws if kw in hay) for role, kws in ROLE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "auditor"


def extract_headings(text: str) -> List[str]:
    headings = []
    for line in text.splitlines()[:1000]:
        m = HEADING_RE.match(line.strip())
        if m:
            headings.append(m.group(2).strip())
    return headings[:25]


def extract_actions(text: str) -> List[str]:
    actions = []
    for line in text.splitlines()[:2000]:
        stripped = line.strip()
        for pat in ACTION_PATTERNS:
            m = pat.search(stripped)
            if m:
                item = m.group(1).strip()
                if 8 <= len(item) <= 240:
                    actions.append(item)
                break
    return actions[:30]


def priority_for(agent: str, artifact_class: str, action: str) -> str:
    low = action.lower()
    if any(k in low for k in ["security", "secret", "token", "governance", "router", "blocked"]):
        return "P0"
    if artifact_class in {"source-of-truth", "requirement"}:
        return "P1"
    if agent in {"sentinel", "auditor", "cartographer"}:
        return "P2"
    return "P3"


def iter_files(root: Path) -> Iterable[Path]:
    ignored = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignored]
        for filename in filenames:
            yield Path(dirpath) / filename


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Repo PDR package into governed queue artifacts.")
    parser.add_argument("--input", required=True, help="Path to extracted package or repo directory")
    parser.add_argument("--output", required=True, help="Directory for generated intake artifacts")
    args = parser.parse_args()

    root = Path(args.input).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)

    manifest: List[Dict[str, Any]] = []
    queue: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []

    for idx, path in enumerate(iter_files(root), start=1):
        rel = path.relative_to(root).as_posix()
        ext = path.suffix.lower()
        text = read_text(path) if ext in TEXT_EXTS else ""
        artifact_class = classify(path, text)
        agent = route(path, text)
        headings = extract_headings(text)
        actions = extract_actions(text)
        digest = sha256_file(path)

        item = {
            "path": rel,
            "size_bytes": path.stat().st_size,
            "sha256": digest,
            "extension": ext,
            "artifact_class": artifact_class,
            "suggested_agent": agent,
            "headings": headings,
            "action_count": len(actions),
        }
        manifest.append(item)
        evidence.append({
            "evidence_id": f"E{idx:04d}",
            "source_path": rel,
            "artifact_class": artifact_class,
            "supports": "package inventory and routing",
            "confidence": "medium" if text else "low",
            "notes": "text inspected" if text else "non-text or unreadable asset",
        })

        for action_idx, action in enumerate(actions, start=1):
            task_id = f"T{len(queue)+1:04d}"
            queue.append({
                "task_id": task_id,
                "priority": priority_for(agent, artifact_class, action),
                "agent_role": agent,
                "mission": action,
                "status": "review-required",
                "source_files": [rel],
                "dependencies": [],
                "evidence_required": [f"E{idx:04d}"],
                "allowed_actions": ["inspect", "summarize", "propose patch", "create handoff"],
                "blocked_actions": ["use secrets", "merge without review", "ignore router"],
                "acceptance_criteria": "human or auditor confirms task is grounded in source evidence",
                "stop_condition": "stop after producing a concrete patch plan or blocked reason",
                "handoff_target": "auditor",
            })

        risk_terms = ["secret", "token", "password", "conflict", "contradiction", "deprecated", "unsafe"]
        for term in risk_terms:
            if term in text.lower():
                risks.append({
                    "risk_id": f"R{len(risks)+1:04d}",
                    "severity": "high" if term in {"secret", "token", "password", "unsafe"} else "medium",
                    "category": "security" if term in {"secret", "token", "password"} else "governance",
                    "description": f"Potential {term} issue detected in {rel}",
                    "evidence": [f"E{idx:04d}"],
                    "owner": "sentinel" if term in {"secret", "token", "password", "unsafe"} else "auditor",
                    "mitigation": "inspect source and decide whether to redact, block, or route to human decision",
                    "status": "review-required",
                })

    summary = {
        "input_root": str(root),
        "file_count": len(manifest),
        "task_count": len(queue),
        "risk_count": len(risks),
        "source_of_truth_count": sum(1 for x in manifest if x["artifact_class"] == "source-of-truth"),
        "chromatic_trees_present": any(Path(x["path"]).name.lower() == "chromatic_trees.md" for x in manifest),
    }

    outputs = {
        "pdr_manifest.json": manifest,
        "work_queue.seed.json": queue,
        "evidence_map.json": evidence,
        "risk_register.json": risks,
        "intake_summary.json": summary,
    }
    for name, data in outputs.items():
        (out / name).write_text(json.dumps(data, indent=2), encoding="utf-8")

    md_lines = ["# Agent Dispatch Board", "", "| task_id | priority | agent_role | status | mission | source_files |", "|---|---:|---|---|---|---|"]
    for task in queue:
        mission = task["mission"].replace("|", "-")[:120]
        md_lines.append(f"| {task['task_id']} | {task['priority']} | {task['agent_role']} | {task['status']} | {mission} | {', '.join(task['source_files'])} |")
    (out / "dispatch_board.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
