# Toolchain Family

Infrastructure and authoring utilities for agent workspaces, handoffs, audits, harvesting, Git worktrees, and skill/plugin operations.

## Purpose

This family is the operational layer for Claude Code and IDE agents. It keeps the workspace inspectable, handoff-ready, validated, and safe to delegate across agents.

## Implemented skills

- `handoff` - produce bounded transfer packages for humans or agents.
- `status` - report operational state, validation, blockers, and next move.
- `harvest` - collect raw evidence from repo/plugin/workspace state.
- `harvest-insights` - convert harvested evidence into prioritized findings.
- `system-audit` - audit structure, manifests, skills, refs, scripts, and readiness.
- `using-git-worktrees` - manage isolated branches/worktrees for parallel agent work.
- `writing-skills` - author and review reusable skill instructions.

## References

- `references/toolchain-operating-model.md`
- `references/handoff-template.md`
- `references/status-report-template.md`
- `references/harvest-checklist.md`
- `references/system-audit-checklist.md`
- `references/git-worktree-playbook.md`
- `references/skill-authoring-standards.md`

## Scripts

- `scripts/status-banner.sh` - existing lightweight status hook helper.
- `scripts/repo-status-summary.sh` - safe repo status snapshot.
- `scripts/plugin-structure-audit.sh` - plugin scaffold structure checker.

## Status

Core implementation complete. Skills are usable for operational workspace control and should be paired with context, security, QA/eval, architecture, and release families for governed agent workflows.
