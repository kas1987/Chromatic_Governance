# SKILL_BRIDGE.md: Poly-Chromatic Operating Skills to Plugin Families

Maps 12 Poly-Chromatic operating skills (ChatGPT native tools) to nearest plugin-family equivalents. Both systems coexist; this bridge clarifies activation, relationship, and when to use each.

---

## Bridge Map

| Operating Skill | Plugin Family Equivalent | Relationship | Use Operating When | Use Plugin When |
|---|---|---|---|---|
| summarize-document | docs-family / data-research-family | Equivalent | ChatGPT native summarization, real-time streaming | Chromatic agent batch processing, taxonomy-driven docs lookup |
| extract-metadata | data-research-family / docs-family | Equivalent | ChatGPT real-time metadata pull | Chromatic agent metadata-first discovery |
| search-knowledge-base | context-family / data-research-family | Partial overlap | ChatGPT internal knowledge search | Chromatic agent cross-repo search via MCP |
| validate-json-schema | toolchain-family / qa-eval-family | Equivalent | ChatGPT inline schema validation | Chromatic agent bulk validation + CI gate |
| generate-test-cases | qa-eval-family / toolchain-family | Equivalent | ChatGPT exploratory test generation | Chromatic agent template-driven test suite generation |
| invoke-webhook | release-family / toolchain-family | Equivalent | ChatGPT CI/CD event dispatch | Chromatic agent release pipeline orchestration |
| track-issue-state | product-family / agent-governance-family | Partial overlap | ChatGPT real-time issue polling | Chromatic agent batch issue triage + dispatch |
| list-repo-files | context-family / docs-family | Equivalent | ChatGPT directory tree (limited depth) | Chromatic agent full file inventory via MCP + CLI |
| read-file-by-path | context-family | Equivalent | ChatGPT small file reads | Chromatic agent large file streaming + pagination |
| write-file-to-repo | toolchain-family / architecture-family | Equivalent | ChatGPT direct commit (requires auth) | Chromatic agent pre-commit validation + hook enforcement |
| run-shell-command | toolchain-family / observability-family | Equivalent | ChatGPT interactive shell (one-shot) | Chromatic agent bash/ps driver with state persistence |
| query-sql-database | data-research-family | Equivalent | ChatGPT direct SQL (read-only) | Chromatic agent SQLite + query caching |

---

## Relationship Types

- **Equivalent**: Operating skill and plugin family serve the same function. Use operating skill in ChatGPT, plugin skill in Chromatic agent.
- **Partial overlap**: Operating skill covers 60-80% of plugin family use cases. Some plugin features have no operating equivalent.
- **Gap**: Operating skill has no plugin equivalent (none in this bridge map).

---

## Activation & Governance

| System | Activation | Governance | Session Scope |
|---|---|---|---|
| Poly-Chromatic Operating Skills | ChatGPT native tool invocation | Broker permission profiles + ChatGPT plugin manifest | Single ChatGPT session |
| Chromatic Plugin Families | MCP tool call (via Claude Code or LLM IDE) | Broker profiles × plugin-access-policy.md mapping | Cross-session via MCP or CLI |

---

## When to Use Operating vs. Plugin

### Use Operating Skills When:
- Agent is ChatGPT native and has no Chromatic harness.
- One-shot invocation (no state persistence needed).
- Real-time knowledge base search (ChatGPT's training cutoff + plugins).

### Use Plugin Skills When:
- Agent runs in Claude Code or Chromatic harness.
- Multi-step workflow with state persistence.
- Cross-session skill composition.
- Auditable invocation logging needed.

---

## Integration Notes

1. **No Migration**: Operating skills remain in ChatGPT plugin system. This map is documentation-only.
2. **No Conflict**: The two systems run in different runtimes (ChatGPT vs. Chromatic). No deprecation of either is planned.
3. **Handoff**: When handing off from ChatGPT to Chromatic agent, use this map to find the plugin family equivalent and invoke via MCP.
4. **Reference**: Link this doc from `AGENT_GUIDE.md` and `SKILL_TAXONOMY.md` for discoverable cross-system guidance.

---

## Related Documents

- `SKILL_TAXONOMY.md` — Plugin family membership and trigger rules
- `AGENT_GUIDE.md` — When to load which family
- `plugin-access-policy.md` — Broker profile to plugin family access mapping
