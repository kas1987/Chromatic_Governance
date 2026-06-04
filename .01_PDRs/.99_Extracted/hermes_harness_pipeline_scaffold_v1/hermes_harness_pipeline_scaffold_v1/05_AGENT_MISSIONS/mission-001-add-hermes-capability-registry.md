# Mission 001: Add Hermes to Capability Registry

## Preferred Model

Hermes or Qwen.

## Objective

Add Hermes as a local agentic worker model in `model-capabilities.yaml`.

## Complexity

C1

## Privacy Class

P1

## Risk Class

Low

## Allowed Files

```text
09_DEPLOYMENT/config/routing/model-capabilities.yaml
```

## Forbidden Files

```text
02_RUNTIME/router/provider_selector.py
config/routing/providers.yaml
09_DEPLOYMENT/config/routing/routing-table.yaml
```

## Steps

1. Add `hermes3:8b` entry.
2. Use capability fields consistent with existing registry structure.
3. Do not remove or rename existing models.
4. Preserve YAML formatting.

## Acceptance Criteria

- `hermes3:8b` exists exactly once.
- It includes best/good/weak capability tags.
- It is documented as local worker model.
- Existing model entries are unchanged.

## Validation Commands

```bash
python - <<'PY'
import yaml
from pathlib import Path
p = Path('09_DEPLOYMENT/config/routing/model-capabilities.yaml')
data = yaml.safe_load(p.read_text())
assert 'hermes3:8b' in data['models']
print('PASS: hermes3:8b registered')
PY
```

## Stop Conditions

- File missing.
- YAML cannot be parsed.
- Existing registry structure differs from expected.
