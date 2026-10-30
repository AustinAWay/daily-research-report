# Daily Research Report

## Set it up in one sentence
Copy this repository into your AI assistant's workspace and say:

> **Hey, set this up.**

The assistant follows **[BOOTSTRAP.md](BOOTSTRAP.md)**: it checks prerequisites, installs dependencies, asks for your
Cartesia key through its secure secret flow (never in chat), creates the ten agents from `agents/`, runs a dry run on the
example study, and schedules a weekday-morning routine. Humans: read **[SETUP.md](SETUP.md)** for the full guide.

## What it makes
Each weekday morning: one recent study, checked against the fundamentals and against who cited it this month, as a
2-4 minute, 1080p30 motion-graphics video with a voiced host, an original score, word-synced visuals and SFX, plus an
accuracy audit, a sources list and an automatic QA report.

- **Accuracy first.** A line-by-line audit happens before any voice is generated; preprints are labelled; citation counts
  are "at least N" from OpenAlex + Semantic Scholar, classified only from citing sentences that can actually be read.
- **Word-synced.** Every visual beat is keyed to a spoken word (TTS word timestamps); every visual hit emits a cue, and a
  sound lands on it within 40 ms.
- **Deterministic, resumable rendering.** Three.js + GSAP pages are seeked frame by frame in headless Chrome, in
  chunks that resume after a crash.
- **Clean audio.** Voice-keyed ducking, -14 LUFS integrated, true peak <= -1 dBTP.
- **No media in git.** Fonts, libraries, sample packs and images are fetched by scripts under their own licenses.

## Layout
```
BOOTSTRAP.md            step-by-step setup for an assistant (idempotent, with checks)
SETUP.md                prerequisites, accounts, roles, schedule
SKILL.md                the recipe (for assistants that load skills)
agents/                 one copy-paste instruction file per role
config.example.yaml     -> config.yaml (topic, voice, render, loudness)
.env.example            -> .env (key names only; never commit .env)
scripts/                pipeline (see SETUP.md section 5); run_episode.sh runs it all
scripts/music/          original score, SFX on cues, mix
templates/page/         the motion-graphics engine + generic, data-driven scenes
templates/episode/      blank episode.yaml
examples/kestin-ai-tutor/  a complete example episode (script, beats, audit, citations, image licenses)
docs/                   style rules, audit template, sound sources
```

## Quick start (by hand)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && npm install
cp -n config.example.yaml config.yaml && cp -n .env.example .env     # then fill .env yourself
bash scripts/fetch_vendor.sh && bash scripts/fetch_sounds.sh
.venv/bin/python scripts/fetch_images.py examples/kestin-ai-tutor
bash scripts/run_episode.sh examples/kestin-ai-tutor 0 --dry-run --skip-citations   # no key needed
bash scripts/run_episode.sh examples/kestin-ai-tutor 1 --skip-citations             # real voice (needs .env)
```

## License
MIT for the code in this repository. Downloaded dependencies keep their own licenses (SETUP.md section 8).
