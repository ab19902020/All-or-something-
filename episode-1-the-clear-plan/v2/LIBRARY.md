# What the film packages need in the studio library

The seven packages in [`film/`](film/) are filmed by AnimnationStuido- (`claude/ollies-episode-production-tdnt6j`)
with the engine patch in [`studio-engine.patch`](studio-engine.patch) (it includes the first version's patch and adds
the `lip_lt` mouth-line setting and the mix's trims, level rider and soft-knee limiter in `audio.py`). *Last
Chance* uses only what *The Handover* already uses there (the boardroom, its foley, Ole and his door); *Upstairs*
and *Bournemouth* only what the other packages already use (the mixed zone, the press room, the corridor, the
boardroom, the dressing room, the stand).
Everything else they use is already in that library, apart from the files below. Each one is a byte-for-byte copy of
a file in one of the show's own repositories (checked by SHA-256), filed under `library/`:

| Filed as (`library/...`) | Copied from |
|---|---|
| `backgrounds/aos/locker-room-wide.png` (every dressing room) | TV-show- `manchester-united-documentary/assets/backgrounds/locker-room/cinematic-red-team-locker-room.png` |
| `backgrounds/aos/stadium-exterior.png` (Hull at dusk) | `.../stadium-exterior/dusk-at-the-red-lit-stadium.png` |
| `backgrounds/aos/mixed-zone.png`, `interview-corridor.png` | `.../mixed-zone/stadium-mixed-zone-corridor-in-red-and-black.png`, `empty-stadium-interview-corridor.png` |
| `backgrounds/aos/office.png`, `press-room.png`, `press-stage.png`, `tunnel.png` | `.../manager-office/modern-football-managers-analysis-office.png`, `.../press-conference/cinematic-empty-sports-press-room.png`, `empty-red-black-press-conference-stage.png`, `.../stadium-tunnel/stadium-tunnel-to-the-pitch.png` |
| `backgrounds/documentary/*.png` (The Mole's sets, the office, the corridor) | the same folder: `manager-office/sunset-football-managers-office.png`, `mixed-zone/red-and-black-press-corridor.png`, `tv-studio/red-and-black-football-interview-studio.png`, `locker-room/cinematic-red-football-locker-room.png`, `tactics-room/red-and-black-football-tactics-room.png` |
| `characters/jason-wilcox/reference/poses/*`, `variants/*` | TV-show- `the-mole/library-overlay/characters/jason-wilcox/reference/` (`claude/new-session-ow0mwl`) |
| `characters/lisandro-martinez/reference/poses/*`, `variants/*` | `the-mole/library-overlay/characters/lisandro-martinez/reference/` |
| `characters/omar-berrada/reference/variants/city-hero.png` | `the-mole/library-overlay/characters/omar-berrada/reference/variants/` |
| `fonts/Oswald.ttf`, `fonts/PermanentMarker-Regular.ttf` | Google Fonts (SIL Open Font License) |

Seven characters' drawing lists (`film.yaml`) as filmed are in [`library/characters/`](library/characters/), to
copy over the library's own: Wilcox and Martínez are filmed from the user's cut-out poses (the ones The Mole uses),
Berrada from his model sheet; Bruno's adds `full`, the hero figure of his model sheet in the full Man United kit; and
Bruno, Martínez, Cunha, Mount and Maguire carry `lip_lt`, the real half-thickness of their drawn mouth line (the
engine otherwise measures the moustache into it and outlines every open mouth far too heavily).

## Rebuilding a package

```bash
cp -r v2/film/v2-month  <AnimnationStuido->/episodes/v2-month
for f in v2/takes/H*.flac v2/takes/R*.flac; do ffmpeg -i $f episodes/v2-month/voiceovers/$(basename ${f%.flac}).wav; done
# v2-month only: the match clips as frames
for k in hull1 hull2; do mkdir -p episodes/v2-month/clips/$k; ffmpeg -i episodes/v2-month/clips/$k.mp4 -q:v 2 episodes/v2-month/clips/$k/%04d.jpg; done
python3 -m studio.film v2-month lines && python3 -m studio.film v2-month timeline
python3 -m studio.film v2-month sound && python3 -m studio.film v2-month render
```

(`M*` takes go to `v2-meeting`, `H*`/`R*` to `v2-month`, `X*` to `v3-upstairs`, `L*` to `v2-mole`, `C*` to
`v2-como`, `K*` to `v2-lastchance`, `B*` to `v3-bournemouth`.) Render each package whole, or only the ranges the
splice list in [`assemble_final.py`](assemble_final.py) names (`render --range A B`, kept as the file it names), then
`python3 v2/assemble_final.py --studio <AnimnationStuido-> --out OUT` joins them.
