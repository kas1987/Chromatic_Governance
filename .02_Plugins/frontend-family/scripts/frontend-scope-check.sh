#!/usr/bin/env bash
set -euo pipefail
root="${1:-.}"
echo "frontend scope check: $root"
if find "$root" -type f \( -name '*.html' -o -name '*.css' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' \) | head -1 | grep -q .; then
  echo "frontend files detected"
else
  echo "no frontend files detected"
fi
if find "$root" -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.webp' -o -name '*.svg' -o -name '*.glb' -o -name '*.gltf' -o -name '*.blend' \) | head -1 | grep -q .; then
  echo "asset files detected - verify source and license"
fi
