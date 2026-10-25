#!/usr/bin/env python3
"""Every line of lines_v2.json in TAKES takes with its character's cloned voice, a few requests at once.
FISH_API_KEY=... python3 v2/fish_batch.py OUT_DIR [--takes 2] [--only ID,ID] [--workers 4]"""
import argparse, json, os, pathlib, sys
from concurrent.futures import ThreadPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "voices"))
import fish_tts as F

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--takes", type=int, default=2); ap.add_argument("--only", default="")
ap.add_argument("--workers", type=int, default=4); ap.add_argument("--model", default="s2.1-pro")
ap.add_argument("--suffix", default="")
a = ap.parse_args()
key = os.environ.get("FISH_API_KEY") or sys.exit("set FISH_API_KEY")
models = json.loads((HERE.parent / "voices" / "fish_models.json").read_text())
lines = json.loads((HERE / "lines_v2.json").read_text())
only = set(filter(None, a.only.split(",")))
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
jobs = []
for ln in lines:
    if only and ln["id"] not in only:
        continue
    for k in range(1, a.takes + 1):
        dest = out / f"{ln['id']}{a.suffix}_t{k}.wav"
        if not dest.exists():
            jobs.append((ln, dest))

def go(job):
    ln, dest = job
    F.tts(key, models[ln["voice"]]["id"], ln.get("say", ln["text"]), dest, a.model)
    return dest.name

with ThreadPoolExecutor(a.workers) as ex:
    for n in ex.map(go, jobs):
        print(n, flush=True)
