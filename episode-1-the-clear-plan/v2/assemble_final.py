#!/usr/bin/env python3
"""The final episode from a splice list: every part's picture is pieced together from what was already rendered and
the stretches rendered again (frame ranges), and every part's sound is its own new mix, so a change in the middle
of a part (Cunha's fallout at Como, two month close-ups, the credits) costs only the frames that changed.

    python3 v2/assemble_final.py --studio <AnimnationStuido- checkout> --out OUT_DIR

PARTS: (slug, [(video file, the part's frame the file starts at, first frame, end frame or None = to the file's
end), ...]). A video file is relative to episodes/<slug>/; frame numbers are the part's own (30 fps): a whole render
starts at frame 0, a range render (render --range A B) at int(A * 30). The pieces of one part tile it with no gap,
and the part's sound is its mix (build/episode_audio.wav) over the same frames. Writes OUT_DIR/master.mp4 (x264
CRF 16; the loudness set to -16 LUFS integrated, true peak under -2 dBTP), OUT_DIR/episode.mp4 (two passes, under
95 MB for GitHub, AAC 128 kb/s) and report.json."""
import argparse
import json
import os
import pathlib
import subprocess

import numpy as np
import soundfile as sf

FPS, SR = 30, 48000
BEST = "BEST"            # the part's whole render: build/master.mp4 when the render was refitted under 95 MB, else
                         # <slug>.mp4
PARTS = [
    ("v2-meeting", [(BEST, 0, 0, None)]),
    ("v2-month", [("build/master.mp4", 0, 0, 2028), ("build/month_cu.mp4", 2028, 2028, 2091),
                  ("build/master.mp4", 0, 2091, 2619), ("build/month_se.mp4", 2619, 2619, 2664),
                  ("build/master.mp4", 0, 2664, None)]),
    ("v3-upstairs", [(BEST, 0, 0, None)]),
    ("v2-mole", [("build/master.mp4", 0, 0, None)]),
    ("v2-como", [("build/master.mp4", 0, 0, 2609), ("build/como_tail.mp4", 2609, 2609, None)]),
    ("v2-lastchance", [("v2-lastchance.mp4", 0, 0, 1926)]),               # to the smash to black
    ("v3-bournemouth", [("build/bou_full_v1.mp4", 0, 0, 1920), ("build/bou_tail.mp4", 1920, 1920, None)]),
    ("v2-lastchance", [("build/lc_credits.mp4", 1926, 1926, None)]),      # the end title, the credits
]


def run(cmd):
    subprocess.run(cmd, check=True)


def best(d, slug):
    """a render's full-quality file: its master if the same render refitted it (written minutes before), else the
    film itself"""
    out, mas = d / f"{slug}.mp4", d / "build" / "master.mp4"
    if mas.exists() and (not out.exists() or mas.stat().st_mtime > out.stat().st_mtime - 3600):
        return mas
    return out


