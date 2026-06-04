---
name: repo-tree-architect
description: Audit and redesign a repository's folder structure, root hygiene, scattered files, and naming conventions. Use when the repo root is cluttered, directories have grown organically without governance, files are misplaced across boundaries, or you need a clean canonical tree before onboarding agents or contributors.
skill_api_version: 1
---

# Repo Tree Architect

Produce a governed, navigable repo layout that reflects the project's actual structure — not its history.

## Core procedure

1. **Map the current tree.** Run a shallow directory listing (depth ≤ 3) and identify every top-level and second-level directory and significant root file.

2. **Classify each node** into one of four categories:
   - `keep` — correct location, correct name, actively used
   - `move` — correct content, wrong location or naming
   - `merge` — content overlaps with another directory; should be consolidated
   - `delete` — dead files, caches, duplicates, generated artefacts that belong in `.gitignore`

3. **Identify root hygiene issues:**
   - Loose files that belong inside a subdirectory
   - Directories with generic names (`misc/`, `old/`, `temp/`, `stuff/`)
   - Missing canonical directories for the project type (e.g., no `docs/`, no `tests/`, no `.github/`)
   - Naming inconsistency (mixed case, mixed delimiters, numeric prefixes without a standard)

4. **Draft the target tree.** Produce a proposed directory layout using a fenced `tree` block. Mark each node as `[new]`, `[moved from X]`, `[merged]`, or `[unchanged]`.

5. **Write a migration plan** as an ordered bash snippet — one operation per line, with a comment explaining the rationale. Prefer `git mv` to preserve history.

6. **Gate check.** Before finalising, confirm:
   - No files are deleted without the user's approval
   - Generated artefacts and build outputs are covered by `.gitignore`, not moved
   - The target tree does not break any known import paths, CI references, or README links

## Output format

```markdown
## Repo tree audit — <repo name>

### Current layout issues
| Path | Category | Issue |
|---|---|---|
| `path` | move/merge/delete | reason |

### Target tree
\`\`\`
root/
├── .github/            [unchanged]
├── src/                [moved from lib/]
│   └── ...
└── docs/               [new]
\`\`\`

### Migration steps
\`\`\`bash
git mv lib/ src/          # lib/ renamed to src/ per project convention
mkdir -p docs/            # create missing docs directory
\`\`\`

### Guardrail checklist
- [ ] No files deleted without explicit approval
- [ ] .gitignore covers all generated artefacts
- [ ] CI references (`workflow.yml`, `Makefile`) updated to reflect new paths
- [ ] README paths updated
```

## Guardrails

- Never delete files during the audit phase — classify only; execute only after user confirmation
- Do not move files that are referenced in CI scripts, Makefiles, or `package.json` scripts without also updating those references in the same migration plan
- If the repo uses numbered directory prefixes (e.g. `.01_`, `.02_`), preserve or extend that scheme — do not flatten it
- Limit scope to the repo root and immediate subdirectories unless the user requests a deep audit
- This skill produces a plan and migration script; use `rpi/implement` to execute the migration
