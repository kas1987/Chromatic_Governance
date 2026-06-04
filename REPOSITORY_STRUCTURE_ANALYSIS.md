# Chromatic Governance Repository Structure & Analysis

**Generated:** 2026-06-04  
**Total Components:** 4 major subsystems + supporting infrastructure  
**Status:** Active governance & orchestration framework

---

## 1. Executive Overview

**Chromatic Governance** is a comprehensive policy and orchestration repository for AI-assisted software delivery. It provides:

- Safe, auditable AI agent access to GitHub repositories through a broker-based architecture
- Product/design record (PDR) pipeline for governing changes
- Extensible plugin families for coding workflows
- Multi-session safety controls and collision detection
- Orchestration, intake, and review automation
- Infrastructure testing and model routing for multi-provider LLM coordination

### Key Principle
> Policy enforcement through code, not manual review gates

---

## 2. Repository Layout & Major Components

### 2.1 `.01_PDRs/` — Product/Design Record Pipeline System

**Purpose:** Structured governance through design records following Backlog → In-Process → Reviewed → Archived workflow

**Structure:**
```
.01_PDRs/
├── .01_Backlog/          # Proposed, not yet prioritized
├── .03_In-Process/       # Actively being worked on
├── .99_Extracted/        # Extracted scaffold bundles from active work
├── PDR_REGISTRY.json     # Single source of truth (metadata, transitions, audit trail)
├── pdr_sync.py           # Automation: sync file system ↔ registry, promote between phases
├── ARTIFACT_TAXONOMY.json # Maps artifact types to governance rules
└── LANGGRAPH_DISPATCHER_SPEC.md  # Dispatcher workflow design
```

**Key Files:**
- **PDR_REGISTRY.json** — Central registry tracking:
  - PDR metadata (id, title, phase, owner, completion %)
  - Status & file location (synced with folder structure)
  - Transition history (when → who → why)
  - Acceptance criteria (gates for promotion)
  - Related issues/PRs (cross-repo links)

- **pdr_sync.py** — CLI tool for:
  - Syncing folder structure with registry
  - Promoting PDRs between phases
  - Audit trail reporting
  - Artifact validation

- **N8N_PHASE1_INTAKE_WORKFLOW_SPEC.md** — Defines intake automation in n8n
- **LANGGRAPH_DISPATCHER_SPEC.md** — Dispatcher workflow for multi-agent coordination

---

### 2.2 `.02_Plugins/` — Claude Code Plugin Families

**Purpose:** Scoped, loadable plugin families for domain-specific coding workflows

**13 Plugin Families** (Total: ~108 skills):

| Family | Skills | Purpose |
|--------|--------|---------|
| **rpi** | 16 | Research, planning, implementation, review, iteration lifecycle |
| **toolchain-family** | 8 | Infrastructure utilities, agent workspaces, repo operations |
| **context-family** | 9 | Context, memory, decision logs, session handoff |
| **security-family** | 8 | Secrets, trust boundaries, prompt injection, permission review |
| **architecture-family** | 8 | Architecture governance, ADRs, interfaces, technical debt |
| **qa-eval-family** | 8 | Testing, acceptance criteria, regression, LLM evals |
| **release-family** | 8 | Release planning, changelogs, deployment, rollback |
| **observability-family** | 9 | Logs, metrics, tracing, incidents, RCA, SLO checks |
| **agent-governance-family** | 10 | Multi-agent delegation, authority maps, conflict resolution |
| **docs-family** | 8 | README, API docs, runbooks, troubleshooting diagrams |
| **product-family** | 8 | Requirements, user stories, MVP planning, UX critique |
| **data-research-family** | 8 | Evidence gathering, benchmarks, API change watches |
| **frontend-family** | 10 | UI/UX delivery, CSS, dashboards, components, 3D assets |

**Key Feature:** Each plugin loads only when relevant, avoiding one monolithic toolkit.

---

### 2.3 `.03_Harness Governance/` — Infrastructure & Orchestration Control Plane

**Purpose:** Orchestration, intake, dispatch, and policy enforcement for AI agent workflows

**Subsystems:**

