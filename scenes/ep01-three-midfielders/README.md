# All or Something, Episode 1: "Three Midfielders"

**Video:** [`all_or_something_ep01_three_midfielders.mp4`](all_or_something_ep01_three_midfielders.mp4)
(1080 × 1920, 9:16, 30 fps, 1 min 27 s, with the soundtrack). A 720p preview is made with `tools/preview.sh`.

A mock-serious football documentary Short: dramatic *All or Nothing* production with sitcom pacing. The characters
stay visually simple (small head turns, gestures, blinks, lip sync, fast reaction shots); the comedy comes from the
edit and the faces. Built from the character sheets and backgrounds in [`images/`](../../images/) and the voice
clips in [`audio/`](../../audio/), exactly as scripted.

## What's in it

| Time | Shot | What happens |
|---|---|---|
| 0:00 | Carrington exterior | Slow push on the training ground under a grey Manchester sky with drizzle. **MANCHESTER / TRANSFER DEADLINE DAY**. Narrator: "Manchester United... transfer deadline day." Overly serious strings and piano. |
| 0:03 | Boardroom wide | Hard cut on the music hit. Carrick at the head of the table under the tactics screen, Bruno beside him, Jim apart down the table with his paperwork, Jason and Omar in the foreground with their backs to camera. Slow push to Carrick: "Right... just two things... Left-back... Striker." |
| 0:07 | Jason / Carrick / Jason | "Sorted." Carrick, relieved: "Brilliant." Jason, casually: "We bought three midfielders." The music stops dead. |
| 0:10 | Carrick close-up | One blink, a tiny head move. "Sorry... I said left-back... and striker." |
| 0:13 | Omar, Jason | Omar, explaining the obvious with both hands: "Yeah... but three midfielders." Jason: "It's three things instead of two... technically... you've won." |
| 0:19 | Carrick | No dialogue: he slowly looks straight down the documentary lens and holds. |
| 0:20 | Bruno close-up | He looks at Carrick, at Jason, then at the lens: "You bought three midfielders?" Jason nods proudly. |
| 0:24 | Carrick | Diplomatic: "Look... I'm not complaining... obviously, love the lads, great window." He leans in: "But who's actually scoring the goals?" |
| 0:32 | The meltdown | Omar: "Bruno." Whip cut to Bruno: "Sorry... what?" Omar, gesturing at him: "He's already here, so technically that's efficient recruitment." Bruno throws his hands out: "So who am I crossing the ball to?" Jason points: "Bruno." Bruno: "Me? I'm taking the corner!" Carrick tries not to react. Bruno: "I'm a midfielder." Jason, nodding happily: "Perfect, we've got loads of midfielders." |
| 0:47 | The left-back | Carrick: "And the left-back?" Jason: "We've got Luke." Slow push on Carrick: "Luke? For the whole season?" Jason freezes, glances at Omar, then at the lens: "Next question." Bruno sinks back into his chair. |
| 0:55 | Jim | Jim lowers his paperwork: "We need to focus on the bigger issues facing Britain." Everyone looks at him. Bruno turns slowly: "Jim... you live in Monaco." Silence. |
| 1:03 | Monaco | Hard cut to Jim in his Monaco office, the harbour behind him, lounge music: "Yes... I live in Monaco." Beat. Smug: "It gives me... an outside perspective." |
| 1:08 | The final review | Smash cut back. Carrick: "Right... so no striker?" Omar: "No striker." "No left-back?" Jason: "No left-back." Carrick looks between the three of them: "But three midfielders?" Jason, Omar and Jim nod; quick punch-ins: "Three midfielders." "Three midfielders." Jim's tiny approving nod. |
| 1:19 | Bruno's button | Close-up; the room goes quiet and grey behind him. Dead expression, straight down the lens: "Saudi Arabia offered me sunshine... I should've gone to Saudi." Cut to black. |
| 1:23 | Title sting | Boom. **ALL OR SOMETHING**, *Everything except what the manager actually asked for.* Narrator: "This is All or Something." Hard ending, so it loops into the opening shot. |

