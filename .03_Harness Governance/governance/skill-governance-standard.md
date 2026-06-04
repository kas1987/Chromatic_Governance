# Skill Governance Standard

## Purpose
Prevent skill sprawl and maintain a reliable, composable Poly-Chromatic skill ecosystem.

## Principles

1. One skill, one primary job.
2. Every skill must have a clear trigger.
3. Every skill must produce a useful output contract.
4. Skills should compose through files, queues, PDRs, and handoffs rather than hidden context.
5. Do not create a new skill when adding a reference/template to an existing skill solves the problem.
6. Keep core `SKILL.md` files compact; move details to references.
7. Prefer deterministic scripts only when repeatable correctness matters.
8. Every execution-oriented skill must include stop conditions.
9. Every governance-oriented skill must include evidence standards.
10. Every cross-LLM skill must output portable Markdown or JSON-compatible structures.

## Required Skill Metadata

Every skill must have:

- Lowercase skill name.
- Clear description with trigger conditions.
- `SKILL.md` entrypoint.
- `agents/openai.yaml` metadata if packaged for ChatGPT UI.
- Optional references/templates/scripts only when materially useful.

## Skill Categories

| Category | Description | Examples |
|---|---|---|
| Operator | Turns goals into project state, queues, and controls. | `project-level-operator` |
| Router | Converts evidence into assigned work. | `repo-pdr-swarm-router` |
| Auditor | Reviews quality, governance, contradictions, or usage. | `chromatic-systems-auditor` |
| Packager | Converts work into reusable artifacts or target-specific formats. | `fusion-computer`, proposed `llm-ide-handoff-packager` |
| Governance | Manages settings, standards, controls, and policy. | proposed `github-org-governance-manager` |
| Registrar | Captures durable memory, decisions, and state. | proposed `chromatic-memory-registrar` |

## New Skill Approval Test

Before creating a new skill, answer:

1. Does an existing skill already cover 70% or more of the need?
2. Is the trigger distinct?
3. Is the output contract distinct?
4. Will this be reused at least three times?
5. Is this better as a reference/template inside an existing skill?
6. Does it need scripts or assets?
7. Can another LLM/IDE use the output?

If answers 1 or 5 are yes, prefer improving an existing skill.

## Versioning

Use semantic intent labels in changelogs:

- `major`: trigger or output contract changes.
- `minor`: new reference/template/script.
- `patch`: wording, bugfix, clarification.

## Review Cadence

- Review skill library monthly or after major repo/PDR milestones.
- Use `skill-agent-utilization-auditor` for utilization review.
- Use `chromatic-systems-auditor` for governance and contradiction review.
