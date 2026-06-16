#!/usr/bin/env python3
"""Validate a YAML or JSON packet (mission packet or eval receipt) against a JSON Schema.

PDR-008 / HERMES-005. Adapted from
chromatic_mission_packet_framework_v1/validation/validate_packet.py and refactored
into importable functions (load_data / iter_validation_errors / validate) so the test
suite can exercise it directly in addition to the CLI entrypoint.

Dependencies (documented per the HERMES-005 stop condition "validator has undocumented
deps"): jsonschema, pyyaml — both pinned in requirements-dev.txt. No other runtime deps.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - exercised only when deps are absent
    print(
        f"Missing dependency: {exc.name}. Install with: pip install jsonschema pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


def load_data(path: Path):
    """Load a packet/schema from a .json, .yaml, or .yml file."""
    text = Path(path).read_text(encoding="utf-8")
    if Path(path).suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def iter_validation_errors(packet, schema):
    """Return validation errors sorted by JSON path (empty list == valid)."""
    validator = Draft202012Validator(schema)
    return sorted(validator.iter_errors(packet), key=lambda e: list(e.path))


def validate(packet, schema) -> bool:
    """Return True iff `packet` conforms to `schema`."""
    return not iter_validation_errors(packet, schema)


def main(argv=None) -> int:
    argv = list(sys.argv if argv is None else argv)
    if len(argv) != 3:
        print(
            "Usage: validate_packet.py <packet.yaml|json> <schema.json>",
            file=sys.stderr,
        )
        return 2

    packet_path = Path(argv[1])
    schema_path = Path(argv[2])

    packet = load_data(packet_path)
    schema = load_data(schema_path)

    errors = iter_validation_errors(packet, schema)
    if errors:
        print(f"FAIL: {packet_path} is invalid")
        for error in errors:
            location = "/".join(str(p) for p in error.path) or "<root>"
            print(f"- {location}: {error.message}")
        return 1

    print(f"PASS: {packet_path} conforms to {schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
