# Context State Schema

Use this schema when creating session briefs, handoff packs, onboarding briefs, or memory-sync updates.

## Canonical sections

```yaml
project:
  name: ""
  repo_or_workspace: ""
  current_branch: ""
  active_plugins: []
  active_agents: []

mission:
  user_goal: ""
  current_scope: ""
  explicit_non_goals: []
  success_criteria: []

state:
  completed: []
  in_progress: []
  blocked: []
  next_actions: []

source_of_truth:
  authoritative_files: []
  secondary_files: []
  stale_or_suspect_files: []
  missing_sources: []

decisions:
  accepted: []
  pending: []
  reversed_or_deprecated: []

assumptions:
  confirmed: []
  inferred: []
  risky_or_unverified: []

risks:
  technical: []
  security: []
  product: []
  operational: []

handoff:
  recipient_agent: ""
  recommended_next_skill: ""
  required_context: []
  commands_to_run: []
  files_to_inspect: []
  files_to_modify: []
```

## Confidence labels

Use these labels whenever a claim may affect implementation, security, architecture, or release decisions:

- `confirmed`: directly supported by file inspection, command output, user instruction, or authoritative docs.
- `inferred`: likely based on surrounding context, but not directly proven.
- `unknown`: not enough evidence.
- `stale-risk`: source exists, but may be outdated.
- `conflict`: two or more sources disagree.

## Compression rule

Keep context brief enough that a fresh agent can act within 3 minutes. Move detail into linked files when possible.
