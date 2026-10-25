# Checks on the finished episode (version 2)

## The file

| | Measured |
|---|---|
| Picture | 1920 × 1080, 30 fps, H.264, 4:2:0 |
| Duration | 10:55.2 (655.17 s) (**19,655 frames**): meeting 3,370 · Hull and the month 5,980 · The Mole 5,776 · Leeds to the end 4,529 |
| Sound | AAC stereo 48 kHz; **−14.4 LUFS** integrated (target −14; the delivered AAC is 0.4 dB under the −14.0 master mix so its true peak stays under −1), loudness range 4.4 LU, **true peak −1.4 dBFS** (target ≤ −1) |
| Black | none (no black stretch of 0.2 s or more anywhere: every part opens and closes on picture) |
| File | `ALL_OR_SOMETHING_EP1_THE_CLEAR_PLAN_1080p.mp4`, 93.0 MB (two-pass, to fit GitHub's 100 MB) |

## Same character, same cut-out, same voice

Stills from every scene were checked by eye (and frames either side of each join in the finished file): each
character is drawn from one cut-out set from the first frame to the last (table in the [README](README.md)). The only
footage kept from the earlier TV-show renders is the Hull match's two broadcast wides (the pitch from the stand, the
players a few pixels tall, no faces), with their clock and score graphics corrected. Every one of the 195 lines is
spoken by that character's Fish Audio clone: the narrator's 58 lines run through all four parts.

## Every line heard in the final mixes (Whisper, `studio.film … check`)

Each part's finished soundtrack was transcribed line by line and compared with the script.

| Part | Lines | Heard as scripted | Flags (all spelling or homophones unless noted) |
|---|---:|---:|---|
| The meeting | 45 | 44 | M14 "Centre-back?" heard as "Center back" |
| Hull and the month | 58 | 54 | R02 Cunha's "Hat-trick" heard as "Hedrick" (his accent; his source recording is heard the same way); R24 "Brighton won three-two" as "Brighton 1 3 2"; R36 the producer's off-camera "Such as?" as "Such out?"; R37 "Sabah" as "Saba" |
| The Mole | 60 | 58 | Leeds heard as "leads" throughout; L025 "Madre mia" translated by Whisper; L040 "Leeds are rubbish" as "Leads are rubbish" |
| Leeds to the end | 32 | 31 | C01 "Elland Road. Bryan Mbeumo" as "Ellen Rode, Brian Mbomo" (names) |

Numbers ("Seventeen", "four-nil") are heard as digits and are not counted as flags. Two problems the first check
found were fixed before the final render: the Hull crowd was masking the narrator over both goals ("Hull scored" heard
as "whole score"), so the crowd and the goal roar were brought down under him; and Maguire's "Execution?" blurred in
the dressing-room reverb, so the line was generated again and the clearest take used (now heard exactly).

## Takes

Every line was generated twice with its character's clone; the take used is the one Whisper heard most accurately,
then the one closest to the character's source recording (TitaNet speaker similarity). Lines that came out wrong
were generated again: "Execution?" (heard as "Explication"), Wilcox's "You wouldn't understand" (came out as "would"),
"Say it." (garbled), "Set pieces. Got it." (would not align word by word for the lip sync), "Sabah" (written
"Sah-bah" so the voice says it properly), and seven very short lines whose first takes sounded least like the
character. Every take used is in [`v2/takes/`](v2/takes/) with its scores in
[`v2/takes_chosen.json`](v2/takes_chosen.json).

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
DIALOGUE label.
