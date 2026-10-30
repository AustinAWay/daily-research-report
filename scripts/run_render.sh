#!/usr/bin/env bash
# Resumable chunked render. usage: run_render.sh WORK_DIR [RANGES]
#   RANGES: "f0:f1 f0:f1 ..." (default: the whole film). Pieces are <= CHUNK frames (default 300), so one piece is a few minutes
#   and a crash loses at most one piece. Re-running skips pieces that already exist (written to .tmp then renamed).
#   Each piece starts one frame early (the first frame after page load can differ); finish.py drops that frame.
#   Optional: RENDER_LOCK=/path/to/lockfile serializes renders on a shared machine (flock).
# Done = every expected piece file exists and this script exited 0. Do not grep a log for a "done" word: an appended log can
# still hold one from an earlier run.
set -euo pipefail
W=$(cd "$1" && pwd); HERE=$(cd "$(dirname "$0")" && pwd); CHUNK=${CHUNK:-300}
FR=$(python3 -c "import json,math;print(round(json.load(open('$W/timing.json'))['dur']*30))")
RANGES=${2:-"0:$FR"}; PD=$W/parts; mkdir -p "$PD"
command -v free >/dev/null && free -g | sed -n 2p
for R in $RANGES; do a=${R%:*}; b=${R#*:}
  for ((s=a; s<b; s+=CHUNK)); do e=$((s+CHUNK)); [ $e -gt $b ] && e=$b
    s0=$((s>0 ? s-1 : 0)); f=$(printf "%s/p%05d_%05d.mp4" "$PD" $s $e)
    [ -s "$f" ] && continue
    cmd=(node "$HERE/render.js" "$W/page" frames $s0 $e "${f%.mp4}.tmp.mp4")
    if [ -n "${RENDER_LOCK:-}" ]; then flock "$RENDER_LOCK" "${cmd[@]}"; else "${cmd[@]}"; fi
    mv "${f%.mp4}.tmp.mp4" "$f"; echo "piece $s-$e (from $s0)"
  done
done
