"""The soundtrack: the dialogue edit plus room tone, weather, foley, the 'serious documentary' score and the title
sting. No sound library: every effect and all the music are synthesised here (numpy / scipy), deterministically.

  - dialogue: every line at its timeline position, levelled; a small-room reverb in the boardroom, a more open one
    in Monaco; the narrator dry and close
  - room tone: grey Manchester outside (wind, drizzle, distant traffic), boardroom HVAC, Monaco sea and gulls
  - score: brooding strings and piano over Carrington, a hit on the cut into the boardroom, a pulsing underscore
    that stops dead after "We bought three midfielders"; a cheesy Riviera lounge loop in Monaco (hard-cut on the
    smash back); a boom + chord for the title that ends hard, so the Short loops
  - foley: whip whoosh, smash-cut hit, paper, chair creak
python3 audio.py -> build/episode_audio.wav (48 kHz stereo)"""
import json, math, numpy as np, soundfile as sf
from scipy import signal
from timeline import TL
from direction import m, ls, le, WHIPS

SR = 48000
TOTAL = TL["total"]
N = int(round(TOTAL * SR))
RNG = np.random.default_rng(2026)
LINES = json.load(open("build/lines.json"))


def db(x): return 10 ** (x / 20)


def at_level(x, target_db):
    """scale x so the RMS of its active part (above -50 dB of its peak) is target_db dBFS"""
    x = np.asarray(x, np.float32)
    mono = x.mean(1) if x.ndim == 2 else x
    a = np.abs(mono)
    if a.max() <= 0: return x
    act = mono[a > a.max() * db(-50)]
    r = np.sqrt(np.mean(act ** 2)) if len(act) else 1.0
    return x * (db(target_db) / max(r, 1e-9))


def bp(x, lo, hi, order=4): return signal.sosfilt(signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)
def lp(x, f, order=4): return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)
def hp(x, f, order=4): return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def noise(n, color="white"):
    w = RNG.standard_normal(n).astype(np.float32)
    if color == "white": return w
    if color == "pink":
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]; a = [1, -2.494956002, 2.017265875, -0.522189400]
        p = signal.lfilter(b, a, w); return (p / (np.std(p) + 1e-9)).astype(np.float32)
    b = np.cumsum(w); b = hp(b, 20, 2); return (b / (np.std(b) + 1e-9)).astype(np.float32)


def fade(n, fin, fout):
    e = np.ones(n, np.float32)
    fi, fo = int(fin * SR), int(fout * SR)
    if fi: e[:fi] = np.linspace(0, 1, fi)
    if fo: e[-fo:] = np.minimum(e[-fo:], np.linspace(1, 0, fo))
    return e


class Bus:
    def __init__(self):
        self.x = np.zeros((N, 2), np.float32)

    def add(self, y, t, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        y = np.asarray(y, np.float32)
        if y.ndim == 1: y = np.stack([y, y], 1)
        gl, gr = math.cos((pan + 1) * math.pi / 4) * 1.4142, math.sin((pan + 1) * math.pi / 4) * 1.4142
        j0 = max(0, i); k0 = j0 - i
        n = min(len(y) - k0, N - j0)
        if n <= 0: return
        self.x[j0:j0 + n, 0] += y[k0:k0 + n, 0] * gain * gl
        self.x[j0:j0 + n, 1] += y[k0:k0 + n, 1] * gain * gr


def reverb_ir(seconds, damp=6000, predelay=0.01, seed=1):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR); t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)).astype(np.float32) * np.exp(-6.9 * t / seconds)[:, None]
    ir[:, 0] = lp(ir[:, 0], damp, 2); ir[:, 1] = lp(ir[:, 1], damp, 2)
    ir = np.concatenate([np.zeros((int(predelay * SR), 2), np.float32), ir])
    return ir / np.sqrt((ir ** 2).sum(0).mean())


