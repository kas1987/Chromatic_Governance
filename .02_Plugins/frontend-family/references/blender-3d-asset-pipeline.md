# Blender and 3D Asset Pipeline

Track source, license, file format, units, scale, origin/pivot, polycount, materials, texture maps, texture resolution, rig/animation status, LODs, export target, optimization notes.

Pipeline: blockout -> model -> UV unwrap -> materials -> texture bake -> rig/animate if needed -> optimize -> export GLB/FBX/OBJ -> validate in target runtime.

For web/runtime delivery, use GLB/GLTF where possible. Compress textures. Watch draw calls, polycount, material count, animation weight, and collision meshes.
