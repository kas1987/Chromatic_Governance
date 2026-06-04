# Skill Versioning Standard

Defines version field and semantics for all 118 plugin skills. Each SKILL.md frontmatter now includes a `version` field using semantic versioning.

---

## Version Field Format

Add to SKILL.md frontmatter (top of file, within `---` markers):

```yaml
---
name: context-monitor
family: context-family
version: 1.0.0
trigger: When an agent loads more than 2 families
description: Monitor session context usage (tokens, families, estimated cost)
---
```

---

## Semantic Versioning Rules

| Part | Increment When | Example |
|---|---|---|
| **MAJOR** | Signature change, required parameters added/removed, output format changed | `1.0.0` → `2.0.0` |
| **MINOR** | New optional features, backward-compatible enhancements | `1.0.0` → `1.1.0` |
| **PATCH** | Bug fixes, documentation improvements, internal refactoring | `1.0.0` → `1.0.1` |

---

## Initial Versions (Backfill)

All existing 118 skills are backfilled with version `1.0.0` (initial release). Future changes follow semantic versioning.

---

## Version Lifecycle

1. **Skill Created**: Version = `1.0.0`
2. **Minor Update**: Increment `1.0.0` → `1.1.0`, update SKILL.md
3. **Major Change**: Increment `1.0.0` → `2.0.0`, update SKILL.md
4. **Deprecation**: Add deprecation notice in SKILL.md (do not remove), bump to `1.99.0`
5. **Retirement**: Move to `.deprecated/` folder, retain in SKILL_TAXONOMY.md with note

---

## Changelog Requirement

Every version bump ≥ `1.1.0` includes a `## Changelog` section in SKILL.md:

```markdown
## Changelog

### v1.1.0 (2026-06-10)
- Added optional parameter `--format json` for structured output
- Improved error messages for token budget overflow

### v1.0.0 (2026-01-15)
- Initial release
```

---

## Version in Invocation Logs

Skill invocation logs include `skill_version`:

```json
{
  "timestamp": "2026-06-04T23:30:45Z",
  "skill_name": "context-monitor",
  "skill_version": "1.0.0",
  "invocation": { ... },
  "result": { ... }
}
```

Enables analytics: "track changes in skill usage after v1.1.0 rollout"

---

## Governance Integration

- CI check: Version field is required in all SKILL.md files (skill-governance.yml validates)
- Invocation logging: skill_version is logged alongside skill_name and family
- SKILL_TAXONOMY.md: List skills with version info for agent discovery
- Deprecation tracking: `.deprecated/` folder marks retired skills

---

## Related Documents

- `SKILL_TAXONOMY.md` — Skill definitions with version info
- `skill-governance.yml` — CI validation of version field format
- `skill-invocation-logging.json` — Invocation log schema includes version
