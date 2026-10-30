#!/usr/bin/env python3
"""Original, cue-driven score for one episode (no third-party melodies or loops). usage: score.py WORK_DIR
Reads timing.json (sections + marks) and cues.json (render.js cues). Writes audio/music_raw.npy (stereo, 48 kHz).
Arc (generic; tune in the episode's `music:` block): cold open = tense pulse under the voice -> show open = full-band
montage that lands on the sonic logo -> study = light pluck groove -> turn = hard stop (true silence through the bleep) ->
fundamentals = piano + pad, curious -> verdict = build -> resolve = the logo motif again on the relative major, over the end card.
Sonic logo: the pickup notes in music.logo land on the tonic on the logo mark."""
import sys, json, numpy as np, pathlib
from lib import *
W = pathlib.Path(sys.argv[1]); T = json.load(open(W / 'timing.json')); M = T['marks']; DUR = T['dur']
ep_music = json.load(open(W / 'music.json')) if (W / 'music.json').exists() else {}
BPM = ep_music.get('bpm', 112); B = 60 / BPM; ROOT = ep_music.get('root', 50)  # D3
PROG = ep_music.get('progression', [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]])  # i  VI  III  VII (minor key)
LOGO = ep_music.get('logo', [0, 3, 5, 7])  # D F G -> A over the tonic chord
N = int((DUR + 3) * SR); bus = {k: np.zeros((N, 2)) for k in ('pad', 'bass', 'lead', 'drums', 'keys')}
sec = {}
for l in T['lines']: s = l.get('section') or 'story'; a, b = sec.get(s, (l['t'], l['t'])); sec[s] = (min(a, l['t']), max(b, l['t'] + l['d']))
def span(name, default): return sec.get(name, default)
def chords(t0, t1, voice, bar=4, vel=70):
    t, i = t0, 0
    while t < t1 - .05:
        d = min(bar * B, t1 - t); ch = PROG[i % len(PROG)]; voice(t, d, ch, i); t += d; i += 1
def pad(t, d, ch, i):
    for k in ch: place(bus['pad'], t, supersaw(ROOT + 12 + k, d, 52, cut=1400, env=(.6, .4, .8, 1.2)), .5)
def bassl(t, d, ch, i):
    for j in range(int(round(d / B))): place(bus['bass'], t + j * B, subbass(ROOT - 12 + ch[0], B * .8, 90), .7)
def plk(t, d, ch, i):
    for j in range(int(round(d / (B / 2)))): place(bus['keys'], t + j * B / 2, pluck(ROOT + 12 + ch[(j * 2) % 3] + 12 * (j % 4 == 3), B * .4, 70), .5, (-.3, .3)[j % 2])
def bel(t, d, ch, i):
    for j, k in enumerate(ch): place(bus['keys'], t + j * B, bell(ROOT + 24 + k, B * 2, 64), .35)
try:
    KICK = OneShot('tr808/bd8/*.WAV', .9); SN = OneShot('tr808/sd8/*.WAV', .6); HH = OneShot('tr808/ch8/*.WAV', .4); CL = OneShot('tr808/cp8/*.WAV', .5)
except AssertionError:
    KICK = SN = HH = CL = None; print('tr808 samples missing: drums skipped (run scripts/fetch_sounds.sh)')
def drums(t0, t1, half=False):
    if KICK is None: return
    t = t0; j = 0
    while t < t1 - .02:
        if j % 4 in ((0,) if half else (0, 2)): place(bus['drums'], t, KICK.get(0), .8)
        if j % 4 in (1, 3) and not half: place(bus['drums'], t, SN.get(0), .5)
        place(bus['drums'], t, HH.get(0), .25 if j % 2 else .35); place(bus['drums'], t + B / 2, HH.get(0), .18)
        t += B; j += 1
# --- arc
c0 = span('cold', (0, M.get('montage', 8)))
chords(0, M.get('montage', c0[1]), pad); chords(0, M.get('montage', c0[1]), bassl)
if 'montage' in M:
    m0, lg = M['montage'], M['logo']; hit = m0 + min(lg - m0 - 1.6, 999)
    chords(m0, lg, pad); chords(m0, lg, bassl); drums(m0, lg - .5)
    for j, k in enumerate(LOGO[:-1]): place(bus['lead'], lg - 1.5 - (len(LOGO) - 1 - j) * B / 2, supersaw(ROOT + 24 + k, B * .45, 96, cut=3800), .5)
    place(bus['lead'], lg - 1.5, supersaw(ROOT + 24 + LOGO[-1], 1.6, 110, cut=4200), .6)
    for k in PROG[0]: place(bus['pad'], lg - 1.5, supersaw(ROOT + 12 + k, 1.6, 90, cut=3000), .5)
st0 = span('story', (M.get('logo', 0), M.get('logo', 0)))
chords(st0[0], st0[1], plk); chords(st0[0], st0[1], bassl); drums(st0[0], st0[1], half=True)
tu = span('turn', None)
if tu: chords(tu[0], tu[1], pad)
fu = span('fundamentals', None)
if fu: chords(fu[0], fu[1], bel); chords(fu[0], fu[1], pad)
ve = span('verdict', None)
if ve: chords(ve[0], ve[1], pad); chords(ve[0], ve[1], bassl); drums(ve[0] + (ve[1] - ve[0]) / 2, ve[1], half=True)
if 'endcard' in M:  # resolve: logo motif on the relative major (+3 semitones)
    e0 = M['endcard'] - 1.2
    for j, k in enumerate(LOGO[:-1]): place(bus['lead'], e0 - (len(LOGO) - 1 - j) * B / 2, pluck(ROOT + 27 + k, B * .45, 90), .6)
    for k in (3, 7, 10, 15): place(bus['pad'], e0, supersaw(ROOT + 12 + k, M['end'] - e0, 70, cut=1800, env=(.05, .5, .8, 2.0)), .45)
    place(bus['keys'], e0, bell(ROOT + 27 + LOGO[-1], 3, 90), .5)
# --- hard stop: true silence from the bleep to the next line
if T.get('bleep'):
    a = int(T['bleep'][0] * SR); nxt = min([l['t'] for l in T['lines'] if l['t'] > T['bleep'][1]] or [T['bleep'][1] + .5])
    for x in bus.values(): x[a - 300:a] *= np.linspace(1, 0, 300)[:, None]; x[a:int(nxt * SR)] = 0
H = ir(2.4, .55); mix = bus['pad'] * .5 + conv(bus['pad'], H) * .35 + bus['bass'] * .8 + bus['lead'] * .6 + conv(bus['lead'], H) * .2 + bus['drums'] * .7 + bus['keys'] * .6 + conv(bus['keys'], H) * .25
mix = mix[:int(DUR * SR)]; mix /= np.abs(mix).max() + 1e-9
(W / 'audio').mkdir(exist_ok=True); np.save(W / 'audio' / 'music_raw.npy', mix.astype(np.float32)); print('score ok', len(mix) / SR, 's')
