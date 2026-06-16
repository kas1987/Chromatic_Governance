# Mission Level Selection Guide

Use this guide before creating a mission packet.

## M1 Basic

Use M1 when the task is simple, bounded, low risk, and easy to validate.

Typical examples:
- Documentation update.
- Small config change.
- Add or update a simple test.
- Minor refactor in one file.

Required:
- Objective.
- Scope.
- Allowed and forbidden files.
- Acceptance criteria.
- Validation checks.
- Stop conditions.

PDR: not required.

## M2 Intermediate

Use M2 when the task has multiple steps, dependencies, one integration point, or moderate risk.

Typical examples:
- Feature with tests.
- API endpoint.
- Database migration.
- Multi-file refactor.

Required:
- M1 fields.
- Background/context.
- Dependencies.
- Constraints.
- Light risk summary.
- Basic rollback plan.
- Light PDR.

## M3 Complex

Use M3 when the task crosses systems, changes architecture, carries significant risk, or impacts production workflows.

Typical examples:
- Major feature.
- Router logic change.
- Performance-sensitive work.
- Security improvement.
- Cross-repo integration.

Required:
- M2 fields.
- Standard PDR.
- Detailed plan.
- Integration map.
- Risk register.
- Comprehensive test plan.
- Rollback plan.
- At least two reviewers or equivalent automated controls.

## M4 Atomic

Use M4 when the task is critical, irreversible, security-sensitive, production-changing, or foundational to architecture.

Typical examples:
- Core architecture change.
- Data model overhaul.
- Secret or credential flow.
- Production rollout.
- Governance or autonomy policy change.

Required:
- Full PDR.
- Full threat/risk model.
- Stakeholder map.
- Impact assessment.
- Full rollback plan.
- Communication plan.
- Formal approval.
- Maximum governance.

## Escalation Rule

Escalate the mission level if any of these are true:

- Scope is unclear or growing.
- Dependencies are complex.
- Risk is underestimated.
- Tests are weak or absent.
- Rollback is unclear.
- Output impacts production, security, data, or governance.
- A local agent cannot prove success with deterministic validation.
