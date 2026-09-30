"""The soundtrack: the dialogue edit, real recorded ambience and foley, the Hull fans' chant, the intro music, the
hopeful music that dies, and the title boom.

  - dialogue: every line at its timeline position, levelled; a small tiled-room reverb in the dressing room; the
    narrator dry and close
  - music: over-serious strings and piano over the MKM Stadium; it stops dead before "Probably" (no music in the
    dressing room); a little hopeful piano on Steve's "Good news", killed on "Ipswich"; the title sting and boom
  - the match: the full-time whistle and a burst of the home crowd on the score, then silence; the crowd under the
    narrator's corners, a roar on each goal; the Hull fans' chant ("you're getting mauled by the tigers", supplied)
    on the second goal and over the reactions, cut dead on the cut back inside; its last line again over the Tigers
    ending, cut hard at the very end so the Short loops
  - ambience and foley: real recordings (BigSoundBank and Wikimedia Commons, CC0; trimmed into ../../audio/sfx by
    tools/get_sfx.py): wind and the crowd arriving outside; air-conditioning and the stadium muffled through the
    walls before the game; a dead-quiet room after it; the clap, footsteps, the store-cupboard stop, the bench, the
    clipboard, a door shutting behind Carrick. No synthetic whooshes or beeps: cuts are hard cuts
python3 audio.py -> build/episode_audio.wav (48 kHz stereo)"""
import json, math, numpy as np, soundfile as sf
from scipy import signal
from timeline import TL
from direction import m, ls, le, wt, we

SR = 48000
TOTAL = TL["total"]
N = int(round(TOTAL * SR))
RNG = np.random.default_rng(2026)
LINES = json.load(open("build/lines.json"))
CHANT = "../../audio/music/tigers-chant_getting-mauled-by-the-tigers.m4a"


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


def bp(x, lo, hi, order=4): return signal.sosfilt(signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x, axis=0)
def lp(x, f, order=4): return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x, axis=0)
def hp(x, f, order=4): return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x, axis=0)


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


# ---------------------------------------------------------------- recorded clips
SFX = "../../audio/sfx/"
_CLIPS = {}


def clip(name):
    """a clip from audio/sfx as float32 (n,) or (n, 2) at 48 kHz"""
    if name not in _CLIPS:
        y, sr = sf.read(SFX + name + ".ogg", dtype="float32", always_2d=False)
        if sr != SR:
            import librosa
            y = librosa.resample(y.T, orig_sr=sr, target_sr=SR).T.astype(np.float32)
        _CLIPS[name] = y
    return _CLIPS[name].copy()


def varispeed(y, semis):
    """pitch (and length) by resampling, as with tape: + semitones = higher and shorter"""
    if abs(semis) < 1e-3: return y
    f = 2 ** (semis / 12)
    n = int(len(y) / f)
    x = np.arange(n) * f
    if y.ndim == 1: return np.interp(x, np.arange(len(y)), y).astype(np.float32)
    return np.stack([np.interp(x, np.arange(len(y)), y[:, c]) for c in range(y.shape[1])], 1).astype(np.float32)


def looped(name, dur, xf=1.5):
    """an ambience clip looped with crossfades to dur seconds"""
    y = clip(name)
    n, k = int(dur * SR), int(xf * SR)
    out = y[:0]
    while len(out) < n:
        if len(out) == 0: out = y.copy(); continue
        r = np.linspace(0, 1, k)[:, None] if y.ndim == 2 else np.linspace(0, 1, k)
        out = np.concatenate([out[:-k], out[-k:] * (1 - r) + y[:k] * r, y[k:]])
    return out[:n]


def big_boom(size=1.0, tail=None):
    """a cinematic impact: bass tom (pitched down) for the punch, gong down an octave and thunder for the body
    and tail, a touch of hall"""
    tom = varispeed(clip("tom_hit"), -5 - 2 * size)
    gong = lp(varispeed(clip("gong_big"), -12), 700, 2).astype(np.float32)
    thun = lp(clip("thunder_roll"), 380, 2).astype(np.float32)
    n = int((2.2 + 2.5 * size) * SR)
    def fit(y):
        if y.ndim == 2: y = y.mean(1)
        a = np.abs(y); i0 = int(np.argmax(a > 0.25 * a.max()))       # start on the attack, not the lead-in
        y = y[max(0, i0 - int(0.004 * SR)):][:n]; return np.pad(y, (0, n - len(y)))
    t = np.arange(n) / SR
    body = at_level(fit(tom), -12) + at_level(fit(gong), -20) * 0.9 * size + at_level(fit(thun), -22) * size
    body *= np.exp(-t / (0.9 + 1.2 * size))
    wet = convolve_st(body, reverb_ir(2.2 + size, 3500, 0.02, 21))[:n]
    out = np.stack([body, body], 1) * 0.85 + wet * 0.28
    if tail is not None:                                   # a short tail (reverb included): out of the way
        out *= np.exp(-np.maximum(0, t - 0.1) / tail)[:, None]     # before the next line starts
    return out


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


