"""
chromatic_skills_server.py

MCP server for on-demand skill serving from the Chromatic plugin ecosystem.
Exposes three tools:
  list_skills(family?)   — discover available skills
  get_skill(skill_name)  — load a skill's full SKILL.md content
  search_skills(query)   — find skills by task description

Run:
  python chromatic_skills_server.py          # stdio transport (default)
  python chromatic_skills_server.py --sse    # SSE transport
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from mcp.server.fastmcp import FastMCP

# Root of the .02_Plugins directory — one level up from this file
PLUGINS_ROOT = Path(__file__).resolve().parent.parent

# Invocation log — written on every get_skill call; gitignored
_INVOCATION_LOG = Path(__file__).resolve().parents[2] / ".agents" / "logs" / "skill-invocation.jsonl"

mcp = FastMCP(
    "chromatic-skills",
    instructions=(
        "Use list_skills to discover available skills. "
        "Use get_skill(name) to load a skill's full instructions. "
        "Use search_skills(query) to find the best skill for a task description. "
        "Load only the skill you need — do not load all skills at once."
    ),
)


# ---------------------------------------------------------------------------
# Skill index
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from body. Returns ({}, full_text) when absent."""
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("---", 3)
    except ValueError:
        return {}, text
    front = yaml.safe_load(text[3:end]) or {}
    body = text[end + 3:].lstrip()
    return front, body


def _build_index(root: Path | None = None) -> list[dict[str, Any]]:
    """Walk plugin families and index every SKILL.md."""
    root = root or PLUGINS_ROOT
    skills: list[dict[str, Any]] = []
    for skill_md in sorted(root.glob("*/skills/*/SKILL.md")):
        family = skill_md.parts[-4]
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        front, _ = _parse_frontmatter(text)
        name = front.get("name") or skill_md.parent.name
        description = front.get("description", "")
        skills.append(
            {
                "name": name,
                "family": family,
                "description": description,
                "path": str(skill_md),
            }
        )
    return skills


# Module-level index — populated on first tool call
_SKILL_INDEX: list[dict[str, Any]] = []


def _index() -> list[dict[str, Any]]:
    global _SKILL_INDEX
    if not _SKILL_INDEX:
        _SKILL_INDEX = _build_index()
    return _SKILL_INDEX


def _reset_index() -> None:
    """Clear the cached index (used in tests)."""
    global _SKILL_INDEX
    _SKILL_INDEX = []


def _log_invocation(skill: str, family: str, outcome: str) -> None:
    """Append a JSONL entry to .agents/logs/skill-invocation.jsonl. Fails silently."""
    try:
        _INVOCATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
            "model": os.environ.get("CLAUDE_MODEL", "unknown"),
            "skill": skill,
            "family": family,
            "outcome": outcome,
        }
        with _INVOCATION_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_skills(family: str = "") -> list[dict[str, str]]:
    """
    List available skills, optionally filtered by family name.

    Args:
        family: Optional family name filter (e.g. "context-family", "rpi").
                Returns all skills when omitted.

    Returns:
        List of {name, family, description} records.
    """
    entries = _index()
    if family:
        family_lower = family.lower()
        entries = [
            e for e in entries
            if family_lower in e["family"].lower() or e["family"].lower() == family_lower
        ]
    return [
        {"name": e["name"], "family": e["family"], "description": e["description"]}
        for e in entries
    ]


@mcp.tool()
def get_skill(skill_name: str) -> str:
    """
    Return the full SKILL.md content for a named skill.

    Args:
        skill_name: Skill name as it appears in list_skills (e.g. "context-monitor").

    Returns:
        Full SKILL.md markdown string, or an error message if not found.
    """
    needle = skill_name.lower().replace(" ", "-").replace("_", "-")
    for entry in _index():
        name_match = entry["name"].lower().replace("_", "-") == needle
        dir_match = Path(entry["path"]).parent.name.lower() == needle
        if name_match or dir_match:
            try:
                content = Path(entry["path"]).read_text(encoding="utf-8")
                _log_invocation(entry["name"], entry["family"], "found")
                return content
            except OSError as exc:
                _log_invocation(entry["name"], entry["family"], "read_error")
                return f"Error reading skill '{skill_name}': {exc}"
    _log_invocation(skill_name, "unknown", "not_found")
    return (
        f"Skill '{skill_name}' not found. "
        f"Call list_skills() to see available skills."
    )


@mcp.tool()
def search_skills(query: str) -> list[dict[str, str]]:
    """
    Search skills by task description. Returns the top 3 matching skills.

    Matching is keyword-based against skill name, description, and family.
    Useful for finding the right skill when you know the task but not the skill name.

    Args:
        query: Natural-language task description (e.g. "track token usage by model").

    Returns:
        List of up to 3 {name, family, description, relevance_score} records,
        ordered highest-relevance first.
    """
    tokens = set(
        t for t in re.split(r"[\s\-_/,.()?!]+", query.lower()) if len(t) > 2
    )
    if not tokens:
        return []

    scored: list[tuple[int, dict[str, Any]]] = []
    for entry in _index():
        haystack = f"{entry['name']} {entry['description']} {entry['family']}".lower()
        score = sum(1 for t in tokens if t in haystack)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: -x[0])
    return [
        {
            "name": e["name"],
            "family": e["family"],
            "description": e["description"],
            "relevance_score": str(score),
        }
        for score, e in scored[:3]
    ]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
