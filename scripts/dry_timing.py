#!/usr/bin/env python3
"""Dry run without any TTS key: fake word timings at a host pace (~3.3 words/s) and a silent vo.wav, so the page, render,
score, SFX and mix steps can all be tested end to end. usage: dry_timing.py EPISODE_DIR VERSION"""
import os, sys, json, re, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); W = C.work_dir(ep, sys.argv[2]); (W / 'vo').mkdir(exist_ok=True)
after = {v['after']: (k, v['dur']) for k, v in ep.get('marks', {}).items()}; t = float(ep.get('lead_in', .3)); lines = []; marks = {}
for l in ep['lines']:
    ws = l['text'].split(); words = []; s = t
    for w in ws: d = .12 + .045 * len(re.sub(r'\W', '', w)); words.append(dict(w=w, s=round(s, 3), e=round(s + d, 3))); s += d + .04
    lines.append(dict(id=l['id'], section=l.get('section', ''), emotion=l.get('emotion'), text=l['text'], take='dry', t=round(t, 3), d=round(s - t, 3), words=words))
    t = s + float(l.get('gap_after', .35))
    if l['id'] in after:
        k, dur = after[l['id']]; marks[k] = round(t, 4)
        if k == 'montage': marks['logo'] = round(t + dur, 4)
        if k == 'endcard': marks['vo_end'] = round(s, 4); marks['end'] = round(t + dur, 4)
        t += dur
dur = round(np.ceil(marks.get('end', t + 1) * 30) / 30, 4)
bleep = None
if ep.get('bleep'):
    L = next(x for x in lines if x['id'] == ep['bleep']['line']); wd = next(w for w in L['words'] if ep['bleep']['word'].lower() in w['w'].lower()); bleep = [wd['s'], wd['e']]
sf.write(W / 'vo' / 'vo.wav', np.zeros(int(dur * 48000), np.float32), 48000, subtype='FLOAT')
json.dump(dict(dur=dur, fps=30, bleep=bleep, marks=marks, lines=lines, dry=True), open(W / 'timing.json', 'w'), indent=1)
print('dry timing', dur, 's', marks)
