#!/usr/bin/env python3
"""Splice the rendered pieces, mux the final mix, make the share encode, measure, and record.
usage: finish.py EPISODE_DIR VERSION
in : <work>/parts/p*.mp4 (run_render.sh), <work>/audio/mix_final.wav (music/mix.py)
out: <work>/out/<id>_v<N>_master.mp4 (x264 crf 15 + AAC 256k), <id>_v<N>_share.mp4 (crf 23, maxrate 7M, faststart),
     contact.jpg, loudness.txt, SHA256SUMS; finals are made read-only; OUTPUTS.md is written LAST (its presence = finished)."""
import os, sys, re, json, glob, hashlib, subprocess, pathlib
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); ver = sys.argv[2]; W = C.work_dir(ep, ver); cfg = C.config(); S = cfg['share']
O = W / 'out'; O.mkdir(exist_ok=True); T = json.load(open(W / 'timing.json')); FPS = 30; NF = round(T['dur'] * FPS)
run = lambda *a: subprocess.run(list(a), check=True, capture_output=True, text=True)
def nframes(p):
    o = run('ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', p).stdout
    return int(o.strip().rstrip(','))  # ffprobe csv can end with a trailing comma
parts = sorted(glob.glob(str(W / 'parts' / 'p*_*.mp4'))); parts = [p for p in parts if '.tmp.' not in p]
spans = [tuple(map(int, re.findall(r'p(\d+)_(\d+)', p)[0])) for p in parts]
cov = 0
for (a, b) in spans:
    if a != cov: raise SystemExit(f'gap or overlap in pieces at frame {cov} (next piece starts {a}); re-run run_render.sh')
    cov = b
if cov < NF: raise SystemExit(f'pieces cover {cov} of {NF} frames; re-run run_render.sh')
inp, fl = [], []
for i, (p, (a, b)) in enumerate(zip(parts, spans)):
    skip = 1 if a > 0 else 0; n = nframes(p)
    if n != b - a + skip: raise SystemExit(f'{p}: {n} frames, expected {b-a+skip}')
    inp += ['-i', p]; fl.append(f'[{i}:v]trim=start_frame={skip},setpts=PTS-STARTPTS[v{i}]')
mix = W / 'audio' / 'mix_final.wav'; ia = len(parts)
fc = ';'.join(fl) + ';' + ''.join(f'[v{i}]' for i in range(len(parts))) + f'concat=n={len(parts)}:v=1:a=0[v]'
master = O / f"{ep['id']}_v{ver}_master.mp4"; share = O / f"{ep['id']}_v{ver}_share.mp4"
for f in (master, share):
    if f.exists(): raise SystemExit(f'{f} exists: never overwrite a final; make a new version folder')
tmp = O / 'master.tmp.mp4'
run('ffmpeg', '-y', '-loglevel', 'error', *inp, '-i', str(mix), '-filter_complex', fc, '-map', '[v]', '-map', f'{ia}:a',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
    '-c:a', 'aac', '-b:a', '256k', '-t', f"{T['dur']:.4f}", '-movflags', '+faststart', str(tmp)); os.replace(tmp, master)
tmp = O / 'share.tmp.mp4'
run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(master), '-c:v', 'libx264', '-preset', 'slow', '-crf', str(S['crf']), '-maxrate', S['maxrate'],
    '-bufsize', S['bufsize'], '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(tmp)); os.replace(tmp, share)
lo = subprocess.run(['ffmpeg', '-nostats', '-i', str(share), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = lo[lo.rfind('Summary:'):]; (O / 'loudness.txt').write_text(summ)
run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(share), '-vf', 'fps=1/2,scale=320:-1,tile=8x10', '-frames:v', '1', str(O / 'contact.jpg'))
run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(share), '-ac', '1', '-ar', '16000', str(W / 'qa_16k.wav'))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
fin = [master, share, O / 'contact.jpg', O / 'loudness.txt']
(O / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in fin))
for p in fin + [O / 'SHA256SUMS']: os.chmod(p, 0o444)
I = re.findall(r'I:\s+(-?[\d.]+) LUFS', summ); TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', summ)
(O / 'OUTPUTS.md').write_text(f"# {ep['id']} v{ver}\n\nshare: {share.name} ({share.stat().st_size} B, {T['dur']:.3f} s, {NF} frames)\n"
    f"master: {master.name}\nloudness: {I[-1] if I else '?'} LUFS, true peak {TP[-1] if TP else '?'} dBTP\nsha256: see SHA256SUMS\n")
print(open(O / 'OUTPUTS.md').read())
