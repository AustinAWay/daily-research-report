#!/usr/bin/env bash
# One episode, end to end. usage: run_episode.sh EPISODE_DIR VERSION [--dry-run] [--skip-citations]
#   full   : citations -> tts -> build_vo -> page -> cues -> score -> sfx -> mix -> render -> finish -> qa -> sfx_align
#   dry-run: no TTS key needed. Synthetic word timings + silent voice -> page -> cues -> 10 stills -> score -> sfx -> mix.
#            Proves the machine can build an episode. Set DRY_FULL=1 to also render + finish a full (silent-voice) film.
# Every step is resumable: TTS takes are cached, render pieces are skipped when present, finish.py refuses to overwrite.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(dirname "$HERE"); EP=$1; V=$2; shift 2
DRY=0; SKIPC=0; for a in "$@"; do case $a in --dry-run) DRY=1;; --skip-citations) SKIPC=1;; esac; done
[ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }      # secrets come from env only; never echoed
PY=${PY:-python3}; [ -x "$ROOT/.venv/bin/python" ] && PY="$ROOT/.venv/bin/python"
W=$($PY -c "import sys;sys.path.insert(0,'$HERE');import drr_config as C;print(C.work_dir(C.episode('$EP'),'$V'))")
step(){ echo "== $(date +%H:%M:%S) $*"; }
command -v free >/dev/null && free -g | sed -n 2p
if [ $SKIPC = 0 ] && [ ! -f "$EP/citations/summary.json" ]; then
  step citations; $PY "$HERE/citations_fetch.py" "$EP"; $PY "$HERE/citations_classify.py" "$EP"; fi
if [ $DRY = 1 ]; then step dry timing; $PY "$HERE/dry_timing.py" "$EP" "$V"
else step tts; $PY "$HERE/tts_cartesia.py" "$EP" "$V"; step build_vo; $PY "$HERE/build_vo.py" "$EP" "$V"; fi
step page; $PY "$HERE/episode.py" "$EP" "$V"
step cues; node "$HERE/render.js" "$W/page" cues "$W/cues.json"
if [ $DRY = 1 ]; then
  D=$($PY -c "import json;print(json.load(open('$W/timing.json'))['dur'])")
  TS=$($PY -c "d=$D;print(','.join(str(round(d*k/10,2)) for k in range(10)))")
  step stills; node "$HERE/render.js" "$W/page" stills "$TS" "$W/stills"
fi
step score; $PY "$HERE/music/score.py" "$W"; step sfx; $PY "$HERE/music/sfx.py" "$W"; step mix; $PY "$HERE/music/mix.py" "$W"
if [ $DRY = 1 ] && [ "${DRY_FULL:-0}" != 1 ]; then step "dry run OK: $W (stills in $W/stills, mix in $W/audio/mix_final.wav)"; exit 0; fi
step render; bash "$HERE/run_render.sh" "$W"
step finish; $PY "$HERE/finish.py" "$EP" "$V"
if [ $DRY = 0 ]; then step qa; $PY "$HERE/qa.py" "$EP" "$V"; fi
step sfx_align; $PY "$HERE/sfx_align.py" "$W"
step "done: $W/out/OUTPUTS.md"
