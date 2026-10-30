#!/usr/bin/env python3
"""Who cited the study recently? usage: citations_fetch.py EPISODE_DIR [--since YYYY-MM-DD] [--until YYYY-MM-DD]
Uses the study DOI in episode.yaml (study.doi). Queries two free indexes and keeps both raw responses:
- OpenAlex: works citing the study (filter cites:<W id>, from/to_publication_date), polite pool via OPENALEX_MAILTO
- Semantic Scholar Graph API: /paper/DOI:<doi>/citations with `contexts` (the sentences that cite it); S2_API_KEY optional
Union by DOI (else normalised title). Writes <episode>/citations/{openalex.json,s2.json,union.json}.
Report the count as "at least N": both indexes lag and miss things."""
import os, sys, json, re, time, datetime, pathlib, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); D = pathlib.Path(ep['_dir']) / 'citations'; D.mkdir(exist_ok=True)
a = sys.argv[2:]; today = datetime.date.today()
since = a[a.index('--since') + 1] if '--since' in a else today.replace(day=1).isoformat()
until = a[a.index('--until') + 1] if '--until' in a else today.isoformat()
doi = ep['study']['doi'].lower().removeprefix('https://doi.org/')
cfg = C.config().get('citations', {}); mail = cfg.get('mailto') or ''
def get(url, hdr={}):
    for k in range(4):
        try:
            r = urllib.request.Request(url, headers={'User-Agent': 'daily-research-report/1.0' + (f' (mailto:{mail})' if mail else ''), **hdr})
            return json.load(urllib.request.urlopen(r, timeout=40))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and k < 3: time.sleep(3 * (k + 1)); continue
            raise
w = get(f'https://api.openalex.org/works/doi:{doi}' + (f'?mailto={mail}' if mail else ''))
wid = w['id'].rsplit('/', 1)[-1]; oa = []; cur = '*'
while cur:
    q = dict(filter=f'cites:{wid},from_publication_date:{since},to_publication_date:{until}', per_page=200, cursor=cur)
    if mail: q['mailto'] = mail
    r = get('https://api.openalex.org/works?' + urllib.parse.urlencode(q)); oa += r['results']; cur = r['meta'].get('next_cursor') if r['results'] else None
json.dump(dict(study=w['id'], since=since, until=until, total_cited_by=w.get('cited_by_count'), results=oa), open(D / 'openalex.json', 'w'), indent=1)
hdr = {'x-api-key': os.environ[cfg.get('s2_api_key_env', 'S2_API_KEY')]} if os.environ.get(cfg.get('s2_api_key_env', 'S2_API_KEY')) else {}
s2 = []; off = 0
while off is not None:
    r = get(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/citations?fields=title,externalIds,publicationDate,venue,contexts,intents&limit=1000&offset={off}', hdr)
    s2 += r.get('data', []); off = r.get('next')
s2 = [c for c in s2 if (c['citingPaper'].get('publicationDate') or '') >= since and (c['citingPaper'].get('publicationDate') or '9') <= until]
json.dump(s2, open(D / 's2.json', 'w'), indent=1)
nt = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())[:80]
U = {}
for x in oa:
    k = (x.get('doi') or '').lower().removeprefix('https://doi.org/') or nt(x.get('title'))
    U.setdefault(k, dict(key=k, title=x.get('title'), date=x.get('publication_date'), venue=((x.get('primary_location') or {}).get('source') or {}).get('display_name'),
                         type=x.get('type'), in_openalex=True, in_s2=False, contexts=[]))
for c in s2:
    p = c['citingPaper']; k = ((p.get('externalIds') or {}).get('DOI') or '').lower() or nt(p.get('title'))
    u = U.setdefault(k, dict(key=k, title=p.get('title'), date=p.get('publicationDate'), venue=p.get('venue'), type=None, in_openalex=False, in_s2=True, contexts=[]))
    u['in_s2'] = True; u['contexts'] += c.get('contexts') or []; u['intents'] = c.get('intents')
json.dump(dict(since=since, until=until, n=len(U), openalex=len(oa), s2=len(s2), works=list(U.values())), open(D / 'union.json', 'w'), indent=1)
print(f'{since}..{until}: OpenAlex {len(oa)}, S2 {len(s2)}, union {len(U)} (say "at least {len(U)}")')
