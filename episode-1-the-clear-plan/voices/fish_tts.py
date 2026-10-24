#!/usr/bin/env python3
"""Speak every line of voices/lines.json with its character's cloned Fish Audio voice (voices/fish_models.json).

  FISH_API_KEY=... python3 voices/fish_tts.py OUT_DIR [--only C01,B05] [--takes 2] [--model s2.1-pro]

Writes OUT_DIR/<id>.wav (44.1 kHz mono, take 1) and OUT_DIR/<id>_t2.wav ... for extra takes, plus
OUT_DIR/manifest.json. Existing files are kept unless --force."""
import argparse
import json
import os
import pathlib
import sys
import time

import requests

API = "https://api.fish.audio"
HERE = pathlib.Path(__file__).resolve().parent


def tts(key, ref, text, dest, model, speed=1.0, temperature=0.7, top_p=0.7):
    body = {"text": text, "reference_id": ref, "format": "wav", "sample_rate": 44100, "normalize": True,
            "latency": "normal", "temperature": temperature, "top_p": top_p,
            "prosody": {"speed": speed, "volume": 0}}
    hdr = {"Authorization": "Bearer " + key, "Content-Type": "application/json", "model": model}
    for attempt in range(4):
        try:
            r = requests.post(API + "/v1/tts", json=body, headers=hdr, timeout=(30, 300))
            if r.status_code == 200 and len(r.content) > 4000:
                dest.write_bytes(r.content)
                return
            err = f"HTTP {r.status_code}: {r.text[:300]}"
        except requests.RequestException as e:
            err = str(e)
        print(f"  retry {attempt + 1}: {err}", flush=True)
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError(err)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--only", default="")
    ap.add_argument("--takes", type=int, default=1)
    ap.add_argument("--model", default="s2.1-pro")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--suffix", default="", help="added to every file name (e.g. _s1)")
    a = ap.parse_args()
    key = os.environ.get("FISH_API_KEY") or sys.exit("set FISH_API_KEY")
    models = json.loads((HERE / "fish_models.json").read_text())
    lines = json.loads((HERE / "lines.json").read_text())
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    man_p = out / "manifest.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    for ln in lines:
        if only and ln["id"] not in only:
            continue
        ref = models[ln["voice"]]["id"]
        for k in range(1, a.takes + 1):
            dest = out / (f"{ln['id']}{a.suffix}.wav" if k == 1 else f"{ln['id']}{a.suffix}_t{k}.wav")
            if dest.exists() and not a.force:
                continue
            tts(key, ref, ln["text"], dest, a.model, ln.get("speed", 1.0))
            man[dest.stem] = dict(voice=ln["voice"], model_id=ref, tts_model=a.model, text=ln["text"])
            print(f"{dest.name}: {ln['voice']}: {ln['text']}", flush=True)
            man_p.write_text(json.dumps(man, indent=1, ensure_ascii=False))
    man_p.write_text(json.dumps(man, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
