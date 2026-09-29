# All or Something

Animated Manchester United mock-documentary shorts (an *All or Nothing* parody), 9:16 portrait for YouTube
Shorts / TikTok. Made the same way as Pass the Mic and the TV Show scenes: recorded voice clips, word-level lip
sync, and characters cut from their model sheets, upscaled and animated in Python, rendered with ffmpeg.

## Layout

| Folder | What's in it |
|---|---|
| [`audio/`](audio/) | The voice-overs, one folder per voice (narrator, Carrick, Jason, Omar, Bruno, Jim), labelled by what's said. [`audio/README.md`](audio/README.md) has every clip's words. |
| [`images/`](images/) | `characters/` (model sheets) and `backgrounds/` (portrait sets). [`images/README.md`](images/README.md) lists them. |
| [`scenes/`](scenes/) | One folder per episode: its code, README and video. Episode 1: [`ep01-three-midfielders/`](scenes/ep01-three-midfielders/). |
| [`pipeline/`](pipeline/) | The proven pipeline code (templates) new scenes are copied from. |
| [`tools/`](tools/) | `new_scene.sh` (start a scene), `stills.py` / `joins.py` / `walkcheck.py` (review), `render.sh`, `preview.sh`. |
| `.claude/` | The `new-scene` workflow Claude follows, and the start-up hook that installs ffmpeg + Python packages. |

## Make a new episode

Open a Claude Code session on this repo and type `/new-scene` followed by the script (or your director's
notes). Put any new voice clips or art in `audio/` and `images/` first, or attach them to the message.

Claude builds the episode in `scenes/<slug>/`, checks it against the quality bar in
[`.claude/skills/new-scene/SKILL.md`](.claude/skills/new-scene/SKILL.md), renders it, pushes it and sends you a
720p preview.

By hand:

```bash
pip install -r requirements.txt                  # plus ffmpeg on PATH (automatic in Claude Code web sessions)
tools/new_scene.sh ep02-some-title               # copies Episode 1's pipeline into scenes/ep02-some-title
```
