"""Tests for chromatic_skills_server — covers index building, all three tools,
and the parse_frontmatter helper."""
import json
import re
from pathlib import Path

import pytest

import chromatic_skills_server as srv

PLUGINS_ROOT = Path(__file__).resolve().parents[2]  # .02_Plugins/


@pytest.fixture(autouse=True)
def reset_index():
    """Each test gets a fresh skill index."""
    srv._reset_index()
    yield
    srv._reset_index()


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter:
    def test_extracts_name_and_description(self):
        text = "---\nname: my-skill\ndescription: Does things.\n---\n\n# Body"
        front, body = srv._parse_frontmatter(text)
        assert front["name"] == "my-skill"
        assert front["description"] == "Does things."
        assert "Body" in body

    def test_returns_empty_dict_when_no_frontmatter(self):
        front, body = srv._parse_frontmatter("# Just a heading\n\nParagraph.")
        assert front == {}
        assert "Just a heading" in body

    def test_returns_empty_dict_on_unclosed_frontmatter(self):
        front, _ = srv._parse_frontmatter("---\nname: broken\n")
        assert front == {}

    def test_empty_frontmatter_returns_empty_dict(self):
        front, _ = srv._parse_frontmatter("---\n---\n\nbody")
        assert front == {}


# ---------------------------------------------------------------------------
# _build_index (against the real plugin directory)
# ---------------------------------------------------------------------------

class TestBuildIndex:
    def test_returns_list_of_dicts(self):
        index = srv._build_index(PLUGINS_ROOT)
        assert isinstance(index, list)
        assert len(index) > 0

    def test_every_entry_has_required_keys(self):
        for entry in srv._build_index(PLUGINS_ROOT):
            assert "name" in entry
            assert "family" in entry
            assert "description" in entry
            assert "path" in entry

    def test_family_names_match_known_families(self):
        known = {
            "rpi-family", "toolchain-family", "context-family", "security-family",
            "architecture-family", "qa-eval-family", "release-family",
            "observability-family", "agent-governance-family", "docs-family",
            "product-family", "data-research-family", "frontend-family",
        }
        for entry in srv._build_index(PLUGINS_ROOT):
            assert entry["family"] in known, f"Unknown family: {entry['family']}"

    def test_skill_count_matches_expected(self):
        index = srv._build_index(PLUGINS_ROOT)
        assert len(index) == 120, f"Expected 120 skills, got {len(index)}"

    def test_no_duplicate_names(self):
        names = [e["name"] for e in srv._build_index(PLUGINS_ROOT)]
        assert len(names) == len(set(names)), "Duplicate skill names found"

    def test_paths_all_exist(self):
        for entry in srv._build_index(PLUGINS_ROOT):
            assert Path(entry["path"]).exists(), f"Missing: {entry['path']}"


# ---------------------------------------------------------------------------
# list_skills
# ---------------------------------------------------------------------------

class TestListSkills:
    def test_returns_all_skills_when_no_filter(self):
        skills = srv.list_skills()
        assert len(skills) == 120

    def test_filters_by_exact_family(self):
        skills = srv.list_skills(family="context-family")
        assert len(skills) == 9
        assert all(s["family"] == "context-family" for s in skills)

    def test_filters_by_partial_family_name(self):
        skills = srv.list_skills(family="context")
        assert all("context" in s["family"] for s in skills)

    def test_each_result_has_name_family_description(self):
        for skill in srv.list_skills():
            assert skill["name"]
            assert skill["family"]
            # description may be empty for some skills — just check key exists
            assert "description" in skill

    def test_unknown_family_returns_empty_list(self):
        assert srv.list_skills(family="nonexistent-family-xyz") == []

    def test_rpi_family_has_17_skills(self):
        assert len(srv.list_skills(family="rpi")) == 17


# ---------------------------------------------------------------------------
# get_skill
# ---------------------------------------------------------------------------

class TestGetSkill:
    def test_returns_skill_content_by_exact_name(self):
        content = srv.get_skill("context-monitor")
        assert "context-monitor" in content.lower()
        assert "## Core procedure" in content or "## core procedure" in content.lower()

    def test_name_lookup_is_case_insensitive(self):
        content = srv.get_skill("Context-Monitor")
        assert "not found" not in content.lower()

    def test_unknown_skill_returns_not_found_message(self):
        result = srv.get_skill("totally-made-up-skill-xyz")
        assert "not found" in result.lower()
        assert "list_skills" in result

    def test_returns_full_markdown_with_frontmatter(self):
        content = srv.get_skill("delegate")
        assert content.startswith("---")

    def test_chromatic_memory_registrar_is_findable(self):
        content = srv.get_skill("chromatic-memory-registrar")
        assert "not found" not in content.lower()

    def test_repo_pdr_swarm_router_is_findable(self):
        content = srv.get_skill("repo-pdr-swarm-router")
        assert "not found" not in content.lower()


# ---------------------------------------------------------------------------
# search_skills
# ---------------------------------------------------------------------------

class TestSearchSkills:
    def test_returns_up_to_three_results(self):
        results = srv.search_skills("track token usage by model session")
        assert len(results) <= 3

    def test_context_monitor_found_for_token_query(self):
        results = srv.search_skills("track token usage by model")
        names = [r["name"] for r in results]
        assert "context-monitor" in names

    def test_results_have_required_fields(self):
        for r in srv.search_skills("security review permissions"):
            assert "name" in r
            assert "family" in r
            assert "description" in r
            assert "relevance_score" in r

    def test_relevance_score_is_numeric_string(self):
        for r in srv.search_skills("release deploy"):
            assert r["relevance_score"].isdigit()

    def test_returns_empty_for_nonsense_query(self):
        results = srv.search_skills("xyzzy quux frobnicate")
        assert results == []

    def test_returns_empty_for_very_short_tokens(self):
        # All tokens <= 2 chars are ignored
        results = srv.search_skills("a b c")
        assert results == []

    def test_handoff_query_finds_relevant_skill(self):
        results = srv.search_skills("convert PDR output to cursor codex handoff")
        names = [r["name"] for r in results]
        assert any("handoff" in n for n in names)

    def test_memory_query_finds_registrar(self):
        results = srv.search_skills("save durable project memory decisions state")
        names = [r["name"] for r in results]
        assert any("memory" in n or "registrar" in n for n in names)
