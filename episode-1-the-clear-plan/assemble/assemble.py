#!/usr/bin/env python3
"""Assemble ALL OR SOMETHING, Episode One: THE CLEAR PLAN, the 15-minute (900 s, 27,000 frames at 30 fps) landscape
master, from five pieces:

  1. the boardroom and the owners' call   TV-show- episode1_scenes1-2_1080p.mp4 (3:17), as rendered; its end title is
                                          redrawn as ALL OR SOMETHING / THE CLEAR PLAN / EPISODE ONE, and the parody
                                          notice is put over the opening seconds
  2. Hull away                            TV-show- episode1_scenes3-4_4k.mp4 (0:47), brought down to 1080p and
                                          corrected to the real match: the lower third's kick-off time becomes the
                                          date, the match clock's minutes and the score cards' minutes become the real
                                          goal times (17', 38'); Bruno's touchline shout (his cloned Fish voice) is
                                          mixed in under the play
  3. part A (new)                         AnimnationStuido- episodes/aos-ep1-a: Hull's dressing room to Leeds week
  4. The Mole                             TV-show- The_Mole_1080p.mp4 without its title sting and without its
                                          next-episode teaser and hedge outro
  5. part B (new)                         AnimnationStuido- episodes/aos-ep1-b: Leeds, Como, the interviews, the
                                          clear plan, the credits

Every piece's sound is levelled to -16 LUFS, the joins inside The Mole are crossfaded over four frames, and the whole
mix is brought to -14 LUFS integrated with true peaks under -1 dBTP.

  python3 assemble.py --src /home/user/src --out OUT_DIR [--fonts FONTS_DIR]

Writes OUT_DIR/pieces/*.mp4|wav, OUT_DIR/all_or_something_ep1_master.mp4 (x264 CRF 18) and a report (report.json)
with every piece's frame count and the master's measured duration, frame count and loudness."""
import argparse
import json
import math
import os
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
TOTAL = 27000
MOLE_KEEP = [(0.0, 19.58), (22.18, 213.96)]       # The Mole's timeline marks: open..cut_title, cut_int1..cut_hedges


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def probe_frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(path)], capture_output=True, text=True,
                         check=True).stdout
    return int(out.strip())


def reader(path, scale=True):
    vf = f"scale={W}:{H}:flags=area,fps={FPS}" if scale else f"fps={FPS}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    p.wait()


def writer(path):
    return subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                             "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)


class Fonts:
    def __init__(self, d):
        self.d = pathlib.Path(d)

    def get(self, name, size, weight=None):
        f = ImageFont.truetype(str(self.d / name), int(size))
        if weight is not None:
            try:
                f.set_variation_by_axes([weight])
            except Exception:
                pass
        return f


def text_centre(dr, cx, y, s, f, fill, track=0):
    ws = [dr.textlength(ch, font=f) for ch in s]
    x = cx - (sum(ws) + track * (len(s) - 1)) / 2
    for ch, w in zip(s, ws):
        dr.text((x, y), ch, font=f, fill=fill)
        x += w + track


def over(img, rgba, k=1.0):
    a = rgba[..., 3:4].astype(np.float32) / 255 * k
    return (img.astype(np.float32) * (1 - a) + rgba[..., :3].astype(np.float32) * a).clip(0, 255).astype(np.uint8)


