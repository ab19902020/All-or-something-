# ALL OR SOMETHING — Clear the Air (portrait short)

A vertical short for Reels, TikTok and Shorts, made from the production pack in [`pack/`](pack/) and reworked: Carrick
and Bruno's private clear-the-air meeting (which Jason has filmed), and halfway through, Gary Neville's surprise
inspection of the standards at Manchester United. Same characters, same voices and the same office as Episode One.
The pack's air-freshener gag is cut; Gary's scene is new.

| | |
|---|---|
| **The film** | [`ALL_OR_SOMETHING_CLEAR_THE_AIR_1080x1920.mp4`](ALL_OR_SOMETHING_CLEAR_THE_AIR_1080x1920.mp4): 1080 × 1920, 30 fps, 1:23.7, H.264 + AAC, no subtitles |
| **Voices** | [`voice/`](voice/): every line as WAV: the pack's cues under its file names (`01_narrator.wav` … `21_gary.wav`; 11–14, the freshener, are cut), and the inspection's new lines (`G01_gary.wav` … `G09_gary.wav`) |
| **Generation manifest** | [`generation_manifest.json`](generation_manifest.json): every line's character, Fish Audio reference ID, model, delivery tag, take, file, measured duration and checksum. No credentials |
| **Stems** | [`stems/`](stems/): `dialogue.wav`, `effects.wav` (room, city, foley), `music.wav`, 48 kHz 32-bit float, each at its level in the mix (before the limiter), so together they rebuild it |
| **Editable project** | [`project/`](project/): the film's production code, the script, the voice requests and take QA, and the character drawing settings this short added |

## The short

| Time | What happens |
|---|---|
| 0:00 | **UNITED ROAD ORIGINAL.** Carrington, the manager's office. Carrick and Bruno at the desk, Jason behind them with the board: CLEAR THE AIR / *no leaks* / 1. TALK 2. LISTEN 3. PHOTO. Narrator: *"A private meeting to clear the air. Jason had invited a camera crew."* Jason waves the camera in. |
| 0:06 | Carrick: *"Bruno, if you've got a problem with the tactics, tell me. Not the television."* Bruno: *"I tried. You said your door was always open."* *"It is."* *"Jason was standing in it."* |
| 0:18 | Smash cut, close on the doorway: Jason fills it, smiling at the camera. Behind him Bruno tries to get past on the left (Jason sidesteps), on the right (Jason sidesteps), then jumps to see over him (Jason goes up on his toes). Squeak, squeak, thud. |
| 0:20 | The honest exchange: *"Maybe I could've been clearer." "And maybe I shouldn't have said it on telly." "So we're all right?" "Yes. I still think the tactics were shit." "Aye. But now you've told me indoors. Progress."* A tiny, reluctant smile. The board gets its tick: **RESOLVED**. Jason turns his tablet to the lens: **UNITED BEHIND THE MANAGER**. |
| 0:37 | **Halfway: the door bangs open.** Gary Neville steps in, lanyard (STANDARDS, *Inspector, self-appointed*). *"Surprise standards inspection."* Jason: *"Gary, you're not Ofsted."* Gary, to the lens: *"No. I'm worse."* |
| 0:44 | *"Manager. Where's the hairdryer?"* Carrick: *"The what?"* *"When I played here, the manager had a hairdryer. You've got a laptop."* |
| 0:52 | *"Captain."* Bruno's arms go straight up, both palms. *"There it is."* |
| 0:55 | Gary reads the board: *"One, talk. Two, listen. Three... photo."* A look at the camera crew. *"Course it is."* |
| 1:00 | *"Who's in charge here?"* Two fingers jab into the frame at Jason, together, either side of his tablet. He looks at one, then the other. *"It's a collaborative structure."* Gary: *"United behind the manager. Says the man stood in the doorway."* |
| 1:08 | The clipboard: Doorway OBSTRUCTED ✗, Hairdryer MISSING ✗, Captain's arms UP ✓, Step 3 PHOTO ✗, Who's in charge **?** *"Special measures."* Stamp: **SPECIAL MEASURES**. |
| 1:12 | Carrick and Bruno look at each other: on the same side at last. *"Next time, just come straight to me." "Move Jason first."* The handshake. Gary, writing, without looking up: *"Handshake... limp."* Cut to black: **ALL OR SOMETHING / CLEAR THE AIR**. |

