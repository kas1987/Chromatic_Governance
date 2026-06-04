# Mission 003: Add Local Agent Eval Receipt Flow

## Preferred Model

Qwen Coder.

## Objective

Add a minimal eval receipt fixture and validation command for local-agent runs.

## Complexity

C2

## Privacy Class

P1

## Risk Class

Medium

## Allowed Files

```text
schemas/
tests/
docs/
```

## Forbidden Files

```text
02_RUNTIME/router/provider_selector.py
```

## Steps

1. Add or adapt eval receipt schema.
2. Add one valid fixture.
3. Add one invalid fixture.
4. Add schema validation test.
5. Document how agents attach receipts to PRs.

## Acceptance Criteria

- Valid receipt passes schema validation.
- Invalid receipt fails schema validation.
- Documentation tells local agents when to generate receipts.

## Validation Commands

```bash
pytest tests -q
```

## Stop Conditions

- Test framework absent and no equivalent exists.
- Schema location conflicts with existing project convention.
