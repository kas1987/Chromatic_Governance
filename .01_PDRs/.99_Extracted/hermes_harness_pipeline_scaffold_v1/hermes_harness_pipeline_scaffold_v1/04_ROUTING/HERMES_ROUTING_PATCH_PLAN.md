# Hermes Routing Patch Plan

## Goal

Add Hermes as a local worker model for C1/C2 agent operations without changing the harness architecture.

## Files To Patch

```text
09_DEPLOYMENT/config/routing/model-capabilities.yaml
09_DEPLOYMENT/config/routing/routing-table.yaml
```

## Proposed Capability Registry Entry

```yaml
hermes3:8b:
  best_at: [instruction, speed, agentic]
  good_at: [reasoning, coding]
  weak_at: [creativity, vision]
  observed_by: "local"
  source: "Nous/Ollama local evaluation"
  notes: "Local agentic worker for C1/C2 queue, handoff, mission packet, classification, and documentation tasks."
```

## Proposed Desktop Routing

```yaml
context_desktop:
  balance:
    C1: [ollama_local:hermes3:8b, ollama_local:llama3.1:8b]
    C2: [ollama_local:hermes3:8b, ollama_local:qwen2.5-coder:14b]
```

## Proposed Remote Desktop Routing

```yaml
context_laptop_remote:
  balance:
    C1: [ollama_local:hermes3:8b]
    C2: [ollama_remote_desktop:hermes3:8b, ollama_remote_desktop:qwen2.5-coder:14b]
```

## Guardrails

- Do not route Hermes to C4.
- C3 route only after eval promotion.
- Use Qwen for code-heavy C2 by default if mission area is code.
- Use Hermes for queue/docs/ops-heavy C2.

## Required Tests

- provider selector returns Hermes for C1 desktop balance when Ollama reachable
- provider selector returns Qwen for code-heavy mission if mission specifies coding specialization
- privacy gate blocks cloud routes for high privacy, but local routes remain available
