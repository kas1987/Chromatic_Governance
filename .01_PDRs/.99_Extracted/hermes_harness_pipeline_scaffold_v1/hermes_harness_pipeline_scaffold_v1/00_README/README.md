# Hermes Harness Pipeline Scaffold v1

## Purpose

This package defines the first implementation scaffold for integrating Hermes and other local/worker models into `chromatic-harness-v2` as bounded execution agents beneath frontier-model mission planning.

## Core Operating Idea

Frontier models should design rails. Local models should run on those rails. CI, tests, schemas, and GitHub review should decide whether the work passes.

```text
Frontier Model
  -> PDR / Mission Packet / Acceptance Criteria / Evals
  -> Queue / Router
  -> Hermes, Qwen, Llama, Gemma, other worker models
  -> Tests / CI / Schemas / Linters
  -> GitHub review automation
  -> Frontier escalation only when blocked, ambiguous, or high risk
```

## Package Contents

| Folder | Purpose |
|---|---|
| `01_PDR` | Product/design record for the pipeline |
| `02_GOVERNANCE` | Authority, risk, escalation, and model-use rules |
| `03_SCHEMAS` | Mission packet and evaluation result schemas |
| `04_ROUTING` | Proposed routing patches and model tier map |
| `05_AGENT_MISSIONS` | Local-agent implementation handoffs |
| `06_EVALS` | Hermes/local model eval design |
| `07_CI` | CI gate plan and test hooks |
| `08_DOCS` | Operator guide and mental model |
| `09_QUEUE` | Seed work queue for beads/local agents |

## v1 Scope

This is a planning and scaffold package. It does not directly patch the repository. Local agents should read the PDR, execute mission packets one at a time, and open PRs with test evidence.

## Recommended First Agent

Start with `mission-001-add-hermes-capability-registry.md`.
