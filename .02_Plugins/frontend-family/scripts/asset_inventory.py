#!/usr/bin/env python3
"""Create a simple asset inventory from a local HTML file or directory.
This script does not download remote assets. It extracts references from HTML/CSS/JS-like text.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ASSET_RE = re.compile(r'''(?:src|href)=["']([^"']+)["']|url\(["']?([^"')]+)["']?\)''', re.I)

def scan_file(path: Path):
    text = path.read_text(errors='ignore')
    refs = []
    for m in ASSET_RE.finditer(text):
        ref = m.group(1) or m.group(2)
        if ref and not ref.startswith(('data:', '#', 'mailto:', 'tel:')):
            refs.append(ref)
    return refs

def classify(ref: str):
    low = ref.lower().split('?')[0]
    if low.endswith(('.png','.jpg','.jpeg','.gif','.webp','.avif','.svg')): return 'image'
    if low.endswith('.css'): return 'stylesheet'
    if low.endswith(('.js','.mjs','.ts')): return 'script'
    if low.endswith(('.woff','.woff2','.ttf','.otf','.eot')): return 'font'
    if low.endswith(('.glb','.gltf','.obj','.fbx','.blend')): return '3d'
    if low.endswith(('.mp4','.webm','.mov','.mp3','.wav','.ogg')): return 'media'
    return 'other'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target', help='HTML/CSS file or directory to scan')
    ap.add_argument('--out', default='asset-inventory.json')
    args = ap.parse_args()
    target = Path(args.target)
    files = [target] if target.is_file() else list(target.rglob('*'))
    rows = []
    for f in files:
        if f.suffix.lower() not in ['.html','.htm','.css','.js','.jsx','.tsx','.vue','.svelte']:
            continue
        for ref in scan_file(f):
            rows.append({'source_file': str(f), 'reference': ref, 'type': classify(ref)})
    summary = {}
    for r in rows:
        summary[r['type']] = summary.get(r['type'], 0) + 1
    payload = {'count': len(rows), 'summary': summary, 'assets': rows}
    Path(args.out).write_text(json.dumps(payload, indent=2))
    print(json.dumps({'written': args.out, 'count': len(rows), 'summary': summary}, indent=2))
if __name__ == '__main__':
    main()
