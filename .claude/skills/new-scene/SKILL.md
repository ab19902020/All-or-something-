---
name: new-scene
description: Make a new All or Something episode or scene (animated, lip-synced, 9:16 portrait video) from a script or director's notes, using the voice clips in audio/ and the character sheets and backgrounds in images/. Use when the user asks for a new episode / scene / short / video, sends a script, or sends new character art or voice clips to animate.
---

# Make a new episode

The user sends a script (or director's notes) and, usually, new voice clips or art. You turn them into a finished
1080 × 1920 (9:16), 30 fps video in `scenes/<slug>/`, the same way Pass the Mic, the TV Show scenes and
`scenes/ep01-three-midfielders/` were made. Read the README of the scene you base the new one on before changing
its code: it explains every stage.

The user judges the result frame by frame. The quality bar at the bottom is what they have asked for so far;
check every item yourself before you show them anything.

## 1. Collect the inputs

- Uploads land in `/root/.claude/uploads/<session id>/` with random names (`ls -t /root/.claude/uploads/*/`).
  Look at every image and listen to (transcribe) every clip, then file them in the repo:
  - voice clips -> `audio/<character>/<who>_<nn>_<what-is-said>.mp3`, words in `audio/transcripts.json` and the
    table in `audio/README.md`. Drop exact duplicates (`md5sum`).
  - character sheets -> `images/characters/<firstname-lastname>.png`; sets -> `images/backgrounds/<place>.png`;
    a line each in `images/README.md`.
- Transcribe with Whisper turbo (sherpa-onnx, model from GitHub releases; see the templates' `transcribe.py`).
  Upload order is not speaking order: order clips by what is said.
- The script names each line's speaker, delivery tag and the shot. A scripted line is often only part of a clip,
  or a clip holds another character's cue words: every line is cut from its clip at word boundaries.
- A scripted word that no clip contains (e.g. a one-word reply) is re-used from another clip of the same voice
  saying that word. If the voice never says it, tell the user which line needs recording.
- No script? Write a short shot-by-shot plan in the same style and show it before building.

## 2. Start the scene folder

```bash
tools/new_scene.sh ep02-<short-title>          # copies the episode pipeline into scenes/ep02-<short-title>
```

Base on the latest episode in `scenes/` (it is already 9:16 and uses these sheets); `pipeline/multi-character`
and `pipeline/single-character` are the older 16:9 templates from the TV Show repo.

## 3. Audio -> lines -> timeline

- Word + phone timings for every clip (pocketsphinx forced alignment of the transcript).
- `lines.py`: one entry per scripted line: speaker, clip, first/last word. Cut at the quietest point in the gap
  around the words, with a few ms of fade. Re-transcribe every cut to prove it holds exactly its words.
- `timeline.py`: lines in script order with the beats between them (reaction holds, the "look to camera" beats),
  so the total hits the script's runtime. Shorts have almost no dead space: gaps of 0.15-0.35 s unless the
  script asks for a hold.

## 4. Characters

- Sheets are RGB on light-grey paper, with labelled cells. Measure each cell on the 1x sheet with a coordinate
  grid; never reuse another sheet's numbers.
- Cut the drawings used (head views, expressions, upper-body gestures, mouths) with a paper-colour flood fill
  plus the dark outline, then check them on **magenta**: white shirts and highlights are the same colour as the
  paper and must stay solid.
- Upscale the parts 4x (Real-ESRGAN, GitHub releases).
- Lip sync: each phone maps to the sheet's mouth set (rest, A, E, I, O, U, smile, frown, wide shout); mouths
  change one frame before the sound; M/B/P closures last at least 2 frames. The drawn mouth is painted out in
  the skin colour and the sheet mouth pasted, scaled and recoloured to that head.
- Blinks: natural, never in sync between characters, plus one forced blink where the script says so.

## 5. Staging and shots

- Backgrounds are 941 × 1672 portrait: upscale 4x, place each character (seated behind the table: table edge in
  front, chair behind), consistent sizes by depth.
- Shots follow the script: wides, singles, close-ups, reaction cuts, slow push-ins, whip / smash cuts, the
  look-to-camera holds.
- Text on screen only where the script asks (opening card, title sting).

## 6. Sound

- Synthesised, no sound library: room tone, the "serious documentary" score (ducks under dialogue, stops dead
  where the script says "music abruptly stops"), the title boom.
- Re-transcribe the final mix to check every line is intelligible.

## 7. Review before rendering

- Render stills at every beat and look at them at full size; consecutive-frame runs for every fast cut and
  gesture (popping, flicker, mouth jumps).
- Fix, re-check, and only then render.

## 8. Render and deliver

- Render in parallel chunks, mux with the mix, CRF so the file stays under 100 MB.
- `tools/preview.sh <video> <scratchpad>/preview.mp4` (use `-vf scale=720:1280` for portrait).
- Pull a few frames from the finished file and check them.
- Write the scene README (what happens by time, how it's made), add it to `scenes/README.md`, commit and push to
  the session's branch, and send the preview with SendUserFile. Say what changed, briefly, in plain words.

## Quality bar (check all of these every time)

- **Nothing see-through**: shirts, collars, highlights, the gap by the tie. Check cut-outs on magenta.
- **Heads and bodies belong together**: no seams, the same collar on every pose, no extra or floating hands.
- **Lip sync** matches the audio at full resolution; mouths closed when not speaking.
- **Staging**: table in front, chairs behind, feet/bodies grounded, consistent sizes.
- **Restrained acting**: blinks, small head turns, gestures on the words the script names. The comedy comes from
  the edit and the faces.
- **Hard cuts on the beat**, no dead air, and a hard ending that loops cleanly into the opening shot.
