# Agent Governance Operating Model

Use this model to keep multi-agent work bounded, reviewable, and safe.

## Principles

1. Mission before agent: define the job before selecting the actor.
2. Narrowest capable actor: assign the smallest scope that can complete the work.
3. Separation of duties: high-risk work needs an independent reviewer.
4. Evidence over confidence: claims should cite files, tests, logs, or explicit user instructions.
5. Stop conditions matter: every delegated task needs a clear point where the agent must pause.
6. Human authority remains supreme for destructive, credentialed, production, legal, financial, or external-side-effect actions.

## Standard governance flow

1. Build or update the agent roster.
2. Map authority for actors and action types.
3. Delegate work with explicit scope and stop conditions.
4. Run work in serial or parallel lanes.
5. Apply review chain.
6. Resolve conflicts using evidence hierarchy.
7. Escalate when risk or ambiguity exceeds agent authority.
8. Run retrospective after meaningful work completes.
