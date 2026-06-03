# Harvest Checklist

Use this checklist to collect raw operational evidence.

## Structure
- Root docs: README, PDR, indexes, scope matrix.
- Manifests: plugin manifests, package files, configs.
- Skills: skill names, frontmatter, placeholder status, references.
- Agents: role files and authority boundaries.
- Hooks/scripts: presence, executable bit, safety of commands.
- Policies: plugin/family policy files.

## Changes
- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- Untracked files
- Recently modified files

## Quality signals
- Tests and validators available
- Validators run and result
- Packaging/zip integrity
- Broken links or missing referenced files
- TODO/FIXME/HACK/XXX markers

## Safety signals
- Secrets or token-like strings
- Destructive commands
- Production endpoints
- Broad permissions or ambiguous authority
