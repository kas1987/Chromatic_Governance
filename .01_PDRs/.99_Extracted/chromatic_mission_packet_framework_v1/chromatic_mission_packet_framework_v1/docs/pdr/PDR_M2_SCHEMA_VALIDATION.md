# PDR: M2 Mission Packet Schema Validation

## Problem

Local agents need structured mission packets so execution can be bounded, testable, and auditable.

## Context

Front-tier models should create mission packets. Local agents should execute inside the packet. CI should validate outcomes.

## Proposed Solution

Add a base JSON Schema, YAML templates, and a validator script.

## Decisions

- Use M1-M4 as mission rigor levels.
- Use JSON Schema as the validation contract.
- Keep YAML as the human-editable mission format.

## Risks

- Schema may be too strict early.
- Agents may bypass validation unless CI enforces it.

## Validation Plan

- Validate one M1 example.
- Validate one M2 example.
- Add CI later.

## Rollback Plan

Revert schema and validator files.
