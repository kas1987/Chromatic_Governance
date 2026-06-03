---
name: release-notes
description: Draft user-facing release notes from a changelog, commit summary, PR list, product brief, or completed release plan. Use when preparing concise release communication, upgrade notes, stakeholder announcements, or marketplace/plugin publication notes.
---

# Release Notes

Write release notes that explain value, impact, upgrade steps, and known limitations for the intended audience.

## Core procedure

1. Identify the audience: end users, developers, operators, customers, internal stakeholders, or marketplace reviewers.
2. Translate technical changes into user impact.
3. Separate highlights, fixes, breaking changes, migration steps, and known issues.
4. Include install/upgrade instructions only when evidence is available.
5. Link release notes back to changelog or release plan when working inside a repo.
6. Keep tone direct, specific, and non-hype.

## Output structure

Use `references/release-notes-template.md` for formal notes. Otherwise provide:

```markdown
# Release Notes - version

## Highlights
- ...

## Improvements
- ...

## Fixes
- ...

## Breaking changes / migration notes
- ...

## Known issues
- ...
```

## Guardrails

- Do not overpromise performance, compatibility, or stability.
- Do not expose confidential implementation details.
- Clearly label known issues and workarounds.
- Use plain language for user-facing notes and technical precision for developer notes.

## Related references

- `references/release-notes-template.md`
- `references/changelog-format.md`
