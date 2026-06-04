"""Tests for parse_repo_pdr.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path so parse_repo_pdr can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Also add skill scripts dir where the canonical copy lives
sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[3]
        / ".02_Plugins"
        / "agent-governance-family"
        / "skills"
        / "repo-pdr-swarm-router"
        / "scripts"
    ),
)

import parse_repo_pdr as prp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

class TestClassify:
    def test_governance_keyword_gives_source_of_truth(self, tmp_path):
        p = tmp_path / "gov.md"
        cls = prp.classify(p, "this is a governance standard for chromatic_trees")
        assert cls == "source-of-truth"

    def test_pdr_keyword_gives_design_record(self, tmp_path):
        p = tmp_path / "PDR-001.md"
        cls = prp.classify(p, "This is a design record and architecture decision")
        assert cls == "design-record"

    def test_script_path_with_no_keywords_gives_implementation_target(self, tmp_path):
        p = tmp_path / "main.py"
        cls = prp.classify(p, "x = 1 + 2")
        assert cls == "implementation-target"

    def test_unknown_extension_binary_like_gives_asset(self):
        # Use a plain path with no keywords so all scores are 0
        p = Path("/fake/root/icon.png")
        cls = prp.classify(p, "")
        assert cls == "asset"

    def test_requirement_keywords(self, tmp_path):
        p = tmp_path / "reqs.md"
        cls = prp.classify(p, "The system must satisfy these requirements and acceptance criteria")
        assert cls == "requirement"

    def test_queue_keywords(self, tmp_path):
        p = tmp_path / "backlog.md"
        cls = prp.classify(p, "This is a task backlog and roadmap queue")
        assert cls == "queue-source"

    def test_memory_keywords(self, tmp_path):
        p = tmp_path / "changelog.md"
        cls = prp.classify(p, "memory and learning from previous changelog entries")
        assert cls == "memory"


# ---------------------------------------------------------------------------
# route
# ---------------------------------------------------------------------------

class TestRoute:
    def test_security_routes_to_sentinel(self, tmp_path):
        p = tmp_path / "sec.md"
        role = prp.route(p, "security bug failure lint coverage test")
        assert role == "sentinel"

    def test_governance_routes_to_auditor(self, tmp_path):
        p = tmp_path / "audit.md"
        role = prp.route(p, "governance audit risk compliance acceptance evidence")
        assert role == "auditor"

    def test_blocked_routes_to_chainbreaker(self, tmp_path):
        p = tmp_path / "blocker.md"
        role = prp.route(p, "blocked dependency ambiguous unknown todo")
        assert role == "chainbreaker"

    def test_tree_routes_to_cartographer(self, tmp_path):
        p = tmp_path / "tree.md"
        role = prp.route(p, "tree folder path repo structure worktree")
        assert role == "cartographer"

    def test_empty_content_falls_back_to_auditor(self):
        # Use a path with no role keywords; empty text → auditor fallback
        p = Path("/fake/root/notes.md")
        role = prp.route(p, "")
        assert role == "auditor"


# ---------------------------------------------------------------------------
# extract_headings
# ---------------------------------------------------------------------------

class TestExtractHeadings:
    def test_extracts_h1_and_h2(self):
        text = "# Title\n## Section\nsome body\n### Sub"
        headings = prp.extract_headings(text)
        assert "Title" in headings
        assert "Section" in headings
        assert "Sub" in headings

    def test_no_headings_returns_empty(self):
        assert prp.extract_headings("just text\nno headings here") == []

    def test_limit_to_25_headings(self):
        lines = [f"# Heading {i}" for i in range(50)]
        headings = prp.extract_headings("\n".join(lines))
        assert len(headings) == 25


# ---------------------------------------------------------------------------
# extract_actions
# ---------------------------------------------------------------------------

class TestExtractActions:
    def test_todo_extracted(self):
        actions = prp.extract_actions("TODO: implement the feature handler")
        assert len(actions) == 1
        assert "implement the feature handler" in actions[0]

    def test_checkbox_extracted(self):
        actions = prp.extract_actions("- [ ] run the test suite against main")
        assert any("run the test suite" in a for a in actions)

    def test_short_items_skipped(self):
        actions = prp.extract_actions("TODO: fix\n- [ ] ok")
        # "fix" and "ok" are < 8 chars, should be excluded
        assert all(len(a) >= 8 for a in actions)

    def test_limit_to_30_actions(self):
        lines = [f"- [ ] do something meaningful with item {i}" for i in range(50)]
        actions = prp.extract_actions("\n".join(lines))
        assert len(actions) == 30


# ---------------------------------------------------------------------------
# priority_for
# ---------------------------------------------------------------------------

class TestPriorityFor:
    def test_security_keyword_gives_p0(self):
        assert prp.priority_for("sentinel", "implementation-target", "fix security token exposure") == "P0"

    def test_source_of_truth_gives_p1(self):
        # action must not contain P0 trigger words (security/secret/token/router/blocked)
        assert prp.priority_for("archivist", "source-of-truth", "review the standard doc") == "P1"

    def test_sentinel_gives_p2(self):
        assert prp.priority_for("sentinel", "implementation-target", "add more coverage to tests") == "P2"

    def test_default_gives_p3(self):
        assert prp.priority_for("janitor", "evidence", "clean up old screenshots") == "P3"

    def test_router_keyword_gives_p0(self):
        assert prp.priority_for("auditor", "design-record", "router configuration must be updated") == "P0"

    def test_blocked_gives_p0(self):
        assert prp.priority_for("chainbreaker", "queue-source", "blocked by upstream dependency") == "P0"


# ---------------------------------------------------------------------------
# iter_files
# ---------------------------------------------------------------------------

class TestIterFiles:
    def test_ignores_git(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("ignored")
        (tmp_path / "real.py").write_text("x = 1")
        files = list(prp.iter_files(tmp_path))
        paths = [f.name for f in files]
        assert "config" not in paths
        assert "real.py" in paths

    def test_ignores_pycache(self, tmp_path):
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "mod.pyc").write_bytes(b"")
        (tmp_path / "mod.py").write_text("pass")
        files = list(prp.iter_files(tmp_path))
        assert not any(f.name == "mod.pyc" for f in files)

    def test_traverses_nested(self, tmp_path):
        (tmp_path / "sub" / "deep").mkdir(parents=True)
        (tmp_path / "sub" / "deep" / "file.md").write_text("# hello")
        files = list(prp.iter_files(tmp_path))
        assert any(f.name == "file.md" for f in files)


# ---------------------------------------------------------------------------
# read_text
# ---------------------------------------------------------------------------

class TestReadText:
    def test_reads_utf8(self, tmp_path):
        p = tmp_path / "f.txt"
        p.write_text("hello world", encoding="utf-8")
        assert prp.read_text(p) == "hello world"

    def test_limit_applied(self, tmp_path):
        p = tmp_path / "big.txt"
        p.write_bytes(b"x" * 300000)
        assert len(prp.read_text(p, limit=100)) == 100

    def test_missing_returns_empty(self, tmp_path):
        assert prp.read_text(tmp_path / "nope.txt") == ""


# ---------------------------------------------------------------------------
# sha256_file
# ---------------------------------------------------------------------------

class TestSha256File:
    def test_deterministic(self, tmp_path):
        p = tmp_path / "f.txt"
        p.write_text("stable content")
        assert prp.sha256_file(p) == prp.sha256_file(p)

    def test_different_content_differs(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("aaa")
        b.write_text("bbb")
        assert prp.sha256_file(a) != prp.sha256_file(b)

    def test_returns_64_hex_chars(self, tmp_path):
        p = tmp_path / "f.txt"
        p.write_text("data")
        digest = prp.sha256_file(p)
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)


# ---------------------------------------------------------------------------
# main (integration)
# ---------------------------------------------------------------------------

class TestMain:
    def test_produces_all_output_files(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        (inp / "README.md").write_text("# My PDR\n\nThis is a governance standard.\n\nTODO: implement the main feature handler properly")
        (inp / "script.py").write_text("# script\nx = 1  # TODO: add security token check here")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        for name in ["pdr_manifest.json", "work_queue.seed.json", "evidence_map.json", "risk_register.json", "intake_summary.json", "dispatch_board.md"]:
            assert (out / name).exists(), f"Missing {name}"

    def test_manifest_has_entry_per_file(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        (inp / "a.md").write_text("# A")
        (inp / "b.py").write_text("x = 1")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        manifest = json.loads((out / "pdr_manifest.json").read_text())
        assert len(manifest) == 2

    def test_summary_file_count_correct(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        for i in range(4):
            (inp / f"f{i}.md").write_text(f"# File {i}")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        summary = json.loads((out / "intake_summary.json").read_text())
        assert summary["file_count"] == 4

    def test_risk_register_captures_security_terms(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        (inp / "bad.py").write_text("secret = 'abc'\ntoken = '123'")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        risks = json.loads((out / "risk_register.json").read_text())
        assert len(risks) > 0
        categories = {r["category"] for r in risks}
        assert "security" in categories

    def test_queue_tasks_have_required_fields(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        (inp / "tasks.md").write_text("TODO: implement the authentication handler module")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        queue = json.loads((out / "work_queue.seed.json").read_text())
        assert len(queue) >= 1
        task = queue[0]
        for field in ["task_id", "priority", "agent_role", "mission", "status", "source_files", "acceptance_criteria"]:
            assert field in task, f"Missing field: {field}"

    def test_empty_input_produces_valid_outputs(self, tmp_path):
        inp = tmp_path / "empty_pkg"
        out = tmp_path / "out"
        inp.mkdir()

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        summary = json.loads((out / "intake_summary.json").read_text())
        assert summary["file_count"] == 0
        assert summary["task_count"] == 0

    def test_dispatch_board_is_valid_markdown_table(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        (inp / "work.md").write_text("TODO: add comprehensive test coverage for the new module")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        board = (out / "dispatch_board.md").read_text()
        assert "# Agent Dispatch Board" in board
        assert "| task_id |" in board

    def test_chromatic_trees_detected_in_summary(self, tmp_path):
        inp = tmp_path / "pkg"
        out = tmp_path / "out"
        inp.mkdir()
        (inp / "chromatic_trees.md").write_text("# ChromaticTrees")

        sys.argv = ["parse_repo_pdr.py", "--input", str(inp), "--output", str(out)]
        prp.main()

        summary = json.loads((out / "intake_summary.json").read_text())
        assert summary["chromatic_trees_present"] is True
