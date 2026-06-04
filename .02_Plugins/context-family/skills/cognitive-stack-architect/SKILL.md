---
name: cognitive-stack-architect
description: Triage scattered, nonlinear, or overloaded thinking into a structured stack of decisions, priorities, and handoffs. Use when the project feels ambiguous, when too many threads are running in parallel, when you cannot determine what to work on next, or when a session has accumulated more open questions than resolved ones.
skill_api_version: 1
---

# Cognitive Stack Architect

Turn noise into a navigable decision stack so the next action is always clear.

## Core procedure

1. **Collect all open threads.** Ask the user (or scan the session context) for every open question, unresolved decision, half-finished idea, blocked task, and deferred concern. Capture them raw — do not filter at this stage.

2. **Categorize each item** using the DECIDE framework:
   - `D` — Decision required before work can proceed (blocking)
   - `E` — Evidence needed before deciding (research first)
   - `C` — Clarification needed from the user (question)
   - `I` — Implementation ready — all decisions made, ready to build
   - `D2` — Defer — real but not now; move to backlog
   - `E2` — Eliminate — not a real concern; safe to drop

3. **Score priority** for each non-deferred item using two axes:
   - **Impact:** `high` / `medium` / `low` — how much does resolving this unblock?
   - **Effort to resolve:** `minutes` / `hours` / `days`
   - Produce a 2×2: quick-wins (high impact, minutes), must-plan (high impact, hours/days), fill-ins (low impact, minutes), deprioritize (low impact, hours/days)

4. **Build the decision stack.** Order items from the top with the highest-leverage item first. The stack is the work queue for the session.

5. **Assign each item to an action lane:**
   - `decide_now` — resolve in this session before moving forward
   - `ask_user` — needs human input; form the question clearly
   - `delegate` — route to an agent or skill (reference which skill)
   - `log_and_defer` — write to `decision-log` or backlog; not this session

6. **Handoff or execute.** For items in `decide_now` or `implement`, either resolve them inline or produce a `handoff-pack` for the next session. For `delegate` items, invoke `/delegate` or the relevant skill.

## Output format

```markdown
## Cognitive stack — <date or session label>

### Collected threads (<N> total)
| # | Thread | Category | Impact | Effort | Lane |
|---|---|---|---|---|---|
| 1 | Should we use X or Y for storage? | D (blocking decision) | high | minutes | decide_now |
| 2 | Need benchmark data before choosing DB | E (evidence) | high | hours | delegate → data-research/benchmark-compare |
| 3 | Refactor module boundaries | I (implementation ready) | medium | days | delegate → architecture/module-boundaries |
| 4 | Old logging approach | D2 (defer) | low | hours | log_and_defer |

### Decision stack (prioritised)
1. **[decide_now]** Storage: X vs Y — resolve by <criteria>
2. **[ask_user]** <Question for user>
3. **[delegate]** Benchmark DB options → `/benchmark-compare "X vs Y throughput"`
4. **[implement]** Module boundary refactor — ready once #3 resolved

### Deferred / eliminated
- <item> — deferred to backlog
- <item> — eliminated (reason)

### Next action
> <One clear sentence: what the agent or user does immediately after reading this>
```

## Guardrails

- Do not resolve decisions unilaterally — surface them; the user or a governed skill decides
- If a thread maps to an existing skill, route it rather than handling it inline (prefer `/delegate`, `/decision-log`, `/handoff-pack`)
- If more than 5 items land in `decide_now`, push the lowest-impact ones to `ask_user` or `log_and_defer` — an overloaded decide-now lane is itself a signal of scope creep
- This skill produces a stack and an action plan; use `rpi/implement` or the referenced skill to execute individual items
- When the session context is `orange` or above, emit the stack and immediately invoke `/handoff-pack` — do not start executing items
