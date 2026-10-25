# Checks on the finished episode (the final cut)

## The file

| | Measured |
|---|---|
| Picture | 1920 × 1080, 30 fps, H.264, 4:2:0 |
| Duration | 14:40.7 (880.70 s) (**26,421 frames**): the meeting 3,372 · Hull and the month 5,950 · Upstairs 1,914 · The Mole 5,816 · Leeds and Como 4,980 · Last Chance 1,926 · Bournemouth 2,145 · the end title and credits 318 |
| Sound | AAC stereo 48 kHz, 128 kb/s; **−16.0 LUFS** integrated (target −16), loudness range 4.4 LU, **true peak −1.5 dBFS** (target ≤ −1) |
| Black | one, on purpose: Last Chance's 0.43 s smash to black on Carrick's last line (13:18.2), as in *The Handover*; every part opens and closes on picture |
| File | `ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`, 93.5 MB (two passes, 709 kb/s video, to fit GitHub's 100 MB) |

## What was rendered again, and the joins

Only what changed: the meeting (Carrick's new takes move its timing), *Upstairs* and *Bournemouth* (new), Como from
Cunha's fallout to its end, two month close-ups (Cunha's and Šeško's, now their kit drawings), Bournemouth's last
seven seconds (a re-voiced line) and the credits. Every splice was checked frame for frame against the original
render at the splice point (the frame before each one matches the original to within the encoder's noise), and the
frames either side of every join in the finished file were looked at. The month and The Mole are the renders from
the last upgrade, with their new mixes under them.

## Carrick's voice in the meeting

His meeting takes, measured against his takes in the rest of the episode:

| | Median pitch | Loudness of the take |
|---|---|---|
| Before (the meeting) | 120–212 Hz, most of them 160–210 | −10.5 to −15 LUFS |
| The rest of the episode | 105–235 Hz, most of them 115–140 | −11 to −16.7 LUFS |
| Now (the meeting) | 106–159 Hz | −12.3 to −16.7 LUFS |

Every one of his 15 meeting lines was generated eight more times with a calm delivery note and the take used is
the one heard word-perfect in his normal pitch and level, closest to his source recording.

## The balance of the soundtrack

Measured on each part's buses before and after the new mix rules (the loudest 3 seconds of effects or music,
against the dialogue's integrated level):

| Part | Effects, before → after | Music, before → after |
|---|---|---|
| The meeting | +9.9 dB (the title boom) → −5.9 dB | −5.9 → −10.9 dB |
| Hull and the month | −1.9 dB (the goal roar) → −4.8 dB | −12.1 → −16.7 dB |
| The Mole | +9.9 dB (the crash) → −5.8 dB | −0.7 dB (the sax) → −10.2 dB |
| Last Chance | +10.4 dB (the smash to black) → −5.5 dB | −5.9 → −10.9 dB |

The meeting's opening music sits 19 dB under the dialogue over the whole scene (it was 13.6).

## Every line heard in the final mixes (Whisper, `studio.film … check`)

Each part's finished soundtrack was transcribed line by line and compared with the script.

| Part | Lines | Heard as scripted | Flags (all spelling, numbers, names or translation) |
|---|---:|---:|---|
| The meeting | 45 | 45 | (the earlier "Centre-back" flag is gone with the new take) |
| Hull and the month | 58 | 55 | R02 Cunha's "Hat-trick" heard as "Hedrick" (his accent); R24 "three-two" as digits; R37 "Sabah" as "Sapa" |
| Upstairs | 20 | 20 | |
| The Mole | 60 | 57 | Martínez's Spanish translated by Whisper (L025, L056); L040 "Leeds" as "Leads" |
| Leeds and Como | 39 | 38 | C01 "Elland Road. Bryan Mbeumo" as "Ellen Road, Brian BMO" (names) |
| Last Chance | 15 | 15 | |
| Bournemouth | 25 | 21 | B06/B07/B09 the scorers' names and the scores as digits ("Ra Yan", "Leni Jorow", "Evan Nelson"); B15 Mount's "Ben" heard as "then" under the room |

Carrick's "Lads! Lads!" (B22) came out as "Lots, lots" in all eight takes, so the line is now "Enough! Enough!"
(heard exactly).

## Takes

Every line was generated at least twice with its character's clone; the take used is the one Whisper heard most
accurately, then the one closest to the character's source recording (TitaNet speaker similarity). The chosen takes
are in [`v2/takes/`](v2/takes/) with their scores in [`v2/takes_chosen.json`](v2/takes_chosen.json).

## Facts on screen and in the narration

Every result, scorer and minute of the season so far was checked against the season ledger at mufcinfo.com (the
script's source 1) and the match reports: Hull 2–0 United (Ajayi 17', Mendy 38'); United 5–2 Ipswich; Everton 2–2
United; United 4–0 Sabah; United 0–1 City; United 2–3 Brighton (League Cup); Fulham 1–1 United; United 1–1 Tottenham;
Atlético 2–0 United (Barrios 1', Lookman 79'); Leeds 1–1 United; Como 4–1 United (Paz 2', 57'; Douvikas 49'; Ramón
76'; Zirkzee 90+1'); United 0–3 Bournemouth (Rayan 38' from Kluivert's free kick, Tavernier 43' after Yoro slipped,
Evanilson 71'; Sky Sports, 25 October 2026).

The real words behind the new scenes, each given by the narrator as paraphrase over a card that names its sources:

- **Martínez after Atlético** (Amazon Prime, 13 October): the players expected more "from upstairs", and he expected
  more from the technical director; Carrick "does his best". He then gave a second interview, met Wilcox and Carrick
  at Carrington, and a statement followed; reports differ on whether it was an apology, and he was reported to have
  been fined (Sky Sports, ESPN, Goal, 14–22 October).
- **Bruno after Como**: not pressing man-to-man was "a decision from the staff", and tactical questions were "on the
  manager and on the staff... not on me" (Sky Sports, 22 October).
- **Cunha at Como**: taken off at half-time (Amad on); reports said he and Carrick had words (Sky Sports and others,
  22–23 October, from unnamed sources).
- **Bournemouth**: Bruno left out and on the bench throughout, Carrick calling it a "pure football" decision; Cunha on
  at half-time; boos at full time after Carrick's name was sung; United's eighth game without a win (Sky Sports,
  Yahoo Sports, 25 October).

Everything said in the board meeting, the dressing rooms and the parody interview lines is invented.
