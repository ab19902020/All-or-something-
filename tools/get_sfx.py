"""Fetch and trim the sound-effect clips listed in audio/sfx/manifest.json into audio/sfx/<name>.ogg (48 kHz, 5 ms
fades). A clip is a BigSoundBank sound ("id", CC0) or any file by "url" (Wikimedia Commons CC0 recordings, with
their "license"). Clips already present are skipped; --force rebuilds them.
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
        key = c.get("url") or c["id"]
        src = cache.get(key)
        if src is None:
            src = os.path.join(tmp, f"src{len(cache)}" + os.path.splitext(key.split("?")[0])[1])
            url = c.get("url") or f"https://bigsoundbank.com/UPLOAD/mp3/{c['id']}.mp3"
            subprocess.run(["curl", "-sSL", "--fail", "--retry", "4", "--retry-delay", "5", "--max-time", "180",
                            "-A", "AllOrSomethingEpisodeTool/1.0 (cartoon production)", "-o", src, url], check=True)
            cache[key] = src
        d = c["end"] - c["start"]
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(c["start"]), "-t", str(d), "-i", src,
                        "-af", f"afade=t=in:d=0.005,afade=t=out:st={max(0, d - 0.005):.3f}:d=0.005",
                        "-ar", "48000", "-c:a", "libvorbis", "-q:a", "6", out], check=True)
        print(name, f"{d:.2f}s", c["title"])
