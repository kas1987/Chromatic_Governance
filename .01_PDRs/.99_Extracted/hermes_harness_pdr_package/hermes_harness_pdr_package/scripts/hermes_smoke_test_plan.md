# Hermes Smoke Test Plan

## Preflight

```bash
ollama list
ollama run hermes3:8b "Return only JSON: {\"status\":\"ok\"}"
python -m pytest tests/test_hermes_routing_policy.py -q
```

## Smoke Test 1: Bead Triage

Prompt Hermes with three sample bead descriptions. Expected output:

```json
{
  "triage": [
    {
      "bead_id": "...",
      "priority": "P1|P2|P3",
      "recommended_owner": "sentinel|auditor|cartographer|archivist|janitor|quartermaster|chainbreaker|financier",
      "reason": "...",
      "stop_condition": "..."
    }
  ]
}
```

## Smoke Test 2: Mission Packet

Prompt Hermes to convert a bead into a mission packet. Required fields:

- mission_id
- objective
- scope
- allowed_files
- forbidden_files
- required_gates
- confidence_required
- stop_conditions
- validation_checks

## Smoke Test 3: Handoff Compression

Input a long handoff. Expected output:

- current objective
- active files
- decisions made
- blockers
- next action

## Smoke Test 4: Governance Checklist

Input a proposed task. Expected output:

- intent gate pass/fail
- scope gate pass/fail
- privacy gate pass/fail
- cost gate pass/fail
- tool gate pass/fail
- final recommendation
