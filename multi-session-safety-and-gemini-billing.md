# Multi-Session IDE/LLM Collision Safety & Gemini Billing Research

**Version:** 2026-06-04  
**Status:** Research & Planning  
**Companion files:** `gemini-vs-chatgpt-usage-guide.md`, `model-effort-routing.md`, `cross-provider-model-routing.md`

---

## Part 1: Gemini $200 Plan — What's Included vs Separate

### Executive Summary

The Gemini $200/year plan provides:
- **Gemini Advanced** (2.0) access with 50 messages/day limit
- **1M free NotebookLM requests** annually (built into plan)
- **Veo video generation credits** (limited)
- **Access to experimental features** (Deep Research, imagen, etc.)

**Critically, this is SEPARATE from:**
- Google Cloud APIs (Vertex AI, PaLM, Gemini API — **billable separately**)
- Google One backup / Drive storage
- Workspace/enterprise Google Docs collaboration features

---

## Part 1a: Gemini Advanced ($200/year)

| Feature | Included | Limit | Notes |
|---------|----------|-------|-------|
| Gemini 2.0 chat access | ✅ Yes | 50 msg/day | Mobile + web |
| File upload (Docs, Drive, Gmail context) | ✅ Yes | Unlimited reads from Drive | No cost for reading; summarizing uses message quota |
| Gemini Deep Research | ✅ Yes (experimental) | ~3–5/day | Uses message quota |
| Veo video generation | ✅ Yes | ~100 credits/month (variable pricing) | Each video generation costs credits; regeneration costs more |
| Imagen 3 image generation | ✅ Yes (if beta access) | Bundled with credit system | May require separate sign-up for Imagen API |
| NotebookLM access | ✅ Yes | Effectively unlimited (1 audio, unlimited Q&A per notebook) | Key value: audio briefing generation + source-grounded synthesis |

---

## Part 1b: Google Cloud APIs — NOT Included in $200 Plan

| API | Use Case | Pricing Model | Cost Range | Condition |
|-----|----------|--------------|-----------|-----------|
| **Vertex AI / Gemini API** | Programmatic access, batch inference, fine-tuning | Per-token (similar to Anthropic) | ~$0.50–$2.50 per 1M input tokens | Must set up Cloud billing separately; tied to GCP project |
| **PaLM 2 / Gemini 1.5 (deprecated/legacy)** | Older code/embedding models | Per API call or per token | Varies; often $0 for some legacy endpoints | Deprecated; Vertex AI is the future path |
| **Cloud Translation API** | Multilingual workflows | Per 100k characters | $15–$25 per 1M chars | Separate GCP billing |
| **Cloud Vision API** | OCR, image labeling | Per 1000 requests | $1.50–$10 per 1k images | Separate GCP billing |
| **Imagen 3 API** | Programmatic image generation | Per image | ~$0.065–$0.13/image | Different from web-based Imagen 3 in Gemini |

---

## Part 1c: How to Know Which You're Using

**Gemini Advanced ($200 plan) — NO additional billing:**
- ✅ Using gemini.google.com in browser
- ✅ Uploading Google Docs to Gemini chat
- ✅ Asking Gemini to summarize Drive files or emails
- ✅ Using NotebookLM (notebooks.google.com)
- ✅ Using experimental features (Deep Research, Veo)

**Google Cloud APIs (separate billing) — WILL incur charges:**
- ❌ Calling `curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0:generateContent` with an API key
- ❌ Using Vertex AI from a GCP project (even if credentials are free-tier)
- ❌ Batch processing with Cloud Tasks or Dataflow calling Gemini API
- ❌ Fine-tuning models via `google-cloud-ai` or Vertex API

---

## Part 1d: Recommendation: Audit Current Setup

**Questions to answer:**
1. Is your `$200 Gemini` credential tied to a **Google Consumer account** or **Google Cloud project**?
   - **Consumer account** → Only the web/mobile experience is covered by $200; any API calls are separate
   - **Cloud project** → Even basic usage triggers GCP billing; must set budget alerts
