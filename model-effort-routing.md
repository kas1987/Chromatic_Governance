# Claude Model × Effort Level Routing Reference

**Version:** 2026-06-02  
**Scope:** Claude Code sessions — all Prism repos on C: + native Claude Code  
**Companion files:** `model-effort-routing.csv`, `cross-provider-model-routing.md`

---

## Pricing (per million tokens)

| Model | Input | Output / Thinking | Notes |
|-------|-------|-------------------|-------|
| Haiku 4.5 | ~$0.80 | ~$4.00 | No extended thinking |
| Sonnet 4.6 | ~$3.00 | ~$15.00 | Thinking at output rate |
| Opus 4.8 | ~$15.00 | ~$75.00 | Thinking at output rate |

> Thinking tokens bill at the model's **output rate**. Verify current pricing at anthropic.com/pricing.

---

## Effort Level × Model Matrix

| Effort | Thinking Budget | Haiku 4.5 | Sonnet 4.6 | Opus 4.8 |
|--------|----------------|-----------|------------|----------|
| **low** | ~0–1k tokens | Fastest, no reasoning | Quick drafts, no inference | Near-instant complex output, no chain |
| **medium** | ~4–8k tokens | N/A (no thinking) | Standard coding/analysis | Solid reasoning, high-trust tasks |
| **high** | ~16–32k tokens | N/A | Deep reasoning, complex debug | Security audits, architecture |
| **max** | ~32–64k+ tokens | N/A | Near-Opus quality reasoning | Maximum capability, mission-critical |

> Haiku 4.5 does **not** support extended thinking. Effort level has no effect beyond context handling.

---

## Model + Effort → C-Level + T-Level Mapping

| Combination | C-Level | T-Level | Est. Cost/Call | Best For |
|------------|---------|---------|---------------|----------|
| Haiku / any | C1–C2 | T1–T2 | $0.001–0.01 | Classification, routing, format, batch |
| Sonnet / low | C2 | T3 | $0.02–0.05 | Quick single-file edits, fast drafts |
| Sonnet / medium | C2–C3 | T3 | $0.05–0.15 | Standard coding, PR review, test gen |
| Sonnet / high | C3–C4 | T3 | $0.15–0.40 | Deep reasoning, multi-file debug, architecture |
| Sonnet / max | C4 | T3–T4 | $0.30–0.80 | Thorough analysis, exhaustive review, pre-mortems |
| Opus / low | C4 | T4 | $0.10–0.25 | Creative synthesis, knowledge-heavy judgment |
| Opus / medium | C4 | T4 | $0.20–0.60 | High-trust decisions, novel architecture |
| Opus / high | C4 | T4 | $0.50–1.50 | Security audits, complex synthesis |
| Opus / max | C4 | T4 | $1.00–3.00 | Maximum capability, irreversible decisions |

---

## The Sonnet High ≈ Opus Low Crossover

This crossover **exists** for reasoning-bound tasks, not knowledge-bound tasks.

### When Sonnet high ≈ Opus low (crossover valid)
- Analytical tasks: structured reasoning, debugging, code review
- Chains of logic: multi-step inference, root-cause analysis
- Plan generation, summarization, structured synthesis

### When Sonnet high < Opus low (crossover fails)
- Creative synthesis requiring broad implicit knowledge
- Novel problem framing and ambiguous requirement scoping
- Tasks needing diverse world-knowledge associations, not inference chains
- High-nuance creative writing or judgment under genuine uncertainty

### Cost at the crossover point

```
Sonnet max:   ~$0.30–0.80/call  (thinking-heavy)
Opus low:     ~$0.10–0.25/call  (no thinking)
```

**Opus low is often CHEAPER than Sonnet max at the crossover.** Thinking tokens compensate for model capacity but are not free. Prefer Opus low over Sonnet max when the task is knowledge-bound and budget allows.

---

## Routing Decision Tree

```
Is the task mechanical? (format, scaffold, extract, no judgment)
  → Haiku (any effort) — C1/C2, T1-T2

Is it a single-file, known-pattern task?
  → Sonnet low/medium — C2, T3

Does it require multi-file reasoning or deep debugging?
  → Sonnet high — C3-C4, T3
  → Compare to Opus low cost; if similar, prefer Opus low for quality

Does it require creative synthesis, novel framing, or knowledge-heavy judgment?
  → Opus low/medium — C4, T4
  → Never try to substitute Sonnet high here; the crossover fails

Is this a mission-critical, high-stakes, or irreversible decision?
  → Opus high/max — C4, T4
  → Require explicit budget gate before dispatch
```

---

## Effort Level Governance Rules

### E1 — Default to session effort for orchestrator, not subagents
The orchestrator inherits the session effort level. Subagents should run at the **minimum effort that satisfies the task** — not the session default.

### E2 — Thinking budgets multiply cost; gate before dispatch
At Sonnet max, a thinking-heavy call can cost **3–5×** the same model at low effort. Before dispatching high/max effort subagents, verify the task is reasoning-bound and the budget allows it.

### E3 — Sonnet max > Opus low cost — prefer Opus low
When the task lands in the crossover zone (analytical, reasoning-bound C3-C4), `Opus low` is typically cheaper AND higher quality than `Sonnet max`. Prefer Opus low unless quota forces otherwise.

### E4 — Haiku effort is a no-op; never set high/max for Haiku subagents
Haiku has no thinking capability. Setting effort high/max wastes dispatch overhead with zero quality gain. Always route Haiku at default/low.

### E5 — Reserve Opus max for explicit high-stakes gates
Opus max ($1–3+/call) is for irreversible decisions, security audits, and correctness-critical one-shots. Require a documented justification at the dispatch site.

---

## Anti-Patterns

| Pattern | Why It's Wrong | Correct Route |
|---------|---------------|---------------|
| Haiku at high/max effort | No thinking support — wasted overhead | Haiku / any |
| Sonnet max when Opus low would suffice | Sonnet max costs more at the crossover | Opus low |
| Opus on C1-C2 tasks | ~10× cost premium for zero quality gain | Haiku |
| Effort level ignored for subagents (inherits session max) | Multiplies cost across all parallel agents | Set effort per agent per task |
| Thinking for knowledge-bound tasks | Thinking improves inference, not recall | Opus low (no thinking) |

---

## References

### Local references

- `model-effort-routing.csv` — Machine-readable version of this table
- `cross-provider-model-routing.md` — Cross-provider companion reference

### External references

- `~/.claude/governance/subagent-token-efficiency.md` — The 5 enforceable routing rules (R1–R5)
- `~/.claude/governance/multi-router-matrix.yaml` — Full C-level × T-level provider matrix
- `~/.claude/governance/model-routing-for-subagents.md` — On-demand subagent routing detail
