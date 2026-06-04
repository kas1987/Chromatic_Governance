# ChromaticTrees Reference

ChromaticTrees is the governing repo-tree system.

## Hierarchy
1. CHROMATIC_TREES.md is the source of truth for repo tree rules.
2. Worktree map JSON is the machine-readable structure.
3. Memory and learning logs record evolving repo wisdom.
4. Claude, Cursor, Codex, Agents, and README bridge files defer to ChromaticTrees.
5. Validator and CI prevent tree drift from returning.

## Required Repo Tree Tasks
When a Repo PDR package touches repository organization, create these tasks if missing:
- create or update CHROMATIC_TREES.md
- create or update worktree map JSON
- identify scattered files and root hygiene issues
- align bridge files to defer to ChromaticTrees
- add validator or CI checks to prevent drift

## Bridge Rule
Bridge files may summarize how to work in the repo, but they must not become competing sources of truth for folder standards.