2. Do you have a `GCP_PROJECT_ID` or `GOOGLE_CLOUD_CREDENTIALS` environment variable set anywhere?
   - If yes → You're using Cloud APIs; these are billed separately
3. Are you calling any APIs programmatically, or only the web interface?
   - Only web (browser/NotebookLM) → No surprise charges
   - Programmatic (Python SDK, REST API endpoints) → Separate billing active

**Action:** Check `c:\.00_Governance\.80_Per_GPT\` and `.02_Plugins\` for any GCP/Vertex AI configuration files.

---

## Part 2: Multi-Session IDE/LLM Collision Safety Protocols

### Reference Sources

Protocols discovered in `C:\Users\kas41\chromatic-harness-v2\01_PROTOCOLS\`:
- **CMP_SPEC.md** — Chromatic Management Protocol (control plane)
- **BEADS_SPEC.md** — Bead lifecycle for intake/action objects
- **PR_COLLISION_CONTROL_PLAYBOOK.md** — Multi-agent PR branch safety
- **lock_pr_branch.py** — File-based locking mechanism
- **parallel-execution-plan.md** — Multi-lane execution coordination

---

## Part 2a: Core Problem

**Symptom:** Multiple Claude IDE sessions, external tools, or concurrent workflows all try to edit the same file or PR branch → merge conflicts, state corruption, or one agent overwrites another's work.

**Why it happens:**
- Claude Code sessions are stateless (no shared session ID across instances)
- GitHub branches can be edited by any authenticated tool
- Python scripts and n8n workflows have no built-in collision detection
- Lock mechanisms don't exist by default in Git

---

## Part 2b: Recommended Pattern — PR Branch Locking (Adapted)

### Core Rules

**Rule 1:** One PR branch = one active mutating agent  
**Rule 2:** Read-only inspection does not require a lock  
**Rule 3:** Write/commit/push requires a lock acquisition  
**Rule 4:** Locks have TTL; expired locks can be replaced  
**Rule 5:** Active locks block new mutation work (fail-fast)

### Lock Lifecycle

```
[Mutation needed]
  ↓
[Acquire lock] ← Check if lock exists; if active, FAIL
  ↓
[Patch / Commit] ← Only this agent commits
  ↓
[Validate] ← Agent runs tests/checks
  ↓
[Comment / Push] ← Report back via GitHub CLI or webhook
  ↓
[Release lock] ← Cleanup; TTL ensures stale locks are safe
```

### Implementation (File-Based Lock)

**Lock file location:** `.00_Governance\00_PLANNING\locks\PR-##.lock.json`

**Lock file schema:**
```json
{
  "lock_id": "LOCK-Chromatic_Governance-PR1",
  "repo": "kas1987/Chromatic_Governance",
  "pr_number": 1,
  "branch": "claude/test-coverage-analysis-XoxC1",
  "holder": "agent-dispatch-review-intake",
  "queue_item_id": "NW-REVIEW-INTAKE-002",
  "started_at": "2026-06-04T20:30:07.936257Z",
  "expires_at": "2026-06-04T21:00:07.936257Z",
  "ttl_minutes": 30
}
```

**Commands:**
```bash
# Acquire lock (fail if already held)
python scripts/lock_pr_branch.py acquire \
  --repo kas1987/Chromatic_Governance \
  --pr-number 1 \
  --branch claude/test-coverage-analysis-XoxC1 \
  --holder "current-agent-name" \
  --queue-item-id "task-id" \
  --ttl-minutes 30

# Check status
python scripts/lock_pr_branch.py status \
  --repo kas1987/Chromatic_Governance \
  --pr-number 1

# Release lock
python scripts/lock_pr_branch.py release \
  --repo kas1987/Chromatic_Governance \
  --pr-number 1
```

---

## Part 2c: Worktree Isolation (Multi-Parallel Edits)

**When to use:** Multiple independent agents working on **different files** in parallel

