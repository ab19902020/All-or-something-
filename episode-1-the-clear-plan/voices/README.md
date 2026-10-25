# Voices: every character cloned in Fish Audio

Each speaking character of the show has one **private** Fish Audio voice model on your account, cloned from **one**
of that character's existing voice uploads (not all of them). The models are listed in
[`fish_models.json`](fish_models.json); the upload each one was cloned from is in [`sources.json`](sources.json).

| Character | Fish model ID | Cloned from (one upload) |
|---|---|---|
| Michael Carrick | `6718a8b753944f098b47d305a601e3c7` | *The Handover* (the sacking), `03-michael-carrick.mp3`, the re-recorded take |
| Bruno Fernandes | `88aecbad4776441fa53134a0544c561c` | Episode 1 recordings, `Bruno/Clony-AI-2Y1Gwqr8neTEo43q.mp3` |
| Harry Maguire | `32d235d432934c7d90483dcc9c24fa3a` | Episode 1 recordings, `harry m/Clony-AI-Kzk4F3tsMBLpnbPz.mp3` |
| Jason Wilcox | `ca08dc712b0b423a8db638fed57d7e41` | *The Mole*, `03-jason-wilcox.mp3` |
| Lisandro Martínez | `cd58f6ba83354fd1a77c62b12f5c81eb` | *The Mole*, `02-lisandro-martinez-1.mp3` |
| Narrator | `31f154b4905e471fb4c5931140c8e53f` | *The Mole*, `01-narrator.mp3` |
| Sir Jim Ratcliffe | `92d6713eeb69455c9385ba6f9fc08658` | *The Handover*, `01-jim-ratcliffe.mp3` |
| Omar Berrada | `31539149ea1f42c2a7fcbc9529738496` | Episode 1 recordings, `omar/Clony-AI-gpqmga8px6et6YNx.mp3` |
| Matheus Cunha | `8c515774bbf24dd39dd8fa2798f74e28` | Episode 1 recordings, `cunha/Clony-AI-EmNDgOEtkRQOseFe.mp3` |
| Benjamin Šeško | `37aa44daaa0b4a3697d290d1cd724d52` | Episode 1 recordings, `sesko/Clony-AI-ntlzQcGzRUduDHjr (1).mp3` |
| Shea Lacey | `287893dd9b674aa9b625611ace4176b9` | Episode 1 recordings, `shea Lacey/Clony-AI-b4zq76b9IO6xK89v.mp3` |
| Mason Mount | `0cd1178e960a4cdd937694e0d8168203` | Episode 1 recordings, `masson/Clony-AI-kuIrCNWgJWiwgK7D.mp3` |
| Documentary producer | `a303b13cbc0f4093a02d418ff8f32f1a` | Episode 1 recordings, `documentary voice/Clony-AI-ejJnYjNNsDz9iBn6.mp3` |
| Joel Glazer | `17da66aa44bb4160957cef0dd0286429` | Episode 1 recordings, `j glazer/Clony-AI-ecyktuuXcVQCHNGa.mp3` |
| Avram Glazer | `1a0c7847afd24d26b19016853f4d5cdd` | Episode 1 recordings, `a glazer/Clony-AI-VGllzn0mfCmq0W7T.mp3` (only 3.4 s exists, so this clone is the weakest) |

"Episode 1 recordings" are the Clony AI clips in `show TV.zip` (TV-show- repo); *The Mole* is on TV-show-
`claude/new-session-ow0mwl`; *The Handover* is on AnimnationStuido- `claude/ollies-episode-production-tdnt6j`.
All models are private and titled "AOS … (parody)".

## Making more lines with any character

The API key is never stored in the repository: pass it in the environment.

```bash
export FISH_API_KEY=...                       # your Fish Audio key
python3 voices/fish_tts.py OUT_DIR            # every line in lines.json, one take each
python3 voices/fish_tts.py OUT_DIR --only C01,B05 --takes 3      # just some lines, three takes each
python3 voices/fish_tts.py OUT_DIR --model s1 --suffix _s1       # the older model, for comparison
```

`lines.json` is a list of `{"id", "speaker", "voice", "text"}`; `voice` is a key of `fish_models.json`. Takes are
44.1 kHz WAV. To clone another character, add it to `sources.json` and run `python3 voices/fish_clone.py --only
<id>` (characters that already have a model are skipped).

## The takes used in this episode

Every new line was generated three times (two takes with Fish's `s2.1-pro`, one with `s1`) and the take used was
chosen by two measurements (`takes_chosen.json`): Whisper had to hear the words as written, and the take had to sound
most like the character's source recording (speaker-embedding similarity, TitaNet). The chosen takes are in
[`takes/`](takes/) (FLAC). Notes:

- "Sabah" is not a word Whisper knows; the take used was generated from the spelling "Sah-bah" so it is pronounced
  right.
- One-word lines ("Together.", "Everyone?", "Not...") score low on similarity because they are too short to measure,
  not because they sound wrong.
- Wilcox's closing "We've got a very clear plan." (W01) is his **original** recording from the opening, used as the
  callback the script asks for; it was not regenerated.
- The reused episodes (the boardroom, Hull, The Mole) keep their original recorded voices; only new dialogue was made
  with the clones.

## Version 2

Every line of the remake (195, The Mole's included) is in [`../v2/lines_v2.json`](../v2/lines_v2.json) and was made
with [`../v2/fish_batch.py`](../v2/fish_batch.py) (several requests at once, two takes per line):

```bash
FISH_API_KEY=... python3 v2/fish_batch.py OUT_DIR --takes 2
```

A line's optional `say` field is what the voice is given when it differs from the script's spelling ("Sah-bah",
"Sheshko"). The takes used are in [`../v2/takes/`](../v2/takes/), scored in
[`../v2/takes_chosen.json`](../v2/takes_chosen.json).
