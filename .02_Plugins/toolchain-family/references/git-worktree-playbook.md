# Git Worktree Playbook

## Create isolated task worktree

```bash
git status --short
git worktree list
git fetch --all --prune
git worktree add ../<repo>-<task> -b <branch-name>
cd ../<repo>-<task>
```

## Use cases

- Parallel agents working on separate features.
- Isolated review or refactor pass.
- Experiment without disturbing the main working tree.
- Release hotfix while feature work continues elsewhere.

## Safety checks before cleanup

```bash
git status --short
git log --oneline -5
git diff --stat
```

Only remove after changes are merged, backed up, committed, or intentionally discarded.

```bash
git worktree remove ../<repo>-<task>
git branch -d <branch-name>
```

Use `git branch -D` only when the loss is intentional and confirmed.

## Multi-agent rule

One agent = one branch = one worktree = one bounded task. Do not let multiple agents mutate the same working tree unless one is strictly reviewing read-only output.
