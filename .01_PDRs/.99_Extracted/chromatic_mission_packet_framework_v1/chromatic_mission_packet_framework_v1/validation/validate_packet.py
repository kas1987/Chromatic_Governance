#!/usr/bin/env python3
"""Validate a YAML or JSON mission packet against a JSON Schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:
    print(f"Missing dependency: {exc.name}. Install with: pip install jsonschema pyyaml", file=sys.stderr)
    sys.exit(2)


def load_data(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: validate_packet.py <packet.yaml|json> <schema.json>", file=sys.stderr)
        return 2

    packet_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2])

    packet = load_data(packet_path)
    schema = load_data(schema_path)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(packet), key=lambda e: list(e.path))
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
