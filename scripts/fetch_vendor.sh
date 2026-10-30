#!/usr/bin/env bash
# Fetch the third-party front-end code and fonts into assets/ (never committed). Needs npm + curl.
#   three.js r170 (MIT) + its examples/jsm postprocessing, GSAP 3.13.0 + CustomEase/SplitText/MorphSVG/DrawSVG
#   (GSAP "standard no-charge license", https://gsap.com/standard-license: free incl. commercial use, but read it),
#   fonts from github.com/google/fonts (SIL Open Font License 1.1).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); A=${ASSETS_ROOT:-$ROOT/assets}; V=$A/vendor; FO=$A/fonts
mkdir -p "$V/jsm" "$FO"; T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
( cd "$T" && npm pack --silent three@0.170.0 gsap@3.13.0 >/dev/null && tar xzf three-0.170.0.tgz && mv package three && tar xzf gsap-3.13.0.tgz && mv package gsap )
cp "$T/three/build/three.module.min.js" "$V/"
for d in postprocessing shaders math utils; do cp -r "$T/three/examples/jsm/$d" "$V/jsm/"; done
for f in gsap CustomEase SplitText MorphSVGPlugin DrawSVGPlugin; do cp "$T/gsap/dist/$f.min.js" "$V/"; done
cp "$T/three/LICENSE" "$V/LICENSE.three.txt"
G=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -fsSL "$G/archivoblack/ArchivoBlack-Regular.ttf" -o "$FO/ArchivoBlack-Regular.ttf"
curl -fsSL "$G/intertight/InterTight%5Bwght%5D.ttf" -o "$FO/InterTight.ttf"
curl -fsSL "$G/dmmono/DMMono-Medium.ttf" -o "$FO/DMMono-Medium.ttf"
curl -fsSL "$G/intertight/OFL.txt" -o "$FO/OFL.txt"
echo "vendor + fonts in $A"
