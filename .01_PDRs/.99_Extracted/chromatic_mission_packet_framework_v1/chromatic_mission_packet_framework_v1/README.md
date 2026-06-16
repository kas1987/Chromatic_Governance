# Chromatic Harness v2 Mission Packet Framework v1

Purpose: provide schemas, templates, governance rules, PDR requirements, and validation scaffolding for M1-M4 mission packets.

Core principle: use the simplest mission packet level that is sufficient, not the simplest one that is convenient.

## Mission Levels

| Level | Name | Use When | PDR Requirement | Governance |
|---|---|---|---|---|
| M1 | Basic | Simple, bounded, low-risk task | None; packet only | Standard |
| M2 | Intermediate | Multiple steps, dependencies, or one integration surface | Light PDR | Elevated |
| M3 | Complex | Cross-system, higher-risk, architecture or production impact | Standard PDR | High |
| M4 | Atomic | Critical, irreversible, security-sensitive, architecture-changing, or production rollout | Full PDR | Maximum |

## Package Contents

- `schemas/mission-packet.schema.json` — base schema for all mission packets.
- `schemas/pdr.schema.json` — PDR schema with M2-M4 depth fields.
- `schemas/governance-register.schema.json` — governance gates and approvals.
- `schemas/supporting-documents.schema.json` — manifest for tests, risks, rollback, impact, stakeholder, and communication docs.
- `templates/` — M1-M4 YAML templates and supporting document templates.
- `docs/` — guidance for level selection, governance, PDR depth, routing, and CI validation.
- `examples/` — sample mission packets for each level.
- `validation/validate_packet.py` — simple local validator using Python jsonschema.
- `queue/seed-work-items.yaml` — implementation tasks for local agents.

## Suggested Repo Placement

```text
10_MISSIONS/
  schemas/
  templates/
  examples/
docs/governance/
docs/pdr/
docs/routing/
validation/
```

## Local Validation

```bash
pip install jsonschema pyyaml
python validation/validate_packet.py examples/M1_basic_docs_update.yaml schemas/mission-packet.schema.json
```

## Operating Rule

Front-tier models create rails: PDR, mission packet, acceptance criteria, risk gates, evals, and stop conditions. Local agents execute inside those rails. CI and tests decide pass/fail. Front-tier review is used for exceptions, ambiguity, and high-impact decisions.
