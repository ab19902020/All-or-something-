#!/usr/bin/env bash
# Build Episode 1, "Three Midfielders", from the sheets / backgrounds in ../../images and the voice clips in
# ../../audio. Needs ffmpeg and python3 with ../../requirements.txt. Models come from GitHub releases only.
#   ./make_episode.sh              full build -> all_or_something_ep01_three_midfielders.mp4
#   JOBS=n ./make_episode.sh       parallel render chunks (default 3: ~3.5 GB of memory each)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p models build
R=https://github.com/xinntao/Real-ESRGAN/releases/download
[ -f models/RealESRGAN_x4plus_anime_6B.pth ] || curl -sSL -o models/RealESRGAN_x4plus_anime_6B.pth $R/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth
[ -e models/sherpa-onnx-whisper-turbo ] || curl -sSL \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-turbo.tar.bz2 | tar xj -C models

# 1. voices: word + phone timings of every clip, every scripted line cut word-exact, the dialogue edit
[ -f phones.json ] || python3 align.py
python3 lines.py
python3 timeline.py > /dev/null

# 2. art: 4x upscale of the sheets and backgrounds, the drawings cut out, face landmarks found
./upscale_all.sh
python3 parts.py > /dev/null
python3 facemarks.py > /dev/null

# 3. sound -> build/episode_audio.wav
python3 audio.py

# 4. picture: parallel chunks, then muxed with the mix
J="${JOBS:-3}"       # each render process needs ~3.5 GB; 4 at once can exceed a cloud session's memory
N=$(python3 -c "import math, timeline; print(int(math.ceil(timeline.TL['total'] * 30)))")
Q=$(( (N + J - 1) / J ))
for k in $(seq 0 $((J - 1))); do
  a=$((k * Q)); b=$(( (k + 1) * Q )); [ $b -gt $N ] && b=$N
  python3 render.py chunk $a $b build/part$k.mp4 > build/render$k.log 2>&1 &
done
wait
for k in $(seq 0 $((J - 1))); do echo "file 'part$k.mp4'"; done > build/parts.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i build/parts.txt -i build/episode_audio.wav \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest \
  -movflags +faststart all_or_something_ep01_three_midfielders.mp4
echo "done -> all_or_something_ep01_three_midfielders.mp4"
