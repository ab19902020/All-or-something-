#!/usr/bin/env bash
# 4x Real-ESRGAN (anime model: clean cartoon line art) of every sheet and background the episode uses -> build/x4/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build/x4
for f in ../../images/backgrounds/{hull-away-dressing-room-pre-match,hull-away-dressing-room-post-match}.png \
         ../../images/characters/{kobbie-mainoo,harry-maguire,steve-holland,michael-carrick,bruno-fernandes}.png \
         ../../images/backgrounds/{hull-stadium-exterior,hull-pitch-corner,hull-tunnel,hull-stadium-strip}.png \
         ../../images/characters/{yuri-tielemans,benjamin-sesko,senne-lammens,luke-shaw}.png; do
  o=build/x4/$(basename "$f")
  [ -f "$o" ] || python3 upscale.py "$f" "$o" RealESRGAN_x4plus_anime_6B
done
