"""Generate takes for a list of lines with Fish clones.
FISH_API_KEY=... python3 gen_takes.py requests.json OUT_DIR   LINES = [{"id","voice","text", "tags": ["[calm] ", ...], "takes": 4, "model": "s2.1-pro"}]
Each tag gets `takes` takes: OUT/<id>_<tagindex>_<k>.wav; the tag is prepended to the text (not spoken)."""
import json, os, pathlib, sys
from concurrent.futures import ThreadPoolExecutor
VOICES = pathlib.Path(__file__).resolve().parents[3] / "episode-1-the-clear-plan" / "voices"
sys.path.insert(0, str(VOICES))
import fish_tts as F
key = os.environ["FISH_API_KEY"]
models = json.load(open(VOICES / "fish_models.json"))
L = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
jobs = []
for ln in L:
    for ti, tag in enumerate(ln.get("tags", [""])):
        for k in range(1, ln.get("takes", 2) + 1):
            d = out / f"{ln['id']}_{ti}_{k}.wav"
            if not d.exists():
                jobs.append((models[ln["voice"]]["id"], tag + ln.get("say", ln["text"]), d, ln.get("model", "s2.1-pro"), ln.get("temp", 0.7)))
def go(j):
    ref, text, d, m, temp = j
    try:
        F.tts(key, ref, text, d, m, temperature=temp)
        return d.name
    except Exception as e:
        return f"FAILED {d.name}: {e}"
with ThreadPoolExecutor(4) as ex:
    for n in ex.map(go, jobs): print(n, flush=True)
print("DONE", len(jobs))
