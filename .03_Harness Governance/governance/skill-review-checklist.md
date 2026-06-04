# Skill Review Checklist

## Intake
- [ ] Skill has a clear purpose.
- [ ] Skill trigger is specific and not overly broad.
- [ ] Expected input is defined.
- [ ] Expected output is defined.
- [ ] Required connectors/tools are identified.
- [ ] User approval or clarification has been captured if needed.

## Scope
- [ ] Skill does one primary job.
- [ ] Overlap with existing skills has been checked.
- [ ] New skill is justified instead of improving an existing skill.
- [ ] Non-goals are clear.

## Structure
- [ ] `SKILL.md` exists.
- [ ] YAML frontmatter includes only `name` and `description`.
- [ ] Name is lowercase and hyphenated.
- [ ] Description includes trigger contexts.
- [ ] Supporting references are one level deep from `SKILL.md`.
- [ ] Example files from initialization are removed if unused.

## Output Contract
- [ ] Outputs are named and reusable.
- [ ] Execution tasks include acceptance criteria.
- [ ] Execution tasks include stop conditions.
- [ ] Governance tasks include evidence requirements.
- [ ] Cross-LLM outputs are portable Markdown or JSON-compatible structures.

## Safety and Governance
- [ ] Destructive actions are blocked unless explicitly authorized.
- [ ] External writes are gated.
- [ ] Secrets/tokens are not requested or stored in skill assets.
- [ ] File or repo mutation rules are clear.
- [ ] Audit trail expectations are defined.

## Packaging
- [ ] Scripts, if any, have been tested.
- [ ] Package size is below 25 MB.
- [ ] Skill validates successfully.
- [ ] Output archive is named `skill.zip`.
