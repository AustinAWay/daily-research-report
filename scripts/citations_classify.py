#!/usr/bin/env python3
"""Classify HOW recent papers cite the study, using only the citing sentences we can actually read.
usage: citations_classify.py EPISODE_DIR
in : citations/union.json, optional citations/review.yaml (manual labels: {key: label}; always wins over the rules)
out: citations/classified.json, citations/summary.json (the numbers the citation beat shows)
Labels: supports (builds on / cites as evidence), mentions (background, no stance), questions (limits, critique, failed replication).
Works with no readable context are counted in the total but NOT classified. Never infer a stance from a title."""
import os, sys, json, re, pathlib, yaml
sys.path.insert(0, os.path.dirname(__file__)); import drr_config as C
ep = C.episode(sys.argv[1]); D = pathlib.Path(ep['_dir']) / 'citations'; U = json.load(open(D / 'union.json'))
rv = yaml.safe_load(open(D / 'review.yaml')) if (D / 'review.yaml').exists() else {}
Q = r"\b(however|but|limit|limitation|caution|mixed|fail|did not|contrary|criti|small sample|short[- ]term|novelty|question)"
S = r"\b(consistent with|in line with|building on|following|demonstrat|showed|found that|evidence|effective|improv|outperform|doubl)"
out = []
for w in U['works']:
    ctx = ' '.join(w['contexts'])
    lab = rv.get(w['key']) or (None if not ctx.strip() else 'questions' if re.search(Q, ctx, re.I) else 'supports' if re.search(S, ctx, re.I) else 'mentions')
    out.append({**w, 'label': lab, 'label_source': 'review' if w['key'] in rv else 'rules' if lab else None})
json.dump(out, open(D / 'classified.json', 'w'), indent=1)
cnt = {k: sum(1 for o in out if o['label'] == k) for k in ('supports', 'mentions', 'questions')}; rd = sum(cnt.values())
card = dict(at_least=U['n'], readable=rd, sources_line='OpenAlex + Semantic Scholar · ' + U['since'] + ' to ' + U['until'],
            rows=[dict(n=cnt['supports'], label='build on it', color='blue'), dict(n=cnt['mentions'], label='mention it', color='ink'),
                  dict(n=cnt['questions'], label='push back', color='coral')],
            footer=f'classified from the {rd} citing sentences we could read')
json.dump(dict(n=U['n'], readable=rd, counts=cnt, card=card), open(D / 'summary.json', 'w'), indent=1)
print(json.dumps(card, indent=1)); print('Check every rules label by reading the contexts in classified.json; put fixes in review.yaml.')
