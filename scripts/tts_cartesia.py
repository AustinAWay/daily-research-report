#!/usr/bin/env python3
"""Generate voice takes for every scripted line with Cartesia TTS (SSE, word timestamps).
usage: tts_cartesia.py EPISODE_DIR VERSION [LINE_ID ...]
Writes <work>/vo/takes/<line><take>.wav + .json (text, words with start/end). Cached: an existing .json is never re-requested.
Each line gets voice.takes takes of its main text plus one take per entry in `alts` (shorter wordings for tight slots).
The API key is read from env (voice.api_key_env) only; it is never printed or written."""
import os, sys, json, base64, wave, requests, numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); ver = sys.argv[2]; only = set(sys.argv[3:])
cfg = C.config(); V = cfg['voice']; SR = int(V.get('sample_rate', 48000))
if not V.get('voice_id'): raise SystemExit('set CARTESIA_VOICE_ID (see .env.example)')
out = C.work_dir(ep, ver) / 'vo' / 'takes'; out.mkdir(parents=True, exist_ok=True)
LET = 'abcdefghijklmnopqrstuvwxyz'
jobs = []
for l in ep['lines']:
    if only and l['id'] not in only: continue
    texts = [l['text']] * int(l.get('takes', V.get('takes', 3))) + l.get('alts', [])
    for i, t in enumerate(texts): jobs.append((l['id'], LET[i], l.get('emotion'), t, float(l.get('speed', V.get('speed', 1.0)))))
def go(job):
    lid, k, emo, txt, spd = job; tag = out / f'{lid}{k}'
    if tag.with_suffix('.json').exists(): return lid + k, 'cached'
    gc = {'speed': spd}
    if emo: gc['emotion'] = emo
    body = dict(model_id=V['model_id'], transcript=txt, voice={'mode': 'id', 'id': V['voice_id']},
                output_format=dict(container='raw', encoding='pcm_f32le', sample_rate=SR), language='en',
                add_timestamps=True, generation_config=gc)
    r = requests.post('https://api.cartesia.ai/tts/sse', json=body, stream=True, timeout=300,
                      headers={'Authorization': 'Bearer ' + C.secret(V.get('api_key_env', 'CARTESIA_API_KEY')), 'Cartesia-Version': V['version']})
    if r.status_code != 200: return lid + k, 'HTTP %d %s' % (r.status_code, r.text[:200])
    pcm = bytearray(); X = []
    for ln in r.iter_lines():
        ln = ln.decode()
        if not ln.startswith('data:'): continue
        ev = json.loads(ln[5:]); t = ev.get('type')
        if t == 'chunk' and ev.get('data'): pcm += base64.b64decode(ev['data'])
        elif t == 'timestamps': wt = ev['word_timestamps']; X += list(zip(wt['words'], wt['start'], wt['end']))
        elif t == 'error': return lid + k, 'ERR ' + str(ev)[:200]
    a = np.frombuffer(bytes(pcm), '<f4').copy()
    with wave.open(str(tag) + '.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes())
    json.dump(dict(id=lid, take=k, text=txt, speed=spd, emotion=emo, dur=len(a) / SR,
                   words=[dict(w=w, s=s, e=e) for w, s, e in X]), open(str(tag) + '.json', 'w'))
    return lid + k, '%.2fs' % (len(a) / SR)
with ThreadPoolExecutor(4) as ex:
    for k, s in ex.map(go, jobs): print(k, s, flush=True)
