#!/usr/bin/env python3
"""
search_skills.py — CLI wrapper around the chromatic-skills MCP server index.

Usage:
  python search_skills.py <query>           # keyword search, prints top 3
  python search_skills.py --list [family]   # list all skills (optional family filter)
  python search_skills.py --get <name>      # print full SKILL.md for a named skill

The script imports chromatic_skills_server directly, so no MCP transport is needed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from any directory by adding the mcp package to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp"))

import chromatic_skills_server as srv


def cmd_search(query: str) -> int:
    results = srv.search_skills(query)
    if not results:
        print("No matching skills found.")
        return 1
    for r in results:
        print(f"[{r['relevance_score']}] {r['name']}  ({r['family']})")
        if r["description"]:
            print(f"    {r['description'][:120]}")
    return 0


def cmd_list(family: str) -> int:
    skills = srv.list_skills(family=family)
    if not skills:
        msg = f"No skills found for family '{family}'." if family else "No skills found."
        print(msg)
        return 1
    for s in skills:
        print(f"{s['name']}  ({s['family']})")
    print(f"\n{len(skills)} skill(s)")
    return 0


def cmd_get(name: str) -> int:
    content = srv.get_skill(name)
    print(content)
    return 0 if "not found" not in content.lower() else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search and retrieve Chromatic plugin skills from the CLI."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", nargs="?", const="", metavar="FAMILY",
                       help="List all skills, optionally filtered by family name")
    group.add_argument("--get", metavar="SKILL_NAME",
                       help="Print the full SKILL.md for the named skill")
    parser.add_argument("query", nargs="?", help="Search query (keyword search)")

    args = parser.parse_args()

    if args.list is not None:
        return cmd_list(args.list)
    if args.get:
        return cmd_get(args.get)
    if args.query:
        return cmd_search(args.query)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
