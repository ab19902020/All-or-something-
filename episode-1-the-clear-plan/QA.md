# Checks on the finished episode

## The master

| | Measured |
|---|---|
| Picture | 1920 × 1080, 30 fps, H.264 (CRF 18), 4:2:0 |
| Duration | 900.0 s (15:00), **27,000 frames** (the target) |
| Sound | AAC stereo 48 kHz; **−14.1 LUFS** integrated (target −14), loudness range 14.0 LU, **true peak −1.1 dBFS** (target ≤ −1) |
| Black frames | two stretches, both in the script: 3:12.1–3:13.1 (the boardroom's cut to black before its title) and 4:03.9–4:04.3 (Hull's hard cut to black at the final whistle) |
| SHA-256 (joined master) | `16e4ac22e83954d8369f55b864b46443a4770202e7c25a0bb1ba8673d979fb47` |

Frames per piece (`assemble/report.json`): boardroom 5,918 · Hull 1,412 · part A 5,907 (its last frame held one extra
frame so the total is exact) · The Mole 6,341 · part B 7,422. A frame grab either side of every join was checked by eye.

## Every new line heard in the final mixes (Whisper, `studio.film … check`)

Part A: 33 lines; 31 heard exactly as scripted. Two flags, both spelling only:

- R01 Cunha "Hat-trick. Captain." heard as "Head trick Captain" (his accent; his original recording was heard the same
  way, "HETTRIK").
- R25 Carrick "Sabah." heard as "Saba" (Whisper has no spelling for the club; the pronunciation is right).

Part B: all 19 lines heard as scripted.

Every take was also chosen by measurement (`voices/takes_chosen.json`): word error rate 0 against the line (apart
from the two spellings above and homophones such as "two"/"to"), and the highest speaker similarity to the
character's source recording among three takes.

## Facts on screen

Every result, scorer and minute on the cards was checked against the season ledger at mufcinfo.com (the script's
source 1): Hull 2–0 United (Ajayi 17', Mendy 38'); United 5–2 Ipswich (Fernandes 40', 61' pen, 68'; Greaves og 56';
Mbeumo 82'; Davis 29', Akpom 90+1'); Everton 2–2 United (Mbeumo 46', Šeško 88'; George 83', Maitland-Niles 90+6');
United 4–0 Sabah (Cunha 27', Fernandes 42', Šeško 45', Martínez 68'); United 0–1 City (Haaland 60'); United 2–3
Brighton, League Cup (Lacey 8', Mount 10'; Kostoulas 45+1', Groß 65', De Cuyper 69'); Fulham 1–1 United (Martínez og
63', Cunha 89'); United 1–1 Tottenham (Mbeumo 73'; Solanke 90+2'); Atlético 2–0 United (Barrios 1', Lookman 79');
Leeds 1–1 United (Mbeumo 35'; Calvert-Lewin 51'); Como 4–1 United (Paz 2', 57'; Douvikas 49'; Ramón 76'; Zirkzee
90+1').

The two post-match positions after Como appear only as paraphrase cards with their sources (no quotation marks, no
generated audio of the real interviews); the comic lines that follow are labelled PARODY DIALOGUE.

## The studio's own checks on the new parts

Contact sheets (three frames of every shot) and lip sheets (the speaker's mouth at each line's stressed words and its
first M/B/P) were made and looked at for both parts; the lip shapes follow the sounds and the cuts land on line ends.