def probe_frames(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                               "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True,
                              check=True).stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    E = pathlib.Path(a.studio) / "episodes"
    O = pathlib.Path(a.out)
    O.mkdir(parents=True, exist_ok=True)
    rep, ys, pieces = {"parts": []}, [], []
    for slug, vids in PARTS:
        tiles = []
        for name, start, f0, f1 in vids:
            src = best(E / slug, slug) if name == BEST else E / slug / name
            n = probe_frames(src)
            f1 = start + n if f1 is None else f1
            lo, hi = f0 - start, f1 - start
            assert 0 <= lo < hi <= n, (slug, name, f0, f1, start, n)
            pieces.append((src, lo, hi))
            tiles.append((str(src.relative_to(E)), f0, f1))
        for (_, _, b), (_, c, _) in zip(tiles, tiles[1:]):
            assert b == c, (slug, "the pieces must tile the part")
        f_lo, f_hi = tiles[0][1], tiles[-1][2]
        # the sound: the part's mix over the same frames
        y, sr = sf.read(E / slug / "build" / "episode_audio.wav", dtype="float32", always_2d=True)
        assert sr == SR
        s0, s1 = int(round(f_lo / FPS * SR)), int(round(f_hi / FPS * SR))
        y = np.pad(y, ((0, max(0, s1 - len(y))), (0, 0)))[s0:s1]
        k = int(0.01 * SR)                                          # 10 ms fades either side of every join
        y[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None]
        y[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
        ys.append(y)
        rep["parts"].append(dict(slug=slug, frames=f_hi - f_lo, seconds=round((f_hi - f_lo) / FPS, 3),
                                 pieces=[list(x) for x in tiles]))
        print(slug, f_hi - f_lo, "frames", round((f_hi - f_lo) / FPS, 2), "s", flush=True)
    total = sum(p["frames"] for p in rep["parts"])
    sf.write(O / "mix_raw.wav", np.vstack(ys), SR, subtype="FLOAT")
    # -16 LUFS integrated, true peak under -2 dBTP (two-pass loudnorm)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(O / "mix_raw.wav"), "-af",
                        "loudnorm=I=-16:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(O / "mix_raw.wav"), "-af",
         f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
         f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
         "-ar", str(SR), "-c:a", "pcm_s24le", str(O / "mix.wav")])
    # the picture: every piece decoded on its own, in order, its frames trimmed by number and piped raw into one
    # encoder (one filter graph over all the files would hold every later piece's frames in memory until its turn)
    master = O / "master.mp4"
    W, H = 1920, 1080
    fb = W * H * 3 // 2
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(O / "mix.wav"), "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-tune", "animation", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
                            "-shortest", str(master)], stdin=subprocess.PIPE)
    for src, lo, hi in pieces:
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-vf",
                                f"trim=start_frame={lo}:end_frame={hi},setpts=PTS-STARTPTS,scale={W}:{H}",
                                "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"],
                               stdout=subprocess.PIPE)
        n, last = 0, None
        while n < hi - lo:
            fr = dec.stdout.read(fb)
            if len(fr) < fb:
                break
            enc.stdin.write(fr)
            last, n = fr, n + 1
        dec.stdout.close()
        dec.wait()
        assert last is not None and n >= hi - lo - 1, (str(src), lo, hi, n)
        while n < hi - lo:                                  # at most one frame short at a file's very end: hold it
            enc.stdin.write(last)
            n += 1
    enc.stdin.close()
    if enc.wait():
        raise SystemExit("the master's encode failed")
    # the delivered file: two passes to fit under 95 MB; its sound encoded once, straight from the mix
    kbps = int(95.0 * 8000 * 0.97 / (total / FPS)) - 128
    log = str(O / "fit")
    common = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-b:v", f"{kbps}k", "-passlogfile", log]
    run(["ffmpeg", "-y", "-v", "error", "-i", str(master)] + common + ["-pass", "1", "-an", "-f", "mp4", os.devnull])
    episode = O / "episode.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(master), "-i", str(O / "mix.wav"), "-map", "0:v", "-map", "1:a"]
        + common + ["-pass", "2", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                    "-shortest", str(episode)])
    for f in (master, episode):
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        b = subprocess.run(["ffmpeg", "-v", "info", "-i", str(f), "-vf", "blackdetect=d=0.2:pix_th=0.06", "-an",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
        rep[f.stem] = dict(file=f.name, frames=probe_frames(f), mb=round(f.stat().st_size / 1e6, 1),
                           loudness_summary=r[r.rindex("Summary:"):],
                           black=[ln.split("black_start:")[1].strip() for ln in b.splitlines() if "black_start" in ln])
    rep["episode"]["video_kbps"] = kbps
    rep["frames"], rep["seconds"] = total, round(total / FPS, 3)
    (O / "report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep[k] for k in ("master", "episode", "frames", "seconds")}, indent=1))


if __name__ == "__main__":
    main()
