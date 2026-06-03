---
name: version-bump
description: Determine and apply version bump recommendations using semantic versioning, conventional commits, package metadata, changelogs, or release scope. Use when deciding major/minor/patch versions, updating version files, aligning plugin/package versions, or explaining version impact before a release.
---

# Version Bump

Recommend and, when explicitly asked, prepare version updates based on release impact.

## Core procedure

1. Find the current version from package metadata, plugin manifests, tags, changelog, or user input.
2. Classify changes:
   - `major`: breaking API, data, contract, behavior, or migration requirement.
   - `minor`: backward-compatible feature or capability addition.
   - `patch`: backward-compatible fix, docs-only correction, or internal repair.
3. Check whether the project uses semver, calendar versioning, custom versioning, or no visible policy.
4. Recommend the next version and list supporting evidence.
5. If asked to edit files, update all authoritative version locations consistently.
6. Add a verification checklist for version consistency.

## Output structure

```markdown
## Version bump recommendation

**Current:** ...
**Recommended:** ...
**Bump type:** major / minor / patch / custom
**Confidence:** high / medium / low

### Evidence
- ...

### Files to update
- ...

### Verification
- ...
```

## Guardrails

- Do not bump versions silently. State the reasoning.
- Do not treat docs-only changes as a release bump unless project policy requires it.
- If multiple version files disagree, stop and call out the conflict.
- Breaking changes override feature/fix categories.

## Related references

- `references/versioning-policy.md`
- `references/release-gate-model.md`