def convolve_st(x, ir):
    if x.ndim == 1: x = np.stack([x, x], 1)
    return np.stack([signal.fftconvolve(x[:, 0], ir[:, 0]), signal.fftconvolve(x[:, 1], ir[:, 1])], 1).astype(np.float32)


# ---------------------------------------------------------------- instruments
def note(nm):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "Eb": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0,
             "Bb": 1, "A#": 1, "B": 2}
    p, o = nm[:-1], int(nm[-1])
    return 440.0 * 2 ** ((names[p] + 12 * (o - 4)) / 12)


def piano_note(f, dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for h, (g, d) in enumerate([(1.0, 1.6), (0.45, 1.1), (0.22, 0.8), (0.12, 0.6), (0.06, 0.4)], 1):
        x += g * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * (1.0 + 0.9 * h) / d)
    return x * np.minimum(1, t / 0.004) * vel * 0.25


def strings(freqs, dur, attack=0.8, release=1.2, bright=1600):
    """a bowed string section: detuned saws, gentle vibrato, low-passed"""
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for f in freqs:
        for det in (-0.09, 0.0, 0.11):
            vib = 1 + 0.003 * np.sin(2 * np.pi * (5.1 + det) * t + RNG.uniform(0, 6))
            ph = 2 * np.pi * np.cumsum(f * (2 ** (det / 12)) * vib) / SR
            x += signal.sawtooth(ph + RNG.uniform(0, 6)).astype(np.float32) * 0.16
    x = lp(x, bright, 2)
    e = np.minimum(1, t / max(attack, 1e-3)) * np.minimum(1, (dur - t) / max(release, 1e-3))
    return (x * np.clip(e, 0, 1)).astype(np.float32)


def stab(freqs, dur=0.35):
    """a short staccato string / brass stab"""
    n = int(dur * SR); t = np.arange(n) / SR
    x = strings(freqs, dur, 0.01, 0.05, 2600)
    return x * np.exp(-t * 7).astype(np.float32)


def boom(dur=3.0, f0=42):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (f0 + 38 * np.exp(-t * 7)) * t) * np.exp(-t * 1.6)
    x += bp(noise(n), 60, 900, 2) * np.exp(-t * 9) * 0.35
    return x.astype(np.float32)


