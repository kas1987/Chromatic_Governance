# Agent Routing Guide

## Front-Tier Models

Use Claude, GPT, Gemini Pro, or equivalent for:
- PDR creation.
- Mission packet design.
- Architecture decisions.
- Eval design.
- Ambiguity resolution.
- M3/M4 review.

## Local Worker Models

Use Hermes, Qwen, Llama, Gemma, and other local models for:
- M1 execution.
- M2 execution when instructions are explicit.
- Queue triage.
- Mission packet reading.
- Handoff generation.
- CI failure summarization.
- Bounded code or documentation changes.

## Tests and CI

Use automated checks as the default reviewer:
- Unit tests.
- Integration tests.
- Schema validation.
- Static analysis.
- Security checks.
- Custom evals.

## GitHub Review Layer

Use GitHub code owners, CI checks, branch protection, and code review bots for final review.

## Escalation Back to Front Tier

Escalate when:
- Tests fail repeatedly.
- Requirements conflict.
- Risk increases.
- A local model changes scope.
- The work touches security, secrets, data protection, or core governance.
