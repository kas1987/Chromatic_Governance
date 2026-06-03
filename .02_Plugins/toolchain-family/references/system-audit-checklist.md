# System Audit Checklist

## Required structure
- `.claude-plugin/plugin.json` exists and is valid JSON.
- `README.md` exists and describes the plugin/family.
- `skills/` contains expected skills.
- Each skill has `SKILL.md` with YAML frontmatter.
- `agents/`, `hooks/`, `policies/`, `references/`, and `scripts/` are present when the family uses them.

## Skill quality
- Description states what the skill does and when to use it.
- Body includes core procedure, output contract, guardrails, and references.
- Placeholder/TODO language is removed before production use.
- Referenced files exist.

## Operational readiness
- Validation script exists and runs.
- Packaging or zip integrity is checked.
- README and PDR reflect current implementation state.
- Risky commands are advisory, not automatic.

## Severity model
- Critical: missing required manifest, invalid JSON, unsafe destructive default, broken package.
- Major: missing core skill, stale placeholder in active family, unrun validation for release candidate.
- Minor: docs mismatch, weak description, missing optional reference.
- Advisory: style improvement, naming polish, future enhancement.
