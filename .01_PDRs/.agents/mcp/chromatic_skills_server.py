#!/usr/bin/env python3

import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import logging

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)

logger = logging.getLogger(__name__)

class SkillInvocationLogger:
    """Logs skill invocations to .agents/logs/skill-invocation.jsonl"""

    def __init__(self, log_path: Optional[Path] = None):
        if log_path is None:
            log_path = Path(__file__).parent.parent / "logs" / "skill-invocation.jsonl"
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_invocation(self, session_id: str, caller_context: dict, tool: str,
                      parameters: dict, skill_name: Optional[str], family_name: Optional[str],
                      status: str, skills_returned: int = 0, error_message: Optional[str] = None,
                      duration_ms: float = 0):
        """Write invocation entry to JSONL log."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "caller_context": caller_context,
            "invocation": {
                "tool": tool,
                "parameters": parameters,
                "skill_name": skill_name,
                "family_name": family_name
            },
            "result": {
                "status": status,
                "skills_returned": skills_returned if skills_returned > 0 else None,
                "error_message": error_message
            },
            "duration_ms": duration_ms
        }

        entry["result"] = {k: v for k, v in entry["result"].items() if v is not None}

        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write invocation log: {e}")


class ChromaticSkillsServer:
    """MCP skill server for on-demand skill loading"""

    def __init__(self, skills_data: dict, session_id: str = "unknown"):
        self.skills_data = skills_data
        self.session_id = session_id
        self.logger = SkillInvocationLogger()
        if HAS_MCP:
            self.server = Server("chromatic-skills-mcp")
            self._register_tools()

    def _get_caller_context(self) -> dict:
        """Extract caller context from environment or MCP request."""
        return {
            "agent_id": os.getenv("CHROMATIC_AGENT_ID", "unknown"),
            "broker_profile": os.getenv("CHROMATIC_BROKER_PROFILE", "read_only"),
            "model": os.getenv("CHROMATIC_MODEL", "unknown")
        }

    def _register_tools(self):
        """Register MCP tools."""
        @self.server.call_tool()
        def list_skills(family: Optional[str] = None) -> str:
            start = time.time()
            caller = self._get_caller_context()
            try:
                results = self._list_skills_impl(family)
                self.logger.log_invocation(
                    self.session_id, caller, "list_skills",
                    {"family": family}, None, family,
                    "success", skills_returned=len(results),
                    duration_ms=(time.time() - start) * 1000
                )
                return json.dumps(results)
            except Exception as e:
                self.logger.log_invocation(
                    self.session_id, caller, "list_skills",
                    {"family": family}, None, family,
                    "error", error_message=str(e),
                    duration_ms=(time.time() - start) * 1000
                )
                raise

        @self.server.call_tool()
        def get_skill(skill_name: str) -> str:
            start = time.time()
            caller = self._get_caller_context()
            try:
                result = self._get_skill_impl(skill_name)
                family = result.get("family") if result else None
                self.logger.log_invocation(
                    self.session_id, caller, "get_skill",
                    {"skill_name": skill_name}, skill_name, family,
                    "success" if result else "not_found",
                    duration_ms=(time.time() - start) * 1000
                )
                return json.dumps(result) if result else json.dumps({"error": "Skill not found"})
            except Exception as e:
                self.logger.log_invocation(
                    self.session_id, caller, "get_skill",
                    {"skill_name": skill_name}, skill_name, None,
                    "error", error_message=str(e),
                    duration_ms=(time.time() - start) * 1000
                )
                raise

        @self.server.call_tool()
        def search_skills(query: str) -> str:
            start = time.time()
            caller = self._get_caller_context()
            try:
                results = self._search_skills_impl(query)
                self.logger.log_invocation(
                    self.session_id, caller, "search_skills",
                    {"query": query}, None, None,
                    "success", skills_returned=len(results),
                    duration_ms=(time.time() - start) * 1000
                )
                return json.dumps(results)
            except Exception as e:
                self.logger.log_invocation(
                    self.session_id, caller, "search_skills",
                    {"query": query}, None, None,
                    "error", error_message=str(e),
                    duration_ms=(time.time() - start) * 1000
                )
                raise

    def _list_skills_impl(self, family: Optional[str] = None) -> List[dict]:
        """List skills, optionally filtered by family."""
        results = []
        for skill_name, skill_data in self.skills_data.items():
            if family is None or skill_data.get("family") == family:
                results.append({
                    "name": skill_name,
                    "description": skill_data.get("description", ""),
                    "family": skill_data.get("family", ""),
                    "version": skill_data.get("version", "1.0.0")
                })
        return results

    def _get_skill_impl(self, skill_name: str) -> Optional[dict]:
        """Get full skill data by name."""
        return self.skills_data.get(skill_name)

    def _search_skills_impl(self, query: str) -> List[dict]:
        """Search skills by keyword (top 3 matches)."""
        if not query:
            return []

        query_lower = query.lower()
        matches = []

        for skill_name, skill_data in self.skills_data.items():
            score = 0
            if query_lower in skill_name.lower():
                score += 10
            if query_lower in skill_data.get("description", "").lower():
                score += 5
            if query_lower in skill_data.get("trigger", "").lower():
                score += 3

            if score > 0:
                matches.append((skill_name, skill_data, score))

        matches.sort(key=lambda x: x[2], reverse=True)
        results = []
        for skill_name, skill_data, _ in matches[:3]:
            results.append({
                "name": skill_name,
                "description": skill_data.get("description", ""),
                "family": skill_data.get("family", ""),
                "version": skill_data.get("version", "1.0.0")
            })
        return results

    def run(self):
        """Start the MCP server."""
        if not HAS_MCP:
            raise RuntimeError("MCP SDK not available")
        self.server.run()

    def get_tools(self) -> List[Tool]:
        """Return list of available MCP tools."""
        return [
            Tool(
                name="list_skills",
                description="List all skills, optionally filtered by family",
                inputSchema={"type": "object", "properties": {
                    "family": {"type": "string", "description": "Optional family filter"}
                }}
            ),
            Tool(
                name="get_skill",
                description="Get full skill definition by name",
                inputSchema={"type": "object", "properties": {
                    "skill_name": {"type": "string", "description": "Name of the skill"}
                }, "required": ["skill_name"]}
            ),
            Tool(
                name="search_skills",
                description="Search for skills by keyword (returns top 3 matches)",
                inputSchema={"type": "object", "properties": {
                    "query": {"type": "string", "description": "Search query"}
                }, "required": ["query"]}
            )
        ]


def load_skills_from_taxonomy(taxonomy_path: Path) -> dict:
    """Load skill definitions from SKILL_TAXONOMY.md."""
    skills = {}
    try:
        with open(taxonomy_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            current_skill = None
            for line in lines:
                if line.startswith('### '):
                    current_skill = line.replace('### ', '').strip()
                    skills[current_skill] = {
                        'name': current_skill,
                        'description': '',
                        'family': None,
                        'trigger': None,
                        'version': '1.0.0'
                    }
                elif current_skill and line.startswith('**Family**:'):
                    skills[current_skill]['family'] = line.split(':', 1)[1].strip()
                elif current_skill and line.startswith('**Trigger**:'):
                    skills[current_skill]['trigger'] = line.split(':', 1)[1].strip()
                elif current_skill and line.startswith('**Description**:'):
                    skills[current_skill]['description'] = line.split(':', 1)[1].strip()
                elif current_skill and line.startswith('**Version**:'):
                    skills[current_skill]['version'] = line.split(':', 1)[1].strip()
    except Exception as e:
        logger.error(f"Error loading taxonomy: {e}")

    return skills


if __name__ == "__main__":
    taxonomy_path = Path(__file__).parent.parent.parent / "SKILL_TAXONOMY.md"
    skills = load_skills_from_taxonomy(taxonomy_path)

    session_id = os.getenv("CHROMATIC_SESSION_ID", f"session_{int(time.time())}")
    server = ChromaticSkillsServer(skills, session_id=session_id)

    if HAS_MCP:
        server.run()
    else:
        print("MCP SDK required to run server. Install with: pip install mcp")
        sys.exit(1)
