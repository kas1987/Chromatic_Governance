"""
validate_skills.py

Validates every SKILL.md in the .02_Plugins directory against the
Chromatic skill governance standard. Exits non-zero on any failure.

Checks:
  1. YAML frontmatter present with 'name' and 'description' fields
  2. Required section headers present (## Core procedure, ## Output format, ## Guardrails)
  3. No two skills share the same 'name' value
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(2)

PLUGINS_ROOT = Path(__file__).resolve().parents[2] / ".02_Plugins"

# Each entry is (regex_pattern, canonical_display_name).
# Patterns accept both the canonical section name and common legacy equivalents
# used in skills that pre-date this governance standard.
REQUIRED_SECTIONS: list[tuple[str, str]] = [
    (
        r"^##\s+(Core\s+procedure|Execution\s+Steps?|Procedure|The\s+Process"
        r"|Execution\b|Step\b|Mode\b|Phase\b|DAG\b)",
        "## Core procedure",
    ),
    (
        r"^##\s+(Output(\s+\w+)?|Expected\s+outputs?|Examples?|Handoff\s+format)",
        "## Output format",
    ),
    (
        r"^##\s+(Guardrails?|Key\s+Rules?|Tool\s+Governance|Red\s+Flags?"
        r"|Safety(\s+Rules?)?|Operating\s+rules?)",
        "## Guardrails",
    ),
]


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("---", 3)
    except ValueError:
        return {}
    return yaml.safe_load(text[3:end]) or {}


def validate() -> int:
    failures: list[str] = []
    seen_names: dict[str, str] = {}  # name -> first path

    skill_files = sorted(PLUGINS_ROOT.glob("*/skills/*/SKILL.md"))
    if not skill_files:
        print(f"ERROR: no SKILL.md files found under {PLUGINS_ROOT}")
        return 1

    for skill_md in skill_files:
        rel = skill_md.relative_to(PLUGINS_ROOT.parent)
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError as exc:
            failures.append(f"{rel}: cannot read file: {exc}")
            continue

        # 1. Frontmatter
        front = _parse_frontmatter(text)
        if not front:
            failures.append(f"{rel}: missing YAML frontmatter (must start with ---)")
            continue

        name = front.get("name", "").strip()
        if not name:
            failures.append(f"{rel}: frontmatter missing 'name' field")

        if not front.get("description", "").strip():
            failures.append(f"{rel}: frontmatter missing 'description' field")

        # 2. Duplicate name check
        if name:
            if name in seen_names:
                failures.append(
                    f"{rel}: duplicate skill name '{name}' "
                    f"(first seen in {seen_names[name]})"
                )
            else:
                seen_names[name] = str(rel)

        # 3. Required section headers
        for pattern, canonical_name in REQUIRED_SECTIONS:
            if not re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                failures.append(f"{rel}: missing required section '{canonical_name}'")

    if failures:
        print(f"Skill governance validation FAILED — {len(failures)} issue(s):\n")
        for f in failures:
            print(f"  FAIL  {f}")
        return 1

    print(
        f"Skill governance validation PASSED — "
        f"{len(skill_files)} skills checked, {len(seen_names)} unique names."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
