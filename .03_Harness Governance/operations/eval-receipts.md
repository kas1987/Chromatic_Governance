# Eval Receipts — Operator Guide (PDR-008 / HERMES-005)

Every completed **local-agent mission** emits one **eval receipt**: a small JSON document
that records what the agent changed, whether it stayed in scope, and whether any stop
condition fired. The receipt is the **CI-gate artifact** (HERMES-006): a mission PR that
lacks a passing receipt fails the gate.

> The eval **receipt** is an operational, per-mission record. It is **distinct** from the
> `hermes_evaluation_result` **scorecard** (a model-quality metric used for routing /
> capability decisions). See PDR-008 Decision 3.

## Contract

- Schema of record: [`schemas/eval_receipt.schema.json`](../schemas/eval_receipt.schema.json)
- Required fields: `mission_id`, `agent_model`, `status`, `files_changed`,
  `validation_results`, `scope_compliance`, `stop_condition_triggered`.
- Optional (additive): `notes`, `pr_ref`, `created_at`.
- `status` ∈ `pass | fail | partial | blocked`; `scope_compliance` ∈
  `compliant | violation | unknown`. Only `status: pass` clears the gate.

## When a local agent generates a receipt

Generate a receipt at the **end of every mission**, before opening (or updating) the PR —
whether the mission passed, failed, was partial, or was blocked. A blocked/failed mission
still emits a receipt (with the appropriate `status` and `stop_condition_triggered: true`);
the receipt is the evidence the mission ran and why it stopped, not a success-only trophy.

## How to attach a receipt to a PR

1. Write the receipt to the mission's evidence path, e.g.
   `.03_Harness Governance/operations/receipts/<mission_id>.eval_receipt.json`.
2. Set `pr_ref` to the PR number/URL once known (e.g. `"#42"`), and `created_at` to the
   emission timestamp.
3. Validate it locally before pushing:

   ```bash
   python "scripts/validate_packet.py" \
     "operations/receipts/<mission_id>.eval_receipt.json" \
     "schemas/eval_receipt.schema.json"
   # exit 0 = PASS (gate-eligible), 1 = schema-invalid, 2 = usage/deps error
   ```

4. Commit the receipt **in the same PR** as the mission's changes so the CI gate
   (HERMES-006) can find and re-validate it.

## Validator

- Script: [`scripts/validate_packet.py`](../scripts/validate_packet.py) — validates any
  JSON/YAML packet (mission packet or eval receipt) against a JSON Schema.
- Dependencies: `jsonschema`, `pyyaml` (pinned in
  [`requirements-dev.txt`](../requirements-dev.txt)). No other runtime deps.

## Tests

`scripts/tests/test_eval_receipt.py` proves a valid fixture passes and an invalid fixture
fails. Run the suite from the `.03_Harness Governance/` root:

```bash
python -m pytest scripts/tests/test_eval_receipt.py -q
```
