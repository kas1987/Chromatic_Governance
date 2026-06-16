"""Tests for token_issuer.GitHubAppTokenIssuer.

Pins the constructor contract and verifies issue_token raises
NotImplementedError so the stub cannot be called in production by accident.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from token_issuer import GitHubAppTokenIssuer


class TestInit:
    def test_stores_app_id(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem")
        assert issuer.app_id == "app-123"

    def test_stores_private_key_path(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem")
        assert issuer.private_key_path == "/path/to/key.pem"

    def test_default_api_version(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem")
        assert issuer.api_version == "2026-03-10"

    def test_custom_api_version(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem", api_version="2025-01-01")
        assert issuer.api_version == "2025-01-01"

    def test_different_instances_are_independent(self):
        a = GitHubAppTokenIssuer("app-1", "/k1")
        b = GitHubAppTokenIssuer("app-2", "/k2")
        assert a.app_id != b.app_id
        assert a.private_key_path != b.private_key_path


class TestIssueTokenStub:
    def test_raises_not_implemented(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem")
        with pytest.raises(NotImplementedError):
            issuer.issue_token("install-456", {"contents": "read"})

    def test_raises_not_implemented_with_repositories(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem")
        with pytest.raises(NotImplementedError):
            issuer.issue_token(
                "install-456",
                {"contents": "read"},
                repositories=["owner/repo"],
            )

    def test_error_message_hints_at_implementation(self):
        issuer = GitHubAppTokenIssuer("app-123", "/path/to/key.pem")
        with pytest.raises(NotImplementedError, match="PyJWT|requests|Octokit"):
            issuer.issue_token("install-456", {})
