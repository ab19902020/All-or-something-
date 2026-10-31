# Production notes — CLEAR THE AIR

## Story and continuity
This revision develops the 29 October 2026 production document ALL_OR_SOMETHING_CLEAR_THE_AIR_PRODUCTION.md. It preserves the literal air-clearing gag and Gary's inspector ending, while giving Carrick and Bruno a genuine resolution. Keep the show's post-match tension as background; do not add real-result graphics or present the invented meeting as news.

The change that matters: the original ended with everyone blaming someone else. Here Carrick and Bruno point at Jason together. Their new alliance is the final visual proof that the meeting worked.

Wilcox must stay mostly behind the main conversation. His doorway obstruction, premature tick, aerosol and prepared announcement tell a parallel story without requiring him to dominate the dialogue. He is a sincere manager of appearances, not a sinister villain. Gary is a late interruption, not the protagonist.

## Performance
- Carrick: understated Geordie delivery; short pauses, tired patience, never a shout. His admission is sincere. “Progress” has a hint of warmth.
- Bruno: Portuguese-accented English consistent with the established series voice; direct and proud, not permanently screaming. The tactics criticism is honest rather than an attempt to restart the fight.
- Wilcox: established northern/Leeds delivery; procedural confidence. Only “collaborative structure” betrays panic.
- Gary: established Manchester/Salford delivery; brisk inspector confidence, final verdict almost bored. Do not play him as a shouting sports commentator.
- Narrator: sober British documentary delivery; no wink and no extra explanatory lines.
Use the Fish Audio API for every voiceover with the existing All or Something cloned character voices. Resolve and verify the actual voice/reference IDs from the project before generation. No voice IDs are supplied or verified in this pack. Do not invent them. Follow 05_Fish_Audio_API_Requirements.txt; no substitute TTS provider is permitted. Directions in square brackets are performance notes, not spoken dialogue. The per-character files contain spoken text only; the CSV maps delivery and cue order. Each cue is under 300 characters.

## Design and assets
Use the approved All or Something complete PNG artwork: oversized expressive heads, compact bodies, bold dark outlines and warm cel shading. Preserve each character's face, beard, hair, skin tone and proportions. Match the most recent approved episode when assembling; this pack does not independently verify the current repository art.

No SVGs, separated limbs, new photorealistic redesigns or generative redrawing between shots. Use whole-character pose swaps and the existing mouth/viseme method. For the handshake and pointing, use complete integrated poses; do not detach arms. Frame the handshake below the chest if exact hand animation becomes distracting.

Asset checklist:
- Carrick: black coaching top; seated neutral, talking, softened expression, handshake and pointing poses.
- Bruno: red United training top; seated defensive, talking, small smile, handshake and pointing poses.
- Wilcox: established jacket outfit; standing doorway, agenda tick, can held, announcement held, deflated reaction.
- Gary: charcoal suit, white shirt, navy tie, plain blue lanyard, clipboard; doorway neutral, speaking, writing and verdict poses.
- Manager's office: portrait master, reverse/tight coverage, door view; same table, lighting and screen direction throughout.
- Props: blue aerosol, flip chart, pen, blank clipboard and announcement card. Set text as editor overlays, not AI-generated lettering.

Exact text overlays:
CLEAR THE AIR / NO LEAKS
RESOLVED
UNITED BEHIND THE MANAGER
STANDARDS
SPECIAL MEASURES

The original source document recorded these repository pointers. They are historical leads, not newly checked files or bundled assets:
https://github.com/ab19902020/TV-show-
manchester-united-documentary/assets/characters/michael-carrick/outfits.png
manchester-united-documentary/assets/characters/michael-carrick/face-visemes.png
manchester-united-documentary/assets/characters/bruno-fernandes/outfits.png
manchester-united-documentary/assets/characters/bruno-fernandes/face-visemes.png
manchester-united-documentary/assets/characters/jason-wilcox/house-style/jason-wilcox__combined-outfits-faces-actions__20260928T155327__2ce63c58.png
manchester-united-documentary/assets/backgrounds/manager-office/modern-football-managers-analysis-office.png
manchester-united-documentary/assets/backgrounds/manager-office/red-black-football-managers-office.png

