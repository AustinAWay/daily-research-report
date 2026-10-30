#!/usr/bin/env bash
# Fetch the CC0 sample libraries into assets/sounds (or $SOUNDS_DIR). Never committed. ~2.3 GB if you take everything;
# the sparse checkouts below take only the folders the score and SFX use.
#   VSCO-2-CE (CC0)        https://github.com/sgossner/VSCO-2-CE
#   Virtuosity Drums (CC0) https://github.com/sfzinstruments/virtuosity_drums
#   TR-808 Fischer (CC0)   https://github.com/tidalcycles/sounds-tr808-fischer
#   Kenney Interface Sounds (CC0) https://kenney.nl/assets/interface-sounds
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); S=${SOUNDS_DIR:-$ROOT/assets/sounds}; mkdir -p "$S"; cd "$S"
sparse() { # dir url paths...
  local d=$1 u=$2; shift 2; [ -d "$d/.git" ] && { echo "have $d"; return; }
  git clone --depth 1 --filter=blob:none --sparse "$u" "$d" && git -C "$d" sparse-checkout set --no-cone "$@" LICENSE '*.md' '*.txt'; }
sparse vsco https://github.com/sgossner/VSCO-2-CE.git 'Keys/' 'Strings/' 'Brass/' 'Percussion/' 'Miscellania Raw/'
sparse vdrums https://github.com/sfzinstruments/virtuosity_drums.git 'Samples/mid/'
[ -d tr808 ] || git clone --depth 1 https://github.com/tidalcycles/sounds-tr808-fischer.git tr808
if [ ! -d kenney_interface/Audio ]; then
  Z=$(curl -fsSL https://kenney.nl/assets/interface-sounds | grep -oE 'https://kenney.nl/media/[^"]+\.zip' | head -1 || true)
  if [ -n "$Z" ]; then curl -fsSL "$Z" -o kenney_interface.zip && mkdir -p kenney_interface && unzip -q -o kenney_interface.zip -d kenney_interface
  else echo "Download Interface Sounds from https://kenney.nl/assets/interface-sounds and unzip it to $S/kenney_interface (it must contain Audio/*.ogg)"; fi
fi
echo "sounds in $S"
