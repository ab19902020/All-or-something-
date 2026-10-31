# ALL OR SOMETHING — Clear the Air (portrait short)

A vertical short for Reels, TikTok and Shorts, made from the production pack in [`pack/`](pack/) (the refined
*Clear the Air*: Carrick and Bruno's private clear-the-air meeting, which Jason has filmed). Same characters, same
voices and the same office as Episode One.

| | |
|---|---|
| **The film** | [`ALL_OR_SOMETHING_CLEAR_THE_AIR_1080x1920.mp4`](ALL_OR_SOMETHING_CLEAR_THE_AIR_1080x1920.mp4): 1080 × 1920, 30 fps, 1:13.4, H.264 + AAC, no subtitles |
| **Voices** | [`voice/`](voice/): the 21 cues as WAV, under the pack's file names (`01_narrator.wav` … `21_gary.wav`) |
| **Generation manifest** | [`generation_manifest.json`](generation_manifest.json): every cue's character, Fish Audio reference ID, model, delivery tag, take, file, measured duration and checksum. No credentials |
| **Stems** | [`stems/`](stems/): `dialogue.wav`, `effects.wav` (room, city, foley), `music.wav`, 48 kHz 32-bit float, each at its level in the mix (before the limiter), so together they rebuild it |
| **Editable project** | [`project/`](project/): the film's production code, the script, the voice requests and take QA, and the character drawing settings this short added |

## The short

| Time | What happens |
|---|---|
| 0:00 | **UNITED ROAD ORIGINAL.** Carrington, the manager's office. Carrick and Bruno at the desk, Jason behind them with the board: CLEAR THE AIR / *no leaks*. Narrator: *"A private meeting to clear the air. Jason had invited a camera crew."* Jason waves the camera in. |
| 0:06 | Carrick: *"Bruno, if you've got a problem with the tactics, tell me. Not the television."* Bruno: *"I tried. You said your door was always open."* *"It is."* *"Jason was standing in it."* |
| 0:18 | The doorway: Jason, in it. He shuffles six inches sideways. He is still mostly in the doorway. |
| 0:20 | The honest exchange: *"Maybe I could've been clearer." "And maybe I shouldn't have said it on telly." "So we're all right?" "Yes. I still think the tactics were shit." "Aye. But now you've told me indoors. Progress."* A tiny, reluctant smile. |
| 0:35 | Behind them, the board gets its tick: **RESOLVED**. Jason, at arm's length, finger on the nozzle of a blue can: *Pssht. Pssht.* |
| 0:39 | *"Jason. What are you doing?" "Clearing the air. It's on the agenda." "That's air freshener." "Fresh start."* (the can held up by his face, like an advert). The first look they have ever shared. |
| 0:48 | *"Next time, just come straight to me." "Move Jason first."* The handshake. Jason raises the tablet for the camera: **UNITED BEHIND THE MANAGER**. |
| 0:56 | The door bangs open: Gary Neville steps into the doorway, lanyard (STANDARDS, *Inspector, self-appointed*). *"Surprise standards inspection." "Gary, you're not Ofsted." "Who's in charge here?"* Two fingers jab into the frame at Jason, together: Carrick's from one side, Bruno's from the other, either side of his UNITED BEHIND THE MANAGER tablet. He looks at one, then the other. *"It's a collaborative structure."* |
| 1:06 | Gary's clipboard: Doorway OBSTRUCTED ✗, Air FRESHENED ✓, Communication TELEVISED ✗, Who's in charge **?** *"Special measures."* Stamp: **SPECIAL MEASURES**. |
| 1:09 | Carrick and Bruno side by side, resigned. Somewhere under the desk, one small accidental *pssht*. Cut to black: **ALL OR SOMETHING / CLEAR THE AIR**. |

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
cue got three takes per tag, 126 in all; every take was transcribed (Whisper) and scored against the character's own
voice (speaker similarity), and the take used is word-perfect, the closest to the character with the asked delivery,
and was listened to. The scores are in [`project/voice/takes_qa.json`](project/voice/takes_qa.json); the take used
for each cue is in the manifest.

## Characters: the drawings All or Something already films them in

| Character | Drawing | In this short |
|---|---|---|
| Michael Carrick | `michael-carrick`, black club tracksuit (`arms`, `track_explain`, `point`, `track`) | as in Episode One |
| Bruno Fernandes | `bruno-fernandes:full`, the full Man United kit, in every shot (his model sheet's upper-body `talk`, `point` and `shrug` also have film entries now, but their mouths don't sync as cleanly as the main drawing's, so they are not used) | the pointing hand is his kit hand drawing |
| Jason Wilcox | `jason-wilcox` cut-out poses in the black tracksuit: `pockets`, `clipboard` (the tablet), `phone` (the can by his face), `point` (the can at arm's length), `crossarms`, `shrug` (`shrug` and `point` are new film entries) | always behind the desk, as in the wides |
| Gary Neville | Overcrap Daily's house-style Gary (the Pass Mic model sheet, the drawing *Consistently Shit* uses): `standing` in the doorway (shown exactly as drawn: he doesn't speak there) and `arms` for all three of his lines (new film entries) | the lanyard and the clipboard are drawn props; the badge says STANDARDS / *Inspector (self-appointed)*, not a real Ofsted badge |

The office is Episode One's (Como's) office, from the desk's side, with the wide angle of the same room for the
door; the board, the can, the tablet, the clipboard and the stamp are drawn into the shots. The handshake close-up
and the two pointing fingers use Carrick's and Bruno's own kit hand drawings.

**Framed for a phone.** The three-shots are tight (Carrick and Bruno at the desk, Jason between and behind them,
the board over Bruno's shoulder), the close-ups fill the frame from the head to below the chest with the desk in
front, and the doorway shots fill the height with the standing figure.

## Sound, titles, length

- **Loudness:** −14.0 LUFS integrated, true peak −1.2 dBTP (measured on the finished MP4's soundtrack). Room tone
  and the city through the window throughout; sparse documentary strings under the narrator only; the sprays are a
  synthesised aerosol hiss; the door bang on Gary with a very short official sting; the pen; the stamp. No laugh
  track.
- **No subtitles.** The only text over the picture is the opening UNITED ROAD ORIGINAL mark and the CARRINGTON place
  title, kept inside the phone-safe area (x 90–900, y 180–1500; the app's buttons sit down the right edge), and the
  end card.
- **Length: 1:13.4, not the pack's 85–90 s.** The pack's times were estimates; with every voice at its natural pace
  and every comic pause the pack asks for held (0.4–0.8 s after the doorway sidestep, 0.5 s after "Progress", 0.6 s
  after "Fresh start", a full second on the two of them pointing), the scene plays in 73 seconds. Filling the rest
  with dead air or slower reads would have flattened the jokes.

## Checks

The film and its checks (every line heard back from the finished mix, the lip sheet, loudness and true peak on the MP4) are added with the render.

## Publishing copy

**Title:** Clear the Air | All or Something

**Description:**

> Carrick and Bruno finally sit down to clear the air. In private. Jason has invited a camera crew. 🎥
>
> What follows: an honest conversation, a whiteboard, a blue can of air freshener, a handshake for the cameras, and
> a surprise standards inspection from Gary Neville. ✅
>
> Fictional AI-animated football satire. Voices are AI clones. A United Road Original.
>
> #ManUtd #ManchesterUnited #Carrick #BrunoFernandes #GaryNeville #JasonWilcox #MUFC #PremierLeague #FootballComedy #AllOrSomething #UnitedRoad #Shorts

## Rebuilding it

The film is made with the AnimnationStuido- studio (`studio/film`), with Episode One's engine patch applied
([`episode-1-the-clear-plan/v2/studio-engine.patch`](../episode-1-the-clear-plan/v2/studio-engine.patch)).

1. Voices (only if you want new takes): `FISH_API_KEY=... python3 project/voice/gen_takes.py project/voice/requests.json OUT`.
2. In the studio: copy `project/film/` to `episodes/clear-the-air/film/`, `project/script.md` to
   `episodes/clear-the-air/`, and each `voice/NN_<name>.wav` to `episodes/clear-the-air/voiceovers/` as
   `ANN-<character id>.wav` (`A01-narrator.wav`, `A02-michael-carrick.wav`, … the manifest's `voice` field gives the
   id); copy `project/library/characters/*` over `library/characters/`.
3. `python3 -m studio.film clear-the-air lines`, then `EP_RES=1080x1920 python3 -m studio.film clear-the-air sound`,
   `... render --jobs 3` and `... check`. The stems: `film/stems.py` (its docstring has the command).
