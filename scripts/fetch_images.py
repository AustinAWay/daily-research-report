#!/usr/bin/env python3
"""Download the episode's still images (episode.yaml `images:` list) into assets/images/<episode id>/<name>.png.
Each entry: {name, url (direct file URL), source (file page), license, author}. Only use images whose license allows reuse
(public domain / CC0 / CC BY / CC BY-SA) and credit them in the end card or description. Converts to 1600 px PNG."""
import os, sys, subprocess, urllib.request, pathlib
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); D = C.assets() / 'images' / ep['id']; D.mkdir(parents=True, exist_ok=True)
for im in ep.get('images', []):
    out = D / f"{im['name']}.png"
    if out.exists(): continue
    raw = D / f"{im['name']}.src"
    r = urllib.request.Request(im['url'], headers={'User-Agent': 'daily-research-report/1.0 (image fetch for an educational video)'})
    raw.write_bytes(urllib.request.urlopen(r, timeout=60).read())
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(raw), '-vf', "scale='min(1600,iw)':-2", str(out)], check=True); raw.unlink()
    print(im['name'], im['license'], im['author'])