**Pattern:**
```bash
# For each agent/epic in the wave:
git worktree add /tmp/swarm-<epic-id> -b swarm/<epic-id>

# Agent 1 works in /tmp/swarm-epic-001
# Agent 2 works in /tmp/swarm-epic-002
# No build lock conflicts; each has its own working tree, branch, and lock state
```

**Constraints:**
- ✅ Use when workers touch **different files**
- ❌ Do NOT use when workers share **same files** (worktrees can't solve same-file conflicts)
- ❌ Overkill for single-worker waves

---

## Part 2d: Session Isolation (Claude Code Native)

**Available in Claude Code runtime:**
```bash
claude --worktree              # Session-level worktree isolation
claude --agent "name" -w       # Agent-level isolation
```

**Benefit:** Automatic collision prevention; Claude manages the git state

**Trade-off:** Limited to Claude Code sessions; doesn't work for external tools (n8n, Python scripts)

---

## Part 2e: Collision Conflict Resolution Matrix

| Scenario | Collision Type | Solution | Priority |
|----------|---|---|---|
| Two agents editing same PR branch | **Mutual exclusion** | PR branch lock + TTL | **HIGH** — implement first |
| Two agents in same worktree, same file | **Same-file conflict** | Serialize edits or split worktrees | **MEDIUM** — unlikely if lane ownership is clear |
| Generated artifacts (yarn.lock, requirements.txt) | **Artifact collision** | Worktree isolation or separate CI step | **MEDIUM** — automate via CI, not hand-edit |
| n8n and Python agent both patching same branch | **Tool collision** | Add n8n → Python lock coordination (webhook-based queue token) | **HIGH** — implement second |
| Human editing in IDE + agent auto-writing | **IDE/agent collision** | IDE-level `.git/index.lock` + sensible workflow (human edits don't commit; agent owns commits) | **LOW** — user behavior boundary |

---

## Part 2f: Current Status in .00_Governance

**Already implemented:**
- ✅ `.01_PDRs/scripts/lock_pr_branch.py` — ready to use
- ✅ `.03_Harness Governance/scripts/dispatch_queue.py` — queue-based dispatch
- ✅ `.agents/review-intake/` directory structure (missions, logs, queue)

**Needed:**
- ⚠️ **Directory:** `.00_PLANNING/locks/` — create and add `.gitkeep`
- ⚠️ **Integration:** Wire lock acquire/release into dispatcher workflow
- ⚠️ **Webhook coordination:** Add lock release trigger to n8n workflow completion or webhook handlers
- ⚠️ **Documentation:** `03_PLAYBOOKS/MULTI_SESSION_SAFETY.md` — operational runbook

---

## Part 3: Recommended Implementation Plan

### Phase 1: Gemini Billing Audit (1–2 hours)

**Deliverable:** `gemini-billing-audit.md` with findings

```
1. Inventory all GCP/Gemini configs in workspace
   - Search .env, settings.json, CloudCredentials files
   - Find any GCP_PROJECT_ID or GOOGLE_CLOUD_CREDENTIALS references
2. Clarify: Consumer account (no API charges) vs. Cloud project (API charges)
3. If Cloud project exists: Set GCP budget alerts ($0.01–$50/mo threshold)
4. Document current usage patterns: web-only vs. programmatic
5. Recommendation: Use Gemini Advanced web/NotebookLM for free; only route programmatic work to Cloud APIs behind a cost gate if needed
```

### Phase 2: PR Branch Locking Deployment (2–3 hours)

**Deliverables:**
- `.00_PLANNING/locks/` directory created
- `lock_pr_branch.py` tested on PR #1
- `.03_Harness Governance/orchestration/README.md` updated with lock instructions
- Integration test: Dispatcher acquires lock, applies changes, releases

**Test scenario:**
```
1. Start two dispatcher instances
2. First dispatcher in PR #1 acquires lock → succeeds
3. Second dispatcher attempts acquire on same PR → fails with "active_lock" message
4. First dispatcher releases lock
5. Second dispatcher acquires → succeeds
```

### Phase 3: Multi-Session Safety Playbook (2–3 hours)

**Deliverable:** `.03_Harness Governance/03_PLAYBOOKS/MULTI_SESSION_SAFETY.md`

**Contents:**
- Core rules (one agent per branch)
- Lock lifecycle (acquire → patch → release)
- Failure modes & recovery (stale lock, lock timeout, human intervention)
- IDE/CLI workflows: when to acquire, when agent owns commit
- Escalation path: if lock can't be released, manual admin unlock procedure

### Phase 4: n8n ↔ Python Dispatcher Coordination (3–4 hours)

**Goal:** When n8n workflow completes, it triggers Python dispatcher to release its lock

**Options:**
- Option A: n8n webhook triggers `lock_pr_branch.py release` at workflow end
- Option B: Python dispatcher polls n8n job status and auto-releases on completion
- Option C: Shared queue file (`next-work.queue.json`) tracks lock + job state atomically

**Recommendation:** Option C (already partially implemented via dispatch_queue.py)

---

## Part 4: File Checklist for Implementation

### Existing (Reference)
- [x] `C:\Users\kas41\chromatic-harness-v2\01_PROTOCOLS\CMP\CMP_SPEC.md`
- [x] `C:\Users\kas41\chromatic-harness-v2\01_PROTOCOLS\BEADS\BEADS_SPEC.md`
- [x] `.01_PDRs/scripts/lock_pr_branch.py`
- [x] `.03_Harness Governance/scripts/dispatch_queue.py`
- [x] `.agents/review-intake/next-work.queue.json`

### To Create / Update
- [ ] `.00_PLANNING/locks/.gitkeep`
- [ ] `.00_PLANNING/locks/schema.json` (lock file schema validator)
- [ ] `.03_Harness Governance/03_PLAYBOOKS/MULTI_SESSION_SAFETY.md`
- [ ] `.03_Harness Governance/orchestration/README.md` (add lock instructions)
- [ ] `gemini-billing-audit.md` (findings + recommendations)
- [ ] Update `README.md` → add "Multi-Session Safety" section with link to playbook

---

## Part 5: Quick-Reference Decision Tree

**Do I need a lock?**
```
Is this a write operation (commit/push)?
  ├─ YES → Acquire lock before mutation
  │        Are there other active agents on this branch?
  │        ├─ YES → Wait for their lock release (fail-fast or queue)
  │        └─ NO → Acquire, proceed
  └─ NO (read-only inspection) → No lock needed
```

**Which isolation pattern?**
```
Are multiple agents working on this task?
  ├─ Single agent → PR branch lock only
  ├─ Multiple agents, different files → PR branch lock + worktree/branch isolation
  └─ Multiple agents, same file → Serialize or abort (not recommended for concurrent edit)
```

**Am I in Claude Code or external tool?**
```
Claude Code IDE session?
  ├─ YES → Use native `--worktree` if available; fallback to PR branch lock
  └─ NO → Use PR branch lock + webhook coordination
```

---

## Next Steps

1. **Confirm Gemini billing status** — Are you using Cloud APIs or just consumer Gemini Advanced?
2. **Choose implementation priority** — Start with PR branch locking (highest ROI) or Gemini audit first?
3. **Ready to proceed?** — User confirms direction; agent creates implementation tickets (.beads/ or task list)

---

## Appendix: Reference Links

- **Gemini Advanced Help:** https://support.google.com/googleone/answer/14057962
- **Google Cloud Gemini API Pricing:** https://cloud.google.com/vertex-ai/pricing (Vertex AI embeddings + APIs)
- **NotebookLM:** https://notebooklm.google.com/ (built into Gemini Advanced)
- **Claude Code Worktree Docs:** Claude Code changelog 2.1.49+
- **Chromatic Harness Reference:** `C:\Users\kas41\chromatic-harness-v2\01_PROTOCOLS\`
