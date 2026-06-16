# Chromatic Governance

Chromatic Governance is a policy and orchestration repository for AI-assisted software delivery.

It contains:
- PDR artifacts and governance records
- plugin and skill governance toolchains
- workflow automation for intake, review, and promotion
- harness scripts for safe, auditable dispatch and execution
- Claude Code hook framework for multi-agent safety (PreToolUse guard, PostToolUse audit, SubagentStop swarm coordination)
- multi-provider LLM routing across Ollama local, Ollama Cloud, Featherless, and Gemini

## Repository Layout

- `.01_PDRs/` — product, design, and governance records
- `.02_Plugins/` — plugin families and validation tooling (13 families, 118 skills)
- `.03_Harness Governance/` — orchestration scripts, tests, and runtime controls
- `.agents/hooks/` — Claude Code hook scripts (guard, audit, snapshot, swarm coordination)
- `.claude/` — Claude Code settings (`settings.json` hooks) and the standalone provider route-selector CLI (`hooks/model-router.sh`, not a Claude hook)
- `.github/` — CI, governance workflows, templates, and automation rules

## Model Routing

Provider tiers (cost/latency ascending):
- **T0** Ollama local — `http://127.0.0.1:11434` — offline, free
- **T1** Ollama Cloud — `https://ollama.com/api` — subscription-backed cloud GPU
- **T2** Featherless — `https://api.featherless.ai/v1` — serverless open-model inference
- **T3** Gemini — high-quality cloud reasoning

See [cross-provider-model-routing.md](cross-provider-model-routing.md) for full routing policy.

## Hook Safety Framework

All agent operations are guarded by four Claude Code hooks:

| Hook event | Script | Purpose |
|---|---|---|
| PreToolUse | `pre_tool_guard.py` | Blocks destructive commands (force-push, --no-verify, DROP TABLE) |
| PostToolUse | `post_tool_audit.py` | Audit trail → `tool-audit.jsonl` |
| Stop | `context_snapshot.py` | Session context snapshot on agent stop |
| SubagentStop | `subagent_stop.py` | Swarm queue coordination |

Validate: `python .agents/hooks/validate_hooks.py` (23/23 checks)

## Local Validation

```powershell
# Governance check (16 files + hook wiring + taxonomy)
python .github/scripts/governance_check.py

# Hook framework validation (23 checks)
python .agents/hooks/validate_hooks.py

# PDR registry validation
python .01_PDRs/pdr_sync.py sync

# Full test suite
python -m pytest ".03_Harness Governance/scripts/tests/test_dispatch.py" -q
```

## Security and Reporting

- Review [SECURITY.md](SECURITY.md) for vulnerability reporting.
- Do not commit secrets, tokens, or private keys.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening pull requests.

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).