def room(x, seconds=2.4, mix=0.25, seed=7):
    ir = reverb_ir(seconds, 5000, 0.02, seed)
    n = len(x)
    return (x if x.ndim == 2 else np.stack([x, x], 1)) * 0.85 + convolve_st(x, ir)[:n] * mix


# ---------------------------------------------------------------- score
def doc_score():
    """over the MKM Stadium: low strings swell and a solemn piano, deadly serious... and stopped dead"""
    t_end = m("music_stop")
    n = int((t_end + 0.01) * SR)
    x = np.zeros((n, 2), np.float32)
    def put(y, t, g=1.0, pan=0.0):
        y = np.asarray(y, np.float32)
        if y.ndim == 1:
            gl, gr = math.cos((pan + 1) * math.pi / 4) * 1.4142, math.sin((pan + 1) * math.pi / 4) * 1.4142
            y = np.stack([y * gl, y * gr], 1)
        i = int(t * SR); j = min(n, i + len(y))
        if i < n: x[i:j] += y[:j - i] * g
    put(strings([note("D2"), note("A2"), note("D3")], t_end + 1.0, 0.9, 0.1, 900), 0.0, 0.9)
    put(strings([note("F3"), note("A3"), note("D4")], t_end + 0.5, 1.4, 0.1, 1400), 0.8, 0.4)     # the swell
    for tn, nm in ((0.25, "A4"), (0.95, "F4"), (1.65, "D4"), (2.35, "E4"), (2.95, "F4")):
        put(piano_note(note(nm), 2.0, 0.9), tn, 0.8, pan=0.2)
        put(piano_note(note(nm) / 2, 2.0, 0.5), tn, 0.6, pan=-0.2)
    y = room(x)[:n]
    y[-int(0.005 * SR):] *= np.linspace(1, 0, int(0.005 * SR))[:, None]      # stopped dead
    return y


def hopeful(dur):
    """'Good news': a little bright piano and strings, rising... (cut off by the caller)"""
    n = int(dur * SR)
    x = np.zeros((n, 2), np.float32)
    ch = strings([note("C4"), note("E4"), note("G4")], dur + 0.5, 0.35, 0.1, 2400)[:n]
    x += np.stack([ch, ch], 1) * 0.45
    for tn, nm in ((0.0, "C5"), (0.22, "E5"), (0.44, "G5"), (0.66, "C6"), (0.9, "E5"), (1.1, "G5")):
        if tn < dur:
            y = piano_note(note(nm), 1.4, 0.8)
            i = int(tn * SR); j = min(n, i + len(y)); x[i:j] += y[:j - i, None]
    return room(x, 1.8, 0.22, 9)[:n]


def title_sting(dur):
    """the chord under the title boom"""
    n = int(dur * SR)
    ch = strings([note("D2"), note("A2"), note("D3"), note("F3"), note("A3")], dur + 1.0, 0.03, 0.5, 2200)[:n]
    y = np.stack([ch, ch], 1)
    return y + convolve_st(ch, reverb_ir(3.0, 4000, 0.03, 3))[:n] * 0.3


_CH = {}


def chant():
    """the supplied Hull fans' chant (8.4 s, 3 lines) at 48 kHz stereo"""
    if "y" not in _CH:
        import librosa
        y, _ = librosa.load(CHANT, sr=SR, mono=False)
        y = y.T if y.ndim == 2 else np.stack([y, y], 1)
        _CH["y"] = y.astype(np.float32)
    return _CH["y"].copy()


# ---------------------------------------------------------------- layers
def dialogue(bus):
    room_s = reverb_ir(0.5, 5600, 0.006, 11)                 # the tiled dressing room
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
            bus.add(convolve_st(y, room_s), v["start"], db(-18))


def bed(bus, name, a, b, level, lowpass=None, highpass=None, fin=0.004, fout=0.004, gain_fn=None):
    """an ambience clip looped from a to b at an RMS level (dB), hard cuts by default"""
    y = looped(name, b - a)
    if lowpass: y = lp(y, lowpass, 2).astype(np.float32)
    if highpass: y = hp(y, highpass, 2).astype(np.float32)
    y = at_level(y, level)
    e = fade(len(y), fin, fout)
    if gain_fn is not None: e = e * gain_fn(a + np.arange(len(y)) / SR)
    bus.add(y * (e[:, None] if y.ndim == 2 else e), a)


