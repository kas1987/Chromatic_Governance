---
name: blender-3d-assets
description: plan advanced blender and 3d asset workflows, including modeling, materials, textures, rigging, export, optimization, web/runtime delivery, and asset library management. use when the user asks about blender, 3d models, textures, glb/gltf, game assets, or 3d ui elements.
---

# Blender 3D Assets

1. Define target runtime: render, web, game engine, AR/VR, video, or asset library.
2. Inventory source assets and license status.
3. Define modeling, UV, material, texture, rig, animation, optimization, and export steps.
4. Set budgets for polycount, texture size, material count, and file size.
5. Produce an asset manifest and pipeline checklist.

Use `references/blender-3d-asset-pipeline.md`.

## Core procedure

See skill description above and `references/` subdirectory for detailed guidance.
Follow the numbered steps in this document, produce the specified output artifacts,
and verify against the guardrails before completing the task.

## Output format

Deliverables as described in the skill body above. Typically includes source files,
component definitions, or documentation placed at paths specified in the skill steps.

## Guardrails

- Limit changes to UI/frontend layer only; do not modify backend logic or APIs
- Validate accessibility (WCAG AA minimum) for any user-facing components produced
- Do not introduce new dependencies without explicit user approval
