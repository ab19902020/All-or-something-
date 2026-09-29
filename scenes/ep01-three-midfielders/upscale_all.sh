#!/usr/bin/env bash
# 4x Real-ESRGAN (anime model: clean cartoon line art) of every sheet and background the episode uses -> build/x4/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build/x4
for f in ../../images/characters/{michael-carrick,jason-wilcox,omar-berrada,bruno-fernandes,jim-ratcliffe}.png \
         ../../images/backgrounds/{carrington-entrance,boardroom-wide,boardroom-side-view,boardroom-window-view,tactics-room-screen,monaco-office}.png; do
  o=build/x4/$(basename "$f")
  [ -f "$o" ] || python3 upscale.py "$f" "$o" RealESRGAN_x4plus_anime_6B
done
