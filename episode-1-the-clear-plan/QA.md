# Checks on the finished episode (final upgrade)

## The file

| | Measured |
|---|---|
| Picture | 1920 × 1080, 30 fps, H.264, 4:2:0 |
| Duration | 12:01.7 (721.67 s) (**21,650 frames**): meeting 3,379 · Hull and the month 5,950 · The Mole 5,816 · Leeds and Como 4,261 · Last Chance 2,244 |
| Sound | AAC stereo 48 kHz; **−14.5 LUFS** integrated (target −14: the mix is −14.1 with its true peak held to −2.5, because AAC adds over a decibel to the limited peaks, and the delivered AAC is 0.4 dB under it), loudness range 4.4 LU, **true peak −1.5 dBFS** (target ≤ −1) |
| Black | one, on purpose: Last Chance's 0.47 s smash to black on Carrick's last line before the end title (11:50.7), as in *The Handover*; every part opens and closes on picture |
| File | `ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`, 93.1 MB (two-pass, to fit GitHub's 100 MB) |

## Same character, same cut-out, same voice

Stills from every scene were checked by eye (and frames either side of each join in the finished file): each
character is drawn from one cut-out set from the first frame to the last (table in the [README](README.md)). Bruno is
the full-kit figure everywhere he appears, from the Hull team talk to Como. The only footage kept from the earlier
TV-show renders is the Hull match's two broadcast wides (the pitch from the stand, the players a few pixels tall, no
faces), with their clock and score graphics corrected. Every one of the 210 lines is spoken by that character's Fish
Audio clone: the new narrator's 59 lines run through all five parts.

## Lip sync

Every bearded or moustached face was rendered at its open vowels before and after the fix, straight from the face
engine, and then cut from the finished video at Bruno's stressed words and first M/B/P in each of his lines (24
moments across the Hull team talk, the touchline and the dressing room, and 16 more at Como): the open mouth now sits inside the beard as
a drawn mouth with a normal outline, closes fully on M, B and P, and the beard around it no longer tears or shows a
dark box. The face-engine check covered every pose of Martínez's (The Mole, the office, Como) and Cunha, Mount and
Maguire too, and their open mouths in the finished parts were looked at in the stills.

## Every line heard in the final mixes (Whisper, `studio.film … check`)

Each part's finished soundtrack was transcribed line by line and compared with the script.

| Part | Lines | Heard as scripted | Flags (all spelling, numbers or translation) |
|---|---:|---:|---|
| The meeting | 45 | 44 | M14 "Centre-back?" heard as "Center back" |
| Hull and the month | 58 | 55 | R02 Cunha's "Hat-trick" heard as "Hedrick" (his accent; his source recording is heard the same way); R24 "Brighton won three-two" as "Brighton 1 3 2"; R37 "Sabah" as "Sapa" |
| The Mole | 60 | 57 | Martínez's Spanish is translated by Whisper (L025 "Madre mia", L056 "Vamos, Alexis. Vamos, hermano."); L040 "Leeds are rubbish" as "Leads are rubbish" |
| Leeds and Como | 32 | 32 | |
| Last Chance | 15 | 15 | |

Numbers ("Seventeen", "four-nil") are heard as digits and are not counted as flags.

## Takes

Every line was generated at least twice with its character's clone; the take used is the one Whisper heard most
accurately, then the one closest to the character's source recording (TitaNet speaker similarity). For this upgrade
the narrator's 59 lines were generated again with the new narrator clone, and *Last Chance*'s 15 lines were new;
the ones that came out wrong were generated four more times (Carrick's "Balanced?!" and "What?", and the narrator's
"caught", which one take turned into "called"). Earlier fixes stand: "Execution?", Wilcox's "You wouldn't
understand", "Say it.", "Set pieces. Got it.", "Sabah" (written "Sah-bah" so the voice says it properly). Every take
used is in [`v2/takes/`](v2/takes/) with its scores in [`v2/takes_chosen.json`](v2/takes_chosen.json).

## Facts on screen and in the narration

Every result, scorer and minute was checked against the season ledger at mufcinfo.com (the script's source 1): Hull
2–0 United (Ajayi 17', Mendy 38'; the second half goalless); United 5–2 Ipswich (Fernandes hat-trick: 40', 61' pen,
68'); Everton 2–2 United (Šeško 88', Maitland-Niles 90+6'); United 4–0 Sabah (Martínez 68', the fourth); United 0–1
City (Haaland 60'); United 2–3 Brighton, League Cup (Lacey 8', Mount 10'); Fulham 1–1 United (Martínez og 63', Cunha
89'); United 1–1 Tottenham (Mbeumo 73'; Solanke 90+2'); Atlético 2–0 United (Barrios 1', Lookman 79'); Leeds 1–1
United (Mbeumo 35'; Calvert-Lewin 51'); Como 4–1 United (Paz 2', 57'; Douvikas 49'; Ramón 76'; Zirkzee 90+1').
Five points from the first five league games and out of the League Cup, as Bruno says.

The two real post-match positions after Como are given by the narrator as paraphrase over cards that name their
sources (no quotation marks, no imitation of the real interviews); the comic lines that follow carry the PARODY
DIALOGUE label. *Last Chance* is wholly fictional: no board meeting after Como is reported, and nothing in it is
presented as fact.
