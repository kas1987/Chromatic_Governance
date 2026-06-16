# PDR-007: Test Coverage Improvements

## Status
Implemented — all gaps resolved, merged to `claude/test-coverage-analysis-U1oaV`

## Date
2026-06-05

## Owner
Kris Sayresmith / Poly-Chromatic

---

## Executive Summary

A coverage audit identified six meaningful gaps in the existing test suite: an entire untested module (`lock_pr_branch.py`), two `main()` functions that were proxied rather than exercised (`log_resolution`, `dispatch_queue`), a stub class with no pinned contract (`token_issuer`), an untested subprocess integration (`acquire_branch_lock`), and four security-sensitive agent hooks with no test infrastructure at all. This PDR tracks the work to close those gaps.

---

## Problem Statement

- `lock_pr_branch.py` had zero tests — the TTL expiry path and the exit-code-2 collision mechanism (the safety guardrail preventing double-dispatch) were completely unverified.
- `test_dispatch.py` and `test_dispatch.py::TestLogResolution` replicated logic manually instead of calling `main()`, leaving `argparse` integration and several CLI branches uncovered (`--item`, `--force`, `--status`, `--max`, queue persistence to disk).
- `token_issuer.GitHubAppTokenIssuer` had no tests; a future implementer could accidentally call the stub in production.
- `acquire_branch_lock()` in `dispatch_queue.py` was always monkeypatched away — the actual subprocess path and OSError fallback were never exercised.
- The four agent hooks (`pre_tool_guard`, `post_tool_audit`, `context_snapshot`, `subagent_stop`) were entirely absent from the coverage scan. `pre_tool_guard` in particular enforces security policy for the entire agent swarm — its block/allow logic had no regression protection.

---

## What Was Added

### New Test Files

| File | Source Under Test | New Tests |
|---|---|---|
| `.03_Harness Governance/scripts/tests/test_lock_pr_branch.py` | `lock_pr_branch.py` | 16 |
| `.03_Harness Governance/scripts/tests/test_log_resolution_main.py` | `log_resolution.py` | 14 |
| `.03_Harness Governance/scripts/tests/test_dispatch_main.py` | `dispatch_queue.py` | 18 |
| `.03_Harness Governance/broker/tests/test_token_issuer.py` | `token_issuer.py` | 8 |
| `.agents/hooks/tests/test_pre_tool_guard.py` | `pre_tool_guard.py` | 18 |
| `.agents/hooks/tests/test_post_tool_audit.py` | `post_tool_audit.py` | 10 |
| `.agents/hooks/tests/test_context_snapshot.py` | `context_snapshot.py` | 11 |
| `.agents/hooks/tests/test_subagent_stop.py` | `subagent_stop.py` | 13 |
| `.agents/hooks/tests/conftest.py` | (path setup) | — |

**Total new tests: ~108**

### Updated Configuration

| File | Change |
|---|---|
| `.03_Harness Governance/pytest.ini` | Added `../../.agents/hooks/tests` to `testpaths`; added `--cov=../../.agents/hooks` |

---

## Coverage Detail by Module

### `lock_pr_branch.py` — new full coverage

| Branch | What is tested |
|---|---|
| `lock_path()` | Slash-to-double-underscore, lives in lock_dir, different PRs produce different paths |
| `acquire` | Creates file, content shape (all fields), active lock returns exit 2, expired lock re-acquired, TTL stored correctly, lock_id format |
| `release` | Removes file, harmless when no lock exists, subsequent acquire succeeds |
| `status` | Prints "unlocked" when no lock, prints JSON content when locked |

### `log_resolution.py` — `main()` now called directly

| Branch | What is tested |
|---|---|
| `resolved` status | JSONL record fields, queue item set to `done`, `resolved_at` timestamp |
| `blocked` status | Queue item set to `blocked` |
| `needs-clarification` status | Queue item status preserved exactly |
| Task not found | Queue file unchanged |
| Missing queue file | No error, JSONL still written |
| Empty queue file | No error |
| Nested log directories | Created automatically |
| `--validation` / `--files` | Multi-value args stored in record |

