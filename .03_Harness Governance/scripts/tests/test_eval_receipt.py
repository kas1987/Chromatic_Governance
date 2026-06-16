"""Tests for the HERMES-005 eval-receipt schema + validate_packet.py.

Validates that:
  - the canonical eval_receipt schema loads and is itself a well-formed JSON Schema,
  - a valid fixture passes validation,
  - an invalid fixture fails validation (and surfaces the expected violations).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

# Add scripts directory to path so validate_packet can be imported.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import validate_packet as vp

# .03_Harness Governance/ root (scripts/tests -> scripts -> root).
ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "eval_receipt.schema.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="module")
def schema():
    return vp.load_data(SCHEMA)


class TestSchemaItself:
    def test_schema_file_exists(self):
        assert SCHEMA.exists(), f"missing canonical schema at {SCHEMA}"

    def test_schema_is_valid_metaschema(self, schema):
        # Raises SchemaError if the schema is malformed.
        Draft202012Validator.check_schema(schema)

    def test_schema_forbids_additional_properties(self, schema):
        assert schema.get("additionalProperties") is False


class TestValidReceipt:
    def test_valid_fixture_passes(self, schema):
        receipt = vp.load_data(FIXTURES / "eval_receipt.valid.json")
        assert vp.validate(receipt, schema) is True

    def test_valid_fixture_has_no_errors(self, schema):
        receipt = vp.load_data(FIXTURES / "eval_receipt.valid.json")
        assert vp.iter_validation_errors(receipt, schema) == []

    def test_cli_returns_zero_for_valid(self, schema):
        rc = vp.main(
            [
                "validate_packet.py",
                str(FIXTURES / "eval_receipt.valid.json"),
                str(SCHEMA),
            ]
        )
        assert rc == 0


class TestInvalidReceipt:
    def test_invalid_fixture_fails(self, schema):
        receipt = vp.load_data(FIXTURES / "eval_receipt.invalid.json")
        assert vp.validate(receipt, schema) is False

    def test_invalid_fixture_surfaces_errors(self, schema):
        receipt = vp.load_data(FIXTURES / "eval_receipt.invalid.json")
        errors = vp.iter_validation_errors(receipt, schema)
        # bad status enum, wrong file_changed type, missing validation_results,
        # wrong stop_condition_triggered type, and an unexpected field.
        assert len(errors) >= 3

    def test_cli_returns_one_for_invalid(self, schema):
        rc = vp.main(
            [
                "validate_packet.py",
                str(FIXTURES / "eval_receipt.invalid.json"),
                str(SCHEMA),
            ]
        )
        assert rc == 1


class TestCliUsage:
    def test_wrong_argc_returns_two(self):
        assert vp.main(["validate_packet.py"]) == 2
