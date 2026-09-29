#!/bin/bash
# Installs the render dependencies (ffmpeg + Python packages) in Claude Code on the web sessions.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"
apt_get() { apt-get install -y -q "$@" >/dev/null 2>&1 || { apt-get update -q >/dev/null && apt-get install -y -q "$@" >/dev/null; }; }
command -v ffmpeg >/dev/null || apt_get ffmpeg
python3 -c "import numpy, scipy, PIL, cv2, skimage, librosa, soundfile, torch, spandrel, sherpa_onnx, pocketsphinx" 2>/dev/null \
  || pip install -q -r requirements.txt
