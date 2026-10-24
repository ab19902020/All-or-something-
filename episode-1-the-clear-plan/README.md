# ALL OR SOMETHING — Episode One: THE CLEAR PLAN

The full 15-minute landscape episode (1920 × 1080, 30 fps, 900 s), made from the director's script in
[`pack/`](pack/MASTER_DIRECTORS_SCRIPT.md): opening day to Como, built from the episodes already made plus new
animation, with every new line voiced by that character's own cloned Fish Audio voice.

**An animated parody.** The results, scorers and minutes are real (checked against mufcinfo.com's season ledger);
the private scenes and dialogue are fictionalised. The real post-match positions after Como appear only as labelled
paraphrase cards; the comic interview lines carry a PARODY DIALOGUE label.

- **The episode:** [`ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`](ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4)
  (H.264 + AAC, under 100 MB so it fits GitHub)
- **Higher-quality master:** [`master/`](master/) in pieces under 100 MB; join with
  `cat master/all_or_something_ep1_master.mp4.part* > all_or_something_ep1_master.mp4` (checksum in
  `master/SHA256SUM`)

## Running order

| Time | Length | Sequence | Made from |
|---|---:|---|---|
| 0:00 | 3:17 | The boardroom and the owners' call | *The Clear Plan* scenes 1–2 (TV-show-), as rendered; parody notice over the opening; end title redrawn as ALL OR SOMETHING / THE CLEAR PLAN / EPISODE ONE |
| 3:17 | 0:47 | Hull away: the team talk and the match | *The Clear Plan* scenes 3–4 (TV-show-), corrected to the real match (see below); Bruno's touchline shout added |
| 4:04 | 3:17 | Hull's dressing room ("Not ideal"), the month of results in the same room (Ipswich, Everton, Sabah, City, Brighton, Fulham), the international break, Tottenham, Atlético, Leeds week | **New** (part A) |
| 7:21 | 3:31 | The Mole | *The Mole* (TV-show-), without its title sting and its next-episode teaser |
| 10:53 | 4:07 | Leeds and the office cutaway; Como (briefing, early goal, half-time, collapse, consolation, the button); the interviews; the corridor; the clear plan; credits | **New** (part B) |

## Voices

Every speaking character was cloned in Fish Audio from **one** of their existing uploads — Carrick from his
re-recorded voice in *The Handover* (the sacking episode). Fifteen private voice models are on the account; their IDs
and sources are in [`voices/`](voices/README.md), with the scripts to make more lines (`fish_tts.py`) or clone more
characters (`fish_clone.py`). The API key is read from the environment and is not stored anywhere in this repository.

All new dialogue — 52 lines — was generated with the clones (three takes per line; the take used was chosen by
Whisper word accuracy and speaker similarity to the source recording). The reused scenes keep their original voices;
Wilcox's last line is his original "We've got a very clear plan." as the script's callback.

## What was corrected in the reused Hull scene

The original Hull render showed a night kick-off at 20:00 and goals at 23' and 61'. The real match (22 August 2026)
had goals at 17' (Ajayi) and 38' (Mendy). In this episode the lower third reads *Premier League | Matchday 1 |
22 August 2026*, the score cards read 17' and 38', and the match clock's minutes were redrawn (22→16, 24→18, 60→37)
so no wrong time is visible. The night lighting of the existing animation was kept.

## How the new scenes were made

With the studio pipeline the earlier episodes used (`studio/film` in AnimnationStuido-): whole drawings from the
character kits, face-warp lip sync from force-aligned phonemes, documentary coverage, and recorded foley and room
tone. The two film packages are in [`film/`](film/) (`aos-ep1-a`, `aos-ep1-b`: script, dialogue edit, acting, shot
list, props and inserts, sound). Three small engine changes they need are in
[`film/studio-patches/studio-engine.patch`](film/studio-patches/studio-engine.patch) (an episode overlay hook for
full-frame graphics, Whisper-safe splitting of long recordings, upscaling of small cut-out drawings).
[`assemble/assemble.py`](assemble/assemble.py) builds the master from the five pieces.

Sets reused from the show: the Hull dressing room, the documentary locker room, the street to Old Trafford, the ground
inside and out, the mixed zone, the press-conference room, the office, the corridor and the boardroom. The away
dressing room at Como is the same room with its reds taken out; the stand at Como is turned blue.

## Checks

See [`QA.md`](QA.md) for the measured duration, frame count, loudness and the line-by-line Whisper check of both new
parts.

## Known limits

- Shea Lacey has no character art in any of the libraries, so his line plays over an insert of his shirt still on its
  hook (captioned "off camera") rather than inventing a likeness.
- The Hull match keeps the existing night-time animation; only the times and graphics were corrected.
- New hands (the tablet, the pen, the marker, the clap) are simple drawn inserts, not from the character kits.
