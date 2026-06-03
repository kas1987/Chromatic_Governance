# Golden Case Schema

Use this structure for stable known-good examples.

```yaml
case_id: GC-001
category: minimal-valid | typical | complex | edge | invalid | adversarial
summary: short description
input: |
  user or system input
context: |
  allowed context, files, fixtures, or assumptions
expected_output: |
  exact or approximate expected result
must_include:
  - required item
must_not_include:
  - prohibited item
scoring_rule: binary | rubric | snapshot | semantic
sensitive_data: none | sanitized | synthetic
linked_acceptance_criteria:
  - AC-1
notes: |
  maintenance notes
```

## Update policy

Update golden cases only when the expected behavior intentionally changes. Record the reason in the decision log or PR notes.
