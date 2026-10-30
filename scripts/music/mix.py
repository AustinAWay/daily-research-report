#!/usr/bin/env python3
"""Final mix: voice + music/SFX with a voice-keyed duck, loudness to -14 LUFS integrated, true peak <= -1 dBTP.
usage: mix.py WORK_DIR [DUCK_DB=9] [BASE_DB=-3]
in : vo/vo.wav, audio/music_fx.npy (sfx.py; falls back to music_raw.npy)   out: audio/mix_final.wav, audio/music_ducked.wav
- duck: 5 ms RMS frames (hop 240), voice present above -42 dBFS, one-pole attack 30 ms / release 350 ms, DUCK dB under the voice
- music-only showcase spans (montage -> logo, endcard -> end) get a lift (+5 / +4 dB, 80 ms ramps)
- the bleep hard stop is true silence in the music bus until the next line
- loudness: ebur128 integrated trim, then alimiter at 192 kHz (inter-sample peaks), re-trim, up to 3 passes until |I+14|<=0.2 and TP<=-1"""
import sys, json, re, subprocess, pathlib, numpy as np, soundfile as sf
SR = 48000; W = pathlib.Path(sys.argv[1]); A = W / 'audio'
DUCK = float(sys.argv[2]) if len(sys.argv) > 2 else 9.0; BASE = float(sys.argv[3]) if len(sys.argv) > 3 else -3.0
T = json.load(open(W / 'timing.json')); MK = T['marks']; DUR = T['dur']
v, _ = sf.read(W / 'vo' / 'vo.wav', dtype='float64'); v = v.mean(1) if v.ndim > 1 else v
src = A / 'music_fx.npy' if (A / 'music_fx.npy').exists() else A / 'music_raw.npy'
m = np.load(src).astype(np.float64); n = min(len(v), len(m)); v, m = v[:n], m[:n]
def seg_gain(n, spans, r=.08):
    g = np.zeros(n); t = np.arange(n) / SR
    for a, b, d in spans: g = np.maximum(g, d * np.clip(np.minimum((t - a) / r + 1, (b - t) / r + 1), 0, 1))
    return 10 ** (g / 20)
spans = [(MK[a], MK[b], d) for a, b, d in (('montage', 'logo', 5.0), ('endcard', 'end', 4.0)) if a in MK and b in MK]
m *= seg_gain(n, spans)[:, None]
if T.get('bleep'):
    nxt = min([l['t'] for l in T['lines'] if l['t'] > T['bleep'][1]] or [T['bleep'][1] + .5])
    a, b, k = int(round(T['bleep'][0] * SR)), int(round(nxt * SR)), int(.006 * SR); m[a - k:a] *= np.linspace(1, 0, k)[:, None]; m[a:b] = 0
hop = 240; fr = np.sqrt(np.convolve(v ** 2, np.ones(hop) / hop, 'same')[::hop] + 1e-12); sp = (20 * np.log10(fr) > -42).astype(float)
g = np.zeros_like(sp); s = 0.0; ka, kr = 1 - np.exp(-1 / (.03 * SR / hop)), 1 - np.exp(-1 / (.35 * SR / hop))
for i, x in enumerate(sp): s += (ka if x > s else kr) * (x - s); g[i] = s
gain = 10 ** (np.interp(np.arange(n) / hop, np.arange(len(g)), -DUCK * g) / 20)
md = m * gain[:, None] * 10 ** (BASE / 20)
def lufs(x, path):
    sf.write(path, np.clip(x, -1, 1).astype(np.float32), SR)
    o = subprocess.run(['ffmpeg', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', o)[-1])
mix = np.stack([v, v], 1) + md; cut = int(round(DUR * SR)); mix[cut:] = 0
I, tp = lufs(mix, A / '_pre.wav'); gf = 10 ** ((-14 - I) / 20); mix *= gf; sf.write(A / 'music_ducked.wav', (md * gf).astype(np.float32), SR)
out = A / 'mix_final.wav'; sf.write(out, mix.astype(np.float32), SR)
for it in range(3):
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(out), '-af', 'aresample=192000,alimiter=limit=0.79:attack=2:release=60:level=0,aresample=48000',
                    '-c:a', 'pcm_f32le', str(A / '_lim.wav')], check=True)
    y, _ = sf.read(A / '_lim.wav', dtype='float32'); y[cut:] = 0; I3, tp3 = lufs(y, A / '_lim.wav'); print(f'pass {it}: {I3:.2f} LUFS, TP {tp3:.2f} dBTP')
    if abs(I3 + 14) <= .2 and tp3 <= -1.0: sf.write(out, y, SR); break
    sf.write(out, (y * 10 ** ((-14 - I3) / 20)).astype(np.float32), SR)
else: raise SystemExit('loudness did not converge; lower BASE_DB or check for clipping SFX')
print('mix_final.wav', lufs(sf.read(out, dtype='float32')[0], A / '_chk.wav'))
