# Voice-overs

One folder per voice. Files are named `<who>_<nn>_<what-is-said>.mp3`; `nn` is the order the lines come in the
script as far as the words show. `audio/transcripts.json` holds what Whisper hears in every clip (fix it by hand
if a word is misheard).

Some clips also contain another character's cue line (for example Omar's clip starts with Carrick's "Yeah, but
three midfielders" cue and Jason's has Carrick's "Who's scoring?"). The pipeline cuts each scripted line out at
its exact word boundaries, so the extra words are simply not used.

| Clip | Length | What's said |
|---|---|---|
| **Narrator** (voice only) | | |
| `narrator/narrator_01_deadline-day-intro.mp3` | 14.6 s | Manchester United, transfer deadline day. The manager asked for two players. He got three midfielders. Nobody appears entirely sure why. This is All or Something. |
| `narrator/narrator_02_everything-except-what-he-asked-for.mp3` | 4.4 s | Everything except what the manager actually asked for. |
| `narrator/narrator_03_new-season-hull-same-corners.mp3` | 33.9 s | Ep2: New season. New Manchester United. Probably. Hull City. Newly promoted. Physical. Aggressive. Dangerous from set pieces. Manchester United knew exactly what was coming. It did not help. Hull City 2, Manchester United 0. 70% possession, zero points. New season, same corners. This is All or Something. |
| **Michael Carrick** | | |
| `michael-carrick/carrick_01_two-things-left-back-striker.mp3` | 14.4 s | Right, just two things. Left back, striker. Brilliant, sorry. I said left back and striker. That's not the same thing. Look, I'm not complaining. |
| `michael-carrick/carrick_02_not-complaining-whos-scoring.mp3` | 19.1 s | Look, I'm not complaining. Obviously, love the lads, great window. But who's actually scoring the goals? And the left back, Luke, for the whole season? |
| `michael-carrick/carrick_01-02_combined-take.mp3` | 24.2 s | Lines 01 and 02 in one take (spare). |
| `michael-carrick/carrick_03_no-striker-brilliant_take1.mp3` | 12.8 s | Right, so no striker, no left back, but three midfielders. Yeah, brilliant, brilliant. |
| `michael-carrick/carrick_03_no-striker-brilliant_take2.mp3` | 11.7 s | The same line, second take. |
| `michael-carrick/carrick_04_no-striker-three-midfielders-short.mp3` | 3.4 s | So no striker, no left back, three midfielders. |
| `michael-carrick/carrick_05_sell-to-buy-good-meeting.mp3` | 26.2 s | From the TV Show pack (*The Clear Plan*): How much is a lot? Right. So. Sell to buy?... Brilliant. Good meeting. Positive. Good meeting. So where's the money actually going? Glazer dividends? Oh. Cheers. |
| `michael-carrick/carrick_06_whats-the-plan-yep-okay.mp3` | 35.1 s | TV Show pack: What's the plan? Right. Yep. Okay. Jason. Who are we signing? I know. I'm just thinking... Fair enough. How much? |
| `michael-carrick/carrick_07_newly-promoted-set-pieces-not-ideal.mp3` | 17.9 s | TV Show pack: Brilliant. Yep. Good input. Newly promoted team. Crowd will be up for it. Do the basics. And most importantly set pieces. Right. Not ideal. It's one game... |
| `michael-carrick/carrick_08_yep-yep-theres-been-positives.mp3` | 20.2 s | TV Show pack: Yep, yep, there you go. Right. International break, get away, reset, come back fresh. Lovely. There've been positives. (ends with a swear) |
| `michael-carrick/carrick_09_number-nine-come-on.mp3` | 17.2 s | TV Show pack: So who's my number nine?... Come on, move. Options. Go on then. Come on. One more. Everyone all right? Okay. Five points. |
| `michael-carrick/carrick_10_fresh-season-same-corner-impact.mp3` | 29.3 s | Ep2: Right lads, fresh season, clean slate. Hull have just come up, so they'll be aggressive, physical, dangerous from set pieces. Already did. Thursday. Same corner though, isn't it? Kobbie, you're on the bench. We've bought midfielders. Right, Hull City, come on! Right, positives. Yep. Yep. Harry, I'm aware. Impact. Nearly impact. Good meeting. |
| **Jason Wilcox** | | |
| `jason-wilcox/jason_01_sorted-three-midfielders.mp3` | 13.8 s | Sorted. We bought three midfielders. Yeah, but three midfielders. It's three things instead of two. Technically, you've won. Who's scoring? Bruno. |
| `jason-wilcox/jason_02_perfect-loads-of-midfielders.mp3` | 13.8 s | Perfect. We've got loads of midfielders. Left back. We've got Luke. For the whole season, next question. No striker. No left back. Three midfielders. |
| **Omar Berrada** | | |
| `omar-berrada/omar_01_market-presented-opportunities.mp3` | 12.0 s | Yeah, but three midfielders. We felt the market presented opportunities and we took those opportunities. Were they the positions we needed? No. |
| `omar-berrada/omar_02_efficient-recruitment.mp3` | 12.6 s | But they were available. Who's scoring the goals? Bruno. He's already here, so technically that's efficient recruitment. Left back, we have internal solutions. |
| `omar-berrada/omar_03_no-striker-three-midfielders.mp3` | 5.8 s | No striker, no left back, three midfielders. |
| **Bruno Fernandes** | | |
| `bruno-fernandes/bruno_01_sorry-what-three-midfielders.mp3` | 16.6 s | Sorry, what? You bought three midfielders? So who am I crossing the ball to? Me? I'm taking the corner. I'm a midfielder. Brilliant. Absolutely brilliant. |
| `bruno-fernandes/bruno_02_should-have-gone-to-saudi.mp3` | 11.0 s | What am I even doing here? Saudi Arabia offered me sunshine and probably a striker. No left back, no striker. I should have gone to Saudi. |
| `bruno-fernandes/bruno_03_nine-of-us-seventy-percent-saudi.mp3` | 45.3 s | Ep2: We've got about nine of us now. Can any of them actually play striker though? So we know they're dangerous from set pieces and the plan is hope they don't get one. Brilliant, absolutely brilliant. We had 70% possession, we lost 2-0. Two set pieces, two goals... So, newly promoted Hull, two set pieces, no goals. Harry, you're a centre-back. And somehow you were the one having shots. What are we actually doing here? Saudi Arabia offered me sunshine, they probably had a striker as well. Can somebody check if Saudi are still calling? I should have went to Saudi. |
| **Kobbie Mainoo** | | |
| `kobbie-mainoo/mainoo_01_again-came-on-after-67-ipswich.mp3` | 24.4 s | Again? I noticed. I came on after 67 minutes, 2-0 down. What exactly was the plan? We didn't score. Didn't Ipswich just get promoted as well? So that's two newly promoted teams in a row then. Lovely. Good start to the season. This... |
| **Harry Maguire** | | |
| `harry-maguire/maguire_01_play-striker-set-pieces-shooting.mp3` | 20.4 s | Can any of them play striker? Both goals were set pieces. The thing you warned us about before the game. Twice. I had to start shooting. Nobody else was doing it. I'm a centre-back and somehow I'm the goal threat. That's probably not ideal. Still, could have been three. |
| **Steve Holland** | | |
| `steve-holland/steve_01_practise-defending-wrong-door-ipswich.mp3` | 11.8 s | Ep2: Should we practise defending those then? That was attacking corners. Michael, wrong door. Excellent. Less excellent. Good news, we've got Ipswich next. |
| **Jim Ratcliffe** | | |
| `jim-ratcliffe/jim_01_bigger-issues-facing-britain.mp3` | 18.6 s | We need to focus on the bigger issues facing Britain. Standards, discipline, efficiency. Everyone always wants more players. Sometimes you have to make do with what you've got. |
| `jim-ratcliffe/jim_02_i-live-in-monaco.mp3` | 12.0 s | That's how you build character and save money. Yes. I live in Monaco. That's completely different. It gives me an outside perspective. |
| `jim-ratcliffe/jim_03_excellent-business-good-meeting.mp3` | 5.4 s | Anyway, three midfielders sounds like excellent business. Good meeting. Good meeting. |

Add new voices the same way: a folder per character, clips renamed by what's said, and a line in the table and
in `transcripts.json`.

## Music (`music/`)

| File | What it is |
|---|---|
| `music/tigers-chant_getting-mauled-by-the-tigers.m4a` | 8.4 s Hull fan chant (supplied): "You're getting mauled by the tigers, mauled by the tigers, you're getting mauled by the tigers." Used in Episode 2 when the 2-0 comes up. |

Voices are checked with speaker fingerprints (wespeaker / TitaNet via sherpa-onnx) before use: a clip whose voice
doesn't match its character is not used (Episode 2's 57-second "Bruno" take was in Jason's voice, so the 45-second
take is used). Steve Holland's voice is the same generated voice as Jason Wilcox's in Episode 1, so an episode
with both of them needs a new voice for one of them.

## Sound effects (`sfx/`)

Real recordings from [BigSoundBank](https://bigsoundbank.com) (CC0: free for any use; credit appreciated:
"Additional sounds: Joseph SARDIN - BigSoundBank.com"). `sfx/manifest.json` lists each clip's source id and the
part used; `python3 tools/get_sfx.py` downloads and trims them into `sfx/<name>.ogg`. Add new effects the same
way.