### `dispatch_queue.py` — `main()` and `acquire_branch_lock()` now covered

| Branch | What is tested |
|---|---|
| `--item` not found | Returns 1 |
| `--item` in human-gate status without `--force` | Returns 1 |
| `--item` with `--force` | Dispatches, writes mission file |
| `--status` flag | Prints JSON counts, exits 0 |
| `--max N` | Limits dispatched items; highest-priority item wins |
| `--dry-run` | No mission files, no queue mutation |
| Queue persistence | Items transition to `in-progress`, `dispatched_at` and `dispatch_id` written |
| `acquire_branch_lock` success | Lock file created at correct path |
| `acquire_branch_lock` no PR number | Returns `True` immediately |
| `acquire_branch_lock` active lock | Returns `False` |
| `acquire_branch_lock` OSError | Returns `False` gracefully |

### `token_issuer.py` — stub contract pinned

Constructor stores `app_id`, `private_key_path`, and `api_version`; `issue_token()` raises `NotImplementedError` with a message that references the intended implementation.

### `pre_tool_guard.py` — security policy fully covered

All 8 destructive patterns tested (`--force`, `-f`, `--hard`, `-D`, root `rm`, `DROP TABLE`, `--no-verify` on push and commit), plus protected-branch push to `main`/`master`. `main()` tested for non-shell tools (pass-through), blocked commands (exit 2, BLOCKED in stderr), allowed commands (exit 0), empty stdin, invalid JSON, empty command, all shell tool aliases, and `cmd` key in `tool_input`.

### `post_tool_audit.py` — audit record and truncation covered

`_summarize()` tested for short responses, large-tool truncation, non-large tools, and dict serialization. `main()` tested for record content, append behaviour, large-response truncation in log, agent ID from env, and invalid JSON resilience.

### `context_snapshot.py` — threshold logic and snapshot record covered

All 10 `_status()` threshold boundaries parametrized. `main()` tested for full usage payload, zero tokens (`unknown`), critical/green status labels, invalid JSON, agent ID, task ID, `total_tokens` fallback, and append behaviour.

### `subagent_stop.py` — queue advancement and completion log covered

`_load_json()` tested for missing file, malformed JSON, and valid data. `_update_queue_item()` tested for in-progress→needs-review advancement, non-matching item, non-in-progress status, and missing queue file. `main()` tested for completion record fields, token counting, `CHROMATIC_TASK_ID` queue advancement, no-task-id path, `total_tokens` fallback, append behaviour, agent ID, and invalid JSON resilience.

---

## Test Isolation Technique for Agent Hooks

The hooks derive their log and queue paths from `Path(__file__).resolve().parents[N]`. Rather than patching `pathlib.Path` globally, tests monkeypatch the module-level `__file__` attribute to a path inside `tmp_path` structured as `tmp_path/.agents/hooks/<hook>.py`. This makes `parents[2]` resolve to `tmp_path`, redirecting all file I/O to the pytest temp directory with no changes to source files.

---

## Acceptance Criteria

- [x] All 8 new test files pass with `pytest` from `.03_Harness Governance/`
- [x] `lock_pr_branch.py` TTL expiry and collision (exit 2) paths covered
- [x] `log_resolution.main()` and `dispatch_queue.main()` called directly in tests
- [x] `token_issuer.issue_token()` `NotImplementedError` assertion present
- [x] `acquire_branch_lock()` subprocess integration and OSError fallback tested
- [x] All four agent hooks included in pytest coverage scan
- [x] `pre_tool_guard.check_command()` covers all 8 destructive patterns

---

## References

- `.03_Harness Governance/pytest.ini` — test runner configuration
- PDR-004 — review intake system (source of `lock_pr_branch`, `dispatch_queue`, `log_resolution`)
- `.agents/hooks/` — agent swarm security hooks
