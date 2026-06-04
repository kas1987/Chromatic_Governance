"""Hook audit validation suite."""
import json
import pathlib
import subprocess
import sys

results = []

# 1. settings.json wiring
s = json.loads(pathlib.Path(".claude/settings.json").read_text(encoding="utf-8"))
events = list(s["hooks"].keys())

# Derive the interpreter from the wired command so this suite tests exactly what
# Claude Code will run (e.g. "py -3"), instead of hardcoding "python" and giving
# a false pass on a box where the live hooks would fail to launch.
_cmd = s["hooks"]["PreToolUse"][0]["hooks"][0]["command"].split()
PY = []
for _tok in _cmd:
    # Stop at the script path token (handles bare, quoted, and
    # $CLAUDE_PROJECT_DIR-anchored forms like "...pre_tool_guard.py").
    if ".py" in _tok:
        break
    PY.append(_tok)
if not PY:
    PY = ["python"]
for e in ["PreToolUse", "PostToolUse", "Stop", "SubagentStop"]:
    results.append(("settings:" + e, e in events))

# 2. Script syntax check
import ast

for f in ["pre_tool_guard.py", "post_tool_audit.py", "subagent_stop.py", "context_snapshot.py"]:
    try:
        ast.parse(pathlib.Path(f".agents/hooks/{f}").read_text(encoding="utf-8"))
        results.append(("syntax:" + f, True))
    except SyntaxError:
        results.append(("syntax:" + f, False))

# 3. Guard: block Main push (exit 2)
r = subprocess.run(
    [*PY, ".agents/hooks/pre_tool_guard.py"],
    input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push origin Main"}, "session_id": "t"}),
    text=True, capture_output=True,
)
results.append(("guard:block_main_push", r.returncode == 2))

# 4. Guard: allow git status (exit 0)
r = subprocess.run(
    [*PY, ".agents/hooks/pre_tool_guard.py"],
    input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}, "session_id": "t"}),
    text=True, capture_output=True,
)
results.append(("guard:allow_status", r.returncode == 0))

# 5. Guard: block --force push (exit 2)
r = subprocess.run(
    [*PY, ".agents/hooks/pre_tool_guard.py"],
    input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push --force origin feat"}, "session_id": "t"}),
    text=True, capture_output=True,
)
results.append(("guard:block_force", r.returncode == 2))

# 6. Guard: block --no-verify (exit 2)
r = subprocess.run(
    [*PY, ".agents/hooks/pre_tool_guard.py"],
    input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit --no-verify -m x"}, "session_id": "t"}),
    text=True, capture_output=True,
)
results.append(("guard:block_no_verify", r.returncode == 2))

# 7. Guard: non-Bash tool skipped (exit 0)
r = subprocess.run(
    [*PY, ".agents/hooks/pre_tool_guard.py"],
    input=json.dumps({"tool_name": "Read", "tool_input": {"path": "README.md"}, "session_id": "t"}),
    text=True, capture_output=True,
)
results.append(("guard:skip_non_bash", r.returncode == 0))

# 8. post_tool_audit: always exits 0
r = subprocess.run(
    [*PY, ".agents/hooks/post_tool_audit.py"],
    input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}, "session_id": "t"}),
    text=True, capture_output=True,
)
results.append(("post_audit:exit0", r.returncode == 0))

# 9. subagent_stop: exits 0
r = subprocess.run(
    [*PY, ".agents/hooks/subagent_stop.py"],
    input=json.dumps({"session_id": "t", "model": "claude", "usage": {}}),
    text=True, capture_output=True,
)
results.append(("subagent_stop:exit0", r.returncode == 0))

# 10. context_snapshot: exits 0 and writes log
r = subprocess.run(
    [*PY, ".agents/hooks/context_snapshot.py"],
    input=json.dumps({"session_id": "validation-run", "model": "test"}),
    text=True, capture_output=True,
)
results.append(("context_snapshot:exit0", r.returncode == 0))
results.append(("context_snapshot:log_written", pathlib.Path(".agents/logs/context-usage.jsonl").exists()))

# 11. context_snapshot log has agent_id field
if pathlib.Path(".agents/logs/context-usage.jsonl").exists():
    last_line = pathlib.Path(".agents/logs/context-usage.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
    entry = json.loads(last_line)
    results.append(("context_snapshot:has_agent_id", "agent_id" in entry))
else:
    results.append(("context_snapshot:has_agent_id", False))

# 12. tool-guard log written by guard block tests
results.append(("guard:log_written", pathlib.Path(".agents/logs/tool-guard.jsonl").exists()))

# 13. subagent completions log written
results.append(("subagent_stop:log_written", pathlib.Path(".agents/logs/subagent-completions.jsonl").exists()))

# 14. governance_check passes
r = subprocess.run([*PY, ".github/scripts/governance_check.py"], text=True, capture_output=True)
results.append(("governance_check:pass", r.returncode == 0))
if r.returncode != 0:
    print("governance_check output:", r.stdout, r.stderr)

# 15. pre-push hook: graceful fallback present
pp = pathlib.Path(".git/hooks/pre-push").read_text(encoding="utf-8")
results.append(("pre_push:graceful_fallback", "continuing" in pp))
results.append(("pre_push:protected_branch_guard", "PROTECTED_BRANCHES" in pp))

passed = sum(1 for _, v in results if v)
total = len(results)
print(f"\nResults: {passed}/{total} passed\n")
for name, ok in results:
    marker = "OK  " if ok else "FAIL"
    print(f"  {marker} {name}")

sys.exit(0 if passed == total else 1)
