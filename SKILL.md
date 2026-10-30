---
name: daily-research-report
description: Make a daily, fact-checked, 2-4 minute motion-graphics video about one research study (voice, original score, word-synced visuals, accuracy audit). Use when asked to run, build, fix or schedule the Daily Research Report, or to "set this up" from this repository (then follow BOOTSTRAP.md).
---

# Daily Research Report

If this repository has not been set up on this machine yet (no `.venv/`, no `assets/vendor/`), follow BOOTSTRAP.md first.

## Recipe for one episode
1. **Pick** one recent study in `config.yaml: topic` (Research Lead). New folder `episodes/<id>/` from `templates/episode/`.
2. **Source** it (agents/source-hunter.md): open the paper itself; record n, design, comparison, outcome, effect, test
   timing, stated limits. `scripts/citations_fetch.py` + `citations_classify.py` for who cited it this month.
3. **Fundamentals + critique** in parallel (agents/fundamentals.md, agents/research-critic.md).
4. **Script** (agents/script-writer.md): `lines` (cold -> story -> turn -> fundamentals -> verdict) and word-keyed `beats`.
5. **Audit before voice** (agents/fact-reviewer.md): every row PASS in `ACCURACY_AUDIT.md`.
6. **Build**: `bash scripts/run_episode.sh episodes/<id> <N>` (TTS takes are cached; render pieces resume).
   Check stills at beat times before the full render (`node scripts/render.js PAGE stills t1,t2 OUT`).
7. **QA + harsh review**: `out/QA.md` must pass; agents/harsh-reviewer.md must sign off. Fixes go into `v<N+1>`; never
   overwrite a finished version (finals are read-only, OUTPUTS.md is written last).
8. **Deliver**: study, verdict, confidence, share MP4 path, caveats. Do not publish anything unless asked.

## Rules that matter
- Every number, name and date on screen or in the voice traces to a source opened this run. Preprints say PREPRINT.
- Citation counts are "at least N". Classify a citation only from a sentence you can read.
- Secrets only from env (`CARTESIA_API_KEY`, `CARTESIA_VOICE_ID`); never print, log or commit them.
- Something moves at all times (no hold > 1.5 s); text on screen >= 1.2 s; every visual hit emits a cue.
- -14 LUFS, true peak <= -1 dBTP; the voice always wins.
- Check `free -g` before renders; on shared machines set `RENDER_LOCK`. Status line every 50 minutes.

## Troubleshooting
- `render.js` exits 2 (NOT READY): a beat references a (line, word) that is not in timing.json; `episode.py` lists them.
- exit 3: a page error; open `work/<id>/v<N>/page/index.html` in a browser and read the console.
- `build_vo.py` picks a bad take: `--pick LINE=take`. A line too long for its slot: add `alts:` or `max_dur:`.
- `mix.py` fails to converge: lower `audio.music_base_db` or `duck_db` in config.yaml.
