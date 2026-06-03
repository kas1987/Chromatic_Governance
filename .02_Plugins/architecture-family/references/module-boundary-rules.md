# Module Boundary Rules

Use these rules unless the project defines a stricter layering model.

## Default dependency direction

1. UI / presentation may depend on application services.
2. Application services may depend on domain logic and interfaces.
3. Domain logic should not depend on UI, infrastructure, or external tools.
4. Infrastructure implements interfaces owned by application or domain layers.
5. Tests may depend on all layers, but fixtures should not become production dependencies.

## Agent edit zones

When assigning agents, define:

- Files they may edit.
- Files they may inspect but not edit.
- Interfaces they must not change without approval.
- Tests or checks they must run.

## Red flags

- Circular imports.
- Feature code reaching directly into storage internals.
- UI code owning business rules.
- Domain logic importing framework-specific adapters.
- Shared utilities with unrelated responsibilities.
- Multiple modules writing the same state without a coordination rule.

## Preferred fixes

- Move logic to the owning layer.
- Create an adapter at the boundary.
- Invert dependency through an interface.
- Split shared utilities by responsibility.
- Add contract tests before changing a boundary.
