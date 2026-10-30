#!/usr/bin/env python3
"""Pick the best take per line, lay the lines out on one timeline, apply the optional bleep, write vo.wav + timing.json.
usage: build_vo.py EPISODE_DIR VERSION [--no-whisper] [--pick LINE=take ...]
Take choice: trim (8 ms threshold, onset -25 ms, offset +60 ms) -> transcribe with faster-whisper small.en (48k->16k, zero-padded)
-> lowest word error vs the script, ties -> the take whose length is closest to the line's median take. A take longer than the
line's `max_dur` is rejected (shorten the wording in `alts` rather than speeding audio up; at most a 0.6 % resample is allowed).
Layout: lines play back to back with `gap_after` (default 0.35 s). Marks reserve music-only gaps, e.g.
  marks: {montage: {after: C02, dur: 7.0}, endcard: {after: V03, dur: 4.4}}  ->  timing.marks.montage / .logo / .endcard / .end"""
import os, sys, json, re, numpy as np, soundfile as sf, scipy.signal as sg
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
args = sys.argv[1:]; ep = C.episode(args[0]); ver = args[1]
WH = '--no-whisper' not in args
PICK = dict(a.split('=') for a in args[args.index('--pick') + 1:]) if '--pick' in args else {}
W = C.work_dir(ep, ver); TK = W / 'vo' / 'takes'; SR = 48000; FPS = 30
nz = lambda s: re.sub(r"[^a-z0-9' ]", '', s.lower().replace('-', ' ')).split()
def trim(x):
    e = np.array([np.sqrt((x[i:i + 480] ** 2).mean()) for i in range(0, max(1, len(x) - 480), 480)])
    on = max(0, int(np.argmax(e > .008)) * 480 - int(.025 * SR)); off = min(len(x), (len(e) - int(np.argmax(e[::-1] > .008))) * 480 + int(.06 * SR))
    return x[on:off], on / SR
def wer(a, b):
    a, b = nz(a), nz(b); d = np.arange(len(b) + 1)
    for i in range(1, len(a) + 1):
        p, d[0] = d.copy(), i
        for j in range(1, len(b) + 1): d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (a[i - 1] != b[j - 1]))
    return d[len(b)] / max(1, len(a))
model = None
if WH:
    from faster_whisper import WhisperModel; model = WhisperModel('small.en', device='cpu', compute_type='int8')
def heard(x):
    y = np.concatenate([np.zeros(8000), sg.resample_poly(x, 1, 3), np.zeros(8000)]).astype(np.float32)
    seg, _ = model.transcribe(y, beam_size=5, language='en'); return ' '.join(s.text for s in seg)
chosen = []
for l in ep['lines']:
    takes = sorted(p.stem for p in TK.glob(f"{l['id']}?.json"))
    if not takes: raise SystemExit(f"no takes for {l['id']}: run tts_cartesia.py first")
    cand = []
    for tk in ([PICK[l['id']]] if l['id'] in PICK else takes):
        J = json.load(open(TK / f'{tk}.json')); x, _ = sf.read(TK / f'{tk}.wav', dtype='float32'); x, on = trim(x)
        if l.get('max_dur') and len(x) / SR > l['max_dur'] * 1.006: continue
        e = wer(J['text'], heard(x)) if WH else 0.0
        cand.append((e, len(x) / SR, tk, J, x, on))
    if not cand: raise SystemExit(f"{l['id']}: every take is longer than max_dur {l['max_dur']}; add a shorter wording to alts")
    med = np.median([c[1] for c in cand]); cand.sort(key=lambda c: (round(c[0], 2), abs(c[1] - med)))
    chosen.append((l, cand[0])); print(f"{l['id']}: {cand[0][2]} wer {cand[0][0]:.2f} dur {cand[0][1]:.2f}", flush=True)
marks_spec = ep.get('marks', {}); after = {v['after']: (k, v['dur']) for k, v in marks_spec.items()}
t = float(ep.get('lead_in', .3)); lines = []; marks = {}; segs = []
for l, (e, d, tk, J, x, on) in chosen:
    lines.append(dict(id=l['id'], section=l.get('section', ''), emotion=l.get('emotion'), text=J['text'], take=tk, t=round(t, 3), d=round(d, 3),
                      words=[dict(w=w['w'], s=round(t + w['s'] - on, 3), e=round(t + w['e'] - on, 3)) for w in J['words']]))
    segs.append((t, x)); t += d + float(l.get('gap_after', .35))
    if l['id'] in after:
        k, dur = after[l['id']]; marks[k] = round(t, 4)
        if k == 'montage': marks['logo'] = round(t + dur, 4)
        if k == 'endcard': marks['vo_end'] = round(t - float(l.get('gap_after', .35)), 4); marks['end'] = round(t + dur, 4)
        t += dur
dur = round(marks.get('end', t + 1.0), 4); dur = round(np.ceil(dur * FPS) / FPS, 4)
a = np.zeros(int(dur * SR) + SR, np.float32)
for t0, x in segs: i = int(round(t0 * SR)); a[i:i + len(x)] += x
bleep = None
if ep.get('bleep'):
    b = ep['bleep']; L = next(l for l in lines if l['id'] == b['line'])
    wd = next(w for w in L['words'] if nz(w['w'])[:1] == nz(b['word'])[:1]); s = wd['s'] + b.get('keep', 0.0) * (wd['e'] - wd['s'])
    i0, i1 = int(s * SR), int(wd['e'] * SR); n = i1 - i0; tt = np.arange(n) / SR
    tone = .25 * np.sin(2 * np.pi * 1000 * tt) * np.clip(np.minimum(tt / .005, (n / SR - tt) / .005), 0, 1)
    a[i0:i1] = tone if b.get('tone', True) else 0; bleep = [round(s, 3), wd['e']]
a = a[:int(dur * SR)]
pk = np.abs(a).max(); a *= .89 / pk  # leave headroom; mix.py sets the final loudness
sf.write(W / 'vo' / 'vo.wav', a, SR, subtype='FLOAT')
T = dict(dur=dur, fps=FPS, bleep=bleep, marks=marks, lines=lines)
json.dump(T, open(W / 'timing.json', 'w'), indent=1)
pg = W / 'page'
if pg.exists():
    tmp = pg / 'timing.js.tmp'; tmp.write_text('window.TIMING=' + json.dumps(T) + ';'); os.replace(tmp, pg / 'timing.js')  # atomic
print('vo.wav', dur, 's; marks', marks)
