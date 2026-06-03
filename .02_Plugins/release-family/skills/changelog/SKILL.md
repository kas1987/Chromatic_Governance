---
name: changelog
description: Generate or update developer-facing changelogs from commits, PRs, issue lists, release notes, or manually provided change summaries. Use when the user asks to summarize changes, maintain CHANGELOG.md, categorize fixes/features/breaking changes, or prepare release history for a plugin, package, app, or repo.
---

# Changelog

Create a structured changelog that records what changed in terms useful to developers and maintainers.

## Core procedure

1. Identify the comparison range: commits, PRs, version diff, branch diff, or provided notes.
2. Group changes under stable categories: `Added`, `Changed`, `Fixed`, `Removed`, `Deprecated`, `Security`, `Docs`, `Internal`, `Breaking`.
3. Prefer user-visible behavior and compatibility impact over implementation trivia.
4. Mark breaking changes explicitly and include migration notes when known.
5. Preserve existing changelog style when editing an existing file.
6. If evidence is incomplete, produce a draft and state the missing source.

## Output structure

```markdown
## [version] - YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Breaking
- ...
```

## Guardrails

- Do not invent issue numbers, PR numbers, authors, or dates.
- Do not include sensitive security details that could enable exploitation before disclosure.
- Do not claim semantic version impact unless versioning policy is known or inferred from conventional commits.
- Keep changelog entries concise and action-oriented.

## Related references

- `references/changelog-format.md`
- `references/versioning-policy.md`