def ambience(bus):
    # outside the MKM Stadium: wind, the road, the crowd arriving in the distance
    t1 = m("cut_room_wide")
    bed(bus, "wind", 0.0, t1, -46, lowpass=1800, fin=0.6)
    bed(bus, "street_distant", 0.0, t1, -48, lowpass=1500, fin=0.6)
    bed(bus, "crowd_large", 0.0, t1, -40, lowpass=1600, fin=0.6)
    # before the game: air-conditioning, the stadium filling up, muffled through the walls
    a, b = m("cut_room_wide"), m("cut_score")
    bed(bus, "room_tone_hvac", a, b, -48, lowpass=5000)
    bed(bus, "crowd_large", a, b, -44, lowpass=420)
    # the match: the crowd under the narrator's corners (the score card itself: a burst, then total silence)
    a, b = ls("nar_knew") - 0.05, m("chant")
    bed(bus, "crowd_large", a, b, -34, lowpass=6000)
    # after the game: a dead-quiet room, the ventilation and nothing else
    a, b = m("cut_post_wide"), m("cut_black")
    bed(bus, "room_tone_hvac", a, b, -51, lowpass=4000)


def music(bus):
    bus.add(at_level(doc_score(), -23), 0.0)
    # "Good news": the hopeful music starts as they look up... and dies on "Ipswich"
    a, b = ls("sh_good_news") + 0.35, wt("sh_ipswich", "ipswich") + 0.04
    hp_ = hopeful(b - a + 0.1)[:int((b - a) * SR)]
    hp_ *= fade(len(hp_), 0.12, 0.05)[:, None]
    bus.add(at_level(hp_, -29), a)
    # the title: the strings chord under the boom, until the chant takes over
    ch = title_sting(m("cut_tigers") - m("cut_title") + 0.3)
    ch[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))[:, None]
    bus.add(at_level(ch, -27), m("cut_title"))


def ev(bus, name, t, level, pan=0.0, semis=0.0, lowpass=None, highpass=None, dur=None):
    y = varispeed(clip(name), semis)
    if y.ndim == 2: y = y.mean(1)
    if dur: y = y[:int(dur * SR)] * fade(min(len(y), int(dur * SR)), 0.0, 0.04)
    if lowpass: y = lp(y, lowpass, 2).astype(np.float32)
    if highpass: y = hp(y, highpass, 2).astype(np.float32)
    bus.add(at_level(y, level), t, 1.0, pan)


def steps(bus, t0, t1, level, pace=0.28, pan=0.0, pan_to=None, lowpass=None):
    """footsteps on the dressing-room floor, one every `pace` s from t0 to t1 (alternating recorded steps)"""
    k, t = 0, t0
    while t < t1:
        p = pan if pan_to is None else pan + (pan_to - pan) * (t - t0) / max(1e-3, t1 - t0)
        ev(bus, "step_a" if k % 2 == 0 else "step_b", t, level + (0 if k % 2 else -1.5), pan=p, lowpass=lowpass,
           semis=-0.5 + 0.4 * (k % 3))
        k += 1; t += pace


