#!/usr/bin/env python3
"""Assemble ALL OR SOMETHING, Episode One: THE CLEAR PLAN (version 2) from its four studio segments
(AnimnationStuido- episodes/, filmed with studio/film; every character the same library cut-out and the same cloned
Fish Audio voice throughout):

  1. v2-meeting   Carrington, the boardroom, the owners' call, the title
  2. v2-month     Hull (the team talk, the match, the dressing room) and the month of results to Leeds week
  3. v2-mole      The Mole, re-voiced line by line, without its title card and next-episode teaser
  4. v2-como      Leeds, Como, the interviews, the clear plan, the credits

The segments are joined with hard cuts (each one opens on a line). Their sound, each mastered at -16 LUFS, is
joined with a 10 ms fade either side of every join and brought to -14 LUFS integrated, true peak under -1.5 dBTP.

  python3 assemble_v2.py --studio /home/user/src/anim-handover --out OUT_DIR

Writes OUT_DIR/master.mp4 (x264 CRF 16), OUT_DIR/episode.mp4 (two-pass, under 95 MB for GitHub) and report.json
(every segment's frame count, the master's duration, frames, loudness and black stretches)."""
import argparse
import json
import os
import pathlib
import subprocess

import numpy as np
import soundfile as sf

FPS, SR = 30, 48000
SEGMENTS = ["v2-meeting", "v2-month", "v2-mole", "v2-como"]


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_frames(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True,
                         check=True).stdout
    return int(out.strip())


def seconds(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True, check=True).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    E = pathlib.Path(a.studio) / "episodes"
    O = pathlib.Path(a.out)
    O.mkdir(parents=True, exist_ok=True)
    rep, srcs, ys = {}, [], []
    for slug in SEGMENTS:
        d = E / slug
        src = d / "build" / "master.mp4"
        if not src.exists():
            src = d / f"{slug}.mp4"
        nf = probe_frames(src)
        n = int(round(nf / FPS * SR))
        wav = O / f"{slug}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_f32le",
             str(wav)])
        y, _ = sf.read(wav, dtype="float32", always_2d=True)
        y = np.pad(y, ((0, max(0, n - len(y))), (0, 0)))[:n]
        k = int(0.01 * SR)                                      # 10 ms fades either side of the join
        y[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None]
        y[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
        ys.append(y)
        srcs.append(src)
        rep[slug] = dict(source=str(src), frames=nf, seconds=nf / FPS)
        print(slug, nf, "frames", round(nf / FPS, 2), "s")
    sf.write(O / "mix_raw.wav", np.vstack(ys), SR, subtype="FLOAT")
    # -14 LUFS integrated, true peak under -1.5 dBTP (two-pass loudnorm)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(O / "mix_raw.wav"), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(O / "mix_raw.wav"), "-af",
         f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
         f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
         "-ar", str(SR), "-c:a", "pcm_s24le", str(O / "mix.wav")])
    # the master: the four pictures end to end, the mix under them
    with open(O / "concat.txt", "w") as fh:
        for s in srcs:
            fh.write(f"file '{s.resolve()}'\n")
    master = O / "master.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(O / "concat.txt"), "-i",
         str(O / "mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-tune", "animation",
         "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
         "-shortest", str(master)])
    # the delivered file: two passes to fit under 95 MB
    dur = seconds(master)
    kbps = int(95.0 * 8000 * 0.97 / dur) - 192
    log = str(O / "fit")
    common = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-b:v", f"{kbps}k", "-passlogfile", log]
    run(["ffmpeg", "-y", "-v", "error", "-i", str(master)] + common + ["-pass", "1", "-an", "-f", "mp4", os.devnull])
    episode = O / "episode.mp4"
    # its sound is encoded once, straight from the mix, 0.4 dB down so the AAC's true peak stays under -1 dBTP
    run(["ffmpeg", "-y", "-v", "error", "-i", str(master), "-i", str(O / "mix.wav"), "-map", "0:v", "-map", "1:a"]
        + common + ["-pass", "2", "-pix_fmt", "yuv420p", "-af", "volume=-0.4dB", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", str(episode)])
    # measurements
    for f in (master, episode):
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        b = subprocess.run(["ffmpeg", "-v", "info", "-i", str(f), "-vf", "blackdetect=d=0.2:pix_th=0.06", "-an",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
        rep[f.stem] = dict(file=f.name, frames=probe_frames(f), seconds=seconds(f), mb=round(f.stat().st_size / 1e6, 1),
                           loudness_summary=r[r.rindex("Summary:"):],
                           black=[ln.split("black_start:")[1].strip() for ln in b.splitlines() if "black_start" in ln])
    (O / "report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep[k] for k in ("master", "episode")}, indent=1))


if __name__ == "__main__":
    main()
