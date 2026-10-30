# BOOTSTRAP: instructions for an AI assistant

**Trigger.** When the user says any of: "Hey, set this up", "Set this up", "Set up the Daily Research Report from this
repo", or "Install the daily research report", execute this file from top to bottom.

**How to run it.**
- Every step is idempotent. Run its *check* first and skip the step when the check already passes.
- After each step, run its *verify* and report one line: `step N: ok` or `step N: FAILED (<reason>)`.
- Stop at the first failure you cannot fix yourself, and tell the user exactly what is needed.
- Never print, echo, log, paste or commit a secret. Never ask for a secret in chat. Use your platform's secret-request or
  vault flow so the value lands in an environment variable or in `.env` without passing through the conversation.
- Never send, post or publish anything during setup. All work stays on this machine.
- Work from the repository root (the folder that holds this file). Below, `$REPO` means that folder.

---

## Step 1: Check prerequisites
Check:
```bash
python3 --version; node --version; npm --version; ffmpeg -version | head -1; ffprobe -version | head -1; git --version; curl --version | head -1
ffmpeg -hide_banner -filters | grep -E 'ebur128|alimiter' ; ffmpeg -hide_banner -encoders | grep libx264
free -g 2>/dev/null || vm_stat; df -h .
```
Need Python >= 3.10, Node >= 18, ffmpeg with libx264 + ebur128 + alimiter, >= 8 GB RAM, >= 3 GB free disk.
Fix: install missing tools with the system package manager (e.g. `apt-get install -y ffmpeg nodejs npm python3-venv git curl unzip`
or `brew install ffmpeg node python git`). Ask the user before installing system packages if you lack permission.
Verify: every command above prints a version; both filters and libx264 are listed.

