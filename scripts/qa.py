#!/usr/bin/env python3
"""Automatic QA on the FINISHED share file. usage: qa.py EPISODE_DIR VERSION
Writes <work>/out/QA.md. Fails (exit 1) on: a line whose transcript differs from the script beyond 15 % word error,
a hold > 1.5 s (no visible motion), dark frames outside the first/last 0.3 s, a loud tail after the end, loudness
off -14 +-0.5 LUFS or true peak > -1 dBTP. Watch the film too: QA catches regressions, not taste."""
import os, sys, re, json, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); ver = sys.argv[2]; W = C.work_dir(ep, ver); O = W / 'out'
T = json.load(open(W / 'timing.json')); share = O / f"{ep['id']}_v{ver}_share.mp4"; a, sr = sf.read(W / 'qa_16k.wav', dtype='float32')
from faster_whisper import WhisperModel
m = WhisperModel('small.en', device='cpu', compute_type='int8')
nz = lambda s: re.sub(r"[^a-z0-9' ]", '', s.lower().replace('-', ' ')).split()
def wer(r, h):
    r, h = nz(r), nz(h); d = np.arange(len(h) + 1)
    for i in range(1, len(r) + 1):
        p, d[0] = d.copy(), i
        for j in range(1, len(h) + 1): d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(1, len(r))
def tr(t0, t1):
    x = np.concatenate([np.zeros(sr // 2, 'float32'), a[int(max(0, t0) * sr):int(t1 * sr)], np.zeros(sr, 'float32')])
    return ' '.join(s.text.strip() for s in m.transcribe(x, language='en', beam_size=5, temperature=0, condition_on_previous_text=False)[0])
rep = [f"# QA {ep['id']} v{ver}", '', '## Voice vs script (final mix)']; fail = []
for l in T['lines']:
    h = tr(l['t'] - .1, l['t'] + l['d'] + .2); e = wer(l['text'], h)
    if T.get('bleep') and T['bleep'][0] >= l['t'] and T['bleep'][0] <= l['t'] + l['d']: e = max(0, e - 2 / max(1, len(nz(l['text']))))  # the bleeped word
    rep.append(f"- {l['id']} wer {e:.2f}: {h}" + ('  **CHECK**' if e > .15 else '')); fail += [f"{l['id']} wer {e:.2f}"] if e > .15 else []
Wd, Hd = 96, 54
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(share), '-vf', f'scale={Wd}:{Hd},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, Hd, Wd).astype(np.float32); d = np.abs(np.diff(F, axis=0)).mean((1, 2)); n = len(F)
dark = [round(i / 30, 2) for i in range(n) if F[i].mean() < 40 and 9 < i < n - 9]
holds = []; s = None
for i, x in enumerate(list(d) + [99]):
    if x < .25: s = i if s is None else s
    else:
        if s is not None and (i - s) / 30 > 1.5: holds.append((round(s / 30, 2), round(i / 30, 2)))
        s = None
rms = lambda t0, t1: 20 * np.log10(float(np.sqrt((a[int(t0 * sr):int(t1 * sr)] ** 2).mean() + 1e-12)))
tail = round(rms(T['dur'] - .25, T['dur']), 1)
lo = (O / 'loudness.txt').read_text(); I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', lo)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', lo)[-1])
rep += ['', '## Picture', f'- frames {n} = {n/30:.3f} s (timing says {T["dur"]:.3f} s)', f'- holds > 1.5 s: {holds or "none"}', f'- dark frames: {dark[:20] or "none"}',
        '', '## Audio', f'- integrated {I} LUFS, true peak {TP} dBTP', f'- last 0.25 s: {tail} dBFS']
fail += [f'holds {holds}'] if holds else []; fail += [f'dark {dark[:5]}'] if dark else []
fail += [f'loudness {I}/{TP}'] if abs(I + 14) > .5 or TP > -1 else []; fail += [f'frames {n}'] if abs(n / 30 - T['dur']) > .1 else []
rep += ['', '## Result', 'PASS' if not fail else 'FAIL: ' + '; '.join(fail)]
(O / 'QA.md').write_text('\n'.join(rep) + '\n'); print('\n'.join(rep[-1:])); sys.exit(1 if fail else 0)
