"""Tests for AuditLog — file creation, secret filtering, and JSONL output."""
import json
import pytest

from audit_log import AuditLog


@pytest.fixture()
def log_path(tmp_path):
    return tmp_path / "logs" / "events.jsonl"


@pytest.fixture()
def log(log_path):
    return AuditLog(log_path)


class TestFileCreation:
    def test_creates_parent_directories(self, log, log_path):
        log.write({"action": "read"})
        assert log_path.exists()

    def test_creates_nested_parent_directories(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c" / "events.jsonl"
        AuditLog(deep).write({"action": "read"})
        assert deep.exists()


class TestOutput:
    def test_writes_valid_json_line(self, log, log_path):
        log.write({"action": "read", "agent_id": "repo_scout"})
        line = log_path.read_text().strip()
        parsed = json.loads(line)
        assert parsed["action"] == "read"
        assert parsed["agent_id"] == "repo_scout"

    def test_appends_on_multiple_writes(self, log, log_path):
        log.write({"seq": 1})
        log.write({"seq": 2})
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["seq"] == 1
        assert json.loads(lines[1])["seq"] == 2

    def test_timestamp_added_to_every_event(self, log, log_path):
        log.write({"action": "read"})
        parsed = json.loads(log_path.read_text())
        assert "timestamp" in parsed

    def test_output_is_sorted_keys(self, log, log_path):
        log.write({"z_field": 1, "a_field": 2})
        raw = log_path.read_text().strip()
        # sort_keys=True means a_field comes before z_field in raw text
        assert raw.index('"a_field"') < raw.index('"z_field"')


class TestSecretFiltering:
    @pytest.mark.parametrize("key", [
        "token",
        "access_token",
        "TOKEN",
        "github_token",
        "secret",
        "client_secret",
        "SECRET_KEY",
    ])
    def test_keys_containing_token_or_secret_are_stripped(self, log, log_path, key):
        log.write({key: "super-sensitive-value", "action": "read"})
        parsed = json.loads(log_path.read_text())
        assert key not in parsed
        assert "action" in parsed

    def test_safe_keys_are_preserved(self, log, log_path):
        log.write({
            "agent_id": "code_sentinel",
            "repo": "example-org/example-repo",
            "allowed": True,
            "reason": "allowed",
            "risk": "low",
        })
        parsed = json.loads(log_path.read_text())
        assert parsed["agent_id"] == "code_sentinel"
        assert parsed["repo"] == "example-org/example-repo"
        assert parsed["allowed"] is True