## Step 2: Python and Node dependencies
Check: `test -x .venv/bin/python && .venv/bin/python -c "import numpy,scipy,soundfile,yaml,requests,pedalboard,faster_whisper" && test -d node_modules/playwright`
Do:
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install
# Chrome: use a system Chrome/Chromium via CHROME_PATH, or install Playwright's bundled one:
[ -n "${CHROME_PATH:-}" ] || npx playwright install chromium
```
Verify: the check command exits 0.

## Step 3: Local config
Check: `test -f config.yaml && test -f .env`
Do: `cp -n config.example.yaml config.yaml; cp -n .env.example .env` (never overwrite existing files).
Ask the user (normal chat; these are not secrets): the research **topic** (default "learning science"), an optional
**viewer name** for the greeting, and what to call their **notes**. Write them into `config.yaml` (`topic`,
`viewer_name`, `notes_name`).
Verify: `.venv/bin/python -c "import sys;sys.path.insert(0,'scripts');import drr_config as C;c=C.config();print(c['topic'])"` prints the topic.

## Step 4: Secrets (through the secret-request flow, never chat)
Needed: `CARTESIA_API_KEY` and `CARTESIA_VOICE_ID`. Optional: `S2_API_KEY`, `OPENALEX_MAILTO`.
Check (prints only yes/no, never the value):
```bash
for v in CARTESIA_API_KEY CARTESIA_VOICE_ID; do val=$(printenv $v || sed -n "s/^$v=//p" .env 2>/dev/null | head -1); case "$val" in ""|your-*) echo "$v: missing";; *) echo "$v: set";; esac; done; unset val
```
Do: for each missing one, use your assistant's secret-request flow (a secure form / vault entry) to have the user provide it,
then make it available as an environment variable or write it into `.env` without displaying it. Tell the user where to get it:
Cartesia API key at https://play.cartesia.ai (API keys page); the voice id from a voice they pick or clone there.
If the user wants to skip voice for now, continue: Step 7 (dry run) needs no key.
Verify: the check prints `set` for both (or the user chose to skip).

## Step 5: Fetch third-party code, fonts and sounds (not stored in git)
Check: `test -f assets/vendor/three.module.min.js && test -f assets/vendor/gsap.min.js && test -d assets/fonts && test -d assets/sounds/tr808 && test -d assets/sounds/kenney_interface/Audio`
Do:
```bash
bash scripts/fetch_vendor.sh      # three.js r170 + addons, GSAP + plugins (npm), Google Fonts (OFL)
bash scripts/fetch_sounds.sh      # CC0 packs, ~1.5 GB; resumable
```
If the Kenney download cannot be scraped, the script prints a manual URL: tell the user, or continue (SFX that need it are skipped).
Verify: the check exits 0; `ls assets/sounds` lists vsco, vdrums, tr808, kenney_interface.

## Step 6: Create the agents
Check: your assistant already has agents or saved instructions named "DRR <Role>" for each file in `agents/`.
Do: for each file in `agents/*.md`, create one agent / saved instruction set named `DRR <Role title>` whose instructions are
the file's full contents plus: "The repository is at $REPO. Work only inside it." If your assistant cannot create separate
agents, save them as one combined instruction set; the Research Lead then plays every role in order.
Roles: research-lead, source-hunter, fundamentals, research-critic, script-writer, fact-reviewer, motion-designer,
sound-designer, render-engineer, harsh-reviewer.
Verify: list your agents; all ten exist (or the combined set exists). Do not duplicate an agent that already exists: update it.

## Step 7: Dry run on the example study (no TTS key needed)
Check: `test -f work/kestin-ai-tutor/v0/audio/mix_final.wav && ls work/kestin-ai-tutor/v0/stills/*.jpg`
Do:
```bash
free -g 2>/dev/null | sed -n 2p
.venv/bin/python scripts/fetch_images.py examples/kestin-ai-tutor
bash scripts/run_episode.sh examples/kestin-ai-tutor 0 --dry-run --skip-citations
```
Takes 3-6 minutes. It builds the page, records 70-ish cues, renders 10 stills, and makes a full score + SFX + mix.
Verify:
- the last line printed is `dry run OK: ...`
- `work/kestin-ai-tutor/v0/stills/` holds 10 JPGs: open two or three and confirm text and visuals are visible (not blank)
- `ffmpeg -hide_banner -nostats -i work/kestin-ai-tutor/v0/audio/mix_final.wav -af ebur128 -f null - 2>&1 | grep -E "I:|Peak"` shows about -14 LUFS
Optional (2-5 hours on a 4-core CPU): `DRY_FULL=1 bash scripts/run_episode.sh examples/kestin-ai-tutor 0 --dry-run --skip-citations` renders the whole film with a silent voice.
Optional (with a key): `bash scripts/run_episode.sh examples/kestin-ai-tutor 1 --skip-citations` makes the real example episode.

## Step 8: Create the weekday-morning routine
Check: your assistant already has a routine named "Daily Research Report".
Do: create a recurring routine named **Daily Research Report**, Monday-Friday at 06:00 in the user's time zone (ask them to
confirm the time), whose instruction is:
> Run the Daily Research Report in $REPO. Act as the DRR Research Lead (agents/research-lead.md). Pick one new study in
> the configured topic, create episodes/<id>/ from templates/episode/episode.yaml, run the roles in order (SETUP.md,
> section 6), build with `bash scripts/run_episode.sh episodes/<id> <N>`, post a status line to the episode PROGRESS.md
> every 50 minutes, and when QA passes and the Harsh Reviewer signs off, tell me the study, the verdict, and the share MP4
> path. Never overwrite a finished version. Never publish anything.

If your assistant has no routine feature, give the user a cron line instead (and do not install it without asking):
`0 6 * * 1-5 cd $REPO && <your assistant CLI> "Run the Daily Research Report ..."`
Verify: the routine is listed with the right days, time and zone.

## Step 9: Report
Tell the user, in one short message: which steps passed, which were skipped and why (e.g. key not provided), where the dry-run
stills are, when the first scheduled run will happen, and how to run one now ("Run today's Daily Research Report").
