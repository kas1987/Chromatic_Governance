# Versioning Policy

Default to Semantic Versioning when no project-specific policy is found.

## Semver defaults

- `MAJOR`: breaking change, removed API, incompatible schema/data migration, changed plugin contract.
- `MINOR`: backward-compatible feature, new skill, new non-breaking capability.
- `PATCH`: bug fix, docs correction, internal cleanup, non-breaking template improvement.

## Conflict handling

If version sources disagree, stop and report the conflict before editing.

Common version sources:

- package metadata
- plugin manifest
- changelog
- git tag
- release notes
- application config

## Recommendation confidence

- `high`: current version and change impact are both clear.
- `medium`: version is clear but impact has unresolved assumptions.
- `low`: version source or impact evidence is incomplete.
