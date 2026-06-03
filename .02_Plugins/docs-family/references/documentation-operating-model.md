# Documentation Operating Model

## Purpose

Docs-family turns implementation, operations, and product knowledge into durable guidance. It is not a dumping ground for every detail. Its job is to help the next user, developer, operator, or agent make the correct next move quickly.

## Source-of-truth order

1. Current code, tests, schemas, manifests, configs, and scripts
2. Recent release notes, migration notes, ADRs, and approved design docs
3. Current runbooks and operational dashboards
4. README, guides, and tutorials
5. Old notes, chat summaries, stale issues, and comments

When sources conflict, cite the conflict and recommend an owner review instead of guessing.

## Documentation classes

- README: orientation, quick start, links, project status
- API docs: interface reference, examples, errors, auth, versions
- Runbook: operational steps, prechecks, verification, rollback, escalation
- Developer guide: setup, workflows, repo map, contribution path
- Troubleshooting: symptom-to-fix diagnosis paths
- Diagram plan: visual explanation specs and source
- Audit: drift, contradictions, stale docs, broken links
- Sync: targeted updates after changes

## Quality bar

Good docs are accurate, scoped, task-oriented, current enough, and explicit about uncertainty. Bad docs sound polished but hide assumptions, omit prerequisites, or promise unsupported behavior.
