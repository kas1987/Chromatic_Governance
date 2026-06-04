# Chromatic Governance — Quick Reference Guide

## At a Glance

**Chromatic Governance** = AI agent safety + policy enforcement + multi-provider LLM orchestration

```
AGENT ACCESS → Broker → GitHub (with audit trail)
Reviews Queue → LangGraph + n8n → Dispatch → Multi-provider routing (T0-T4)
PDRs → Registry → Backlog → In-Process → Reviewed
```

---

## Four Main Domains

### 1. **PDR Pipeline** (.01_PDRs/)
Govern design/product decisions through structured records.

**Key files:**
- `PDR_REGISTRY.json` — Central registry (metadata, transitions, audit)
- `pdr_sync.py` — CLI to sync folder structure ↔ registry, promote phases
- Workflow: Backlog → In-Process → Completed → Reviewed → Archived

**When to use:** Document architecture decisions, design records, governance transitions.

---

### 2. **Plugin Families** (.02_Plugins/)
13 scoped, loadable plugin families (108 skills total).

**Key families:**
- `rpi` — Full RPI lifecycle (research → implementation → review)
- `security-family` — Trust boundaries, secrets, permissions
- `agent-governance-family` — Multi-agent delegation, conflict resolution
- `architecture-family` — ADRs, interfaces, migrations
- `qa-eval-family` — Testing, regressions, LLM evals

**When to use:** Load plugin family matching your domain to get 8-10 relevant coding skills.

---

### 3. **Harness Governance** (.03_Harness Governance/)
Orchestration, intake, dispatch, policy enforcement.

**Key subsystems:**
- `orchestration/` — LangGraph workflows + n8n integration + model router
- `broker/` — GitHub agent access with policies, audit trail
- `scripts/` — Test suites (pytest, PowerShell)
- `governance/` — Policy definitions, authority maps
- `03_PLAYBOOKS/` — Operational procedures (safety, recovery, rollback)
- `security/` — ABAC patterns, threat models

**When to use:** Set up multi-session coordination, dispatch workflows, agent access control.

---

### 4. **GitHub Integration** (.github/)
CI/CD workflows, governance templates, automation rules.

---

## Critical Reference Files (Root)

| File | Read First If… |
|------|---|
| `REPOSITORY_STRUCTURE_ANALYSIS.md` | You want full architecture overview |
| `multi-session-safety-and-gemini-billing.md` | Multiple agents might run simultaneously |
| `cross-provider-model-routing.md` | Routing decisions across T0-T4 providers |
| `gemini-billing-audit.md` | Concerned about unexpected API charges |
| `INFRASTRUCTURE_TEST_REPORT.md` | Validating provider endpoints |

---

## Common Tasks

### Task: Document a design decision
1. Create PDR file in `.01_PDRs/.01_Backlog/`
2. Run `python .01_PDRs/pdr_sync.py --add-file <path>`
3. File automatically added to `PDR_REGISTRY.json`

### Task: Load coding skills for a domain
1. Identify relevant plugin family (e.g., `qa-eval-family`)
2. Load `.02_Plugins/qa-eval-family` in VS Code
3. Skills appear in LM context

### Task: Set up multi-agent safety
1. Read `.03_Harness Governance/03_PLAYBOOKS/MULTI_SESSION_SAFETY.md`
2. Review lock schema: `.00_PLANNING/locks/pr_branch_lock.schema.json`
3. Integrate lock acquire/release into dispatcher (code snippet provided)

### Task: Validate infrastructure
```powershell
# Test all providers (T0-T4) and routing
.\test_infrastructure.ps1

# Test PDR sync and transitions
python .01_PDRs/pdr_sync.py --validate

# Test taxonomy graph
python taxonomy_sync.py --export json
```

### Task: Review/approve a PR
1. Broker checks permissions via `policy_engine.py`
2. Audit log records action immutably
3. Workflow approves if policy passes

---

## Data Model Overview

