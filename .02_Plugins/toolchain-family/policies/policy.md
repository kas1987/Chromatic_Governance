# Toolchain Family Policy

The toolchain family may inspect workspace structure, summarize status, prepare handoffs, assist with worktree planning, and audit plugin scaffolds.

## Allowed by default

- Read files and manifests relevant to the requested scope.
- Run non-destructive status and validation commands.
- Create reports, handoffs, checklists, and skill instruction drafts.
- Recommend worktree and branch plans.

## Requires explicit approval

- Deleting files, branches, or worktrees.
- Publishing, deploying, or pushing to remote repositories.
- Modifying production configuration.
- Running commands that may expose secrets or send data externally.

## Escalate

Escalate to security-family for secrets, credentials, permissions, prompt injection, dependency risk, or production access.
Escalate to release-family for deploy/release approval.
Escalate to architecture-family for boundary/API/migration decisions.
