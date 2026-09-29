#!/usr/bin/env bash
# Start a new scene folder from one of the pipeline templates (code only: no art, no audio, no builds).
#   tools/new_scene.sh <scene-slug> [single-character | multi-character]   (default: multi-character)
# Creates scenes/<scene-slug>/ with an empty src/. Then copy the sheets, backgrounds and voice clips it uses from
# images/ and audio/ into src/ (see .claude/skills/new-scene/SKILL.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NEW="$ROOT/scenes/$1"; BASE="$ROOT/pipeline/${2:-multi-character}"
[ -d "$BASE" ] || { echo "no template $BASE"; exit 1; }
[ -e "$NEW" ] && { echo "$NEW already exists"; exit 1; }
mkdir -p "$NEW/src"
(cd "$BASE" && find . -type f ! -name README.md ! -path './__pycache__/*' | while read -r f; do
  mkdir -p "$NEW/$(dirname "$f")"; cp -p "$f" "$NEW/$f"
done)
echo "created scenes/$1 from pipeline/$(basename "$BASE"):"; ls "$NEW"
