# ALL OR SOMETHING — Episode One: THE CLEAR PLAN

**The remake, final upgrade.** The whole episode is built in one pipeline so that every character is the same
cut-out and the same cloned voice from the first frame to the last, the narrator runs through every section, and the
edit is tight: the results land under the narrator's lines, with no silent establishing shots and no dead holds.
This upgrade adds:

- **Bruno in the full Man United kit** (crest, adidas, captain's armband), one cut-out everywhere he appears.
- **Cleaner lip sync** for the bearded and moustached faces (Bruno most of all, and Martínez, Cunha, Mount, Maguire):
  their open mouths no longer show a dark box or tear the beard (see "How it was made").
- **A new narrator**, cloned from the Clony AI recording supplied for him, voicing all 59 narrator lines.
- **Last Chance**, after Como: The Handover re-made shot for shot, but Carrick is not sacked. "We backed you" stays;
  it is his last chance, and the man on standby is already outside the door.
- **Smaller fixes:** the tablet Wilcox holds up to the documentary camera now has his arm coming in from the bottom of
  the frame (the hand and sleeve used to float in mid-air), and the end credits moved to the new last scene.

**An animated parody.** The results, scorers and minutes are real (checked against mufcinfo.com's season ledger);
the private scenes and dialogue are fictionalised. The real post-match positions after Como are given by the
narrator as paraphrase, on cards that name their sources; the comic interview lines carry a PARODY DIALOGUE label.

- **The episode:** [`ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`](ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4)
  (1920 × 1080, 30 fps, H.264 + AAC, under 100 MB so it fits GitHub)
- **The script:** [`v2/SCRIPT_V2.md`](v2/SCRIPT_V2.md) (every line, with its ID)
- **Checks:** [`QA.md`](QA.md)
- **The first version** (15:00, which reused the earlier renders) is kept in [`v1/`](v1/).

## Running order

Twelve minutes two (721.7 s). Hard cuts between the five parts; the narrator opens each one.

| Time | Length | Part | What happens |
|---|---:|---|---|
| 0:00 | 1:53 | The meeting | Carrington. The boardroom: Wilcox's "very clear plan" on a tablet at 3%, the buzzwords, "who are we signing?" and the music stops, Ratcliffe's "No." to every position, "responsive squad optimisation", the objectives, "Debt.", the owners' camera-off call (41 seconds, thirty about the microphone), "Hull. Don't lose." Title. |
| 1:53 | 3:18 | Hull and the month | Hull away: the set-pieces team talk, the match (17', 38'), Bruno on the touchline, "Not ideal", "Execution?", BASICS over SET PIECES. Then every result to Leeds week under the narrator, each answered in the same dressing room: Ipswich (the hat-trick, the tablet held up to the lens), Everton (Šeško's eight-minute winner), Sabah, City (expected goals), Brighton ("Not..."), Fulham, the opening month ("Sabah."), Tottenham, the RESET sheet, Atlético. |
| 5:11 | 3:14 | The Mole | Martínez in the hedge, the conspiracy board, the plant, Wilcox's Leeds top, the 214-slide right of reply, Omar's City scarf, the two of them pointing at each other. Re-voiced; no title card, no teaser. |
| 8:25 | 2:22 | Leeds, Como and the plan | Leeds 1-1 and the office (the tiny clap, the blue mug); Como: COMPACT, the pen click, Paz after two minutes, PRESS / TOGETHER, the collapse, the consolation, "We've used that one", the interviews, the corridor, CLEAR PLAN - FINAL - FINAL 2, A PLAN. |
| 10:47 | 1:15 | Last Chance | The morning after Como, the boardroom. "We're very disappointed... this is your last chance." Wilcox: "We backed you." Carrick finally says it (three midfielders, no striker, no left back), Omar's "very balanced squad", "It is what it is." Then: "We've asked someone to be on standby." The door. "Hello, Michael!" End title, credits. |

## One cut-out per character, everywhere

Every character is filmed from the AnimnationStuido- library cut-outs, the ones *The Handover* and *The Mole* use,
and nobody changes drawing between scenes.

| Character | Cut-out (library drawing) | Where |
|---|---|---|
| Michael Carrick | `michael-carrick` black club tracksuit: `track`, with its arms-crossed, pointing, explaining, three-quarter and walking-away poses | everywhere |
| Sir Jim Ratcliffe | `jim-ratcliffe` suit: `suit`, `point` | the meeting, Last Chance |
| Jason Wilcox | `jason-wilcox` cut-out poses (black tracksuit): `pockets`, `crossarms`, `clipboard` (his tablet); The Mole's Leeds-top versions of the same poses | everywhere |
| Omar Berrada | `omar-berrada` `front` (The Mole's City-scarf version of it) | the meeting, The Mole, the office, Last Chance |
| Bruno Fernandes | `bruno-fernandes` `full`: his model sheet's hero figure in the full Man United kit, crest, adidas and captain's armband (new) | Hull to Como |
| Harry Maguire | `harry-maguire` `front` | Hull to Como |
| Lisandro Martínez | `lisandro-martinez` cut-out poses (home kit): `stand`, `point`, `crossarms` (The Mole's camouflage versions of the same) | the month, The Mole, the office, Como |
| Ole Gunnar Solskjær | `ole-gunnar-solskjaer` suit poses: `arms`, `wave`, `shrug`, `neutral`, his walk cycle (The Handover's) | Last Chance |
| Matheus Cunha, Benjamin Šeško, Mason Mount, Kobbie Mainoo, Joshua Zirkzee | the library's `front` / `squad` drawings | the dressing rooms |
| Shea Lacey | no art exists in any library: his line plays over his shirt on its hook (captioned "off camera") | the month |
| Joel and Avram Glazer | camera off: two video-call tiles on the boardroom screen | the meeting |
| The narrator, the documentary producer | voice only | |

## One cloned voice per character, everywhere

Every line in the episode — 210 of them, The Mole's included — is spoken by that character's private Fish Audio
clone, each made from one existing recording: Carrick's from *The Handover*, Ole's from *The Handover*, the narrator's
from the Clony AI recording supplied for him (kept in [`voices/sources/`](voices/sources/)). The models and their
sources are in [`voices/`](voices/README.md). Each line was generated at least twice and the take used was chosen by
measurement (Whisper word accuracy, then speaker similarity to the character's source recording); lines that came
out wrong were generated again. The chosen takes are in [`v2/takes/`](v2/takes/) with their scores in
[`v2/takes_chosen.json`](v2/takes_chosen.json); the Glazers' takes are band-limited like a laptop speaker in the
room. The API key is read from the environment and is not stored anywhere in this repository.

| Voice | Lines | Voice | Lines |
|---|---:|---|---:|
| Narrator | 59 | Omar Berrada | 5 |
| Michael Carrick | 41 | Joel Glazer | 3 |
| Lisandro Martínez | 32 | Ole Gunnar Solskjær | 2 |
| Jason Wilcox | 26 | Avram Glazer, Matheus Cunha, Benjamin Šeško, the producer | 2 each |
| Bruno Fernandes | 13 | Shea Lacey, Mason Mount | 1 each |
| Sir Jim Ratcliffe | 12 | | |
| Harry Maguire | 7 | | |

## How it was made

With the studio pipeline (`studio/film` in AnimnationStuido-): whole drawings from the library, face-warp lip sync
from force-aligned phonemes, documentary coverage, recorded foley and room tone. The five film packages are in
[`v2/film/`](v2/film/) (each: `script.md`, `film/` lines, timeline, acting, shots, props and sound):

| Package | What it films |
|---|---|
| `v2-meeting` | Carrington; the boardroom (The Handover's set and coverage) with the big screen as a running gag: CONNECTING... 3% behind Ratcliffe for the whole list of positions, the objectives, the owners' camera-off call, CALL ENDED 0:41; the title |
| `v2-month` | Hull: the team talk, the match (the episode's own animated broadcast wides, minutes corrected to 17' and 38', in `clips/`), the touchline, the dressing room; then every result of the month as a score card under the narrator, answered in the same room |
| `v2-mole` | The Mole, re-voiced line by line, without its title card and its next-episode teaser, every hold of half a second or more a quarter shorter |
| `v2-como` | Leeds and the office; Como (the lake, the briefing, the pen, the goals, half-time, the button); the interviews; the corridor; the clear plan |
| `v2-lastchance` | The Handover's boardroom, shots, beats and door, re-voiced as Carrick's last chance; the end title and the credits |

**The lip-sync fix.** The face engine measures how thick a character's drawn mouth line is and draws the open mouth's
outline as heavy. On a face with a moustache right over the mouth it measured the moustache as part of the line, so
every open mouth got an outline several times too heavy: a dark box in the beard. A new per-drawing setting,
`lip_lt` (the line's real half-thickness), fixes it; Bruno's new drawing also drops the mouth "erase" band (for
clean-shaven straight mouths) and opens a little less, so the beard no longer tears.

[`v2/assemble_v2.py`](v2/assemble_v2.py) joins the five parts and sets the loudness. The engine changes the
packages need, this fix included, are in [`v2/studio-engine.patch`](v2/studio-engine.patch); the drawing lists as
filmed are in [`v2/library/`](v2/library/) and what else the packages need from the library is in
[`v2/LIBRARY.md`](v2/LIBRARY.md). [`v2/fish_batch.py`](v2/fish_batch.py) generates every line of
[`v2/lines_v2.json`](v2/lines_v2.json) with the clones.

## Known limits

- Shea Lacey has no character art in any library, so he stays off camera.
- The Hull match is the earlier animated broadcast (night-lit) with its clock and score graphics corrected.
- Hands holding things (the tablet, the pen, the eraser, the clap) are simple drawn inserts, not from the kits.
- Bruno's full-kit drawing is one standing pose (his kit sheet has no other full-kit poses), so he no longer claps.
