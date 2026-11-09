"""the breakdown's soundtrack: the voice, a synthesised pulse-and-pad bed, whooshes on each scene, hits on the slams,
ticks on the counters, the crowd under the banner. -> mix.wav at -14 LUFS (run from anim-handover)"""
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from studio.film import audio as A
import make as M

D = os.path.dirname(os.path.abspath(__file__))
SR = A.SR
TOTAL = M.TOTAL
RNG = np.random.default_rng(5)


def whoosh(dur=0.5, level=-30, rise=True):
    n = int(dur * SR)
    y = RNG.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32)
    seg = n // 8
    for k in range(8):                                        # a band sweeping up (or down)
        u = k / 7 if rise else 1 - k / 7
        lo = 300 + 2600 * u
        part = A.bp(y[k * seg:(k + 1) * seg + 1], lo, lo * 2.2).astype(np.float32)
        out[k * seg:k * seg + len(part)] = part[:len(out[k * seg:k * seg + len(part)])]
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return A.at_level(np.stack([out * env, out * env * 0.9], 1), level)


def sub_hit(level=-22, f=48):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t * (1 + 0.6 * np.exp(-t * 18))) * np.exp(-t * 5)
    return A.at_level(np.stack([y, y], 1).astype(np.float32), level)


def pulse_bed():
    """a dark pulse at 100 bpm (a sub thump on every beat, a ticking hat on the off-beat) and a minor pad"""
    n = int(TOTAL * SR)
    y = np.zeros(n, np.float32)
    beat = 60 / 100
    t = 0.0
    k = 0
    while t < TOTAL - 1.4:
        i = int(t * SR)
        m = int(0.32 * SR)
        tt = np.arange(m) / SR
        thump = np.sin(2 * np.pi * 52 * tt * (1 + 0.5 * np.exp(-tt * 30))) * np.exp(-tt * 9)
        y[i:i + m] += (0.9 if k % 4 == 0 else 0.6) * thump[:len(y[i:i + m])]
        j = int((t + beat / 2) * SR)
        h = A.bp(RNG.standard_normal(int(0.05 * SR)), 6000, 12000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 70)
        y[j:j + len(h)] += 0.12 * h[:len(y[j:j + len(h)])]
        t += beat
        k += 1
    bed = np.stack([y, y], 1)
    chords = [["D2", "A2", "F3"], ["Bb1", "F2", "D3"], ["C2", "G2", "E3"], ["A1", "E2", "C#3"]]
    cl = 4 * beat * 2
    t = 0.0
    c = 0
    while t < TOTAL - 1.0:
        dur = min(cl, TOTAL - t)
        pad = A.strings([A.note(x) for x in chords[c % 4]], dur + 0.6, 0.6, 0.8, 1100)[:int(dur * SR)]
        i = int(t * SR)
        bed[i:i + len(pad), 0] += 0.5 * pad[:len(bed[i:i + len(pad)])]
        bed[i:i + len(pad), 1] += 0.5 * pad[:len(bed[i:i + len(pad)])]
        t += cl
        c += 1
    bed *= A.fade(len(bed), 0.8, 1.2)[:, None]
    return bed.astype(np.float32)


def main():
    dlg, fx, mus = A.Bus(TOTAL), A.Bus(TOTAL), A.Bus(TOTAL)
    vo, sr = sf.read(f"{D}/vo.wav", dtype="float32")
    import librosa
    if sr != SR:
        vo = librosa.resample(vo, orig_sr=sr, target_sr=SR)
    vo = A.at_level(A.bp(vo, 70, 15000).astype(np.float32), -20)
    dlg.add(vo, 0.0)
    # scene changes
    for t0 in (M.ls("V03"), M.ls("V05"), M.ls("V07"), M.ls("V08"), M.ls("V10"), M.ls("V11")):
        fx.add(whoosh(0.5, -30), t0 - 0.35)
    # slams and stamps
    for t0, lvl in ((M.wt("V01", "eighteenth"), -20), (M.wt("V07", "thirty"), -22), (M.wt("V08", "two"), -25),
                    (M.wt("V08", "paying"), -23)):
        fx.add(sub_hit(lvl), t0)
        A.ev(fx, "impacts/tom-hit", t0, lvl - 6, semis=-6, lowpass=1600)
    A.ev(fx, "impacts/tom-hit", M.wt("V01", "relegation"), -32, semis=-2, lowpass=2400)
    # the form strip and the counters: ticks
    t0 = M.wt("V02", "eight", 2)
    for i in range(8):
        A.ev(fx, "foley/pen-click-a", t0 + 0.12 * i, -36, semis=4 + (i % 3), highpass=1500, dur=0.05)
    for i in range(8):
        A.ev(fx, "foley/pen-click-b", M.wt("V02", "eight") + 0.06 * i, -40, semis=8, highpass=1500, dur=0.04)
    for i in range(14):
        A.ev(fx, "foley/pen-click-b", M.wt("V07", "thirty") + 0.05 * i, -40, semis=8, highpass=1500, dur=0.04)
    # the morph, the canyon, the counters running through it
    fx.add(whoosh(0.7, -33), M.wt("V03", "becomes"))
    fx.add(whoosh(0.45, -31, rise=False), M.wt("V04", "canyon") - 0.1)
    A.ev(fx, "sport/ball-kick", M.wt("V04", "lose"), -34)
    A.ev(fx, "sport/whistle-ref", M.ls("V05") + 0.1, -40, semis=2)
    # Villa: two goals inside four minutes
    for t0 in (M.wt("V05", "two") - 0.25, M.wt("V05", "four")):
        fx.add(sub_hit(-30, 60), t0)
    # the owners: a paper on the table, the crowd under the banner
    A.ev(fx, "paper/paper-handle", M.wt("V08", "borrowed"), -40)
    A.bed(fx, "crowd/crowd-large", M.ls("V10") - 0.3, M.ls("V11") + 0.2, -42, lowpass=3000, fin=0.6, fout=0.8)
    A.bed(fx, "crowd/crowd-large", M.wt("V09", "fans"), M.ls("V10") - 0.3, -48, lowpass=2500, fin=0.6, fout=0.3)
    # the end card
    te = M.TIMES["V11"][1] + 0.35
    fx.add(sub_hit(-24, 44), te)
    mus.add(pulse_bed(), 0.0)
    A.master(dlg, [fx], [mus], target=-14.0, out=f"{D}/mix.wav")


if __name__ == "__main__":
    main()
