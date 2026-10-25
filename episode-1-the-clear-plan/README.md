# ALL OR SOMETHING — Episode One: THE CLEAR PLAN

**Version 2: the remake.** The whole episode is rebuilt in one pipeline so that every character is the same cut-out
and the same cloned voice from the first frame to the last, the narrator runs through every section, and the edit is
tight: the results land under the narrator's lines, with no silent establishing shots and no dead holds.

**An animated parody.** The results, scorers and minutes are real (checked against mufcinfo.com's season ledger);
the private scenes and dialogue are fictionalised. The real post-match positions after Como are given by the
narrator as paraphrase, on cards that name their sources; the comic interview lines carry a PARODY DIALOGUE label.

- **The episode:** [`ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`](ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4)
  (1920 × 1080, 30 fps, H.264 + AAC, under 100 MB so it fits GitHub)
- **The script:** [`v2/SCRIPT_V2.md`](v2/SCRIPT_V2.md) (every line, with its ID)
- **Checks:** [`QA.md`](QA.md)
- **The first version** (15:00, which reused the earlier renders) is kept in [`v1/`](v1/).

## Running order

Ten minutes fifty-five (655 s). Hard cuts between the four parts; the narrator opens each one.

| Time | Length | Part | What happens |
|---|---:|---|---|
| 0:00 | 1:52 | The meeting | Carrington. The boardroom: Wilcox's "very clear plan" on a tablet at 3%, the buzzwords, "who are we signing?" and the music stops, Ratcliffe's "No." to every position, "responsive squad optimisation", the objectives, "Debt.", the owners' camera-off call (41 seconds, thirty about the microphone), "Hull. Don't lose." Title. |
| 1:52 | 3:19 | Hull and the month | Hull away: the set-pieces team talk, the match (17', 38'), Bruno on the touchline, "Not ideal", "Execution?", BASICS over SET PIECES. Then every result to Leeds week under the narrator, each answered in the same dressing room: Ipswich (the hat-trick, the tablet), Everton (Šeško's eight-minute winner), Sabah, City (expected goals), Brighton ("Not..."), Fulham, the opening month ("Sabah."), Tottenham, the RESET sheet, Atlético. |
| 5:12 | 3:13 | The Mole | Martínez in the hedge, the conspiracy board, the plant, Wilcox's Leeds top, the 214-slide right of reply, Omar's City scarf, the two of them pointing at each other. Re-voiced; no title card, no teaser. |
| 8:24 | 2:31 | Leeds, Como and the plan | Leeds 1-1 and the office (the tiny clap, the blue mug); Como: COMPACT, the pen click, Paz after two minutes, PRESS / TOGETHER, the collapse, the consolation, "We've used that one", the interviews, the corridor, CLEAR PLAN - FINAL - FINAL 2, A PLAN. Credits. |

## One cut-out per character, everywhere

Every character is filmed from the AnimnationStuido- library cut-outs, the ones *The Handover* and *The Mole* use,
and nobody changes drawing between scenes. The opening no longer uses the TV-show renders (a different set of
drawings): it is rebuilt in the same boardroom, with the same people, as *The Handover*.

| Character | Cut-out (library drawing) | Where |
|---|---|---|
| Michael Carrick | `michael-carrick` black club tracksuit: `track`, with its arms-crossed, pointing, explaining and walking-away poses | everywhere |
| Sir Jim Ratcliffe | `jim-ratcliffe` suit: `suit`, `point` | the meeting |
| Jason Wilcox | `jason-wilcox` cut-out poses (black tracksuit): `pockets`, `crossarms`, `clipboard` (his tablet); The Mole's Leeds-top versions of the same poses | everywhere |
| Omar Berrada | `omar-berrada` `front` (The Mole's City-scarf version of it) | the meeting, The Mole, the office |
| Bruno Fernandes | `bruno-fernandes` `front`, `clap` | Hull to Como |
| Harry Maguire | `harry-maguire` `front` | Hull to Como |
| Lisandro Martínez | `lisandro-martinez` cut-out poses (home kit): `stand`, `point`, `crossarms` (The Mole's camouflage versions of the same) | the month, The Mole, the office, Como |
| Matheus Cunha, Benjamin Šeško, Mason Mount, Kobbie Mainoo, Joshua Zirkzee | the library's `front` / `squad` drawings | the dressing rooms |
| Shea Lacey | no art exists in any library: his line plays over his shirt on its hook (captioned "off camera") | the month |
| Joel and Avram Glazer | camera off: two video-call tiles on the boardroom screen | the meeting |
| The narrator, the documentary producer | voice only | |

## One cloned voice per character, everywhere

Every line in the episode — 195 of them, The Mole's included — is spoken by that character's private Fish Audio
clone (made from one of their existing uploads; Carrick's from *The Handover*). The models and their sources are in
[`voices/`](voices/README.md). Each line was generated twice and the take used was chosen by measurement (Whisper
word accuracy, then speaker similarity to the character's source recording); a handful of lines that came out wrong
were generated again. The chosen takes are in [`v2/takes/`](v2/takes/) with their scores in
[`v2/takes_chosen.json`](v2/takes_chosen.json); the Glazers' takes are band-limited like a laptop speaker in the
room. The API key is read from the environment and is not stored anywhere in this repository.

| Voice | Lines | Voice | Lines |
|---|---:|---|---:|
| Narrator | 58 | Omar Berrada | 4 |
| Michael Carrick | 34 | Joel Glazer | 3 |
| Lisandro Martínez | 32 | Avram Glazer, Matheus Cunha, Benjamin Šeško, the producer | 2 each |
| Jason Wilcox | 25 | Shea Lacey, Mason Mount | 1 each |
| Bruno Fernandes | 13 | | |
| Sir Jim Ratcliffe | 9 | | |
| Harry Maguire | 7 | | |

## How it was made

With the studio pipeline (`studio/film` in AnimnationStuido-): whole drawings from the library, face-warp lip sync
from force-aligned phonemes, documentary coverage, recorded foley and room tone. The four film packages are in
[`v2/film/`](v2/film/) (each: `script.md`, `film/` lines, timeline, acting, shots, props and sound):

| Package | What it films |
|---|---|
| `v2-meeting` | Carrington; the boardroom (The Handover's set and coverage) with the big screen as a running gag: CONNECTING... 3% behind Ratcliffe for the whole list of positions, the objectives, the owners' camera-off call, CALL ENDED 0:41; the title |
| `v2-month` | Hull: the team talk, the match (the episode's own animated broadcast wides, minutes corrected to 17' and 38', in `clips/`), the touchline, the dressing room; then every result of the month as a score card under the narrator, answered in the same room |
| `v2-mole` | The Mole, re-voiced line by line, without its title card and its next-episode teaser, every hold of half a second or more a quarter shorter |
| `v2-como` | Leeds and the office; Como (the lake, the briefing, the pen, the goals, half-time, the button); the interviews; the corridor; the clear plan; the credits |

[`v2/assemble_v2.py`](v2/assemble_v2.py) joins them and sets the loudness (−14 LUFS). The engine changes the
packages need are in [`v1/film/studio-patches/studio-engine.patch`](v1/film/studio-patches/studio-engine.patch) (an
episode overlay hook, Whisper-safe splitting of long recordings, upscaling of small cut-outs).
[`v2/fish_batch.py`](v2/fish_batch.py) generates every line of [`v2/lines_v2.json`](v2/lines_v2.json) with the
clones.

## Known limits

- Shea Lacey has no character art in any library, so he stays off camera.
- The Hull match is the earlier animated broadcast (night-lit) with its clock and score graphics corrected.
- Hands holding things (the tablet, the pen, the eraser, the clap) are simple drawn inserts, not from the kits.
