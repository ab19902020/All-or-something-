# Images

All art for the show. Scenes copy what they use from here into their own `src/` folder.

## Characters (`characters/`)

Character model sheets, 1122 × 1402 unless noted: a hero drawing, full-body turnaround, head close-up views,
facial expressions, a mouth / phoneme set for lip sync, hand poses, upper-body gesture poses and leg/walk poses.
The episode pipeline cuts drawings from these by box (`parts.py`), so a new sheet needs its boxes measured once
(grid it, as in the new-scene skill). Characters used so far: Carrick, Jason, Omar, Bruno, Jim (Episode 1).

| File | Who | Notes |
|---|---|---|
| `michael-carrick.png` | Michael Carrick | Black tracksuit. 9 mouths; gestures: arms crossed, explaining, pointing, thinking, talking. |
| `jason-wilcox.png` | Jason Wilcox | Black tracksuit. 10 mouths; gestures: arms crossed, pointing, explaining, holding tablet, thinking. Drawn very like Mark Goldbridge, so Episode 1 restyles him (silver short hair, stubble, navy tracksuit): see `restyle_jason` in the episode's `parts.py`. |
| `omar-berrada.png` | Omar Berrada | Dark suit, red tie. 9 mouths; gestures: arms crossed, explaining, pointing, clipboard, phone. |
| `bruno-fernandes.png` | Bruno Fernandes | Home kit, captain's armband. 10 mouths; gestures: pointing, celebrate, talking, shrug. |
| `jim-ratcliffe.png` | Jim Ratcliffe | Dark suit, maroon tie. 9 mouths; gestures: neutral, pointing, explaining, thinking. **Main Jim sheet.** |
| `yuri-tielemans.png` | Yuri Tielemans | Midfielder, #8, home kit. 6 mouths (A E I O U closed), 8 expressions, eye positions; poses: talking 1 & 2, pointing, arms crossed, shrug, thinking; 4-frame walk and run cycles. |
| `senne-lammens.png` | Senne Lammens | Goalkeeper, #1, black keeper kit and gloves. Same layout as Tielemans (6 mouths, 8 expressions, eye positions, 6 speaking poses, walk and run cycles). |
| `benjamin-sesko.png` | Benjamin Šeško | Forward, #30, home kit, sleeve tattoos. Same layout as Tielemans. |
| `kobbie-mainoo.png` | Kobbie Mainoo | Midfielder, #37, home kit. Same layout as Tielemans. 1121 × 1403. |
| `luke-shaw.png` | Luke Shaw | Left-back, #23, home kit, beard. 10 mouths (rest, A, E, I, O, U, smile, frown, wide shout), 6 expressions; poses: pointing, celebrate, talking, shrug; 3-pose walk and run. 1086 × 1448. |
| `harry-maguire.png` | Harry Maguire | Defender, #5, home kit. Same layout as Shaw (10 mouths, 6 expressions, 4 gesture poses, walk and run). |
| `steve-holland.png` | Steve Holland | Coach, black club tracksuit, shaved head, stubble. Same layout as Shaw. |
| `jim-ratcliffe-alt.png` | Jim Ratcliffe | Older, softer sheet (1024 × 1136) with extra poses in a red training top. Spare / reference. |

## Backgrounds (`backgrounds/`)

All portrait 941 × 1672 (9:16), for Shorts / TikTok.

| File | What it shows |
|---|---|
| `carrington-entrance.png` | Carrington training-complex entrance: glass front, red canopy, pitches to the left. |
| `boardroom-wide.png` | Boardroom down the length of the table: tactics screen, chairs both sides, a tablet. |
| `boardroom-side-view.png` | Boardroom from the window side: red carpet, chairs along the table, tactics screen. |
| `boardroom-window-view.png` | Boardroom towards the corner windows onto the pitches; club crest on the wall. |
| `tactics-room-screen.png` | Close on the end of the table and the tactics screen (good for singles / close-ups). |
| `monaco-office.png` | Luxury office with the Monaco harbour view (Jim's cutaway). |
| `hull-stadium-exterior.png` | MKM Stadium, Hull: sunny exterior, tiger flags and banners (Episode 2 opening). |
| `hull-away-dressing-room-pre-match.png` | Hull away dressing room before the game: United kits hanging, tactics board on a stand, central table with bottles, tiger rug. |
| `hull-away-dressing-room-post-match.png` | The same room after the game: towels, bottles, muddy boots and kit bags everywhere, the tactics board on the wall, the door open to the tunnel. |
| `hull-tunnel.png` | The players' tunnel, amber and black tiger murals, the pitch at the end. |
| `hull-pitch-corner.png` | Corner flag with the "HULL" stand behind (set-piece flashes, the Tigers song ending). |
| `hull-stadium-strip.png` | Five landscape panels in one image: exterior with the tiger statue, the home dressing room ("TO THE PITCH" door), the tunnel ("TIGERS TOGETHER"), the pitch wide with the dugout, the home dressing room after the game. |
