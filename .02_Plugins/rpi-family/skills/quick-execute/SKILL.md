---
name: quick-execute
description: Use when a task is mechanical and well-specified — docs, config updates, scaffolding, single-function additions, renames, or template fills — and you need to execute it inline without dispatching subagents. Do NOT use for tasks requiring judgment, architecture decisions, or security-sensitive code.
---

# Quick Execute

## Model
Use **haiku** for this skill. Escalate to sonnet only if you hit an ambiguous decision during execution.

## Overview

Single-pass inline execution. No subagent dispatch, no review chains. Execute → self-review → commit.

**Core principle:** Mechanical tasks done right the first time cost less than review loops on simple work.

---

## Mechanical Task Classification

Score the task against these 5 signals. **≥3 signals = eligible for quick-execute.**

- [ ] Changes touch ≤3 files
- [ ] No new function signatures or interfaces designed during execution
- [ ] Output format is prescribed (template, config schema, naming pattern)
- [ ] No conditional logic introduced (no new if/switch/loop)
- [ ] Acceptance criteria are verifiable without running code

**<3 signals → escalate to `superpowers:subagent-driven-development`.**

---

## When to Use

- Writing or updating markdown docs, READMEs, SKILL.md files
- Config file updates (JSON, YAML, TOML)
- Scaffolding from a template
- Renaming files or variables
- Adding a single well-defined function with no design choices
- Filling in an evaluation matrix or checklist

**Never use for:**
- Tasks requiring design decisions during execution
- Security-sensitive code (auth, crypto, permissions, secrets)
- Cross-module integration (contract or interface changes)
- Tasks that previously failed or were attempted more than once

---

## Relationship to Other Skills

- Run **quick-execute** FIRST for execution
- Run **inline-review** AFTER execution as the self-check gate
- If the change exceeds inline-review thresholds (>100 LOC, >3 files) → escalate to `superpowers:requesting-code-review` before committing

---

## The Process

### Step 1 — Read the full spec before touching anything

Read every requirement. Identify all files to change. Do not start editing until you have the complete picture.

If anything in the spec is ambiguous → **stop and ask**. Do not infer.

### Step 2 — Execute all changes inline

Make every change in this session. No subagents.

### Step 3 — Self-review checklist (inline, no subagent)

Answer all 5 questions before committing:

1. **Spec match** — Does output match the spec exactly? No extras, nothing missing?
2. **No placeholders** — Any `[TBD]`, `TODO`, or unfilled template fields?
3. **Tests pass** — Run them if the task touched logic. Skip if docs/config only.
4. **Commit format** — Does the commit message follow `type(scope): description`?
5. **Index updated** — If this adds to a tracked list (INDEX.md, registry, etc.), is it updated?

All 5 PASS → commit. Any FAIL → fix inline, re-check that question.

### Step 4 — Commit

```bash
git add <specific files>
git commit -m "<type>(<scope>): <description>"
```

---

## Example

**Goal:** Add a new audit decision row to `.agents/audits/INDEX.md`

**Classification (score the 5 signals):**
- [x] Changes touch ≤3 files (1 file: INDEX.md)
- [x] No new function signatures or interfaces
- [x] Output format is prescribed (existing table row format)
- [x] No conditional logic introduced
- [x] Acceptance criteria verifiable without running code (`grep "pdf-export" INDEX.md`)

Score: 5/5 ✓ — eligible for quick-execute

**Step 1 — Read the spec:** Add row for `pdf-export → defer` decision made today. Match existing table format: `| YYYY-MM-DD | Gap | Decision | Solution | Status | Link |`

**Step 2 — Execute:** Append row to INDEX.md table.

**Step 3 — Self-review:**
1. Spec match: Row added, matches format exactly ✓
2. No placeholders: No `[TBD]` in row ✓
3. Tests pass: N/A (doc only) ✓
4. Commit format: `docs(audits): pdf-export → defer` ✓
5. Index updated: This IS the index — no secondary tracking needed ✓

**Step 4 — Commit:** `git add .agents/audits/INDEX.md && git commit -m "docs(audits): pdf-export → defer"`

---

## Red Flags — Stop and Escalate

- "This is simple enough to skip the checklist" → No. Run all 5 questions.
- "I'll just spawn a quick subagent to double-check" → No. Inline only.
- "This got more complex during execution" → Stop. Escalate to `superpowers:subagent-driven-development`.
- "I need to make a design decision here" → Stop. Escalate.
- Score was ≥3 signals but execution revealed 4th file needed → Stop. Escalate.

## Rationalization Table (RED baseline — tested 2026-04-02)

| Rationalization | Reality |
|----------------|---------|
| "The spec is clear enough, I don't need the classification checklist" | Classification prevents costly escalations. Always score. |
| "I can skip self-review for obvious changes" | "Obvious" changes cause the most missed INDEX.md updates. Run all 5. |
| "Spawning a quick subagent is more thorough" | Inline review is sufficient for mechanical tasks. Save the subagent cost. |
| "This is mostly mechanical but has one design choice" | One design choice = not mechanical. Escalate to subagent-driven-development. |
| "I need to see the code before I can review it" | You wrote the code. Self-review means reviewing what you just did — no external input needed. |
| "I'll do the review after I get confirmation the approach is right" | Review happens before commit, not after confirmation. Execute → self-review → commit. |

## RED Baseline Results (tested 2026-04-02)

Subagent dispatched without skill on two scenarios:
- Scenario A: Update INDEX.md (mechanical doc task) → PASS. Executed correctly.
- Scenario B: Review 45 LOC utility function after writing it → FAIL. Agent asked "what's the code?" instead of reviewing inline.

**Key failure:** Agents treat self-review as requiring external input. Without the skill, they ask for code/confirmation instead of running the inline checklist on what they just wrote.

**Fix applied:** Added "I need to see the code" rationalization to table. Step 3 clarified: self-review means reviewing your own output, no external input needed.

---

## Superpowers Comparison

| Concern | superpowers:subagent-driven-development | quick-execute |
|---------|----------------------------------------|---------------|
| Agents per task | 3 (implementer + 2 reviewers) | 0 (inline only) |
| Review loops | Always: spec + quality | Never: self-checklist only |
| Model | Not specified | haiku default |
| When to use | Complex, judgment-heavy, multi-file | Mechanical, prescribed, ≤3 files |
| Token cost | High | ~30% of subagent-driven-dev |

## Examples

### Execute a prescribed doc update
```
/quick-execute update CHANGELOG.md with today's release notes per the template in docs/CHANGELOG-TEMPLATE.md
```
Expected: Reads template, writes entry, self-reviews inline, done. No agents spawned.

### Execute a config-only change
```
/quick-execute set "effortLevel" to "high" in ~/.claude/settings.json
```
Expected: Reads file, edits value, verifies JSON valid, done. ≤3 tool calls.

### When to escalate to subagent-driven-development
Use `superpowers:subagent-driven-development` when the task requires judgment on design, touches >3 files, or has unclear acceptance criteria.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Task requires more than 3 files | Task is not mechanical | Escalate to `superpowers:subagent-driven-development` |
| Self-review asks for code | Agent lost inline context | Invoke `/inline-review` immediately after writing; do not pass work to a subagent |
| Output includes rationale sections | Skill drift into verbose mode | Re-invoke with "checklist and action only, no rationale" explicit instruction |
| Edit produces wrong output | Prescribed task had ambiguous instructions | Clarify exact values/paths before invoking; quick-execute follows instructions literally |


## See Also
- `skills/shared/references/mvs-template.md`