### PDR Registry
```json
{
  "pdrs": [
    {
      "id": "example-001",
      "title": "Agent Access Broker",
      "phase": "In-Process",        // Backlog, In-Process, Completed, Reviewed, Archived
      "owner": "user@example.com",
      "completion": 85,             // Percentage
      "acceptance_criteria": [...],
      "transitions": [              // Audit trail
        {"from": "Backlog", "to": "In-Process", "at": "2026-06-01", "by": "user@example.com", "reason": "Approved in standup"}
      ]
    }
  ]
}
```

### Taxonomy Graph
```json
{
  "nodes": [                   // Skills, providers, components
    {"id": "skill-routing", "type": "skill", "tier": "T1"},
    {"id": "provider-gemini", "type": "provider", "tier": "T3"}
  ],
  "edges": [                   // Relationships
    {"source": "skill-routing", "target": "provider-gemini", "relation": "routes_to"}
  ]
}
```

### Policy Rule (ABAC)
```yaml
- rule_id: "review-approval"
  effect: "allow"
  principal: "agent:reviewer"
  action: "approve:pr"
  resource: "repo:chromatic-governance"
  conditions:
    - "request.author != principal.id"  # Can't approve own PRs
    - "request.tests == 'passing'"       # Tests must pass
```

---

## Deployment & Safety

### Multi-Session Collision Detection
- **Lock file:** `.00_PLANNING/locks/<branch>.lock.json` (TTL = 24h by default)
- **Mechanism:** Dispatcher checks lock before allowing branch edit
- **Recovery:** Playbook in `03_PLAYBOOKS/MULTI_SESSION_SAFETY.md`

### Audit Trail
- **Location:** `broker/audit.log` (immutable)
- **Contents:** Every agent action (author, action, resource, result, timestamp)
- **Retention:** 1+ years (configurable)

### Testing Before Merge
```powershell
# Required before any PR merge
python -m pytest ".03_Harness Governance/scripts/tests/test_dispatch.py" -q
.\test_infrastructure.ps1
python .01_PDRs/pdr_sync.py --validate
```

---

## Permission Model (Least Privilege)

**Default:** Agent has NO permissions until explicitly granted.

**Granted via YAML profile:**
```yaml
agent: "reviewer-bot"
permissions:
  - action: "read:pr"
    resource: "repo:*"
  - action: "comment:pr"
    resource: "repo:chromatic-governance:pr:*"     # Scoped to repo + PR
  - action: "approve:pr"
    resource: "repo:chromatic-governance:pr:*"
    conditions:
      - "review.tests == 'passing'"                 # Conditional approval
```

---

## Troubleshooting

### Infrastructure tests fail
→ Check provider credentials in `.03_Harness Governance/config/`
→ Run individual provider tests before multi-provider tests
→ See `INFRASTRUCTURE_TEST_REPORT.md`

### PDR sync out of sync
→ Run `python .01_PDRs/pdr_sync.py --sync-all`
→ Check `PDR_REGISTRY.json` for conflicts
→ See `.01_PDRs/README.md` for state machine rules

### Multi-session collision
→ Check `.00_PLANNING/locks/` for stale locks
→ Run emergency unlock procedure in `03_PLAYBOOKS/MULTI_SESSION_SAFETY.md`
→ Verify no dispatcher processes are hanging

### Unexpected Gemini charges
→ Verify no long-lived API credentials in workspace
→ See `gemini-billing-audit.md` for audit findings
→ Check `.03_Harness Governance/config/` for keys (should be empty)

---

## Key Principles

1. **Policy as Code** — Rules enforced programmatically, not manual gates
2. **Audit Everything** — Immutable logs of all agent actions
3. **Least Privilege** — Agents start with no permissions
4. **Graceful Degradation** — System continues if optional components fail
5. **Safety First** — Multi-session collision detection, lock TTLs, recovery procedures
6. **Extensible** — Plugin architecture for domain-specific skills
7. **Validated** — Schema validators on all critical data structures

---

**Last Updated:** 2026-06-04
**For full details:** See [REPOSITORY_STRUCTURE_ANALYSIS.md](REPOSITORY_STRUCTURE_ANALYSIS.md)
