#!/usr/bin/env bash
# Print an HTML document to PDF with headless Chrome. Page size comes from the file's
# CSS @page rule (e.g. `@page { size: 960pt 540pt; margin: 0 }`). With PyMuPDF installed,
# it also writes one PNG per page (<out>-p1.png …) so you can look at every page.
#   pdf.sh <file.html> <out.pdf>
set -euo pipefail
in=$1; out=$2
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
"$CHROME" --headless=new --disable-gpu --allow-file-access-from-files --virtual-time-budget=4000 \
  --no-pdf-header-footer --print-to-pdf="$out" "file://$abs" >/dev/null 2>&1
python3 - "$out" <<'PY' 2>/dev/null || echo "$out (install PyMuPDF for page PNGs: pip install pymupdf)"
import sys, pymupdf
doc = pymupdf.open(sys.argv[1])
for i, page in enumerate(doc):
    page.get_pixmap(dpi=144).save(sys.argv[1][:-4] + f"-p{i+1}.png")
print(f"{sys.argv[1]} ({len(doc)} pages) + page PNGs")
PY
