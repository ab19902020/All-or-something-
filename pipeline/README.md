# Pipeline templates

New All or Something episodes start from the latest episode in `scenes/` (already 9:16). These are the
older code-only pipelines from the TV Show repo (`ab19902020/TV-show-`), copied here so every new scene
starts from something that already works. **Don't edit these in place for a scene**: `tools/new_scene.sh`
copies one into `scenes/<slug>/` and the work happens there. Each template's README describes the scene it was
first built for and explains every stage.

| Template | Built for | Use it when |
|---|---|---|
| `multi-character/` | *The Clear Plan* Ep. 1 (Carrick, Jason, Omar, Jim in the boardroom) | Several characters, several locations, a shot list, lines cut word-exact from voice clips, synthesised music / foley, lower thirds and title card. |
| `single-character/` | Jim Ratcliffe, INEOS office | One character, full-body rig: walks, sitting, arm-pose torsos, turnaround views, separate mouth sheet. |

Both render at 30 fps. They were built for 16:9; All or Something is 9:16 portrait, so set the output size
(1080 × 1920) and re-frame the shots in `direction.py` for each new scene.

Models are downloaded by each template's make script from GitHub releases only (Real-ESRGAN for the 4x upscale,
Whisper turbo through sherpa-onnx for transcription); pocketsphinx does the forced alignment.
