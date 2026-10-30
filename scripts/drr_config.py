"""Config + episode loading shared by every script. Values like ${VAR} expand from the environment (and .env if present).
Secrets are never written to disk, logged or printed: only `secret(name)` reads them, at the moment of use."""
import os, re, json, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parent.parent

def _load_dotenv():
    p = ROOT / '.env'
    if p.exists():
        for ln in p.read_text().splitlines():
            m = re.match(r'\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$', ln)
            if m and m.group(1) not in os.environ: os.environ[m.group(1)] = m.group(2)
_load_dotenv()

def _expand(v):
    if isinstance(v, str): return re.sub(r'\$\{([A-Z0-9_]+)\}', lambda m: os.environ.get(m.group(1), ''), v)
    if isinstance(v, dict): return {k: _expand(x) for k, x in v.items()}
    if isinstance(v, list): return [_expand(x) for x in v]
    return v

def config():
    p = ROOT / 'config.yaml'
    if not p.exists(): p = ROOT / 'config.example.yaml'
    return _expand(yaml.safe_load(p.read_text()))

def secret(env_name):
    v = os.environ.get(env_name, '')
    if not v: raise SystemExit(f'missing env {env_name} (put it in .env; see .env.example)')
    return v

def episode(ep_dir):
    ep_dir = pathlib.Path(ep_dir); cfg = config()
    e = yaml.safe_load((ep_dir / 'episode.yaml').read_text())
    sub = {'VIEWER_NAME': cfg.get('viewer_name', ''), 'NOTES_NAME': cfg.get('notes_name', 'your research notes')}
    def fill(s):
        s = s.replace('{VIEWER_NAME}', sub['VIEWER_NAME']).replace('{NOTES_NAME}', sub['NOTES_NAME'])
        return re.sub(r'\s+([,.])', r'\1', re.sub(r',\s*\.', '.', s)).strip()  # "All right, ." -> "All right."
    for l in e['lines']:
        l['text'] = fill(l['text']); l['alts'] = [fill(a) for a in l.get('alts', [])]
    e['_dir'] = str(ep_dir); return e

def work_dir(ep, version):
    cfg = config(); d = (ROOT / cfg['work_root']).resolve() / ep['id'] / f'v{version}'
    d.mkdir(parents=True, exist_ok=True); return d

def assets():
    return (ROOT / config()['assets_root']).resolve()
