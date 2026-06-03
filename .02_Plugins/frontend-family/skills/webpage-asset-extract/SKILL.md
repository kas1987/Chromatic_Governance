---
name: webpage-asset-extract
description: inventory, extract, classify, and plan migration of webpage assets from urls, local html, css, and frontend bundles. use when the user asks to copy a site style, inspect a webpage, collect images/fonts/icons/scripts/media/3d assets, or create an asset manifest.
---

# Webpage Asset Extract

1. Confirm whether the source is a URL, local file, exported HTML bundle, screenshot, or repository.
2. State the permission/licensing assumption before recommending reuse.
3. Create an asset inventory grouped by images, fonts, icons, CSS, JS, media, and 3D assets.
4. Separate first-party assets from framework/CDN/vendor assets.
5. Recommend keep, recreate, replace, or ignore for each category.
6. Produce a migration plan with target folders and naming conventions.

For local HTML/CSS bundles, use `scripts/asset_inventory.py` to create `asset-inventory.json`.

Use `references/webpage-asset-extraction-playbook.md`.
