#!/usr/bin/env bash
# Render an HTML or SVG file to PNG with headless Chrome. 2× pixels by default;
# SCALE=1 gives the exact size (e.g. a 1080×1920 deliverable).
#   [SCALE=1] render.sh <file.html|file.svg> <out.png> [width=1440] [height=900] [query]
# Set height to the page's full height, or the bottom gets cut off. Then look at the PNG before showing it.
# query is appended to the URL, e.g. "?dark" or "?t=2.5".
set -euo pipefail
in=$1; out=$2; w=${3:-1440}; h=${4:-900}; q=${5:-}
CHROME="${CHROME:-}"
if [[ -z "$CHROME" ]]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "$(command -v google-chrome || true)" "$(command -v chromium || true)" "$(command -v chromium-browser || true)"; do
    [[ -n "$c" && -x "$c" ]] && CHROME="$c" && break
  done
fi
[[ -z "$CHROME" ]] && { echo "Chrome not found. Set CHROME=/path/to/chrome" >&2; exit 1; }
abs="$(cd "$(dirname "$in")" && pwd)/$(basename "$in")"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor="${SCALE:-2}" \
  --allow-file-access-from-files --virtual-time-budget=4000 --window-size="$w,$h" \
  --screenshot="$out" "file://$abs$q" >/dev/null 2>&1
echo "$out"
