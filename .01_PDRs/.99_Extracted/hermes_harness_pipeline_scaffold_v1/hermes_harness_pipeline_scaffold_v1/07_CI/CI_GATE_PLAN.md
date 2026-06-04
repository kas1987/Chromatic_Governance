# CI Gate Plan for Local Agent Work

## Required Checks

Every local-agent PR should include:

1. Mission packet reference.
2. Eval receipt.
3. Changed-file list.
4. Validation command output.
5. Scope compliance statement.

## Suggested CI Jobs

| Job | Purpose |
|---|---|
| schema-validate | Validate mission packets and eval receipts |
| yaml-parse | Confirm routing/config YAML parses |
| router-tests | Confirm provider selector behavior |
| docs-lint | Validate docs and markdown links |
| unit-tests | Run existing project tests |

## GitHub Review Rule

If all checks pass and risk class is low/medium, GitHub reviewers can approve without frontier-model review.

If risk class is high, or if governance/routing behavior changes, require frontier review or human review.