def sm(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- 1. the boardroom
def disclaimer_layer(F):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = F.get("Inter.ttf", 30, 600)
    s = "ANIMATED PARODY — PRIVATE SCENES AND DIALOGUE ARE FICTIONALISED"
    tw = sum(dr.textlength(ch, font=f) for ch in s) + 2 * (len(s) - 1)
    dr.rectangle((W / 2 - tw / 2 - 28, 46, W / 2 + tw / 2 + 28, 108), fill=(10, 10, 12, 200))
    dr.rectangle((W / 2 - tw / 2 - 28, 46, W / 2 - tw / 2 - 20, 108), fill=(218, 22, 30, 255))
    text_centre(dr, W / 2, 60, s, f, (240, 240, 240, 255), 2)
    return np.asarray(im)


def title_layer(F, u):
    """ALL OR SOMETHING / THE CLEAR PLAN / EPISODE ONE, u s after it appears (a punch-in, the rule drawing out)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    text_centre(dr, W / 2, 300, "ALL OR SOMETHING", F.get("BebasNeue-Regular.ttf", 64), (230, 230, 230, 255), 12)
    text_centre(dr, W / 2, 380, "THE CLEAR PLAN", F.get("BebasNeue-Regular.ttf", 190), (255, 255, 255, 255), 8)
    w = int(620 * sm(u / 0.35))
    dr.rectangle((W // 2 - w // 2, 600, W // 2 + w // 2, 608), fill=(218, 22, 30, 255))
    k = int(255 * sm((u - 0.3) / 0.3))
    text_centre(dr, W / 2, 640, "EPISODE ONE", F.get("BebasNeue-Regular.ttf", 64), (236, 236, 236, k), 6)
    a = np.asarray(im).astype(np.float32)
    s = 1.0 + 0.08 * math.exp(-u * 7.0)
    if s > 1.001:
        import cv2
        M = cv2.getRotationMatrix2D((W / 2, 450), 0, s)
        a = cv2.warpAffine(a, M, (W, H))
    return a.clip(0, 255).astype(np.uint8)


def boardroom(src, out, F):
    """the opening as rendered, the notice over its first seconds, its end title redrawn"""
    # first pass: measure every frame (the whole film never sits in memory)
    cen, edge = [], []
    for f in reader(src, scale=False):
        cen.append(f[400:700:4, 560:1360:4].mean())
        edge.append(np.r_[f[:300:8].ravel(), f[800::8].ravel()].mean())
    cen, edge = np.array(cen), np.array(edge)
    n = len(cen)
    # the end title: the last stretch of frames whose picture is only a centred title on black
    k = n - 1
    while k > 0 and edge[k] < 6:
        k -= 1
    black0 = k + 1                                   # from here on the edges are black: the title card
    t_on = next(i for i in range(black0, n) if cen[i] > 12)
    peak = cen[t_on:].max()
    dis = disclaimer_layer(F)
    w = writer(out)
    for i, f in enumerate(reader(src, scale=False)):                 # second pass: the picture
        t = i / FPS
        if 0.4 <= t <= 4.8:
            f = over(f, dis, sm((t - 0.4) / 0.3) * (1 - sm((t - 4.5) / 0.3)))
        if i >= black0:
            f = np.zeros_like(f)
            if i >= t_on:
                bright = min(1.0, cen[i] / peak * 1.15)           # follow the original's own fade
                f = over(f, title_layer(F, (i - t_on) / FPS), bright)
        w.stdin.write(f.tobytes())
    w.stdin.close()
    w.wait()
    return dict(frames=n, title_black=black0, title_on=t_on)


# ---------------------------------------------------------------- 2. Hull
HULL_CLOCK = [(28.2, 31.8, "16"), (33.1, 35.8, "18"), (35.8, 39.8, "37")]   # minutes 22 / 24 / 60 -> the real ones
HULL_CARD = [(31.8, 33.1, "17'"), (39.8, 41.2, "38'")]                      # the score cards' 23' / 61'


def hull_lower_third(F):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rectangle((84, 812, 900, 1004), fill=(12, 12, 14, 254))
    dr.text((122, 822), "HULL AWAY", font=F.get("BebasNeue-Regular.ttf", 74), fill=(240, 240, 240, 255))
    dr.rectangle((122, 912, 420, 917), fill=(218, 22, 30, 255))
    dr.text((122, 938), "Premier League  |  Matchday 1  |  22 August 2026", font=F.get("Inter.ttf", 34, 500),
            fill=(232, 232, 232, 255))
    return np.asarray(im)


def fix_clock(f, minutes, F):
    """the score bug's clock: its minutes redrawn, its seconds (the original pixels) kept"""
    reg = f[60:112, 415:530]
    g = reg.mean(2)
    if (g > 140).sum() < 40 or f[80:100, 398:410].mean() > 60:
        return f                                   # no bug in this frame
    cols = (g > 140).any(0)
    runs, on = [], False
    for x, c in enumerate(cols):
        if c and not on:
            s0, on = x, True
        if not c and on:
            runs.append((s0, x - 1))
            on = False
    if on:
        runs.append((s0, len(cols) - 1))
    colon = next((r for r in runs if r[1] - r[0] <= 6), None)
    if colon is None:
        return f
    x_end = 415 + colon[0] - 3
    bg = np.median(f[66:106, 404:414].reshape(-1, 3), 0)
    f[64:108, 417:x_end + 1] = bg
    ys, xs = np.nonzero(g > 140)
    col = tuple(int(c) for c in np.percentile(reg[g > 140].reshape(-1, 3), 70, axis=0))
    im = Image.fromarray(f)
    dr = ImageDraw.Draw(im)
    fn = F.get("Inter.ttf", 30, 500)
    bb = dr.textbbox((0, 0), minutes, font=fn)
    top = 60 + ys.min()
    dr.text((x_end - (bb[2] - bb[0]) - bb[0] - 1, top - bb[1]), minutes, font=fn, fill=col)
    return np.asarray(im).copy()


def fix_card(f, text, F):
    reg = f[690:745, 900:1020].mean(2)
    if (reg > 120).sum() < 30:
        return f
    for y in range(692, 744):                       # fill the old minute with the gradient either side of it
        a, b = f[y, 900:918].mean(0), f[y, 1002:1020].mean(0)
        f[y, 918:1002] = np.linspace(a, b, 84)
    im = Image.fromarray(f)
    dr = ImageDraw.Draw(im)
    fn = F.get("Oswald.ttf", 46, 500)
    tw = dr.textlength(text, font=fn)
    bb = dr.textbbox((0, 0), text, font=fn)
    dr.text((960 - tw / 2, 700 - bb[1]), text, font=fn, fill=(194, 194, 195))
    return np.asarray(im).copy()


def hull(src, out, F):
    l3 = hull_lower_third(F)
    w = writer(out)
    n = 0
    for i, f in enumerate(reader(src)):
        t = i / FPS
        if 0.5 <= t < 3.75:                         # the corrected lower third, over the old one's whole life
            f = over(f, l3, sm((t - 0.5) / 0.2) * (1 - sm((t - 3.2) / 0.3)) if t > 0.7 else sm((t - 0.5) / 0.2))
        for a, b, mins in HULL_CLOCK:
            if a <= t < b:
                f = fix_clock(f, mins, F)
        for a, b, txt in HULL_CARD:
            if a <= t < b:
                f = fix_card(f, txt, F)
        w.stdin.write(f.tobytes())
        n += 1
    w.stdin.close()
    w.wait()
    return dict(frames=n)


# ---------------------------------------------------------------- 4. The Mole
def mole(src, out):
    keep = [(round(a * FPS), round(b * FPS)) for a, b in MOLE_KEEP]
    w = writer(out)
    n = 0
    for i, f in enumerate(reader(src, scale=False)):
        if any(a <= i < b for a, b in keep):
            w.stdin.write(f.tobytes())
            n += 1
    w.stdin.close()
    w.wait()
    return dict(frames=n, keep_frames=keep)


# ---------------------------------------------------------------- sound
SR = 48000


def read_audio(path, seconds=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    y = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    if seconds is not None:
        n = int(round(seconds * SR))
        y = np.vstack([y, np.zeros((max(0, n - len(y)), 2), np.float32)])[:n]
    return y


def write_wav(path, y):
    import soundfile as sf
    sf.write(str(path), y, SR, subtype="FLOAT")


def lufs(y):
    import soundfile as sf
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav") as tf:
        sf.write(tf.name, y, SR)
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", tf.name, "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    line = [l for l in r.splitlines() if l.strip().startswith("I:")][-1]
    return float(line.split()[1])


def level(y, target=-16.0):
    g = 10 ** ((target - lufs(y)) / 20)
    return y * g


def crossjoin(parts, xf):
    """pieces joined end to end with a short fade out / fade in (xf samples) either side of every join, so no join
    clicks and the total length is exactly the pieces' lengths"""
    h = xf // 2
    ramp = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    out = []
    for i, p in enumerate(parts):
        p = p.copy()
        if i > 0:
            p[:h] *= ramp
        if i < len(parts) - 1:
            p[-h:] *= ramp[::-1]
        out.append(p)
    return np.vstack(out)


def bruno_shout(path, at, sr=SR):
    """Bruno's touchline shout, small in the stadium: band-limited, a little of the bowl round it"""
    from scipy.signal import butter, sosfilt, fftconvolve
    y = read_audio(path).mean(1)
    sos = butter(2, [220, 5200], "bandpass", fs=sr, output="sos")
    y = sosfilt(sos, y).astype(np.float32)
    rng = np.random.default_rng(4)
    n = int(0.9 * sr)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / (0.22 * sr)).astype(np.float32)
    wet = fftconvolve(y, ir)[:len(y)] * 0.035
    z = np.stack([y * 0.95 + wet, y * 0.8 + wet * 1.1], 1)
    return z, int(at * sr)


def best(d):
    """a studio episode's full-quality render (build/master.mp4, kept when the committed copy was refitted under
    100 MB), else the committed one"""
    m = d / "build" / "master.mp4"
    return m if m.exists() else d / f"{d.name}.mp4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/home/user/src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fonts", default="/home/user/src/anim-handover/library/fonts")
    ap.add_argument("--only", default="", help="pieces to (re)build: boardroom,hull,mole (default: missing ones)")
    a = ap.parse_args()
    S = pathlib.Path(a.src)
    O = pathlib.Path(a.out)
    P = O / "pieces"
    P.mkdir(parents=True, exist_ok=True)
    F = Fonts(a.fonts)
    srcs = {
        "boardroom": S / "tv-hull/manchester-united-documentary/episode-1-not-ideal/episode1_scenes1-2_1080p.mp4",
        "hull": S / "tv-hull/manchester-united-documentary/episode-1-not-ideal/episode1_scenes3-4_4k.mp4",
        "part_a": best(S / "anim-handover/episodes/aos-ep1-a"),
        "mole": S / "tv-mole/the-mole/The_Mole_1080p.mp4",
        "part_b": best(S / "anim-handover/episodes/aos-ep1-b"),
    }
    shout = S / "anim-handover/episodes/hull-shout/voiceovers/H00-bruno-fernandes.wav"
    only = set(filter(None, a.only.split(",")))
    rep = {}
    # ---- pictures
    for name, fn in (("boardroom", lambda: boardroom(srcs["boardroom"], P / "1_boardroom.mp4", F)),
                     ("hull", lambda: hull(srcs["hull"], P / "2_hull.mp4", F)),
                     ("mole", lambda: mole(srcs["mole"], P / "4_mole.mp4"))):
        target = {"boardroom": "1_boardroom", "hull": "2_hull", "mole": "4_mole"}[name]
        if name in only or not (P / f"{target}.mp4").exists():
            print("building", name, flush=True)
            rep[name] = fn()
        else:
            rep[name] = dict(frames=probe_frames(P / f"{target}.mp4"))
    for name, target in (("part_a", "3_part_a"), ("part_b", "5_part_b")):
        run(["ffmpeg", "-y", "-v", "error", "-i", str(srcs[name]), "-an", "-c:v", "copy", str(P / f"{target}.mp4")])
        rep[name] = dict(frames=probe_frames(P / f"{target}.mp4"))
    # the studio's chunked render can come out a frame under its timeline: hold part A's last frame (the mug on the
    # sill, a still insert) for the missing frames, so the master is exactly TOTAL frames
    short = TOTAL - sum(rep[k]["frames"] for k in ("boardroom", "hull", "part_a", "mole", "part_b"))
    if short > 0:
        tmp = P / "3_part_a_padded.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(P / "3_part_a.mp4"), "-vf", f"tpad=stop_mode=clone:stop={short}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", "-r", str(FPS), str(tmp)])
        tmp.replace(P / "3_part_a.mp4")
        rep["part_a"] = dict(frames=probe_frames(P / "3_part_a.mp4"), held_last_frame=short)
    order = ["boardroom", "hull", "part_a", "mole", "part_b"]
    files = ["1_boardroom", "2_hull", "3_part_a", "4_mole", "5_part_b"]
    frames = [rep[k]["frames"] for k in order]
    print("frames", dict(zip(order, frames)), "total", sum(frames), flush=True)
    # ---- sound: each piece at its own length, levelled, then end to end
    secs = [n / FPS for n in frames]
    ys = []
    for k, n in zip(order, secs):
        if k == "mole":
            full = read_audio(srcs["mole"])
            parts = [full[int(round(x * FPS)) * SR // FPS:int(round(y_ * FPS)) * SR // FPS] for x, y_ in MOLE_KEEP]
            y = crossjoin(parts, 4 * SR // FPS)
            y = np.vstack([y, np.zeros((max(0, int(round(n * SR)) - len(y)), 2), np.float32)])[:int(round(n * SR))]
        else:
            y = read_audio(srcs[k], n)
        if k == "hull":
            z, at = bruno_shout(shout, 33.3)
            z = z * (10 ** ((lufs(y) - 9.0 - lufs(z)) / 20))         # 9 LU under the crowd's level
            e = min(len(y), at + len(z))
            fade = np.ones(e - at, np.float32)
            y[at:e] += z[:e - at] * fade[:, None]
        y = level(y, -16.0)
        ys.append(y)
        rep.setdefault(k, {})["seconds"] = n
    mix = np.vstack(ys)
    write_wav(O / "mix_raw.wav", mix)
    # final loudness: -14 LUFS integrated, true peak under -1 dBTP (two-pass loudnorm)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(O / "mix_raw.wav"), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(O / "mix_raw.wav"), "-af",
         f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
         f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
         "-ar", str(SR), "-c:a", "pcm_s24le", str(O / "mix.wav")])
    # ---- the master
    with open(O / "concat.txt", "w") as fh:
        for f in files:
            fh.write(f"file '{(P / (f + '.mp4')).resolve()}'\n")
    master = O / "all_or_something_ep1_master.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(O / "concat.txt"), "-i",
         str(O / "mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-tune", "animation",
         "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
         "-shortest", str(master)])
    nf = probe_frames(master)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(master)], capture_output=True, text=True, check=True).stdout)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(master), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    summ = r[r.rindex("Summary:"):]
    rep["master"] = dict(file=master.name, frames=nf, seconds=dur, target_frames=TOTAL, loudness_summary=summ)
    (O / "report.json").write_text(json.dumps(rep, indent=1, default=str))
    print(json.dumps(rep["master"], indent=1))


if __name__ == "__main__":
    main()
