# All or Something, Episode 2: "Welcome to Hull"

**Video:** [`all_or_something_ep02_welcome_to_hull.mp4`](all_or_something_ep02_welcome_to_hull.mp4)
(1080 × 1920, 9:16, 30 fps, 1 min 36 s, with the soundtrack). A 720p preview is made with `tools/preview.sh`.

The next episode of the mock-serious documentary: opening day of the new season, away at newly promoted Hull. The
same look and grammar as Episode 1 (slugs, name captions, slow pushes, hard cuts, a voice-only narrator), with
fast comedy cuts; everyone treats complete chaos as a normal professional football operation.

## What's in it

| Time | Shot | What happens |
|---|---|---|
| 0:00 | MKM Stadium | Slow push, **HULL / OPENING DAY**, over-serious strings and piano. Narrator: "New season... new Manchester United..." The music stops dead. "Probably." |
| 0:04 | Away dressing room | Hard cut inside. Slug: AWAY DRESSING ROOM, MKM Stadium, Hull. The squad (Lammens, Šeško, Bruno, Maguire) sits behind the table, Kobbie at the far end on his own, Carrick and Steve at the tactics board. Carrick points at the board: "Hull have just come up... aggressive... physical... dangerous from set pieces." |
| 0:12 | Carrick / Steve | Steve looks up from his clipboard: "Should we practise defending those then?" "Already did. Thursday." "That was attacking corners." Carrick looks at the board, back at Steve: "Same corner though, isn't it?" Bruno slowly looks into the lens. |
| 0:20 | The Mainoo gag | "Kobbie... you're on the bench." "Again?" "We've bought midfielders." "I noticed." Bruno: "We've got about nine of us now." Maguire: "Can any of them play striker?" Silence: the players turn to Carrick one by one. |
| 0:28 | The wrong door | Carrick looks away, claps, "Right... Hull City... COME ON!" and strides off across the room. Nobody follows. Steve: "Michael... wrong door." Carrick at a door marked STORE CUPBOARD: stops, reads it, looks back at everyone, turns round, walks off the other way. |
| 0:35 | Full time | Smash cut: black, **HULL CITY 2, MANCHESTER UNITED 0**, the whistle and a burst of the home end, then silence. Narrator: "Manchester United knew exactly what was coming." 23' CORNER, the ball swung in, GOAL, HULL 1-0. "It did not help." 58' CORNER, GOAL, HULL 2-0, and the Hull fans: "You're getting mauled by the tigers." Carrick staring from the touchline, Maguire lost, Bruno shouting. |
| 0:43 | Dressing room, after | Hard cut to total silence, the room wrecked. Carrick in exactly the same spot, Steve beside him, Maguire and Bruno from behind. "Right... positives." Nobody speaks. Bruno: "We had seventy percent possession." "Excellent." "We lost two-nil." Steve checks the clipboard: "Less excellent." |
| 0:51 | Set pieces | Harry's hand goes up, slightly: "Both goals were set pieces." "Yep." "The thing you warned us about before the game." "Yep." "Twice." "Harry... I'm aware." Tiny zoom; the hand comes slowly down. |
| 0:58 | Kobbie | Whip across the room to Kobbie, arms folded: "I came on after sixty-seven minutes, two-nil down... What exactly was the plan?" Carrick thinks: "Impact." "We didn't score." "Nearly impact." Kobbie stares into the lens. |
| 1:07 | The striker | Bruno stands up: "So... newly promoted Hull... two set pieces... no goals." Maguire: "I had to start shooting." "You're a centre-back." "Nobody else was doing it." Carrick starts to say something, stops, looks away. |
| 1:16 | Ipswich | Steve: "Good news." They all look up; a little hopeful music. "We've got Ipswich next." The music dies. Kobbie: "Didn't Ipswich just get promoted as well?" They all turn to Carrick. Into the lens: "Good meeting." He walks straight out; a door shuts. |
| 1:24 | Bruno | He watches him go, turns to us, the room going grey behind him: "Can somebody check if Saudi are still calling?" |
| 1:27 | Title | Hard cut to black, the boom: **ALL OR SOMETHING / NEW SEASON. SAME CORNERS.** Narrator: "New season, same corners. This is All or Something." |
| 1:33 | Tigers ending | The chant again over the pitch: HULL 2-0 UNITED, then Maguire blank, Kobbie arms folded, Steve and his clipboard, Bruno finished, Carrick walking away. Cut dead, so it loops into the opening. |

**Beyond the script:** the narrator's "Manchester United knew exactly what was coming... It did not help." over
the goals (from his recording); the four new squad players as background characters; the STORE CUPBOARD door; the
match captions and scoreboards; the door shutting behind Carrick.

**Voices:** all from `audio/`. Steve Holland uses the same generated voice as Jason Wilcox in Episode 1 (the
user's choice). Pauses inside lines are trimmed to 0.14 s and every line plays 12 % faster (pitch unchanged)
to keep it tight.

## How it's made

The Episode 1 pipeline (see [its README](../ep01-three-midfielders/README.md)), with these additions:

- `parts.py`: the new drawings (Mainoo, Maguire, Steve Holland, Šeško, Tielemans, Shaw, Lammens, and Carrick's
  side, back, pointing and walking poses; Bruno's back and shouting poses). The torso extension now tells skin from
  shirt by hue, so dark skin and collar lines are handled.
- `props.py`: the STORE CUPBOARD door (the stadium strip's dressing-room door with its lettering repainted and wall
  added), and Maguire's raised hand (his sheet's open palm, its forearm continued so it rises from below the frame).
- `render.py`: actors that walk and change drawing on keyframes (Carrick's walk and the door), Steve's clipboard,
  Bruno standing up, Carrick's clap and exit, the corner kicks (a drawn ball), the goal and Tigers scoreboards.
- `audio.py`: the supplied Hull fans' chant, real crowd, whistle, clap, footsteps, ball kick and door recordings
  (BigSoundBank and Wikimedia Commons, all CC0, listed in `audio/sfx/manifest.json`), the music that stops dead,
  and the hopeful music that dies on "Ipswich".

`./make_episode.sh` builds everything. Quick checks: `EP_RES=540x960 python3 render.py still 20 40 60`;
`python3 check_audio.py --words` re-transcribes every line from the finished mix.
