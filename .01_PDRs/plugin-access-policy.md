# plugin-access-policy.md: Broker Profile to Plugin Family Access Mapping

Defines which plugin families an agent may load based on its broker permission profile. This policy maps the Chromatic broker authorization plane to the skill ecosystem access control plane.

---

## Broker Profile Access Map

### read_only
**Description**: Read-only access. No commits, no CI/CD invocation.

**Allowed Families**:
- `context-family` — Session context monitoring, token budgeting
- `data-research-family` — Web search, knowledge base queries, data extraction
- `docs-family` — Documentation reading, navigation, cross-repo docs lookup
- `observability-family` — Logging, metrics, status checks (read-only)

**Rationale**: These families pose no mutation risk. A read-only agent gathers information, observes system state, and extracts knowledge without altering code or CI/CD state.

**Example Invocations**:
- `search_skills("token budget")` → context-family
- `search_skills("web search")` → data-research-family
- `list_skills("docs-family")` → docs-family

---

### issue_triage
**Description**: Read-only + issue triage. Can label, comment, assign issues but not commit code.

**Allowed Families**:
- All from `read_only`
- `product-family` — Issue templating, roadmap operations, feature flag management
- `agent-governance-family` — Agent dispatch, skill loading governance, session lifecycle

**Rationale**: Triage agents need to understand product context and coordinate with other agents. No code mutation is allowed.

**Example Invocations**:
- `get_skill("issue-classifier")` → product-family
- `get_skill("agent-dispatcher")` → agent-governance-family

---

### patch_standard
**Description**: Patch-level commits, full CI/CD. Can commit code, trigger workflows, deploy.

**Allowed Families**:
- All from `issue_triage`
- `rpi` — Repository information and PR metadata
- `architecture-family` — Component design, refactoring decisions, module organization
- `qa-eval-family` — Test generation, coverage analysis, quality gates
- `release-family` — Version management, changelog, release coordination
- `toolchain-family` — Build, lint, format, test runners, shell automation

**Rationale**: Standard patch agents need the full toolkit to implement features, run tests, and push to main. Elevated privileges are justified by comprehensive governance checks (CI, code review, pre-commit hooks).

**Example Invocations**:
- `list_skills("qa-eval-family")` → qa-eval-family
- `get_skill("run-test-suite")` → toolchain-family

---

### cleanup_limited
**Description**: Limited cleanup. Can fix build failures, update deps, refactor. No new features.

**Allowed Families**:
- `rpi` — Repository information
- `docs-family` — Documentation fixes
- `toolchain-family` — Build/lint/format fixes
- `context-family` — Context monitoring

**Rationale**: Cleanup agents are scoped to maintenance tasks. They can fix broken builds and update infrastructure but cannot implement features (which require design review). Restricted from product and governance families.

**Example Invocations**:
- `search_skills("format code")` → toolchain-family
- `get_skill("dependency-updater")` → toolchain-family

---

## Enforcement & Verification

1. **At MCP Server Invocation**: The MCP `get_skill()`, `list_skills()`, and `search_skills()` tools check the caller's broker profile (passed via MCP context or environment) and return only allowed families.

2. **In CLI**: The `search-skills.py` CLI wrapper accepts `--profile <profile>` to scope results.

3. **In CI/CD**: The `skill-governance.yml` workflow validates that PR author's broker profile matches family membership of skills modified.

4. **No Bypass**: The policy is enforced at the tool boundary, not by agent self-discipline.

---

## Broker Profile Semantics (Authz Model)

| Profile | Description | Scope | Code Mutation | CI/CD | Vault Access |
|---|---|---|---|---|---|
| `read_only` | Observer, telemetry | Information gathering | ❌ No | ❌ No | ❌ No |
| `issue_triage` | Triage coordinator | Issue/label management | ❌ No | ❌ No | ❌ No |
| `patch_standard` | Feature developer | Full dev-to-prod cycle | ✅ Yes | ✅ Yes | ⚠️ Limited |
| `cleanup_limited` | Maintenance drone | Broken build fixes, refactoring | ✅ Yes (limited) | ⚠️ Certain workflows only | ❌ No |

---

## Policy Updates

This policy document is **additive** — it does not override `permission_profiles.yaml` or other broker configs. It is the authoritative map between broker profiles and plugin families. Updates to either broker profiles or plugin families require:

1. Update this document.
2. Update the MCP server enforcement code (if enforcement logic changes).
3. Notify all agents via AGENT_GUIDE.md changelog.

---

## Related Documents

- `SKILL_BRIDGE.md` — Poly-Chromatic operating skills to plugin family mapping
- `SKILL_TAXONOMY.md` — Full plugin family definitions and trigger rules
- `AGENT_GUIDE.md` — Agent-level skill loading guidance
- `permission_profiles.yaml` — Broker profile definitions (Chromatic harness config)

---

## Quick Reference

```
read_only
├── context-family
├── data-research-family
├── docs-family
└── observability-family

issue_triage (read_only + )
├── product-family
└── agent-governance-family

patch_standard (issue_triage + )
├── rpi
├── architecture-family
├── qa-eval-family
├── release-family
└── toolchain-family

cleanup_limited
├── rpi
├── docs-family
├── toolchain-family
└── context-family
```
