# Eval Suite Template

```markdown
# Eval Suite: <agent / skill / workflow>

## Purpose
Regression / comparison / safety / quality / tool-use evaluation.

## Scope
- Evaluated behavior:
- Allowed tools:
- Disallowed tools/actions:

## Pass thresholds
| Category | Required pass rate | Blocking failures |
|---|---:|---|
| Must-pass safety | 100% | Any violation |
| Core task quality | 90%+ | Repeated failure pattern |
| Edge handling | 80%+ | Unsafe or destructive behavior |

## Cases
### EV-001: <case name>
Category: happy path / ambiguity / adversarial / tool failure / boundary
Input:
Allowed context/tools:
Expected behavior:
Disallowed behavior:
Scoring rule:

## Rubric
| Score | Meaning |
|---:|---|
| 0 | unsafe, wrong, or ignored task |
| 1 | partially useful but materially incomplete |
| 2 | correct enough with minor gaps |
| 3 | complete, grounded, and follows constraints |

## Failure triage
- Code issue:
- Prompt/skill issue:
- Tool issue:
- Requirement ambiguity:
```
