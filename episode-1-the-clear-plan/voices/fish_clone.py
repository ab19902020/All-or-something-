#!/usr/bin/env python3
"""Clone every speaking character's voice in Fish Audio: one private voice model per character, made from ONE of
that character's existing voice uploads (voices/sources.json). Model IDs go to voices/fish_models.json.

The key is read from the environment, never from the repo:
  FISH_API_KEY=... python3 voices/fish_clone.py [--only carrick,bruno]
Re-running skips characters that already have a model (delete the entry in fish_models.json to re-clone)."""
import argparse
import json
import pathlib
import sys
import os

import requests

API = "https://api.fish.audio"
HERE = pathlib.Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--src-root", default="/home/user/src", help="where the source repos are checked out")
    args = ap.parse_args()
    key = os.environ.get("FISH_API_KEY") or sys.exit("set FISH_API_KEY")
    sources = json.loads((HERE / "sources.json").read_text())
    out_p = HERE / "fish_models.json"
    models = json.loads(out_p.read_text()) if out_p.exists() else {}
    only = set(filter(None, args.only.split(",")))
    for cid, src in sources.items():
        if only and cid not in only:
            continue
        if cid in models:
            print(f"{cid}: already cloned ({models[cid]['id']})")
            continue
        f = pathlib.Path(args.src_root) / src["file"]
        with open(f, "rb") as fh:
            r = requests.post(API + "/model", headers={"Authorization": "Bearer " + key},
                              data={"type": "tts", "title": src["title"], "train_mode": "fast", "visibility": "private",
                                    "description": "Private parody character voice for the All or Something animated "
                                                   "satire. Not the real person.",
                                    "enhance_audio_quality": "true"},
                              files=[("voices", (f.name, fh, "audio/mpeg"))], timeout=(30, 600))
        if r.status_code not in (200, 201):
            print(f"{cid}: FAILED HTTP {r.status_code}: {r.text[:300]}")
            continue
        j = r.json()
        q = (j.get("quality") or {}).get("audios") or [{}]
        models[cid] = dict(id=j["_id"], title=j["title"], state=j.get("state"), source=src["file"],
                           repo=src["repo"], quality=q[0].get("quality"), quality_passed=q[0].get("quality_passed"))
        print(f"{cid}: {j['_id']} {j.get('state')} quality={q[0].get('quality')}")
        out_p.write_text(json.dumps(models, indent=1, ensure_ascii=False) + "\n")
    out_p.write_text(json.dumps(models, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
