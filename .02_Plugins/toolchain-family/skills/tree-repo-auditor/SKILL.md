---
name: tree-repo-auditor
description: Enforce numbered folder and subfolder naming standards across a repository. Audit whether directories follow an established numeric prefix convention (e.g. .01_, .02_, 01-, 1.) and produce a compliance report with remediation steps. Use when repo directories have grown without consistent naming, when onboarding contributors, or before a structural refactor.
skill_api_version: 1
---

# Tree Repo Auditor

Make directory naming deterministic and auditable so agents, contributors, and CI systems can navigate by convention rather than memory.

## Core procedure

1. **Detect the naming convention in use.** Scan the top two levels of the directory tree for numeric prefix patterns. Identify the dominant scheme:
   - Dot-prefixed integers: `.01_Name`, `.02_Name`
   - Dash-delimited integers: `01-name`, `02-name`
   - Plain integers: `01_name`, `1-name`
   - Mixed or absent (no convention detected)

2. **Audit compliance.** For every directory at the governed depth (default: top-level + one level deep), evaluate:
   - `compliant` — matches the detected or specified convention
   - `non-compliant` — has content but no numeric prefix
   - `gap` — numeric sequence has a missing number (e.g. 01, 02, 04 — 03 is missing)
   - `duplicate` — two directories share the same numeric prefix
   - `inconsistent` — prefix present but uses a different delimiter or casing than the convention

3. **Produce a compliance report** listing every finding with the affected path, violation type, and recommended corrected name.

4. **Draft rename operations.** For each non-compliant or inconsistent directory, produce a `git mv` command that moves it to the correct name. Assign the next available number for unordered directories.

5. **Sequence the renames.** Order operations to avoid conflicts (e.g. rename gaps before inserting into them). Note any operations that require downstream reference updates.

6. **Gate check.** Flag any rename that would break known file references (CI scripts, markdown links, Python imports) and include the corresponding fix in the migration plan.

## Output format

```markdown
## Tree naming audit — <repo name>

**Convention detected:** `.NN_Name` (dot-prefixed two-digit integer + underscore + PascalCase)

### Compliance summary
| Directory | Status | Issue | Recommended name |
|---|---|---|---|
| `03_Reports` | compliant | — | — |
| `misc` | non-compliant | No numeric prefix | `07_Misc` |
| `04_Config` | duplicate | Same prefix as `04_Assets` | `08_Config` |

### Rename operations
\`\`\`bash
git mv misc/ .07_Misc/          # assign next available prefix
git mv 04_Config/ .08_Config/   # resolve duplicate prefix
\`\`\`

### Reference updates required
- `.github/workflows/ci.yml` line 14: `04_Config/` → `.08_Config/`
```

## Guardrails

- Do not execute renames — produce a plan only; use `rpi/implement` to apply
- When no convention is detected, present two or three candidate conventions (with pros/cons) and ask the user to choose before proceeding
- If renaming would break CI, imports, or documented paths, the migration plan MUST include the corresponding fixes — do not produce a partial plan
- Limit the default audit depth to two levels; deeper audits require explicit user instruction
- Numbered hidden directories (`.01_`, `.02_`) follow the same rules as visible ones — do not skip them
