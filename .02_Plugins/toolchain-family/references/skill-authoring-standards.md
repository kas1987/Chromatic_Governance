# Skill Authoring Standards

## Frontmatter

Use only:

```yaml
---
name: lower-kebab-name
description: A compact trigger description that explains what the skill does and when to use it.
---
```

## Body sections

Recommended sections:

1. Title
2. One-sentence purpose
3. Core procedure
4. Output contract
5. Guardrails
6. Related references

## Description quality

The description must include trigger language such as:

- Use when the user asks to...
- Use for...
- Use after...

Avoid vague descriptions like `helps with development`.

## Reference files

Use references for:

- Long templates
- Checklists
- Schemas
- Playbooks
- Policy models

Keep references one level from the skill when possible.

## Scripts

Use scripts for deterministic operations such as validation, packaging, parsing, conversion, or repeatable audits. Do not use scripts for judgment-heavy analysis that the model can perform directly.
