#!/usr/bin/env python3

import json
import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List

def load_taxonomy():
    """Load SKILL_TAXONOMY.md and parse skill definitions."""
    taxonomy_path = Path(__file__).parent / "SKILL_TAXONOMY.md"
    if not taxonomy_path.exists():
        return {}

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
                        'trigger': None
                    }
                elif current_skill and line.startswith('**Family**:'):
                    skills[current_skill]['family'] = line.split(':', 1)[1].strip()
                elif current_skill and line.startswith('**Trigger**:'):
                    skills[current_skill]['trigger'] = line.split(':', 1)[1].strip()
                elif current_skill and line.startswith('**Description**:'):
                    skills[current_skill]['description'] = line.split(':', 1)[1].strip()
    except Exception as e:
        print(f"Error loading taxonomy: {e}", file=sys.stderr)

    return skills

def search_skills(query: str, skills: dict, limit: int = 3) -> List[dict]:
    """Search skills by keyword matching."""
    if not query:
        return []

    query_lower = query.lower()
    matches = []

    for skill_name, skill_data in skills.items():
        score = 0
        if query_lower in skill_name.lower():
            score += 10
        if query_lower in skill_data.get('description', '').lower():
            score += 5
        if query_lower in skill_data.get('trigger', '').lower():
            score += 3

        if score > 0:
            matches.append((skill_name, skill_data, score))

    matches.sort(key=lambda x: x[2], reverse=True)
    return [skill for _, skill, _ in matches[:limit]]

def list_family_skills(family: str, skills: dict) -> List[dict]:
    """List all skills in a family."""
    return [skill for skill in skills.values() if skill.get('family') == family]

def format_output(skills: List[dict], output_format: str = 'text') -> str:
    """Format skill results for output."""
    if output_format == 'json':
        return json.dumps(skills, indent=2)

    if not skills:
        return "No skills found."

    lines = []
    for i, skill in enumerate(skills, 1):
        lines.append(f"\n{i}. {skill.get('name', 'Unknown')}")
        if skill.get('description'):
            lines.append(f"   Description: {skill['description']}")
        if skill.get('family'):
            lines.append(f"   Family: {skill['family']}")
        if skill.get('trigger'):
            lines.append(f"   Trigger: {skill['trigger']}")

    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Search Chromatic skill ecosystem via CLI (for environments without MCP)"
    )
    parser.add_argument(
        'query',
        nargs='?',
        help="Skill search query (keyword or family name)"
    )
    parser.add_argument(
        '--family',
        help="List all skills in a specific family"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=3,
        help="Maximum results to return (default: 3)"
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help="Output format (default: text)"
    )
    parser.add_argument(
        '--profile',
        choices=['read_only', 'issue_triage', 'patch_standard', 'cleanup_limited'],
        help="Filter by broker profile access (optional)"
    )

    args = parser.parse_args()

    skills = load_taxonomy()
    if not skills:
        print("Error: SKILL_TAXONOMY.md not found or empty", file=sys.stderr)
        sys.exit(1)

    results = []
    if args.family:
        results = list_family_skills(args.family, skills)
    elif args.query:
        results = search_skills(args.query, skills, limit=args.limit)
    else:
        print("Error: provide a search query or --family argument", file=sys.stderr)
        sys.exit(1)

    if args.profile:
        profile_access = {
            'read_only': ['context-family', 'data-research-family', 'docs-family', 'observability-family'],
            'issue_triage': ['context-family', 'data-research-family', 'docs-family', 'observability-family',
                           'product-family', 'agent-governance-family'],
            'patch_standard': ['context-family', 'data-research-family', 'docs-family', 'observability-family',
                             'product-family', 'agent-governance-family', 'rpi', 'architecture-family',
                             'qa-eval-family', 'release-family', 'toolchain-family'],
            'cleanup_limited': ['rpi', 'docs-family', 'toolchain-family', 'context-family']
        }
        allowed_families = profile_access.get(args.profile, [])
        results = [s for s in results if s.get('family') in allowed_families]

    output = format_output(results, output_format=args.format)
    print(output)

    if not results:
        sys.exit(1)

if __name__ == '__main__':
    main()