## Voices: Fish Audio, the series' own clones

Every line was generated through the Fish Audio API (`s2.1-pro`) with the All or Something clones listed in
[`episode-1-the-clear-plan/voices/`](../episode-1-the-clear-plan/voices/README.md); no other TTS was used and no
voice is sped up or slowed down. The key was read from the `FISH_API_KEY` environment variable and is not in any file.

| Character | Fish reference ID | Same voice as |
|---|---|---|
| Narrator | `38127b71f1f24705817138aeeb97812d` | Episode One's narrator (the final cut) |
| Michael Carrick | `6718a8b753944f098b47d305a601e3c7` | Episode One (the calm meeting voice) |
| Bruno Fernandes | `88aecbad4776441fa53134a0544c561c` | Episode One |
| Jason Wilcox | `ca08dc712b0b423a8db638fed57d7e41` | Episode One and *The Mole* |
| Gary Neville | `ac703e6eaf354ef8b7a768a9f76d4db2` | **new**: cloned for this short from the Gary Neville voiceover of the Overcrap Daily video *Consistently Shit* (`02-gary-neville.mp3`), now kept in the voices' [`sources/`](../episode-1-the-clear-plan/voices/sources/) |

The pack's delivery notes went in front of each line as a bracketed performance tag (directed, never spoken: e.g.
`[quiet, firm, calm, understated, never shouting]` for Carrick, so he stays the calm Carrick of Episode One). Each
cue got three takes per tag (126 for the pack's cues, 54 for the inspection's nine new lines); every take was
transcribed (Whisper) and scored against the character's own voice (speaker similarity), and the take used is
word-perfect and the closest to the character with the asked delivery (Carrick's *"The what?"* also the calmest, to
match his other lines). The scores are in [`project/voice/`](project/voice/) (`takes_qa*.json`); the take used for
each line is in the manifest.

## Characters: the drawings All or Something already films them in

| Character | Drawing | In this short |
|---|---|---|
| Michael Carrick | `michael-carrick`, black club tracksuit (`arms`, `track_explain`, `track`) | as in Episode One |
| Bruno Fernandes | `bruno-fernandes:full`, the full Man United kit, in every shot (his model sheet's upper-body `talk`, `point` and `shrug` also have film entries now, but their mouths don't sync as cleanly as the main drawing's, so they are not used) | the pointing hand and the two open palms (*"Captain."*) are his kit hand drawings |
| Jason Wilcox | `jason-wilcox` cut-out poses in the black tracksuit: `pockets`, `clipboard` (the tablet), `crossarms`, `shrug`, `point` (`shrug` and `point` are new film entries) | always behind the desk, as in the wides; the hand ticking the board wears his tracksuit sleeve (he has no kit hand sheet, so the hand is drawn from Carrick's) |
| Gary Neville | Overcrap Daily's house-style Gary (the Pass Mic model sheet, the drawing *Consistently Shit* uses): `standing` in the doorway (shown exactly as drawn: he doesn't speak there) and `arms` for all his lines (new film entries) | the lanyard and the clipboard are drawn props, and the hand writing on the clipboard is his own kit hand drawing; the badge says STANDARDS / *Inspector (self-appointed)*, not a real Ofsted badge |

The office is Episode One's (Como's) office, from the desk's side, with the wide angle of the same room for the
door (the office's narrow door is replaced there by a wide open doorway with a corridor behind it, so Jason can stand in it and Bruno can try to get past him, and Gary arrives through the same doorway); the board, the tablet, the clipboard and the stamp are drawn into the shots. Carrick and Bruno sit behind the desk with only the real outlines of the laptop, the pen pot and the books in front of them, so their bodies are whole. The handshake close-up
and the two pointing fingers use Carrick's and Bruno's own kit hand drawings.

**Lip sync.** Every mouth is driven by the line's own phonemes (a frame ahead of the sound, closures held for the
M, B and P) and opens with its loudness, as in Episode One. For the bigger portrait close-ups the openings were
checked frame by frame and made clearer: Bruno's mouth now opens properly inside the beard (`jaw` 1.0 → 1.7),
Carrick's a little wider (1.6 → 1.9), and Gary's lip line, which had drawn every half-open mouth as a dark bar, is
thin again (`lip_lt` 0.4 at 8×, `jaw` 1.6). Only drawings whose mouths sync cleanly are used for a speaking line;
the settings are in [`project/library/characters/`](project/library/characters/).

