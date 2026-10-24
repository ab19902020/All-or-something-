# Claude production handoff

Read MASTER_DIRECTORS_SCRIPT.md first. The deliverable requested here is a script package; this ZIP does not contain the source videos, PNG library or rendered audio. Fetch the exact source revisions listed in the master script. Keep their projects in separate checkouts so branch switching does not hide a scene.

## Voice status

Existing recordings stay locked. `source_recorded_lines.py` maps the opening's line IDs to MP3 files. `source_audio_transcripts.json` provides recovered early-season recording filenames and approximate segment times; it is an automatic transcript, not authoritative spelling. `source_mole.md` contains the full original Mole script and line numbering. The Mole README says L061 and L063 were not recorded; both are omitted from this compilation.

The NEW lines below are a proposed extension for the Como ending, not replacements for the user's recorded work. They have not been generated. Direction tags describe intended performance and are not guaranteed Clony syntax; put directions in the app's direction field where supported, and keep them out of spoken text. Export one clean take per ID at 48 kHz if the voice tool supports that format.

## Narrator — four new lines

N01 — serious documentary delivery; small pause after “refreshed”.

After the break, United returned refreshed. The results returned unchanged.

N02 — neutral factual bridge; do not sound conspiratorial until the next fictional scene.

Madrid brought another defeat. Before Leeds, Lisandro began looking for answers closer to home.

N03 — dry, underplayed; land “football” lightly.

The plan had survived the meeting. It was finding the football more difficult.

N04 — tired gravity, not a trailer voice.

Four-one. The consolation was on the scoreboard. It had not reached the dressing room.

## Carrick — nine new lines

C01 — deliberately reassuring: Stay compact. Make them play in front of us.

C02 — patient: When the moment is right.

C03 — small, embarrassed correction: That wasn't it.

C04 — firmer at half-time: We need to be braver.

C05 — single clear instruction: Together.

C06 — mild irritation: That's usually what together means.

C07 — exhausted: Not ideal.

C08 — controlled frustration, no shouting: I can draw the arrows. I can't carry eleven people along them.

C09 — quieter after a breath: We'll review it.

C07 can reuse the earlier “Not ideal” recording if its performance fits; do not regenerate it automatically.

## Bruno — six new lines

B01 — genuine request for clarity: And when do we go?

B02 — probing: So we go to them?

B03 — short, suspicious: Everyone?

B04 — drained: Michael. We've used that one.

B05 — clipped, mounting frustration: We gave them space. We gave them time. By the fourth goal, I thought we were giving them the stadium tour.

B06 — quieter, looking back into the building: I just wanted us to make them uncomfortable. At the moment, that's only happening in here.

## Maguire — one new line

M01 — completely sincere: Is there a signal?

## Strict existing-voices-only alternative

The user previously wanted to avoid remaking voices. Preserve that option without pretending new recordings already exist. For a build with no additional voice generation:

- Replace N01 with a silent RESET card; N02 with the verified Atlético result and LEEDS WEEK card; omit N03 and N04, allowing the original music/room tone to carry those shots.
- Perform the Como briefing silently: COMPACT on board, Bruno's raised hand, Carrick clicking pen, the players prematurely standing. This is the same visual joke without words.
- Half-time: Carrick writes PRESS TOGETHER; Bruno gestures around the room; Maguire handles the pen. No invented spoken line.
- After Como use the existing “Not ideal” and Bruno's existing “Michael, do not say not ideal” as an editorial reprise, with a clear flashback/reprise treatment rather than pretending they are genuine post-match comments.
- Keep both factual interview paraphrase cards. Replace the new Bruno and Carrick speech sections with silent reactions, a close-up of the pen and magnets, and press-room camera flashes. Do not fake their real interview recordings.
- Return to Wilcox's existing clear-plan line for the final callback.

This alternative preserves the 15-minute scene allocations through visual storytelling; do not simply freeze a single image for the duration of omitted speech. The primary script supplies a fuller spoken finale if new lines are wanted.

## Asset/build checklist

Reuse: boardroom, corridor, training-ground exterior, dressing room, mixed zone, press conference, tactics room; existing player and executive cutouts; Mole hedge, camouflage, pot, soil, Leeds shirt and City scarf variants.

New or adapted: Como establishing plate in the established style; neutral Como away dressing-room dressing; blue opponent magnets; editable result/date cards; pen and cap; final presentation filename insert. Opponent players can remain distant silhouettes or scorecard representations; no new speaking Como cast is required.

Portrait adaptation is scene-specific. Confirm pixel dimensions of every imported render. Boardroom and Mole are documented as landscape already. If a different portrait cut has a better performance, preserve its audio while rebuilding the wide composition from its art. Do not auto-fill by stretching or cutting off heads and hands.

## Required checks before rendering final master

1. Confirm source files and durations. Resolve missing raw `show TV.zip` audio using the finished landscape render where necessary.
2. Audition selected lines against transcripts. In particular correct misrecognitions such as “leak-up”, “Benjamin Zinjad” and “clay plan” in subtitles, not by changing audio.
3. Align edits to whole phrases; remove unused Mole title/teaser segments. Check actual selected duration before enforcing the 3:10 budget.
4. Correct Hull daylight/clock/goal graphics. Do not leave original fictional goal timings visible underneath corrected cards.
5. Check match order: City precedes Brighton; Atlético precedes Leeds. Stop at Como's immediate aftermath.
6. Label factual paraphrase cards and fictional dialogue differently. Do not use quotation marks around paraphrases. Keep sources in project documentation.
7. Check landscape crop, mouth timing, scene continuity, music ducking and readable result cards on a phone-sized preview.
8. Render a complete 900-second timeline with final credits included. Validate actual duration, frame count, audio peaks and no black/empty frames. At 30 fps the target is 27,000 frames.

No source clips have been downloaded into this handoff, no voice generation has been performed, and no finished-video QA is claimed. This package contains the director's script, source references, recovered source text, and the new dialogue needed to continue production.