#### 2.3.1 **orchestration/** — Multi-provider LLM dispatch & workflow engine
- **langgraph/** — LangGraph-based workflow definitions
  - `review_dispatch_graph.py` — Review queue dispatch state machine
  - Lock-based multi-session collision safety
- **n8n/** — n8n (Make) integration layer
  - Workflow import/validation
  - Dispatch hooks to trigger jobs
- **model-router/** — Cross-provider model routing (T0→T4)
  - Ollama (T0 local) → Featherless (T1) → Gemini (T3) → Anthropic (T4)
  - Model availability and cost routing logic

#### 2.3.2 **broker/** — GitHub Agent Access Broker
- **src/policy_engine.py** — Policy evaluation for agent actions
- **src/audit_log.py** — Immutable audit trail for all agent operations
- **tests/** — Permission and policy validation tests
- **config/** — YAML-based permission profiles and rules

#### 2.3.3 **scripts/** — Validation, testing, automation
- Python test suites for dispatch, integration, and infrastructure
- `test_infrastructure.ps1` — PowerShell validation harness
- Hook scripts for pre-commit, pre-push validation

#### 2.3.4 **security/** — Trust boundary controls
- ABAC (Attribute-Based Access Control) patterns
- Threat models and risk matrices
- Least-privilege default permissions

#### 2.3.5 **governance/** — Policy and authority records
- Policy definitions for review gates, approval chains
- Authority mapping for role-based access

#### 2.3.6 **schemas/** — JSON schema validators
- Workflow schema validation
- Lock file schema (pr_branch_lock.schema.json)
- Message contract validation

#### 2.3.7 **03_PLAYBOOKS/** — Operational procedures
- **MULTI_SESSION_SAFETY.md** — Lock lifecycle, collision recovery
- Domain-specific playbooks for emergency procedures, rollback

#### 2.3.8 **config/** — Runtime configuration
- Provider credentials (T0-T4)
- Model availability matrices
- Routing decision parameters

---

### 2.4 `.github/` — CI/CD & GitHub Automation

**Standard location for:**
- Workflow automation (YAML)
- Governance templates
- PR automation and labeling rules
- Branch protection and merge strategies

---

### 2.5 Supporting Components

#### `.00_PLANNING/locks/`
- **pr_branch_lock.schema.json** — JSON schema for multi-session collision detection
- Lock file format definition for branch coordination

#### `.agents/`
- **hooks/** — Pre-commit, pre-push hooks for validation
- **logs/** — Test and execution logs (JSON timestamped format)
- **review-intake/** — Review queue staging area

#### `.claude/`
- Claude agent customization and instruction files
- Agent-specific configuration

#### Root Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Quick start and repository overview |
| `CONTRIBUTING.md` | Development flow, validation expectations, PR guidelines |
| `SECURITY.md` | Vulnerability reporting process |
| `CODE_OF_CONDUCT.md` | Community participation guidelines |
| `LICENSE` | MIT License |

#### Root Analysis & Reference Files

| File | Purpose |
|------|---------|
| `gemini-billing-audit.md` | Audit of Gemini API usage and $200 plan coverage |
| `multi-session-safety-and-gemini-billing.md` | Comprehensive reference on collision safety + billing |
| `cross-provider-model-routing.md` | Model routing strategy across T0-T4 providers |
| `gemini-vs-chatgpt-usage-guide.md` | Provider selection guidance |
| `model-effort-routing.csv` | Effort estimation by model tier |
| `cross-provider-model-routing.csv` | Routing decision matrix |
| `repos-cleanup-inventory.md` | Repository maintenance tracker |
| `vscode-extension-stack.md` | Extension ecosystem documentation |
| `INFRASTRUCTURE_TEST_REPORT.md` | Latest test results and validation |
| `ENCODING_FIXES_VERIFICATION.md` | UTF-8 encoding validation report |

#### Configuration & Data Files

| File | Purpose |
|------|---------|
| `.gitignore` | Git exclusion rules |
| `.gitleaks.toml` | Secret scanning configuration |
| `.markdownlint.json` | Markdown linting rules |
| `pytest.ini` | Python pytest configuration |
| `taxonomy.db` | SQLite graph database (11 nodes, 5 edges) |
| `taxonomy.json` | JSON export of taxonomy graph |
| `taxonomy_sync.py` | Synchronization tool for taxonomy ↔ database |

---

## 3. Data & Integration Flows

### 3.1 PDR Lifecycle Pipeline
```
Intake → Backlog → Pre-flight checks → In-Process → Completed → Review → Archived
         ↓                                    ↓
    pdr_zip_intake.py           pdr_sync.py (automation)
    Validation → Registry         File system ↔ Registry sync
```

### 3.2 Orchestration & Dispatch
```
Review Queue → LangGraph State → Dispatcher → n8n Job → Agent Execution → Audit Log
               Machine         (Python)      (Workflow)  (Multi-provider)
               ↓
           Lock Collision
           Detection (SQLite)
```

### 3.3 Multi-Provider LLM Routing
```
Input → Router (Effort/Cost/Availability) → Model Selection
        ↓
   Cross-provider matrix (CSV)
   Model routing rules
   Tier-based escalation (T0→T1→T3→T4)
```

---

## 4. Key Features & Governance Mechanisms

### 4.1 Safe Agent Access
- **GitHub App Integration** — Short-lived installation tokens (no long-lived PATs)
- **Least-Privilege Permissions** — YAML-based permission profiles
- **Broker Pattern** — All agent access flows through policy-enforcing broker
- **Audit Trail** — Immutable logging of all agent actions

### 4.2 Multi-Session Safety
- **Lock-based Collision Detection** — SQLite-backed branch locking with TTL
- **PR Branch Coordination** — Prevents simultaneous edits to same PR branch
- **Lock Recovery Procedures** — Operational playbooks for emergency unlock
- **Graceful Degradation** — System continues if lock mechanism unavailable

### 4.3 Policy & Governance
- **PDR Pipeline** — Design records flow through defined stages with acceptance criteria
- **Policy Engine** — Attribute-based access control (ABAC) for enforcement
- **Schema Validation** — JSON schema validators for all critical data structures
- **Audit Trail** — Complete transition history and decision logs

### 4.4 Multi-Provider LLM Coordination
- **Cross-Provider Routing** — Seamless fallback across Ollama (T0), Featherless (T1), Gemini (T3), Anthropic (T4)
- **Cost & Effort Optimization** — Routing decisions based on model tier and complexity
- **Infrastructure Testing** — Comprehensive test suite validating all provider endpoints
- **Taxonomy Graph** — Queryable SQLite database of skills, providers, and relationships

### 4.5 Extensible Workflows
- **Plugin Architecture** — 13 scoped plugin families (108 skills) load only when needed
- **LangGraph State Machines** — Complex workflows defined as declarative state graphs
- **n8n Integration** — No-code orchestration layer for business logic
- **Webhook Hooks** — Pre-commit, pre-push validation gates

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | LangGraph, Python | Stateful workflow execution with collision detection |
| **Workflow Automation** | n8n (Make) | No-code business logic and integrations |
| **Agent Access** | GitHub App, GitHub API | Safe, audited repository access |
| **Policy Engine** | Python ABAC | Attribute-based access control |
| **Data Storage** | SQLite | Taxonomy graph, lock coordination, audit logs |
| **Configuration** | YAML | Permission profiles, routing rules |
| **Testing** | pytest, PowerShell | Infrastructure and integration validation |
| **CI/CD** | GitHub Actions | Automated workflows and gates |
| **Documentation** | Markdown | Runbooks, playbooks, design records |

---

## 6. Development & Validation

### 6.1 Local Validation
```powershell
# Test dispatch orchestration
python -m pytest ".03_Harness Governance/scripts/tests/test_dispatch.py" -q

# Test infrastructure (multi-provider endpoints)
.\test_infrastructure.ps1

# Sync PDR registry
python .01_PDRs/pdr_sync.py --promote

# Validate taxonomy
python taxonomy_sync.py --export json
```

### 6.2 Merge Checklist (from CONTRIBUTING.md)
- [ ] Issue linkage documented
- [ ] Tests or validation updated
- [ ] No credentials committed
- [ ] Changes are scoped and auditable
- [ ] Related PDR entries updated
- [ ] Risk and rollback notes included

---

## 7. Security & Compliance

### 7.1 Trust Boundaries
- **Agent Isolation** — Agents run in sandboxed mode, access mediated by broker
- **Credential Management** — No secrets in repo (`.gitignore`, `.gitleaks.toml`)
- **Audit Trail** — All agent actions logged immutably
- **Least Privilege** — Granular permission profiles per agent/action

### 7.2 Vulnerability Reporting
- Private disclosure via GitHub Security Advisories
- No public disclosure until fix/mitigation published
- See [SECURITY.md](SECURITY.md) for details

---

## 8. Notable Recent Work

### 8.1 Gemini Billing & Multi-Session Safety (2026-06-04)
- **Audit Result:** Zero active Google Cloud API credentials → zero surprise Cloud billing
- **Safe to use:** $200 Gemini plan covers Advanced + NotebookLM (no API charges)
- **Reference:** `multi-session-safety-and-gemini-billing.md`
- **Implementation:** Lock schema + playbook for multi-agent collision prevention

### 8.2 Encoding Fixes (2026-06-04)
- **Issue:** Unicode/UTF-8 errors in test infrastructure
- **Fix:** Added explicit UTF-8 encoding to Python file I/O and PowerShell Out-File
- **Result:** All test suites now handle international characters correctly
- **Details:** `ENCODING_FIXES_VERIFICATION.md`

### 8.3 Cross-Provider Model Routing (Ongoing)
- **Goal:** Seamless escalation T0 (local) → T1 (API) → T3 (Gemini) → T4 (Anthropic)
- **Mechanism:** Cost/effort-based routing decisions stored in CSV matrices
- **Integration:** Wired into orchestration layer and model router

---

## 9. Recommended Next Steps

1. **Review Safety Playbook** — familiarize with multi-session collision procedures
2. **Run Infrastructure Tests** — validate all provider endpoints are responsive
3. **Explore Plugin Families** — load only the domains relevant to current work
4. **Audit Recent Changes** — use Git history to understand recent additions
5. **Validate Local Setup** — run pytest and PowerShell test suites
6. **Review PDR Registry** — understand current work in the pipeline

---

## 10. Key References

| Reference | Location |
|-----------|----------|
| Contributing guidelines | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security reporting | [SECURITY.md](SECURITY.md) |
| Code of conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| GitHub agent access | [.03_Harness Governance/README.md](.03_Harness%20Governance/README.md) |
| Plugin families | [.02_Plugins/README.md](.02_Plugins/README.md) |
| PDR pipeline | [.01_PDRs/README.md](.01_PDRs/README.md) |
| Multi-session safety | [multi-session-safety-and-gemini-billing.md](multi-session-safety-and-gemini-billing.md) |
| Model routing | [cross-provider-model-routing.md](cross-provider-model-routing.md) |

---

**Document Generated:** 2026-06-04 @ 21:30 UTC
