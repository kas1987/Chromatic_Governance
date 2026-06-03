# Changelog Format

Use this category order unless an existing changelog uses another convention:

1. Breaking
2. Added
3. Changed
4. Fixed
5. Removed
6. Deprecated
7. Security
8. Docs
9. Internal

## Entry rules

- Start with a past-tense verb.
- Describe user/developer impact, not only implementation detail.
- Keep one change per bullet.
- Add migration notes under `Breaking` when required.
- Do not invent dates, issue IDs, PR IDs, or authors.

## Example

```markdown
## [1.4.0] - 2026-06-03

### Added
- Added release gate validation for plugin deployment workflows.

### Fixed
- Fixed stale context handling in generated handoff packs.
```
