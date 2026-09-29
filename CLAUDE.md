# All or Something: working notes for Claude

See `README.md` for the layout. To make an episode or scene, follow `.claude/skills/new-scene/SKILL.md`.

- Source files live in `audio/` (voice clips, named `<who>_<nn>_<words>.mp3`, words in `audio/transcripts.json`)
  and `images/` (`characters/` sheets, `backgrounds/`). Keep them there, named that way; add new uploads there
  and update the two READMEs.
- Each episode is its own folder in `scenes/`, started with `tools/new_scene.sh`. Never edit `pipeline/` for a
  scene; improve a template only when a fix should apply to every future scene.
- Output is 9:16 portrait, 1080 × 1920, 30 fps. Finished videos are committed (keep each file under 100 MB);
  build products are git-ignored (`.gitignore`).
- Models come from GitHub releases only (HuggingFace is unreachable from cloud sessions).
- Dependencies are installed by `.claude/hooks/session-start.sh` in web sessions (`requirements.txt`).
- Keep the repo root clean: no loose uploads, no scratch files.