**Carrick keeps still.** His head's idle sway is a third of everyone else's, and his nods and turns half, so in the
big portrait close-ups he plays as calm and understated as in Episode One.

**Framed for a phone.** The three-shots are tight (Carrick and Bruno at the desk, Jason between and behind them,
the board over Bruno's shoulder), the close-ups fill the frame from the head to below the chest with the desk in
front, and the doorway shots fill the height with the standing figure.

## Sound, titles, length

- **Loudness:** −14.0 LUFS integrated, true peak −1.2 dBTP (measured on the finished MP4's soundtrack). Room tone
  and the city through the window throughout; sparse documentary strings under the narrator only; trainer squeaks in the
  doorway; the door bang on Gary with a very short official sting; his pen after every verdict; Bruno's sleeves; the
  stamp. No laugh
  track.
- **No subtitles.** The only text over the picture is the opening UNITED ROAD ORIGINAL mark and the CARRINGTON place
  title, kept inside the phone-safe area (x 90–900, y 180–1500; the app's buttons sit down the right edge), and the
  end card.
- **Length: 1:23.7**, every voice at its natural pace (none sped up), the comic beats held: the doorway dance, a
  beat after "Progress", a beat after each of Gary's verdicts, a full second on the two fingers.

## Checks

CHECKS_PENDING

## Publishing copy

**Title:** Clear the Air | All or Something

**Description:**

> Carrick and Bruno finally sit down to clear the air. In private. Jason has invited a camera crew. 🎥
>
> Then Gary Neville walks in with a clipboard. Standards inspection. The hairdryer is missing. The captain's arms
> are up. Step three is "photo". Nobody knows who's in charge. ✅
>
> Fictional AI-animated football satire. Voices are AI clones. A United Road Original.
>
> #ManUtd #ManchesterUnited #Carrick #BrunoFernandes #GaryNeville #JasonWilcox #MUFC #PremierLeague #FootballComedy #AllOrSomething #UnitedRoad #Shorts

## Rebuilding it

The film is made with the AnimnationStuido- studio (`studio/film`), with Episode One's engine patch applied
([`episode-1-the-clear-plan/v2/studio-engine.patch`](../episode-1-the-clear-plan/v2/studio-engine.patch)).

1. Voices (only if you want new takes): `FISH_API_KEY=... python3 project/voice/gen_takes.py project/voice/requests.json OUT` (and `requests_inspection.json` for Gary's scene).
2. In the studio: copy `project/film/` to `episodes/clear-the-air/film/`, `project/script.md` to
   `episodes/clear-the-air/`, and each `voice/NN_<name>.wav` to `episodes/clear-the-air/voiceovers/` as
   `ANN-<character id>.wav` (`A01-narrator.wav`, `A02-michael-carrick.wav`, … the manifest's `voice` field gives the
   id); copy `project/library/characters/*` over `library/characters/`.
3. `python3 -m studio.film clear-the-air lines`, then `EP_RES=1080x1920 python3 -m studio.film clear-the-air sound`,
   `... render --jobs 3` and `... check`. The stems: `film/stems.py` (its docstring has the command).
