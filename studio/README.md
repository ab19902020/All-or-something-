# United Road Studio

United Road Studio turns the animation workflow already used in the United Road repositories into a local production application.

The intended workflow is:

**upload artwork -> upload voiceovers -> director/production notes -> local Whisper timing -> local direction plan -> 720p review render -> mandatory self-review -> human approval -> 4K master**

The app is deliberately local-first. Routine production can run without spending ChatGPT or Claude usage.

## What works in this branch

- Local project/episode library with persistent notes and assets.
- Character, background, style-reference and voiceover uploads.
- **Style-only reference policy**: style references are separated from character/background assets.
- Local faster-whisper transcription with word timestamps.
- Local directing through Ollama when available, with a deterministic offline fallback.
- Local ComfyUI image generation when configured.
- Automatic style profiling from style-reference images through a local vision model.
- Three review render profiles, including high-quality 720p and 720p60.
- Final 4K60 render is locked until the latest preview passes QA and the director approves it.
- Mandatory deterministic self-review for broken/blank/frozen frames.
- Optional local vision self-review for face/mouth/limb/prop/layering/style-continuity problems.
- Adapter for the existing Python episode engines so finished renderers can keep doing the high-quality work they already do.
- In-app video player and QA findings.

## Start the Studio

Python 3.11 or 3.12 is recommended.

    python -m venv .venv

Windows:

    .venv\Scripts\activate
    pip install -r studio\requirements.txt
    python -m studio.run

macOS/Linux:

    source .venv/bin/activate
    pip install -r studio/requirements.txt
    python -m studio.run

Studio opens at http://127.0.0.1:8765.

By default project media lives outside the repository at:

- Windows: %USERPROFILE%\UnitedRoadStudio
- macOS/Linux: ~/UnitedRoadStudio

Set URS_WORKSPACE if you want a different location.

## Local AI (optional but recommended)

### Ollama

Run a local text model for directing and a local vision model for visual self-review. The model names are editable inside Settings.

Defaults:

- Director: qwen2.5:7b
- Vision QA: qwen2.5vl:7b

If Ollama is unavailable, episode planning falls back to offline deterministic rules. Rendering and deterministic QA still work.

### ComfyUI

Run ComfyUI locally (default http://127.0.0.1:8188) and enter the exact checkpoint filename in Studio Settings.

Generated images never need to leave the machine. If a local vision model is available, Studio first describes uploaded references as style only and appends that description to the image prompt rather than copying their composition.

## Using an existing high-quality episode engine

The generic renderer is only a fallback. To preserve the quality of the existing episodes, point Studio at a local checkout of an existing renderer such as the Passmic project:

1. Open **Settings**.
2. Set **Renderer** to Existing episode engine.
3. Set **Existing engine repo path** to the local repository folder.
4. Set **Existing scene path** to a supported scene, for example episode/scenes/cartman_room.py.
5. Build a preview.

Studio recognizes the existing tools/render_episode.py vector engine and tools/render_scene.py bitmap engine. Review renders are copied back into the Studio project, where the in-app player and QA gate can inspect them.

The next engine-adapter phase is to convert a newly uploaded episode brief/assets/voiceovers directly into those existing scene formats, so no manual scene-file selection is necessary.

## Render policy

- **Quick Draft**: 960x540, 24fps.
- **Director Review**: 1280x720, 30fps, high review quality.
- **Motion Review**: 1280x720, 60fps.
- **Final Master**: 3840x2160, 60fps, approval required.

This prevents wasting time on 4K while shots are still being changed.

## Self-review

Every preview can run two QA layers:

1. **Deterministic QA** — catches missing frames, blank/overexposed frames and frozen video.
2. **Local vision QA** — when a vision model is connected, samples the preview and checks for head/face drift, detached mouths, floating props, limb/layer failures, clipping, continuity problems and style drift.

A blocking QA failure returns the episode to Draft. The 4K approval button remains locked until the latest QA report passes.

## Development check

    python -m compileall studio
    python -m unittest studio.tests.test_core -v
