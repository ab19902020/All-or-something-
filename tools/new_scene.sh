#!/usr/bin/env bash
# Start a new episode / scene folder from an existing one's pipeline code (no builds, no video, no README).
#   tools/new_scene.sh <slug> [base]      base: a folder in scenes/ (default: the latest episode) or a template
#                                         in pipeline/ (single-character, multi-character: the older 16:9 ones)
# Creates scenes/<slug>/. The art and voices stay in images/ and audio/; the new episode's lines.py, direction.py
# and perf.py are then rewritten for its script (see .claude/skills/new-scene/SKILL.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { echo "usage: tools/new_scene.sh <slug> [base]"; exit 1; }
NEW="$ROOT/scenes/$1"
if [ $# -ge 2 ]; then
  BASE="$ROOT/scenes/$2"; [ -d "$BASE" ] || BASE="$ROOT/pipeline/$2"
else
  BASE="$(ls -d "$ROOT"/scenes/ep*/ 2>/dev/null | sort | tail -1)"; BASE="${BASE%/}"
fi
[ -d "$BASE" ] || { echo "no base folder: $BASE"; exit 1; }
[ -e "$NEW" ] && { echo "$NEW already exists"; exit 1; }
mkdir -p "$NEW"
(cd "$BASE" && find . -type f \( -name '*.py' -o -name '*.sh' -o -path './fonts/*' -o -name '.gitignore' \) \
    ! -path './build/*' ! -path './models/*' ! -path './__pycache__/*' | while read -r f; do
  mkdir -p "$NEW/$(dirname "$f")"; cp -p "$f" "$NEW/$f"
done)
echo "created scenes/$1 from $(basename "$BASE"):"; ls "$NEW"