A later Library entry records Gary Neville standards inspector character sheet.png. Inspect it against approved cast art before using it; its existence alone does not confirm cutout or animation readiness. No images, voice files or final video are included in this writing pack.

## Camera and editing
1080 × 1920, 9:16, 30 fps target. Keep a consistent left/right axis: Carrick screen-left, Bruno screen-right, Jason behind. At the ending, a slightly wider two-shot lets Carrick and Bruno read as a pair. Use medium close-ups for most dialogue; reserve the master for Jason's business and the synchronized point.

Use small documentary reframes, one restrained push-in on the doorway gag and one short reaction zoom after “Fresh start.” No constant floating or zooming. Hold faces still when a line lands. Do not cut away from the sincere admissions too quickly.

Suggested shot order:
1. Master with narrator; Jason beckons camera.
2. Carrick medium: tactics/television.
3. Bruno medium: open door.
4. Carrick: “It is.”
5. Bruno: “Jason was standing in it.”
6. Door insert: Jason's inadequate sidestep.
7. Matched close-ups: mutual admissions.
8. Two-shot: “So we're all right?” / “tactics were shit.”
9. Carrick close: “indoors. Progress.” Bruno reaction.
10. Background insert: tick, can, two sprays.
11. Three-shot for aerosol exchange; reaction two-shot after “Fresh start.”
12. Medium two-shot for agreement and handshake; widen to reveal announcement.
13. Door view: Gary enters. No elaborate walk cycle.
14. Jason objection; Gary question.
15. Master: both point at Jason simultaneously; hold one second.
16. Jason lowers card: collaborative structure.
17. Gary writing, then verdict.
18. Two-shot with Jason in rear; tiny spray; cut to black.

The script time bands are a planning envelope. Generate/record voices first, measure every clip, then place reactions. Preserve 0.4–0.8 seconds after doorway sidestep, 0.5 seconds after “Progress,” 0.6 seconds after “Fresh start,” and one second after the synchronized point. If the performance runs long, allow up to 95 seconds instead of speeding up voices. No forced 30-second compression.

## Sound
Quiet office room tone throughout; slightly reduced for the final pointing beat. Sparse dry documentary music only under the opening, then fade before the substantive conversation. No canned laughter. Two short aerosol sprays, soft pen tick, card rustle and firm door opening. Gary can get a very brief official-sounding sting, well below dialogue. End with a tiny accidental spray after the verdict; no additional spoken joke.

Dialogue should remain clearly above effects. Practical delivery target: around −14 LUFS integrated and true peaks no higher than −1 dBTP, checked after rendering. Save clean isolated speech and separate effects/music stems. Use original or cleared music and effects.

## Captions and branding
Manually check subtitles against actual spoken audio; do not use the rough scene times as a final SRT. Two lines maximum, bold white with dark outline. Keep important faces/props clear. For 1080 × 1920, start with an action-safe area around x=90–900 and y=180–1500; preview in the target app because overlays vary. Captions usually sit around y=1250–1450, adjusted per shot.

One small UNITED ROAD ORIGINAL mark at the opening and ALL OR SOMETHING at the cut to black; no long outro. Include “Fictional AI-animated football satire” in publishing copy. Do not add a real Ofsted badge or imply an actual inspection.

Optional clean dialogue replacement: “Yes. I still think the tactics were rubbish.” Keep the remainder unchanged and align captions to the selected take.

## Assembly and quality checks
1. Match cast and office art against the approved episode before making variants.
2. Record separate lines using voice_cues.csv; retain clean takes and existing voice mapping privately.
3. Measure audio; build the conversation edit and reaction holds before animating.
4. Add whole-character poses, mouth animation, eye lines and restrained background business.
5. Add props, legible text overlays, effects and captions.
6. Watch once without sound: the doorway, spray, handshake and synchronized point must read clearly.
7. Listen without picture: the reconciliation must make sense and each voice remain distinct.
8. Check for facial drift, mismatched mouths, detached hands, stretched backgrounds, caption collisions and duplicate audio.
9. Export H.264 MP4 with AAC audio, 1080 × 1920 at 30 fps; view the final export on a phone. Keep editable project and assets together.

Status: refined screenplay, director notes, voice cue list and handoff prompt complete. Artwork collection, voice recording and final animation remain production steps, not completed deliverables in this ZIP.
