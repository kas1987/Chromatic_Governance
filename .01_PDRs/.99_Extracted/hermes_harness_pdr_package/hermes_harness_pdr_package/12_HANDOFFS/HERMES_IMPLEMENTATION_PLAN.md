# Hermes Implementation Plan

## Objective

Implement Hermes as a governed local/Ollama model option for Chromatic Harness v2.

## Phase 0: Preflight

1. Confirm repo branch.
2. Run harness boot/guard flow.
3. Confirm Ollama is reachable.
4. Confirm Hermes model tag exists.

Suggested commands:

```bash
bd prime
bd ready
git branch --show-current
git status --short
ollama list
python scripts/session_unified_guard.py --surface auto --invoked-by automation
```

## Phase 1: Registry Patch

Target:

```text
09_DEPLOYMENT/config/routing/model-capabilities.yaml
```

Add Hermes model profile.

Acceptance:

- YAML parses.
- Model ID matches installed Ollama tag.
- Notes clearly restrict Hermes to local operational worker use.

## Phase 2: Routing Patch

Target:

```text
09_DEPLOYMENT/config/routing/routing-table.yaml
```

Add Hermes to C1/C2 local routes.

Recommended first placement:

```yaml
context_desktop:
  balance:
    C1: [ollama_local:hermes3:8b, ollama_local:llama3.1:8b]
    C2: [ollama_local:hermes3:8b, ollama_local:qwen2.5-coder:14b]
```

Do not add Hermes to C3/C4 default routes.

## Phase 3: Governance Doc

Add:

```text
docs/governance/HERMES_ROUTING_POLICY.md
```

Use the supplied file from this package.

## Phase 4: Validation Protocol

Add:

```text
docs/validation/HERMES_EVALUATION_PROTOCOL.md
```

Use supplied benchmark criteria.

## Phase 5: Tests

Create or update tests:

```text
tests/test_hermes_routing_policy.py
```

Minimum cases:

1. Hermes is returned for desktop/balance/C1 when Ollama is reachable.
2. Hermes is returned for desktop/balance/C2 when Ollama is reachable.
3. Hermes is not default for C3/C4 routes.
4. Registry includes Hermes model profile.
5. Routing table model tag is consistent with registry.

## Phase 6: Benchmark

Run local sample tasks:

- 20 C1 bead summaries
- 20 C1 handoff compressions
- 20 C2 mission packets
- 20 C2 governance checklist validations
- 20 C2 docs cleanup tasks

Record results in JSON using:

```text
schemas/hermes_evaluation_result.schema.json
```

## Phase 7: Review Gate

Promote Hermes only if it meets thresholds:

- C1 success >= 90%
- C2 operational success >= 80%
- malformed output <= 5%
- critical governance violations = 0
- hallucinated path/file references <= 5%

## Rollback

Revert routing-table Hermes entries first. Keep docs and capability registry if useful as experimental history.
