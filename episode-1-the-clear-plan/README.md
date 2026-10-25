# ALL OR SOMETHING — Episode One: THE CLEAR PLAN

**The final cut.** The whole episode is built in one pipeline so that every character is the same cut-out and the
same cloned voice from the first frame to the last, the narrator runs through every section, and the edit is tight.
This cut adds and fixes:

- **Carrick's voice in the meeting** is his voice from the rest of the episode again: calm, low, deadpan. His first
  takes there came out pitched up and pushed; every one of his 15 meeting lines was generated again and the calmest
  word-perfect take used (see [`voices/`](voices/README.md)).
- **The soundtrack rebalanced:** music and effects come down everywhere and are held under the dialogue (no effect or
  music moment may come within 4 dB / 9 dB of the dialogue's level), the music ducks deeper under every line, and
  the finished file is mixed to −16 LUFS instead of −14, with a clean limiter instead of a saturating one.
- **Upstairs**, after Atlético: Martínez's television interview calling out "upstairs" and the technical director,
  his second interview, and the board's meeting about it (his real words on a card; the rest is parody).
- **Cunha and Carrick fall out** at Como: Cunha was taken off at half-time, and he has some feedback.
- **Bruno blames the staff** after Como ("We were told not to press... That one is not on me").
- **Bournemouth**, today's game: Bruno left out, 0–3 at Old Trafford, and the whole dressing room arguing.
- **One drawing each for Cunha and Šeško** (their kit drawings): two close-ups in the month used other drawings and
  were rendered again.
- From the last upgrade: Bruno in the full Man United kit, cleaner lip sync for the bearded faces, the new narrator,
  and *Last Chance*.

**An animated parody.** The results, scorers and minutes are real (checked against mufcinfo.com's season ledger);
the private scenes and dialogue are fictionalised. The real post-match words (Martínez after Atlético, Bruno and
Carrick after Como) are given by the narrator as paraphrase, on cards that name their sources; the comic interview
lines after them carry a PARODY DIALOGUE label. Bournemouth's facts are from the reports of the same day.

- **The episode:** [`ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`](ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4)
  (1920 × 1080, 30 fps, H.264 + AAC, under 100 MB so it fits GitHub)
- **The script:** [`v2/SCRIPT_V2.md`](v2/SCRIPT_V2.md) (every line, with its ID)
- **Checks:** [`QA.md`](QA.md)
- **The first version** (15:00, which reused the earlier renders) is kept in [`v1/`](v1/).

## Running order

Fourteen minutes forty (880.7 s). Hard cuts between the parts; the narrator opens every one of them.

| Time | Length | Part | What happens |
|---|---:|---|---|
| 0:00 | 1:52 | The meeting | Carrington. The boardroom: Wilcox's "very clear plan" on a tablet at 3%, the buzzwords, "who are we signing?" and the music stops, Ratcliffe's "No." to every position, "responsive squad optimisation", the objectives, "Debt.", the owners' camera-off call (41 seconds, thirty about the microphone), "Hull. Don't lose." Title. |
| 1:52 | 3:18 | Hull and the month | Hull away: the set-pieces team talk, the match (17', 38'), Bruno on the touchline, "Not ideal", "Execution?", BASICS over SET PIECES. Then every result to Leeds week under the narrator, each answered in the same dressing room: Ipswich (the hat-trick, the tablet held up to the lens), Everton (Šeško's eight-minute winner), Sabah, City (expected goals), Brighton ("Not..."), Fulham, the opening month ("Sabah."), Tottenham, the RESET sheet, Atlético. |
| 5:10 | 1:03 | Upstairs | Madrid, after Atlético: Martínez's interview (his real words on a card), "Upstairs." "Who's upstairs?" "The technical director." The second interview: "I am not going to close my mouth." The board meeting: "Technically... we are." "It's you, Jason." "In a sense." Fined; a statement; a new theory. |
| 6:14 | 3:13 | The Mole | Martínez in the hedge, the conspiracy board, the plant, Wilcox's Leeds top, the 214-slide right of reply, Omar's City scarf, the two of them pointing at each other. Re-voiced; no title card, no teaser. |
| 9:28 | 2:46 | Leeds, Como and the plan | Leeds 1-1 and the office (the tiny clap, the blue mug); Como: COMPACT, the pen click, Paz after two minutes, PRESS / TOGETHER, the collapse, the consolation, "We've used that one"; Cunha, taken off at half-time: "Forty-five minutes, Michael?"; Bruno: "We were told not to press... That one is not on me."; Carrick's reply, the corridor, CLEAR PLAN - FINAL - FINAL 2, A PLAN. |
| 12:14 | 1:04 | Last Chance | The morning after Como, the boardroom. "This is your last chance." Wilcox: "We backed you." Carrick finally says it, Omar's "very balanced squad", "It is what it is." "We've asked someone to be on standby." The door. "Hello, Michael!" Smash to black. |
| 13:18 | 1:11 | Bournemouth | Four days later, Old Trafford: one name missing from the team sheet. "It's a pure football decision." "Is this because of what I said?" "That one's not on me." 0-3 (Rayan, Tavernier, Evanilson), Cunha on at half-time, the boos. The row: "I asked for minutes. Not these minutes!", "It's upstairs! I said it!", "So did I!", "Enough!" "Not..." "Don't!" |
| 14:30 | 0:10 | The end | ALL OR SOMETHING / LAST CHANCE. The credits. |

## One cut-out per character, everywhere

Every character is filmed from the AnimnationStuido- library cut-outs, the ones *The Handover* and *The Mole* use,
and nobody changes drawing between scenes.

| Character | Cut-out (library drawing) | Where |
|---|---|---|
| Michael Carrick | `michael-carrick` black club tracksuit: `track`, with its arms-crossed, pointing, explaining, three-quarter and walking-away poses | everywhere |
| Sir Jim Ratcliffe | `jim-ratcliffe` suit: `suit`, `point` | the meeting, Upstairs, Last Chance |
| Jason Wilcox | `jason-wilcox` cut-out poses (black tracksuit): `pockets`, `crossarms`, `clipboard` (his tablet); The Mole's Leeds-top versions of the same poses | everywhere |
| Omar Berrada | `omar-berrada` `front` (The Mole's City-scarf version of it) | the meeting, Upstairs, The Mole, the office, Last Chance |
| Bruno Fernandes | `bruno-fernandes` `full`: his model sheet's hero figure in the full Man United kit, crest, adidas and captain's armband | Hull to Bournemouth |
| Harry Maguire | `harry-maguire` `front` | Hull to Bournemouth |
| Lisandro Martínez | `lisandro-martinez` cut-out poses (home kit): `stand`, `point`, `crossarms` (The Mole's camouflage versions of the same) | the month, Upstairs, The Mole, the office, Como, Bournemouth |
| Ole Gunnar Solskjær | `ole-gunnar-solskjaer` suit poses: `arms`, `wave`, `shrug`, `neutral`, his walk cycle (The Handover's) | Last Chance |
| Matheus Cunha, Benjamin Šeško | their kits' `front` drawings, and only those (two month close-ups that used other drawings were rendered again) | the dressing rooms, the touchline |
| Mason Mount, Kobbie Mainoo, Joshua Zirkzee | the library's `squad` / `front` drawings | the dressing rooms |
| Shea Lacey | no art exists in any library: his line plays over his shirt on its hook (captioned "off camera") | the month |
| Joel and Avram Glazer | camera off: two video-call tiles on the boardroom screen | the meeting |
| The narrator, the documentary producer | voice only | |

## One cloned voice per character, everywhere

Every line in the episode — 262 of them, The Mole's included — is spoken by that character's private Fish Audio
clone, each made from one existing recording: Carrick's from *The Handover*, Ole's from *The Handover*, the narrator's
from the Clony AI recording supplied for him (kept in [`voices/sources/`](voices/sources/)). The models and their
sources are in [`voices/`](voices/README.md). Each line was generated at least twice and the take used was chosen by
measurement (Whisper word accuracy, then speaker similarity to the character's source recording); lines that came
out wrong were generated again. The chosen takes are in [`v2/takes/`](v2/takes/) with their scores in
[`v2/takes_chosen.json`](v2/takes_chosen.json); the Glazers' takes are band-limited like a laptop speaker in the
room. The API key is read from the environment and is not stored anywhere in this repository.

| Voice | Lines | Voice | Lines |
|---|---:|---|---:|
| Narrator | 72 | Omar Berrada, Matheus Cunha | 7 each |
| Michael Carrick | 48 | The producer | 4 |
| Lisandro Martínez | 37 | Joel Glazer, Benjamin Šeško | 3 each |
| Jason Wilcox | 28 | Avram Glazer, Mason Mount, Ole Gunnar Solskjær | 2 each |
| Sir Jim Ratcliffe, Bruno Fernandes | 17 each | Shea Lacey | 1 |
| Harry Maguire | 12 | | |

## How it was made

With the studio pipeline (`studio/film` in AnimnationStuido-): whole drawings from the library, face-warp lip sync
from force-aligned phonemes, documentary coverage, recorded foley and room tone. The seven film packages are in
[`v2/film/`](v2/film/) (each: `script.md`, `film/` lines, timeline, acting, shots, props and sound):

| Package | What it films |
|---|---|
| `v2-meeting` | Carrington; the boardroom (The Handover's set and coverage) with the big screen as a running gag: CONNECTING... 3% behind Ratcliffe for the whole list of positions, the objectives, the owners' camera-off call, CALL ENDED 0:41; the title |
| `v2-month` | Hull: the team talk, the match (the episode's own animated broadcast wides, minutes corrected to 17' and 38', in `clips/`), the touchline, the dressing room; then every result of the month as a score card under the narrator, answered in the same room |
| `v3-upstairs` | Madrid's mixed zone (Martínez, the paraphrase card, the parody), the second interview, the boardroom by day (the three executives, The Handover's set), the statement card, Martínez in the corridor |
| `v2-mole` | The Mole, re-voiced line by line, without its title card and its next-episode teaser, every hold of half a second or more a quarter shorter |
| `v2-como` | Leeds and the office; Como (the lake, the briefing, the pen, the goals, half-time, the button); Cunha's fallout; the interviews; the corridor; the clear plan |
| `v2-lastchance` | The Handover's boardroom, shots, beats and door, re-voiced as Carrick's last chance; the end title and the credits |
| `v3-bournemouth` | Old Trafford, the team sheet, Bruno and Carrick before the game, the four cards, Cunha on the touchline, Carrick at full time, the row (the month's dressing room, everyone in it) |

**The lip-sync fix.** The face engine measures how thick a character's drawn mouth line is and draws the open mouth's
outline as heavy. On a face with a moustache right over the mouth it measured the moustache as part of the line, so
every open mouth got an outline several times too heavy: a dark box in the beard. A new per-drawing setting,
`lip_lt` (the line's real half-thickness), fixes it; Bruno's new drawing also drops the mouth "erase" band (for
clean-shaven straight mouths) and opens a little less, so the beard no longer tears.

**The mix.** Every part's soundtrack is built the same way by the engine's `master()`: the effects and ambience
trimmed 2 dB and the music 5 dB, then a level rider that holds any 400 ms of effects at least 4 dB, and of music at
least 9 dB, under the dialogue's own level (it dips just ahead of a boom and lets go after, so nothing is chopped),
the music ducked 12 dB under every line, and a soft-knee limiter that leaves everything under −7 dBFS untouched.
Measured before the change, the meeting's title boom, The Mole's crash and Last Chance's smash to black each came
about 10 dB over the dialogue, and The Mole's sax reveal as loud as the voices; they now sit 5 to 6 dB under.

**Only what changed was rendered again.** [`v2/assemble_final.py`](v2/assemble_final.py) builds the episode from a
splice list: the parts whose pictures did not change are used as they were rendered, Como is its first 87 seconds
as rendered plus the new stretch from Cunha's fallout on, two month close-ups and the credits are short range
renders dropped into place, and every part's sound is its new mix. It sets the loudness (−16 LUFS) and makes the
master and the file under 95 MB. The engine changes the packages need (the lip-sync setting and the mix included)
are in [`v2/studio-engine.patch`](v2/studio-engine.patch); the drawing lists as
filmed are in [`v2/library/`](v2/library/) and what else the packages need from the library is in
[`v2/LIBRARY.md`](v2/LIBRARY.md). [`v2/fish_batch.py`](v2/fish_batch.py) generates every line of
[`v2/lines_v2.json`](v2/lines_v2.json) with the clones.

## Known limits

- Shea Lacey has no character art in any library, so he stays off camera.
- The Hull match is the earlier animated broadcast (night-lit) with its clock and score graphics corrected.
- Hands holding things (the tablet, the pen, the eraser, the clap) are simple drawn inserts, not from the kits.
- Bruno's full-kit drawing is one standing pose (his kit sheet has no other full-kit poses), so he no longer claps.
- Cunha and Šeško have one kit drawing each, a standing pose, so they argue with their faces, not their hands.
- Bournemouth's starting line-ups were not yet published in detail when this was made: the team sheet's names are
  blurred apart from Fernandes among the substitutes, and the row's lines make no claim about who played.
