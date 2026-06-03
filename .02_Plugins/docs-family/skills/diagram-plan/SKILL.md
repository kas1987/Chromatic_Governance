---
name: diagram-plan
description: plan documentation diagrams for architecture, data flow, sequence flow, deployment, entity relationships, plugin families, and agent workflows. use when asked to create diagram specs, mermaid diagrams, visual documentation plans, or decide which diagrams a project needs.
---

# Diagram Plan

## Mission

Create diagram specifications that clarify system structure without becoming decorative or misleading.

## Inputs to collect

- Architecture notes, repo structure, interfaces, data flows, deployment model, or process description
- Audience and decision the diagram must support
- Preferred diagram format, such as Mermaid, PlantUML, draw.io, or plain spec

## Procedure

1. Identify the question the diagram must answer. If there is no question, do not create a diagram for decoration.
2. Choose one diagram type per question: context, container, component, sequence, data flow, state, deployment, or ERD.
3. Keep each diagram bounded to one level of abstraction.
4. Name nodes with real system terms and note unknown boundaries.
5. Represent trust boundaries, external systems, and state changes when relevant.
6. Provide both diagram source and a short interpretation.
7. Flag areas requiring architecture, security, or data owner review.

## Guardrails

- Do not invent commands, endpoints, flags, environment variables, owners, or support promises.
- Treat code, tests, manifests, schemas, and current configuration as stronger evidence than old prose docs.
- Keep docs scoped to the audience and task; avoid turning every document into a full encyclopedia.
- Surface uncertainty directly with TODO, needs-owner-review, or unverified labels.
- Escalate security-sensitive docs, secret handling, production operations, destructive commands, and permission changes to the relevant family before finalizing.

## Expected outputs

- Diagram inventory or diagram spec
- Mermaid or other diagram source when requested
- Assumptions and unknowns
- Recommended placement in docs

## Reference loading

Load these files only when needed for the current documentation task:

- `../../references/diagram-plan-template.md`
- `../../references/documentation-operating-model.md`
- `../../references/doc-quality-checklist.md`

## Completion checklist

- Audience and scope are explicit.
- Claims are grounded in source files or clearly marked as assumptions.
- Setup, usage, validation, and escalation paths are present when relevant.
- Links and file paths are checked where possible.
- Open questions are separated from confirmed instructions.
