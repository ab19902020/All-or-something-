# Voice-overs

One folder per voice. Files are named `<who>_<nn>_<what-is-said>.mp3`; `nn` is the order the lines come in the
script as far as the words show. `audio/transcripts.json` holds what Whisper hears in every clip (fix it by hand
if a word is misheard).

Some clips also contain another character's cue line (for example Omar's clip starts with Carrick's "Yeah, but
three midfielders" cue and Jason's has Carrick's "Who's scoring?"). The pipeline cuts each scripted line out at
its exact word boundaries, so the extra words are simply not used.

| Clip | Length | What's said |
|---|---|---|
| **Narrator (Mark Goldbridge, on screen at his desk)** | | |
| `narrator/narrator_01_deadline-day-intro.mp3` | 14.6 s | Manchester United, transfer deadline day. The manager asked for two players. He got three midfielders. Nobody appears entirely sure why. This is All or Something. |
| `narrator/narrator_02_everything-except-what-he-asked-for.mp3` | 4.4 s | Everything except what the manager actually asked for. |
| **Michael Carrick** | | |
| `michael-carrick/carrick_01_two-things-left-back-striker.mp3` | 14.4 s | Right, just two things. Left back, striker. Brilliant, sorry. I said left back and striker. That's not the same thing. Look, I'm not complaining. |
| `michael-carrick/carrick_02_not-complaining-whos-scoring.mp3` | 19.1 s | Look, I'm not complaining. Obviously, love the lads, great window. But who's actually scoring the goals? And the left back, Luke, for the whole season? |
| `michael-carrick/carrick_01-02_combined-take.mp3` | 24.2 s | Lines 01 and 02 in one take (spare). |
| `michael-carrick/carrick_03_no-striker-brilliant_take1.mp3` | 12.8 s | Right, so no striker, no left back, but three midfielders. Yeah, brilliant, brilliant. |
| `michael-carrick/carrick_03_no-striker-brilliant_take2.mp3` | 11.7 s | The same line, second take. |
| `michael-carrick/carrick_04_no-striker-three-midfielders-short.mp3` | 3.4 s | So no striker, no left back, three midfielders. |
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
| **Jim Ratcliffe** | | |
| `jim-ratcliffe/jim_01_bigger-issues-facing-britain.mp3` | 18.6 s | We need to focus on the bigger issues facing Britain. Standards, discipline, efficiency. Everyone always wants more players. Sometimes you have to make do with what you've got. |
| `jim-ratcliffe/jim_02_i-live-in-monaco.mp3` | 12.0 s | That's how you build character and save money. Yes. I live in Monaco. That's completely different. It gives me an outside perspective. |
| `jim-ratcliffe/jim_03_excellent-business-good-meeting.mp3` | 5.4 s | Anyway, three midfielders sounds like excellent business. Good meeting. Good meeting. |

Add new voices the same way: a folder per character, clips renamed by what's said, and a line in the table and
in `transcripts.json`.