**Not recorded yet:** Bruno's "Jim... you live in Monaco." None of Bruno's clips contain it, so the line has a
silent slot of the right length and Bruno mouths it in time. Record it (same voice), save it as
`audio/bruno-fernandes/bruno_03_jim-you-live-in-monaco.mp3` and rebuild: `lines.py` picks it up automatically,
aligns it and the slot takes its real length.

The recorded delivery runs longer than the script's 65-70 s guide, so pauses inside lines are trimmed to 0.24 s and
every line plays 6 % faster (pitch unchanged); the episode is 86.9 s.

## How it's made

The same approach as Pass the Mic and the TV Show scenes (Jim Ratcliffe, Roy Keane, *The Clear Plan*): recorded
voices, word-level alignment, characters cut from their sheets, upscaled and animated in Python, rendered with ffmpeg.
`make_episode.sh` runs the whole pipeline.

1. **Voices** (`align.py`, `lines.py`, `timeline.py`): pocketsphinx gives word and phone timings for every clip.
   Each scripted line is cut from its clip at its exact word boundaries (the quietest point next to the first and
   last word); lines that are only part of a clip, or clips that also hold someone else's cue, are handled the same
   way. `timeline.py` lays the lines out in script order with the beats between them and names the marks that the
   shots and the acting hang off. `check_audio.py --words` re-transcribes every line from the finished mix.
2. **Art** (`upscale_all.sh`, `parts.py`, `facemarks.py`): the sheets and backgrounds are upscaled 4x with
   Real-ESRGAN (anime model). Each drawing used is cut out with a flood fill of the paper (so white eyes, shirts and
   shoes stay solid, checked on magenta). The open mouths on the gesture poses are painted shut so the lip sync can
   drive them. Eyes, mouth and chin are found automatically; Bruno's beard needed hand-measured mouth points.
3. **Faces** (`face.py`, `cast.py`): each character keeps the head drawn on its own body (no head swaps, no seams).
   The jaw drops per phone with a painted mouth interior; the pupils are lifted out and re-placed for every look
   (to the speaker, to the lens); lids blink (never in sync); brows, smile, tilt, nod and turn are warps.
4. **Acting** (`perf.py`): delivery tags from the script set brows and smile per line; eyes go to whoever is talking
   (a beat late) or to the person being spoken to; small nods land on the stressed words; the script's beats are
   cues: Carrick's look into the lens, Bruno's look Carrick -> Jason -> lens, Jason's freeze and glance, Carrick
   leaning in, Bruno sinking back, the nods.
5. **Shots** (`direction.py`, `render.py`): singles are three layers: the set behind (a boardroom plate, blurred
   for shallow depth of field), the character, and the table edge in front (cut from a plate's own table, so
   everyone sits at the same table). The wide, the three-shot and Monaco place characters in the plate with the
   plate's furniture in front of them. Eyelines follow the seating in the wide. Slow pushes, handheld drift, a whip
   cut, a smash cut, quick punch-ins.
6. **Graphics** (`graphics.py`): the opening text, the title card, Jim's paperwork, the grey-sky grade and drizzle
   for Carrington, vignette and grain.
7. **Sound** (`audio.py`): everything synthesised, no sound library: wind, drizzle and traffic outside; boardroom
   room tone; the documentary score with its hit on the first cut and its dead stop; the Riviera lounge loop in
   Monaco (hard-cut on the smash); a low drone under Bruno's button; the title boom, cut hard at the end.
8. **Render** (`render.py chunk`): 1080 × 1920 frames in parallel chunks, muxed with the mix.

Quick checks: `python3 render.py still 5 20.4 64.6` writes single frames to `build/stills/`;
`EP_RES=540x960 python3 render.py still ...` for fast low-res ones.
