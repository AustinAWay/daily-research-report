#!/usr/bin/env python3
"""Does every sound land on its picture cue? usage: sfx_align.py WORK_DIR
On the isolated SFX bus (audio/sfx_only.npy): transients = first sample where the 1 ms envelope reaches 50 % of its local max
(search -60..+120 ms); swells (whoosh/riser/revcym/rewind) = 30 ms-RMS peak within +-120 ms. Flags anything over 2 frames."""
import sys, json, pathlib, numpy as np
SR = 48000; W = pathlib.Path(sys.argv[1]); x = np.load(W / 'audio' / 'sfx_only.npy'); x = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
h = SR // 1000; env = x[:len(x) // h * h].reshape(-1, h).max(1); sm = np.convolve(env ** 2, np.ones(30) / 30, 'same') ** .5
C = json.load(open(W / 'cues.json')); SW = {'whoosh', 'riser', 'revcym', 'rewind'}; out = []; bad = 0
for t, k, w in C:
    ms = int(t * 1000)
    if k in SW: a, b = ms - 120, ms + 120; seg = sm[max(0, a):b]; dd = int(seg.argmax()) + max(0, a) - ms; how = 'peak '
    else: a, b = ms - 60, ms + 120; seg = env[max(0, a):b]; dd = int(np.argmax(seg >= .5 * seg.max())) + max(0, a) - ms; how = 'onset'
    fr = abs(dd) / 1000 * 30; bad += fr > 2
    out.append('%8.3f %-8s %s %+5d ms (%.1f fr)  %s%s' % (t, k, how, dd, fr, w, '  <-- >2fr' if fr > 2 else ''))
out.append(f'cues {len(C)}, over 2 frames: {bad}'); (W / 'audio' / 'qa_sfx_align.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(l for l in out if '>2fr' in l)); print(out[-1]); sys.exit(1 if bad else 0)
