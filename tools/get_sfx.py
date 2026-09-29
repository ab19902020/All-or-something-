"""Fetch and trim the sound-effect clips listed in audio/sfx/manifest.json (BigSoundBank, CC0) into
audio/sfx/<name>.ogg (48 kHz, 5 ms fades). Clips already present are skipped; --force rebuilds them.
  python3 tools/get_sfx.py [--force] [name ...]"""
import json, os, sys, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SFX = os.path.join(ROOT, "audio", "sfx")
man = json.load(open(os.path.join(SFX, "manifest.json")))
force = "--force" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("--")]
cache = {}
with tempfile.TemporaryDirectory() as tmp:
    for name, c in man.items():
        if name.startswith("_") or (only and name not in only): continue
        out = os.path.join(SFX, name + ".ogg")
        if os.path.exists(out) and not force: continue
        src = cache.get(c["id"])
        if src is None:
            src = os.path.join(tmp, c["id"] + ".mp3")
            subprocess.run(["curl", "-sSL", "--max-time", "120", "-o", src,
                            f"https://bigsoundbank.com/UPLOAD/mp3/{c['id']}.mp3"], check=True)
            cache[c["id"]] = src
        d = c["end"] - c["start"]
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(c["start"]), "-t", str(d), "-i", src,
                        "-af", f"afade=t=in:d=0.005,afade=t=out:st={max(0, d - 0.005):.3f}:d=0.005",
                        "-ar", "48000", "-c:a", "libvorbis", "-q:a", "6", out], check=True)
        print(name, f"{d:.2f}s", c["title"])
