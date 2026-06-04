# Hermes Routing Policy

## Purpose

Define when Hermes may be used inside Chromatic Harness v2.

## Canonical Role

Hermes is a local model used by existing agents. It is not a new agent identity.

```text
Agent Role -> Router -> ollama_local:hermes3:8b -> bounded operational task
```

## Allowed Uses

Hermes may be used for:

- C1 mechanical tasks
- C2 structured operational tasks
- bead triage
- queue summaries
- mission packet drafts
- handoff compression
- documentation cleanup
- governance checklist summaries
- low-risk local classification

## Blocked Uses By Default

Hermes should not be the default for:

- C3 root-cause analysis
- C4 architecture or invention
- policy creation
- autonomous destructive actions
- secret handling workflows
- merge decisions
- high-risk git autonomy decisions

## Privacy

Hermes via local Ollama keeps inference local. Even so, all existing privacy gates remain in force. Local routing does not mean unrestricted routing.

## Confidence Requirements

Hermes output must be validated before task completion.

Minimum validation expectations:

- JSON parses when JSON is required.
- File paths exist or are explicitly marked proposed.
- No forbidden files/actions are included.
- Stop conditions are preserved.
- Acceptance criteria are present.

## Promotion Rule

Hermes may become the default local operational worker only after benchmark evidence meets the evaluation protocol.

## Rollback Rule

If Hermes produces malformed handoffs, hallucinated file paths, or governance drift, remove it from routing defaults and mark it experimental-only.
