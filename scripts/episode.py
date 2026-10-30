#!/usr/bin/env python3
"""Prepare the render page for one episode version and pre-check every word key.
usage: episode.py EPISODE_DIR VERSION
- copies templates/page -> <work>/page, links assets/vendor + assets/fonts, copies the episode's images into page/img
- writes page/episode.js (beats, sources, credits, open, scenes; citation numbers merged from <episode>/citations/summary.json)
- writes page/timing.js from <work>/timing.json (atomic)
- checks that every beat's (line, word) exists in the voice timing, so a re-worded line fails HERE and not as a NOT READY render."""
import os, sys, json, re, shutil, pathlib
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); ver = sys.argv[2]; W = C.work_dir(ep, ver); A = C.assets(); ED = pathlib.Path(ep['_dir'])
pg = W / 'page'
shutil.copytree(C.ROOT / 'templates' / 'page', pg, dirs_exist_ok=True)
for d in ('vendor', 'fonts'):
    if not (A / d).exists(): raise SystemExit(f'missing {A/d}: run scripts/fetch_vendor.sh')
    if not (pg / d).exists(): os.symlink(A / d, pg / d)
(pg / 'img').mkdir(exist_ok=True)
for b in ep.get('beats', []) + [{'image': i} for i in ep.get('open', {}).get('images', [])]:
    if b.get('image'):
        src = A / 'images' / ep['id'] / f"{b['image']}.png"
        if not src.exists(): raise SystemExit(f'missing image {src}: run scripts/fetch_images.py {ED}')
        shutil.copy(src, pg / 'img' / src.name)
summ = ED / 'citations' / 'summary.json'
cites = json.load(open(summ)) if summ.exists() else None
beats = []
for b in ep.get('beats', []):
    b = dict(b)
    if b['type'] == 'citations':
        if not cites: raise SystemExit('citations beat needs citations/summary.json (scripts/citations_classify.py)')
        bd = b.get('data', {}); rows = [{**r, **(bd.get('rows') or [{}] * 9)[i]} for i, r in enumerate(cites['card']['rows'])]
        b['data'] = {**cites['card'], **{k: v for k, v in bd.items() if k != 'rows'}, 'rows': rows}
    beats.append(b)
E = dict(scenes=ep.get('scenes', ['open', 'beats', 'end']), open=ep.get('open', {}), beats=beats,
         sources=ep.get('sources', []), credits=ep.get('credits', ''))
(pg / 'episode.js').write_text('window.EPISODE=' + json.dumps(E) + ';')
T = json.load(open(W / 'timing.json'))
tmp = pg / 'timing.js.tmp'; tmp.write_text('window.TIMING=' + json.dumps(T) + ';'); os.replace(tmp, pg / 'timing.js')
nz = lambda s: re.sub(r"[^a-z0-9']", '', s.lower())
LN = {l['id']: l for l in T['lines']}; bad = []
def chk(line, word):
    if line not in LN: bad.append(f'line {line}'); return
    if word is None: return
    ws = [nz(x['w']) for x in LN[line]['words']]; q = nz(word)
    if q not in ws and not any(x.startswith(q) for x in ws): bad.append(f'{line}:{word}')
for b in beats:
    for k in ('on', 'shatter_on', 'on_count', 'on_breakdown'):
        if k in b or k == 'on': chk(b['line'], b.get(k))
    for x in b.get('bars', []): chk(x.get('line', b['line']), x.get('on'))
    for r in (b.get('data') or {}).get('rows', []): chk(b['line'], r.get('on'))
if bad: raise SystemExit('word keys missing from the voice timing (re-worded line?): ' + ', '.join(bad))
if ep.get('music'): json.dump(ep['music'], open(W / 'music.json', 'w'))
print('page ready:', pg)
