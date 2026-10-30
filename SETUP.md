# Setup guide: prerequisites, roles, accounts, schedule

This is the human-readable guide. If you are an AI assistant asked to "set this up", follow **BOOTSTRAP.md** step by step;
it does everything below in order and checks each step.

## 1. What you get
Every weekday morning, a team of agents picks one recent study, checks it against the fundamentals and its recent
citations, writes and fact-checks a 2-4 minute script, voices it, scores it, renders a 1080p30 motion-graphics video, runs
automatic QA, and hands you the finished MP4 with an accuracy audit and a sources list.

## 2. Machine requirements
| need | version / size | why |
|---|---|---|
| Linux or macOS, x86_64 or arm64 | | |
| Python | 3.10+ | pipeline scripts (`requirements.txt`, installed into `.venv`) |
| Node.js + npm | 18+ | the renderer (`render.js`, Playwright) |
| Chrome / Chromium | any current | headless rendering; Playwright's bundled Chromium works (`npx playwright install chromium`) |
| ffmpeg + ffprobe | 5+ with libx264, ebur128, alimiter | encode, splice, loudness |
| git, curl, unzip | | fetch scripts |
| RAM | 8 GB minimum, 16 GB comfortable | each headless Chrome render ~1.5 GB; audio steps ~2 GB |
| Disk | ~3 GB free | sample packs (~1.5 GB), vendor libs, one episode's frames/pieces |
| CPU | 4+ cores (more = faster) | CPU rendering is about 1-3 s per frame per render process: a 3-minute film (~5,400 frames) takes about 2-5 hours on 4 cores. With RAM to spare, run 2-3 `run_render.sh` processes on disjoint frame ranges; `Q=lite` trades post-FX for speed |

On a shared machine, set `RENDER_LOCK` (a file path) so only one render runs at a time, and check `free -g` before builds.

## 3. Accounts and keys (you bring your own)
| what | required? | where it goes |
|---|---|---|
| **Cartesia** text-to-speech API key | yes, for real episodes (the dry run needs none) | env `CARTESIA_API_KEY` (in `.env`, git-ignored) |
| Cartesia voice id | yes | env `CARTESIA_VOICE_ID`: pick or clone a voice in your Cartesia account |
| OpenAlex | no key needed | optional `OPENALEX_MAILTO` (an email for the polite pool) |
| Semantic Scholar Graph API | no key needed | optional `S2_API_KEY` for higher rate limits |
| Images | no account | Wikimedia Commons (CC0 / PD / CC BY / CC BY-SA); credit every image |
| Music / SFX | no account | original score generated locally + CC0 packs (docs/SOUND_SOURCES.md) |
| GSAP | no account | fetched from npm; GSAP's "standard no-charge license" (read it before commercial use) |

Never paste a key into chat, a script, a commit or a log. Keys go only in `.env` (copied from `.env.example`) or your
assistant's own secret store, which exports them as environment variables.

## 4. The agent roles
Each role has a generic, copy-paste instruction file in `agents/`. One assistant can play every role in sequence, or you
can create one agent per role. Recommended: one coordinator plus helpers.

| role | file | does |
|---|---|---|
| Research Lead (coordinator) | agents/research-lead.md | picks the study, dispatches the roles, enforces time boxes, ships |
| Source Hunter | agents/source-hunter.md | primary sources, core facts, recent citations, licensed images |
| Fundamentals Researcher | agents/fundamentals.md | the underlying science, sourced |
| Research Critic | agents/research-critic.md | design threats, overclaiming, the "hold on" caveat, verdict |
| Report / Script Writer | agents/script-writer.md | voice-over lines + word-keyed on-screen beats (episode.yaml) |
| Fact Reviewer (single-source-of-truth) | agents/fact-reviewer.md | line-by-line accuracy audit before any voice is made |
| Motion Designer | agents/motion-designer.md | the page engine and beat visuals; stills checks |
| Sound Designer | agents/sound-designer.md | score, SFX on cues, mix to -14 LUFS |
| Render Engineer | agents/render-engineer.md | chunked render, finish, QA |
| Harsh Final Reviewer | agents/harsh-reviewer.md | watches the film, blocks the ship until must-fixes are fixed |

## 5. Pipeline (what runs, in order)
```
citations_fetch.py -> citations_classify.py        who cited the study recently, and how
tts_cartesia.py -> build_vo.py                     voice takes -> best take per line -> vo.wav + timing.json
episode.py                                         page for this episode (beats keyed to spoken words)
render.js cues                                     every visual hit -> cues.json
music/score.py -> music/sfx.py -> music/mix.py     original score, SFX on cues, ducked mix at -14 LUFS
run_render.sh -> finish.py                         resumable chunked render -> master + share MP4
qa.py, sfx_align.py                                transcript, holds, dark frames, loudness, SFX timing
```
`scripts/run_episode.sh EPISODE_DIR VERSION` runs all of it. `--dry-run` runs without a TTS key (synthetic timing,
silent voice, stills only) to prove the machine works.

## 6. Daily schedule (weekdays; times in your local zone)
| time | step | budget |
|---|---|---|
| 06:00 | Research Lead picks the study; Source Hunter + citations | 40 min |
| 06:40 | Fundamentals + Research Critic (in parallel) | 30 min |
| 07:10 | Script Writer | 30 min |
| 07:40 | Fact Reviewer audit -> fixes -> re-audit | 30 min |
| 08:10 | Voice (TTS + build_vo), page, stills check, score / SFX / mix | 40 min |
| 08:50 | Render (chunked, resumable) + finish + QA | 2-4 h on a 4-core CPU |
| ~12:00 | Harsh Final Reviewer; must-fixes go into v<N+1> (re-render only the changed frame ranges) | 30-60 min |
| ~12:30 | Deliver: share MP4 path, audit, sources, caveats | |

On a faster machine (8+ cores, or several render processes) everything after 08:50 shrinks accordingly.
Status line every 50 minutes in the episode's PROGRESS.md. Cut scope before accuracy.

## 7. Files you edit
- `config.yaml` (copy of config.example.yaml): topic, viewer name, voice model/speed, render and loudness settings.
- `.env` (copy of .env.example): keys and optional paths. Never committed.
- `episodes/<id>/episode.yaml`: one per episode (start from templates/episode/episode.yaml).

## 8. Licenses of what gets downloaded
Code here is MIT. Downloaded at setup and never committed: three.js (MIT), GSAP + plugins (GSAP standard license), Google
Fonts (OFL), sample packs (CC0), Playwright (Apache-2.0), pedalboard (GPL-3, used as a tool), faster-whisper (MIT) and its
model weights. Images: per-file Commons licenses recorded in each episode's IMAGES.md.
