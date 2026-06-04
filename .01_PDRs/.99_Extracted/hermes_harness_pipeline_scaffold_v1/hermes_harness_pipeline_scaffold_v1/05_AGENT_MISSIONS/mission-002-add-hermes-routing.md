# Mission 002: Add Hermes to Routing Table

## Preferred Model

Qwen Coder or controlled Hermes after Mission 001 passes.

## Objective

Add Hermes to selected local Ollama C1/C2 routing paths.

## Complexity

C2

## Privacy Class

P1

## Risk Class

Medium

## Allowed Files

```text
09_DEPLOYMENT/config/routing/routing-table.yaml
```

## Forbidden Files

```text
02_RUNTIME/router/provider_selector.py
config/routing/providers.yaml
```

## Steps

1. Add Hermes to `context_desktop.balance.C1` before Llama.
2. Add Hermes to `context_desktop.balance.C2` before Qwen for ops/docs routes only if routing supports coarse model selection.
3. Add Hermes to `context_laptop_remote.balance.C2` before Qwen.
4. Do not touch C4.
5. Avoid routing Hermes as first choice for code-specialized work unless future classifier supports task area.

## Acceptance Criteria

- Hermes appears in C1/C2 local routes.
- Hermes does not appear in C4 routes.
- YAML parses.
- Existing provider syntax is preserved.

## Validation Commands

```bash
python - <<'PY'
import yaml
from pathlib import Path
p = Path('09_DEPLOYMENT/config/routing/routing-table.yaml')
data = yaml.safe_load(p.read_text())
text = p.read_text()
assert 'ollama_local:hermes3:8b' in text or 'ollama_remote_desktop:hermes3:8b' in text
for ctx, modes in data.items():
    if not isinstance(modes, dict):
        continue
    for mode, levels in modes.items():
        if isinstance(levels, dict) and 'C4' in levels:
            assert not any('hermes' in str(x).lower() for x in levels['C4'])
print('PASS: Hermes routing added without C4 promotion')
PY
```

## Stop Conditions

- Routing table structure is unexpected.
- Hermes would become default for C4.
- Tests fail after one retry.