def whoosh(dur=0.45, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    x = noise(n, "pink")
    f = np.linspace(400, 3800, n) if up else np.linspace(3800, 400, n)
    out = np.zeros(n, np.float32)
    for i in range(0, n, 1024):
        fc = f[i]
        sos = signal.butter(2, [fc * 0.6, min(SR / 2 - 100, fc * 1.6)], btype="band", fs=SR, output="sos")
        out[i:i + 1024] = signal.sosfilt(sos, x[i:i + 1024])
    return out * np.sin(np.pi * t / dur) ** 2 * 0.5


def riser(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    x = whoosh(dur, True) * (t / dur) ** 2 * 2.0
    return x.astype(np.float32)


def chair_creak():
    n = int(0.55 * SR); t = np.arange(n) / SR
    f = 300 + 110 * np.sin(2 * np.pi * 2.6 * t)
    x = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * (np.sin(np.pi * t / 0.55) ** 2)
    return (bp(x, 380, 2200, 2) * (0.5 + 0.5 * (noise(n) > 0.4)) * 0.3).astype(np.float32)


def paper_rustle(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.zeros(n, np.float32)
    for _ in range(14):
        c = RNG.uniform(0, dur); w = RNG.uniform(0.01, 0.05)
        env += np.exp(-((t - c) / w) ** 2) * RNG.uniform(0.4, 1)
    return (bp(noise(n), 1800, 9000, 2) * env * 0.4).astype(np.float32)


def gull():
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 1500 + 700 * np.sin(np.pi * t / 0.6) ** 2 - 500 * t
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return (x * np.sin(np.pi * t / 0.6) ** 3 * 0.2).astype(np.float32)


# ---------------------------------------------------------------- score
def doc_score():
    """0 -> the cut into the boardroom: brooding; the cut: a hit; then a pulsing underscore until the stop"""
    t_hit, t_stop = m("cut_wide"), m("music_stop")
    n = int((t_stop + 0.01) * SR)
    x = np.zeros((n, 2), np.float32)
    def put(y, t, g=1.0, pan=0.0):
        y = np.asarray(y, np.float32)
        if y.ndim == 1:
            gl, gr = math.cos((pan + 1) * math.pi / 4) * 1.4142, math.sin((pan + 1) * math.pi / 4) * 1.4142
            y = np.stack([y * gl, y * gr], 1)
        i = int(t * SR); j = min(n, i + len(y))
        if i < n: x[i:j] += y[:j - i] * g
    # exterior: low strings swell, solemn piano, a riser into the cut
    put(strings([note("D2"), note("A2"), note("D3")], t_hit + 0.2, 1.4, 0.1, 900), 0.0, 0.9)
    for tn, nm in ((0.35, "A4"), (1.15, "F4"), (1.95, "D4"), (2.6, "E4")):
        put(piano_note(note(nm), 2.0, 0.9), tn, 0.8, pan=0.2)
        put(piano_note(note(nm) / 2, 2.0, 0.5), tn, 0.6, pan=-0.2)
    put(riser(1.1), t_hit - 1.1, 0.35)
    # the hit on the cut
    put(boom(2.6), t_hit, 1.3)
    put(stab([note("D3"), note("F3"), note("A3"), note("D4")], 0.6), t_hit, 1.0)
    # underscore: staccato low strings in 8ths at 104 bpm over a pad, Dm - Bb - F - C
    beat = 60 / 104
    prog = [("D2", ["D3", "F3", "A3"]), ("Bb1", ["D3", "F3", "Bb3"]), ("F2", ["C3", "F3", "A3"]), ("C2", ["C3", "E3", "G3"])]
    k, t = 0, t_hit + 2 * beat
    while t < t_stop:
        bass, chord = prog[(k // 8) % 4]
        put(stab([note(bass), note(bass) * 2], 0.22) * (1.0 if k % 2 == 0 else 0.7), t, 0.9)
        if k % 8 == 0:
            put(strings([note(c) for c in chord], 8 * beat / 2 + 0.6, 0.25, 0.4, 1500), t, 0.55)
        if k % 4 == 2:                                     # a soft timpani on the off-beat
            put(boom(0.6, 60) * 0.35, t, 0.6)
        t += beat / 2; k += 1
    ir = reverb_ir(2.4, 5000, 0.02, 7)
    wet = convolve_st(x, ir)[:n]
    y = x * 0.85 + wet * 0.25
    y[-int(0.006 * SR):] *= np.linspace(1, 0, int(0.006 * SR))[:, None]      # stops dead
    return y


def lounge(dur):
    """Monaco: a smug little Riviera bossa loop (e-piano, bass, shaker)"""
    n = int(dur * SR)
    x = np.zeros((n, 2), np.float32)
    bpm = 118; beat = 60 / bpm
    chords = [["F3", "A3", "C4", "E4"], ["E3", "G3", "B3", "D4"], ["D3", "F3", "A3", "C4"], ["G3", "B3", "D4", "F4"]]
    bass = ["F2", "E2", "D2", "G2"]
    pattern = [0, 1.5, 3, 4.5, 6]                                   # bossa comping hits within 2 bars (in beats)
    t = 0.0; bar = 0
    while t < dur:
        ch = chords[bar % 4]
        for p in pattern:
            tt = t + p * beat / 2
            if tt >= dur: break
            nn = int(0.5 * SR); tv = np.arange(nn) / SR
            y = np.zeros(nn, np.float32)
            for nm in ch:
                f = note(nm)
                y += (np.sin(2 * np.pi * f * tv) + 0.25 * np.sin(4 * np.pi * f * tv)) * np.exp(-tv * 5)
            y *= 0.12 * (1 + 0.2 * np.sin(2 * np.pi * 5 * tv))
            i = int(tt * SR); j = min(n, i + nn)
            x[i:j, 0] += y[:j - i] * 0.9; x[i:j, 1] += y[:j - i]
        for bt, dv in ((0, 1.0), (1.5, 0.7), (2, 0.9), (3.5, 0.7)):
            tt = t + bt * beat
            if tt >= dur: break
            y = piano_note(note(bass[bar % 4]), 0.5, 1.0) * 1.4 * dv
            i = int(tt * SR); j = min(n, i + len(y)); x[i:j] += y[:j - i, None]
        for s8 in range(8):
            tt = t + s8 * beat / 2
            if tt >= dur: break
            nn = int(0.06 * SR)
            y = hp(noise(nn), 6000, 2) * np.exp(-np.arange(nn) / SR * 60) * (0.08 if s8 % 2 else 0.05)
            i = int(tt * SR); j = min(n, i + nn); x[i:j] += y[:j - i, None]
        t += 4 * beat; bar += 1
    return x * fade(n, 0.05, 0.0)[:, None]


def title_sting(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = boom(dur, 38) * 1.2
    x += bp(noise(n), 200, 5000, 2) * np.exp(-t * 7) * 0.25
    ch = strings([note("D2"), note("A2"), note("D3"), note("F3"), note("A3")], dur + 1.0, 0.03, 0.5, 2200)[:n]
    y = np.stack([x + ch * 0.6, x + ch * 0.6], 1)
    return y + convolve_st(y.mean(1), reverb_ir(3.0, 4000, 0.03, 3))[:n] * 0.3


# ---------------------------------------------------------------- layers
def dialogue(bus):
    room_s = reverb_ir(0.45, 5200, 0.006, 11)
    room_m = reverb_ir(0.8, 6500, 0.012, 12)
    for lid, v in TL["lines"].items():
        if LINES[lid].get("missing"): continue
        y, sr = sf.read(f"build/lines/{lid}.wav", dtype="float32")
        if y.ndim > 1: y = y.mean(1)
        y = hp(y, 75, 2).astype(np.float32)
        nar = v["speaker"] == "narrator"
        y = at_level(y, -18.5 if nar else -20.0)
        y = np.clip(y, -0.95, 0.95)
        bus.add(y, v["start"], 1.0)
        if not nar:
            monaco = m("cut_monaco") <= v["start"] < m("cut_ck8")
            wet = convolve_st(y, room_m if monaco else room_s)
            bus.add(wet, v["start"], db(-17 if monaco else -19))


def ambience(bus):
    # grey Manchester: wind, drizzle, distant traffic
    t1 = m("cut_wide")
    n = int((t1 + 0.02) * SR)
    wind = lp(noise(n, "pink"), 600, 2) * (1 + 0.35 * np.sin(np.arange(n) / SR * 0.9))
    rain = hp(noise(n), 3500, 2) * (0.6 + 0.4 * (noise(n) > 1.8))
    traffic = lp(noise(n, "brown"), 180, 2)
    amb = at_level(wind, -40) + at_level(rain, -46) + at_level(traffic, -44)
    bus.add(amb * fade(n, 0.6, 0.004), 0.0)
    # the boardroom: HVAC + a faint office murmur; much quieter behind Bruno's last close-up
    for a, b in ((m("cut_wide"), m("cut_monaco")), (m("cut_ck8"), m("cut_black"))):
        n = int((b - a) * SR)
        hv = at_level(lp(noise(n, "brown"), 220, 2), -48) + at_level(lp(noise(n, "pink"), 2500, 2), -60)
        mur = at_level(bp(noise(n, "pink"), 250, 1400, 2) * (1 + 0.5 * np.sin(np.arange(n) / SR * 0.31)), -58)
        g = np.ones(n, np.float32)
        tt = a + np.arange(n) / SR
        q = np.clip((tt - m("cut_br8") - 0.2) / 1.0, 0, 1)
        g *= (1 - 0.8 * q)
        bus.add((hv + mur) * g * fade(n, 0.003, 0.003), a)
    # Monaco: the sea, a breeze, gulls
    a, b = m("cut_monaco"), m("cut_ck8")
    n = int((b - a) * SR)
    tt = np.arange(n) / SR
    waves = lp(noise(n, "pink"), 900, 2) * (0.55 + 0.45 * np.sin(2 * np.pi * tt / 3.7) ** 2)
    bus.add(at_level(waves, -40) * fade(n, 0.003, 0.003), a)
    for tg, pan in ((a + 0.6, -0.5), (a + 2.9, 0.6), (a + 4.4, -0.2)):
        if tg < b - 0.6: bus.add(at_level(gull(), -40), tg, 1.0, pan)


def music(bus):
    bus.add(at_level(doc_score(), -24), 0.0)
    a, b = m("cut_monaco"), m("cut_ck8")
    lg = lounge(b - a)
    lg[-int(0.005 * SR):] *= np.linspace(1, 0, int(0.005 * SR))[:, None]           # smash cut: gone
    bus.add(at_level(lg, -31), a)
    # Bruno's button: a low, sad drone under him
    a, b = m("cut_br8"), m("cut_black")
    d = strings([note("D2"), note("A2")], b - a + 0.05, 1.2, 0.05, 500)
    bus.add(at_level(d, -40) * fade(len(d), 0.8, 0.01), a)
    # title: riser, boom and chord, cut hard at the very end (the Short loops)
    st = title_sting(TOTAL - m("cut_title") + 0.5)
    bus.add(at_level(st, -20), m("cut_title"))


def foley(bus):
    for tw in WHIPS:
        bus.add(at_level(whoosh(0.34, True), -24), tw - 0.18)
    tsm = m("cut_ck8")                                     # smash cut back to Manchester
    hit = boom(0.9, 55) * 0.8 + bp(noise(int(0.9 * SR)), 300, 4000, 2) * np.exp(-np.arange(int(0.9 * SR)) / SR * 14) * 0.3
    bus.add(at_level(hit, -22), tsm)
    bus.add(at_level(whoosh(0.3, False), -30), m("cut_monaco") - 0.05)
    bus.add(at_level(chair_creak(), -33), m("cut_br6") + 0.15, 1.0, -0.2)
    bus.add(at_level(paper_rustle(0.5), -34), ls("jr_bigger_issues") - 0.4, 1.0, 0.1)


def main():
    dlg, amb, mus, fx = Bus(), Bus(), Bus(), Bus()
    dialogue(dlg); ambience(amb); music(mus); foley(fx)
    # the music ducks under the dialogue
    env = np.abs(dlg.x.mean(1))
    env = lp(env, 6, 1)
    duck = 1.0 / (1.0 + 7.0 * np.clip(env / db(-26), 0, 1))
    duck = np.clip(duck, db(-7), 1.0).astype(np.float32)
    mix = dlg.x + amb.x + mus.x * duck[:, None] + fx.x
    # master: gentle soft clip to -1 dBFS, then the very end cut hard (10 ms)
    peak = db(-1)
    mix = mix * db(4.5)
    mix = np.tanh(mix / peak) * peak
    mix[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    sf.write("build/episode_audio.wav", mix.astype(np.float32), SR, subtype="PCM_24")
    r = np.sqrt(np.mean(mix ** 2))
    print(f"build/episode_audio.wav  {len(mix) / SR:.2f}s  rms {20 * np.log10(r + 1e-9):.1f} dBFS  peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS")


if __name__ == "__main__":
    main()
