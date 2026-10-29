# Clear the Air — production source

**Status: character art created; script and film package prepared. New dialogue and final video are pending Fish Audio authentication. This is not a finished episode.**

This short preserves the saved 30-second script. Its visual source is the same whole-drawing `studio/film` pipeline used for the final *The Clear Plan*, rather than an unrelated generative-video workflow.

- Art references inspected: Carrick and Bruno's model sheets in `AnimnationStuido-`, branch `claude/ollies-episode-production-tdnt6j`.
- Existing Neville art there is explicitly `style: provisional`; the new inspector sheet is a replacement outfit/style asset, leaving the original kit intact.
- Saved Fish voice models reused for Carrick, Bruno, Wilcox and narrator. Neville's labelled source recording is from *The Appeals Department*, `01-gary-neville-1.mp3` (42.7 seconds). A private Fish clone still needs to be created or an existing Neville model selected.
- Existing episode source: `All-or-something-`, branch `ccr-1e3fcc91-jkv5yq`, `episode-1-the-clear-plan/v2/`.
- Engine and base library: `AnimnationStuido-`, branch `claude/ollies-episode-production-tdnt6j`. Apply `pack/studio-engine.patch` to that pinned base, then install this film under `episodes/clear-the-air/` and merge `library-overlay/` into its library.
- The engine renders a landscape master; the shot layout reserves the central 9:16 crop for a 1080×1920 Shorts export. No final render or portrait QA has been performed yet.

`generate_voices.py` reads `FISH_API_KEY` from the environment; no credential is committed. It creates Gary's private clone only if no Gary model has been recorded locally, saves returned identity, and generates one take of every line. Existing takes are retained on resume. Review each take before choosing any additional generation.

`film/timeline.py` rejects overlong takes. It never chops words, silently speeds speech up, or fabricates alignment. After synthesis, align actual audio with the existing studio voice tools, review every shot and mouth chart, mix to −16 LUFS and verify the final export before marking this episode complete.
