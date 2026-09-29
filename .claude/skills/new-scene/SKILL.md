---
name: new-scene
description: Make a new All or Something episode or scene (animated, lip-synced, 9:16 portrait video) from a script or director's notes, using the voice clips in audio/ and the character sheets and backgrounds in images/. Use when the user asks for a new episode / scene / short / video, sends a script, or sends new character art or voice clips to animate.
---

# Make a new episode

The user sends a script (or director's notes) and, usually, new voice clips or art. You turn them into a finished
1080 × 1920 (9:16), 30 fps video in `scenes/<slug>/`, the same way `scenes/ep01-three-midfielders/` was made (and,
before it, Pass the Mic and the TV Show scenes). **Read `scenes/ep01-three-midfielders/README.md` first**: it
explains every stage, and its code is the starting point.

The user judges the result frame by frame. The quality bar at the bottom is what they have asked for so far;
check every item yourself before you show them anything.

## 1. Collect the inputs

- Uploads land in `/root/.claude/uploads/<session id>/` with random names (`ls -t /root/.claude/uploads/*/`).
  Look at every image and transcribe every clip, then file them in the repo:
  - voice clips -> `audio/<character>/<who>_<nn>_<what-is-said>.mp3`, the words in `audio/transcripts.json` and the
    table in `audio/README.md`. Drop exact duplicates (`md5sum`); keep second takes as `_take2`.
  - character sheets -> `images/characters/<firstname-lastname>.png`; sets -> `images/backgrounds/<place>.png`;
    a line each in `images/README.md`.
- Transcribe with Whisper turbo through sherpa-onnx (model from GitHub releases, see `make_episode.sh`).
  Upload order is not speaking order: order clips by what is said.
- Map every scripted line to the clip and words it comes from. A clip often holds several lines, or another
  character's cue words: lines are cut at word boundaries, so that is fine. A scripted line nobody recorded gets a
  silent, lip-synced slot (`MISSING` in `lines.py`) and you tell the user exactly which line to record and where
  to save it.
- No script? Write a short shot-by-shot plan in the same style and show it before building.

## 2. Start the episode folder

```bash
tools/new_scene.sh ep02-<short-title>        # copies the latest episode's code (no builds, video or README)
cd scenes/ep02-<short-title>
./make_episode.sh                             # downloads the models, then builds (see step 8)
```

Dependencies are installed by the session-start hook (`requirements.txt` + ffmpeg).

## 3. Voices -> lines -> timeline

- `align.py`: put each clip's corrected transcript in `TEXT`; words missing from the dictionary go in `EXTRA`
  (ARPAbet). It asserts the aligned words match, so a wrong transcript fails loudly.
- `lines.py`: one `(id, clip, words, occurrence)` per scripted line, in script order. Pauses inside a line are
  trimmed to `MAXGAP`; `TEMPO` speeds every line up without changing pitch (Episode 1 used 1.06 to keep the pace).
- `timeline.py`: `SEQ` lays out the lines with the beats between them. A `("gap", s, "cut_x")` mark starts shot
  `x` and holds for `s` seconds, so a reaction shot's hold goes on its own gap. Shorts have almost no dead air:
  0.06-0.16 s between lines unless the script asks for a hold.

## 4. Characters

- `parts.py`: one box per drawing used, on the 1x sheet (grid them first: a coordinate grid over the sheet). The
  matte is a paper flood fill; check every `build/parts/check_*.jpg` on magenta. Open mouths on gesture poses are
  painted shut (`CLOSE`) so the lip sync can drive them. Paper trapped between the legs (the sheet's floor
  shadow closes the gap) stays solid white: find it on magenta and add the gap to `HOLES`.
- `facemarks.py`: a head box per talking drawing; eyes, mouth and chin are found automatically. Check
  `build/parts/marks_*.jpg`; beards and faint mouth lines need hand points in `cast.py` `OVR`.
- `cast.py`: which way each drawing faces. Characters are sized by eye distance, so every drawing of a character
  comes out the same size.

## 5. Acting and shots

- `perf.py`: each line's delivery tag (brows / smile), who it is said to, and its stressed words (nods); the
  script's beats as cues: `GAZE` (looks: a character, `"cam"`, `"down"`), `EXPR`, `NODS`, `TURN`, blinks
  (`FORCED`, `NOBLINK`), `body()` (lean in, sink back).
- `direction.py`: one entry per shot. `single(...)` = the set behind (plate, view, blur), the character (screen
  position of his eyes, eye distance), the table edge in front; `world(...)` = characters placed in a plate with
  the plate's furniture in front (`OCCL` polygons, in 1x plate px). `EYES` sets the eyelines from the seating so
  looks cut together. Pushes, drift, whips, smash cuts, punch-ins (`cams` keyframes).
- `graphics.py`: on-screen text only where the script asks for it (opening card, title sting).

## 6. Sound

`audio.py`: dialogue at its timeline positions, room tone per location, the synthesised score (it ducks under
dialogue; "music stops" means a hard stop), foley, the title sting cut hard at the end so the Short loops.
`python3 check_audio.py --words` must hear every line correctly in the finished mix.

## 7. Review before rendering

- `python3 render.py still <t> ...` at every beat; look at them at full size (`build/stills/`).
- Check eyelines (who looks at whom), mouths closed when not talking, the table edge, text placement.
- Fix, re-check, and only then render.

## 8. Render and deliver

```bash
./make_episode.sh                    # ~15-25 min on 4 cores for 90 s; CRF 19 keeps it well under 100 MB
../../tools/preview.sh <video>.mp4 <scratchpad>/preview.mp4      # a small portrait copy for chat
```

- Pull a few frames from the finished file (`ffmpeg -ss T -i video -frames:v 1`) and check them.
- Write the episode README (what happens by time, what is missing, how it's made), add it to `scenes/README.md`,
  commit and push to the session's branch, and send the preview with SendUserFile. Say what changed, briefly, in
  plain words, and list any line that still needs recording.

## Quality bar (check all of these every time)

- **Nothing see-through**: shirts, collars, eye whites, shoes. Check cut-outs on magenta; no paper fringe.
- **Faces**: lip sync matches the audio at full size; mouths closed when not speaking; natural blinks, never in
  sync; eyes on the speaker or where the script sends them (the lens), never drifting.
- **Scale against the room**: in any shot that shows the set's furniture, size people by the chairs: a seated
  character's shoulders fill the chair back and the head rises above it; nearer chairs mean bigger people. The
  user checks this. Group shots in portrait work best as a lineup (`group`) rather than small figures in a wide.
- **Staging**: the table in front of seated characters, furniture in front / behind correctly, consistent sizes,
  feet on the floor with a contact shadow when standing.
- **Restrained acting**: small head turns, gestures on the words the script names; the comedy comes from the edit
  and the faces.
- **Pacing**: hard cuts on the beat, no dead air, the script's holds where it asks, and a hard ending that loops
  cleanly into the opening shot.
