# ADR-002: PR-Only Agent Writes

## Status

Accepted

## Context

Agents can make useful changes quickly, but direct writes to protected branches create quality, security, and governance risk.

## Decision

Agents may create branches and pull requests. They may not push directly to `main` or protected release branches.

## Consequences

- Human review remains available.
- CI gates can run before merge.
- Bad changes are easy to close/revert.
- Agent productivity remains high without sacrificing control.
