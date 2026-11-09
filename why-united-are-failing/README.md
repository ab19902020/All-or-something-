# WHY UNITED ARE FAILING — a 60-second tactical breakdown (portrait, YouTube Shorts)

Made from scratch: every frame is drawn by code (no cut-outs, no stock footage, no club crest). The voiceover is the
All or Something narrator's Fish Audio clone. Facts are as of Monday 9 November 2026, the day after United 4-4 Aston
Villa.

| | |
|---|---|
| **The video** | [`WHY_UNITED_ARE_FAILING_1080x1920.mp4`](WHY_UNITED_ARE_FAILING_1080x1920.mp4): 1080 × 1920, 30 fps, 61.4 s, H.264 + AAC 256k, −14.6 LUFS, true peak −1.7 dBTP |
| **Voice** | [`voice/voiceover.wav`](voice/voiceover.wav) (the clean voice track), [`voice/mix.wav`](voice/mix.wav) (the full mix) |
| **Project** | [`project/`](project/): `make.py` draws every frame, `audio.py` builds the soundtrack, `bd_vo.py` assembles the voice track; the voice requests, takes scores, picks and word timings |

## The script (narrator, Fish Audio `s2.1-pro`, reference `38127b71f1f24705817138aeeb97812d`)

| Time | Line | On screen |
|---|---|---|
| 0:00 | *Manchester United are eighteenth. In the relegation zone.* | **18TH** slams in; RELEGATION ZONE |
| 0:04 | *Eight points from ten games. Eight league games without a win.* | P10 W1 D5 L4 GD −5 PTS 8; the form strip EVE D, MCI L, FUL D, TOT D, LEE D, BOU L, CHE L, AVL D |
| 0:09 | *Start on the pitch. Carrick's four-two-three-one becomes a three-one-six with the ball.* | a tactics board: the 4-2-3-1 morphs into the 3-1-6 (the right-back tucking into midfield) |
| 0:14 | *Six men ahead of it, one man holding. Lose it, and there's a canyon between the press and the back four.* | the six ringed, then the lone holder; the ball lost; THE CANYON opens between the lines and three counters run through it |
| 0:21 | *Against Villa, two-nil down inside four minutes. Full-backs high, two centre-backs left alone.* | the clock: 0-1 1', 0-2 4'; 26 SHOTS · 3.09 xG CONCEDED; the full-backs push up, the two centre-backs isolated |
| 0:28 | *Thirty conceded this season. More than any team in Europe's top five leagues.* | **30**; MOST IN EUROPE'S TOP 5 LEAGUES (Opta) |
| 0:33 | *Then look upstairs. The Glazers bought this club with borrowed money in 2005. Twenty years on, the club is still paying for it.* | LOOK UPSTAIRS; **2005**, the takeover funded by borrowing; 2005 → 2026; STILL PAYING |
| 0:42 | *Ratcliffe runs the football, owns under a third, and the fans are turning on both.* | RATCLIFFE RUNS THE FOOTBALL; the ownership ring, ~29% INEOS, the Glazer family the majority; the crowd turning red |
| 0:48 | *Sunday's banner: we don't want a new stadium. We want the owners out.* | the banner, painted on as it is read |
| 0:53 | *It isn't one coach. It's the shape on the pitch, and the structure above it.* | THE STRUCTURE over THE SHAPE; end card |

## The sound

Every line is its Fish Audio take whole: nothing is cut inside a line, each is trimmed only at its quiet ends with
soft fades, and the lines sit on a faint room tone (an earlier version shortened the pauses inside lines and spliced
at non-silent points, and its master limiter waveshaped the voice's peaks: both made it glitchy, and both are gone).
Under the voice: a synthesised pulse-and-pad bed, ducked under every line, smooth whooshes on the scene changes,
hits on the slams, ticks on the counters, the crowd under the banner. Mastered with a look-ahead limiter (ffmpeg
`alimiter`), no clipping or waveshaping.

## The facts behind it

- **Table:** 18th, 8 points from 10 games (1W 5D 4L, 14 scored, 19 conceded), eight league games without a win
  (Everton D, City L, Fulham D, Spurs D, Leeds D, Bournemouth L, Chelsea L, Villa D), which NBC Sports reports equals
  their worst winless run in the Premier League.
- **Villa:** 4-4 at Old Trafford on 8 Nov; Villa scored after 59 seconds and in the 4th minute. Goal's tactics board
  describes Carrick's 4-2-3-1 morphing into a 3-1-6 in possession with Dalot tucking inside, full-backs caught high,
  "the distance between their pressing line and the back four remained dangerously large", 26 shots to 11, 3.09 xG
  conceded.
- **30 conceded** in all competitions, the most in Europe's top five leagues (OptaJoe, via NBC Sports).
- **Ownership:** the Glazers' 2005 takeover was a leveraged buyout; the family remains the majority owner; INEOS / Sir
  Jim Ratcliffe hold about 29% and run football operations. The banner ("We don't want a new stadium, we want the
  owners out") was shown during the Villa game (The Peoples Person, 9 Nov).

Sources: [Wikipedia, 2026–27 Manchester United F.C. season](https://en.wikipedia.org/wiki/2026%E2%80%9327_Manchester_United_F.C._season);
[NBC Sports live blog, United 4-4 Villa](https://www.nbcsports.com/soccer/live/manchester-united-vs-aston-villa-live-updates-score-goals-highlights-stats-2026-november-8);
[Goal, the tactics board](https://www.goal.com/en/news/manchester-united-vs-aston-villa-the-tactics-board-chaotic-eight-goal-thriller-exposes-structural-fragility-in-both-camps/blt7a1d1567e83698de);
[ESPN match report](https://www.espn.com/soccer/story/_/id/50421297/man-united-aston-villa-premier-league);
[The Peoples Person, the banner](https://thepeoplesperson.com/2026/11/09/man-united-fans-unveil-anti-owner-banner-vs-aston-villa-321818/);
[Yahoo Sports, Ratcliffe and the Glazers](https://sports.yahoo.com/articles/ratcliffe-buy-glazers-man-utd-070000176.html).

## Publishing copy

**Title:** Why Man United Are Failing (in 60 seconds) #shorts

**Description:**

> 18th. Eight without a win. A 3-1-6 with a canyon in the middle, and owners the fans want gone. The shape on the
> pitch, and the structure above it. Stats to 8 Nov 2026.
>
> #ManUtd #ManchesterUnited #MUFC #Carrick #Glazers #GlazersOut #INEOS #PremierLeague #TacticalAnalysis #Shorts

## Making it again

Voices: `FISH_API_KEY=... python3 project/../../clear-the-air/project/voice/gen_takes.py project/vo.json takes`
(the key is read from the environment only), then `python3 project/bd_vo.py DIR` with `pick.json` in `DIR`. Frames:
`python3 project/make.py frames`; sound (from the AnimnationStuido- checkout, for its audio helpers):
`PYTHONPATH=. python3 project/audio.py`; then mux with ffmpeg.
