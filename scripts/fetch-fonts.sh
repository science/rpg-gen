#!/usr/bin/env bash
# Fetch the vendored display/body fonts as TrueType into static/fonts/.
# The fonts are also committed to the repo; this script documents their
# provenance and lets you re-fetch them reproducibly.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p static/fonts

# An old Android UA makes the Google Fonts CSS API serve plain TrueType
# (a modern UA returns woff2; an MSIE UA returns EOT — neither embeds cleanly).
UA="Mozilla/5.0 (Linux; U; Android 2.3.3; en-us) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"

# face name -> Google Fonts family query
fetch() {
  local name="$1" fam="$2" url
  url=$(curl -fsSL -H "User-Agent: $UA" "https://fonts.googleapis.com/css?family=$fam" \
        | grep -oE "https://[^)]+" | head -1)
  [ -n "$url" ] || { echo "no URL for $name ($fam)" >&2; return 1; }
  curl -fsSL -H "User-Agent: $UA" "$url" -o "static/fonts/$name.ttf"
  echo "fetched static/fonts/$name.ttf"
}

fetch Limelight-Regular     "Limelight"
fetch Cinzel-Regular        "Cinzel"
fetch Cinzel-SemiBold       "Cinzel:600"
fetch Cinzel-Bold           "Cinzel:700"
fetch EBGaramond-Regular    "EB+Garamond"
fetch EBGaramond-Italic     "EB+Garamond:italic"
fetch SpecialElite-Regular  "Special+Elite"

echo "done."