def foley(bus):
    """every cue is keyed to the picture: who moves, when (see perf.py / direction.py for the same marks)"""
    # into the dressing room: a hard cut, the room settles
    ev(bus, "creak_small", m("cut_room_wide") + 1.3, -46, pan=-0.3, semis=-2)
    # Steve and his clipboard
    ev(bus, "paper_short", m("cut_sh1") + 0.02, -42, pan=0.1)
    ev(bus, "page_turn", m("cut_sh5") + 0.03, -40)
    ev(bus, "page_turn", m("cut_sh6") + 0.02, -39)
    # Bruno's look into the lens, the players turning to Carrick
    ev(bus, "creak_small", m("cut_br1") + 0.1, -46, semis=-1)
    ev(bus, "creak_small", m("cut_wide2") + 0.25, -44, pan=-0.3, semis=-2)
    ev(bus, "creak_short", m("cut_wide2") + 0.55, -46, pan=0.25, semis=-4)
    ev(bus, "cloth_c", m("cut_wide2") + 0.35, -46)
    # the clap, hard; then off he goes: footsteps across the room, nobody else moves
    ev(bus, "clap_single", m("clap"), -22)
    ev(bus, "cloth_a", m("clap") - 0.05, -40)
    steps(bus, m("cut_walk") + 0.05, m("cut_sh3") + 0.25, -35, pan=0.2, pan_to=0.8)
    # at the store cupboard: he walks up, stops dead... turns... and walks back the other way
    steps(bus, m("cut_ck7") + 0.02, m("cut_ck7") + 0.34, -33)
    ev(bus, "cloth_e", m("cut_ck7") + 0.66, -42)
    steps(bus, m("cut_ck7") + 1.16, m("cut_score"), -33, pan=0.0, pan_to=-0.6)
    # SMASH CUT: full time. The whistle, a burst of the home end... then nothing
    ev(bus, "tom_hit", m("cut_score"), -26, semis=-5, lowpass=900)
    ev(bus, "whistle_ref", m("cut_score") + 0.02, -27, dur=0.95)
    bus.add(at_level(crowd_burst(0.7), -27), m("cut_score") + 0.04)
    # the corners: the kick; the goals: the roar
    for n, tc in ((1, ls("nar_knew") - 0.05 + 0.55), (2, m("flash2") - 0.02 + 0.12)):
        ev(bus, "ball_kick", tc, -30, pan=-0.4)
    bus.add(at_level(crowd_burst(1.6, roar=True), -24), we("nar_knew", "coming") - 0.35)
    bus.add(at_level(crowd_burst(1.2, roar=True), -24), m("chant"))
    # after the game: the silence is the sound. Harry's hand, the bench as Bruno gets up, Kobbie's folded arms
    ev(bus, "cloth_b", m("cut_mg2") + 0.05, -42)
    ev(bus, "cloth_f", m("cut_mg5") + 0.25, -46)
    ev(bus, "creak_long", m("cut_br5") + 0.06, -36, semis=-4)
    ev(bus, "cloth_d", m("cut_br5") + 0.12, -40)
    ev(bus, "creak_small", m("cut_br6") + 0.02, -44, semis=-2)
    ev(bus, "creak_short", m("cut_hope") + 0.02, -44, pan=-0.2, semis=-3)             # they all look up
    ev(bus, "creak_small", m("cut_turn") + 0.15, -44, pan=0.3, semis=-2)              # ...and turn to Carrick
    # Carrick walks straight out; a door shuts behind him while Bruno watches
    steps(bus, m("ck_exit") + 0.04, m("cut_br7") + 0.4, -36, pan=0.3, pan_to=0.9, lowpass=5000)
    ev(bus, "door_shut", m("cut_br7") + 0.42, -33, pan=0.8, lowpass=3500)
    # the title: the big boom
    bus.add(at_level(big_boom(1.0), -16), m("cut_title"))


def crowd_burst(dur, roar=False):
    """the home crowd: a burst of cheering (a roar for a goal), from the crowd recording and applause"""
    n = int(dur * SR)
    c = looped("crowd_large", dur + 0.5)[:n]
    c = c if c.ndim == 2 else np.stack([c, c], 1)
    a = clip("applause_big")
    a = (a if a.ndim == 2 else np.stack([a, a], 1))[:n]
    a = np.pad(a, ((0, n - len(a)), (0, 0)))
    t = np.arange(n) / SR
    env = np.minimum(1, t / (0.06 if roar else 0.03)) * np.exp(-np.maximum(0, t - (0.35 if roar else 0.12)) / (0.9 if roar else 0.25))
    y = (at_level(c, -20) * (1.6 if roar else 1.0) + at_level(a, -22)) * env[:, None]
    y *= fade(n, 0.0, 0.06)[:, None]
    return room(y, 2.8, 0.3, 17)[:n]


def fans(bus):
    """the Hull fans' chant: the first two lines on the second goal, cut dead on the cut back inside; the last line
    over the Tigers ending, cut hard at the very end"""
    y = chant()
    a, b = m("chant"), m("cut_post_wide")
    c1 = y[:int(min(5.55, b - a) * SR)].copy()
    c1[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))[:, None]
    bus.add(at_level(c1, -19), a)
    c2 = y[int(5.2 * SR):].copy()
    c2 = c2[:int((TOTAL - m("cut_tigers")) * SR)]
    bus.add(at_level(c2, -18), m("cut_tigers"))


def main():
    dlg, amb, mus, fx, crowd = Bus(), Bus(), Bus(), Bus(), Bus()
    dialogue(dlg); ambience(amb); music(mus); foley(fx); fans(crowd)
    # the music ducks under the dialogue
    env = np.abs(dlg.x.mean(1))
    env = lp(env, 6, 1)
    duck = 1.0 / (1.0 + 7.0 * np.clip(env / db(-26), 0, 1))
    duck = np.clip(duck, db(-7), 1.0).astype(np.float32)
    mix = dlg.x + amb.x + mus.x * duck[:, None] + fx.x + crowd.x
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
