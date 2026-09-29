"""The soundtrack: the dialogue edit, real recorded ambience and foley, the intro music and the title boom.

  - dialogue: every line at its timeline position, levelled; a small-room reverb in the boardroom, a more open one
    in Monaco; the narrator dry and close
  - music: brooding strings and piano over the Carrington intro only; it ends on a big cinematic boom as the
    film cuts into the boardroom (no music under the meeting); a smug Riviera lounge loop in Monaco, hard-cut on
    the smash back; the title boom, cut hard at the very end so the Short loops
  - ambience and foley: real recordings (BigSoundBank, CC0, trimmed into ../../audio/sfx by tools/get_sfx.py):
    rain, wind and distant traffic outside; air-conditioning and a muffled city in the boardroom; a marina and
    gentle sea in Monaco; chair creaks, cloth on every gesture, pen clicks, Jim's paperwork, a mug set down.
    No synthetic whooshes or beeps: cuts are hard cuts, and the two big moments get a layered boom (bass tom +
    gong and thunder pitched down)
python3 audio.py -> build/episode_audio.wav (48 kHz stereo)"""
import json, math, numpy as np, soundfile as sf
from scipy import signal
from timeline import TL
from direction import m, ls, le

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


# ---------------------------------------------------------------- score
def doc_score():
    """the intro only: low strings swell and a solemn piano under the Carrington exterior and the narrator,
    ending exactly on the cut into the boardroom (where the boom lands)"""
    t_hit = m("cut_wide")
    n = int((t_hit + 0.01) * SR)
    x = np.zeros((n, 2), np.float32)
    def put(y, t, g=1.0, pan=0.0):
        y = np.asarray(y, np.float32)
        if y.ndim == 1:
            gl, gr = math.cos((pan + 1) * math.pi / 4) * 1.4142, math.sin((pan + 1) * math.pi / 4) * 1.4142
            y = np.stack([y * gl, y * gr], 1)
        i = int(t * SR); j = min(n, i + len(y))
        if i < n: x[i:j] += y[:j - i] * g
    put(strings([note("D2"), note("A2"), note("D3")], t_hit + 0.4, 1.2, 0.1, 900), 0.0, 0.9)
    put(strings([note("F3"), note("A3")], t_hit - 1.0, 1.0, 0.1, 1300), 1.2, 0.35)       # the swell into the cut
    for tn, nm in ((0.3, "A4"), (1.1, "F4"), (1.9, "D4"), (2.55, "E4")):
        put(piano_note(note(nm), 2.0, 0.9), tn, 0.8, pan=0.2)
        put(piano_note(note(nm) / 2, 2.0, 0.5), tn, 0.6, pan=-0.2)
    ir = reverb_ir(2.4, 5000, 0.02, 7)
    wet = convolve_st(x, ir)[:n]
    y = x * 0.85 + wet * 0.25
    y[-int(0.006 * SR):] *= np.linspace(1, 0, int(0.006 * SR))[:, None]      # out on the cut
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
    """the chord under the title boom"""
    n = int(dur * SR)
    ch = strings([note("D2"), note("A2"), note("D3"), note("F3"), note("A3")], dur + 1.0, 0.03, 0.5, 2200)[:n]
    y = np.stack([ch, ch], 1)
    return y + convolve_st(ch, reverb_ir(3.0, 4000, 0.03, 3))[:n] * 0.3


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


def bed(bus, name, a, b, level, lowpass=None, fin=0.004, fout=0.004, gain_fn=None):
    """an ambience clip looped from a to b at an RMS level (dB), hard cuts by default"""
    y = looped(name, b - a)
    if lowpass:
        y = (lp(y, lowpass, 2) if y.ndim == 1 else np.stack([lp(y[:, 0], lowpass, 2), lp(y[:, 1], lowpass, 2)], 1)).astype(np.float32)
    y = at_level(y, level)
    e = fade(len(y), fin, fout)
    if gain_fn is not None: e = e * gain_fn(a + np.arange(len(y)) / SR)
    bus.add(y * (e[:, None] if y.ndim == 2 else e), a)


def ambience(bus):
    # outside Carrington: rain on the concrete, wind, traffic in the distance
    t1 = m("cut_wide")
    bed(bus, "rain_concrete", 0.0, t1, -41, fin=0.5)
    bed(bus, "wind", 0.0, t1, -45, lowpass=1800, fin=0.8)
    bed(bus, "street_distant", 0.0, t1, -47, lowpass=1500, fin=0.8)
    # the boardroom: air-conditioning and the city muffled through the glass; it drains away behind Bruno's
    # last close-up, and stops dead on the cut to black
    quiet = lambda tt: 1 - 0.85 * np.clip((tt - m("cut_br8") - 0.2) / 1.2, 0, 1)
    for a, b in ((m("cut_wide"), m("cut_monaco")), (m("cut_ck8"), m("cut_black"))):
        bed(bus, "room_tone_hvac", a, b, -47, lowpass=5000, gain_fn=quiet)
        bed(bus, "city_through_window", a, b, -55, lowpass=900, gain_fn=quiet)
    # Monaco: the marina (boats, water against the pontoons) and a gentle sea
    a, b = m("cut_monaco"), m("cut_ck8")
    bed(bus, "marina", a, b, -39)
    bed(bus, "sea_gentle", a, b, -45, lowpass=4000)


def music(bus):
    bus.add(at_level(doc_score(), -24), 0.0)
    a, b = m("cut_monaco"), m("cut_ck8")
    lg = lounge(b - a)
    lg[-int(0.005 * SR):] *= np.linspace(1, 0, int(0.005 * SR))[:, None]           # smash cut: gone
    bus.add(at_level(lg, -32), a)
    # the title: the strings chord under the boom, cut hard at the very end (the Short loops)
    ch = title_sting(TOTAL - m("cut_title") + 0.5)
    bus.add(at_level(ch, -27), m("cut_title"))


def ev(bus, name, t, level, pan=0.0, semis=0.0, lowpass=None, highpass=None):
    y = varispeed(clip(name), semis)
    if y.ndim == 2: y = y.mean(1)
    if lowpass: y = lp(y, lowpass, 2).astype(np.float32)
    if highpass: y = hp(y, highpass, 2).astype(np.float32)
    bus.add(at_level(y, level), t, 1.0, pan)


def words(lid):
    return {w["w"]: TL["lines"][lid]["start"] + w["s"] for w in LINES[lid]["words"]}


def foley(bus):
    """every cue is keyed to the picture: who moves, when (see perf.py / direction.py for the same marks)"""
    # the cut into the boardroom lands on a boom, and the room settles
    bus.add(at_level(big_boom(0.6, tail=0.12), -19), m("cut_wide"))
    ev(bus, "creak_small", m("cut_wide") + 1.1, -44, pan=0.3, semis=-2)
    # Jason, pleased with himself: a pen click right after "we bought three midfielders"
    ev(bus, "pen_click_a", le("js_bought") + 0.08, -33, pan=0.05)
    # Carrick's close-up: the tiny head move is his chair
    ev(bus, "creak_short", m("cut_ck2") + 0.18, -45, semis=-3)
    # Omar's explaining hands, Jason's three fingers going up
    ev(bus, "cloth_a", ls("om_yeah_but") + 0.02, -38)
    ev(bus, "cloth_b", m("cut_js3") - 0.04, -36, pan=-0.1)
    # Carrick looks into the lens: nothing but the room
    ev(bus, "creak_small", m("cut_br1") + 0.1, -44, semis=-1)                 # Bruno turning
    ev(bus, "cloth_e", m("cut_br1") + 0.5, -46)
    ev(bus, "creak_mid", m("ck_lean") + 0.02, -38, semis=-3)                   # Carrick leans in
    ev(bus, "cloth_c", m("ck_lean") + 0.08, -41)
    ev(bus, "cloth_e", m("cut_br2") - 0.03, -35, semis=2)                      # the whip round to Bruno
    ev(bus, "creak_short", m("cut_br2") + 0.02, -42, semis=-1)
    ev(bus, "cloth_d", ls("om_efficient") + 0.1, -39, pan=0.1)                 # Omar gestures at Bruno
    ev(bus, "cloth_a", ls("br_crossing") + 0.18, -36, semis=2)                 # Bruno throws a hand out
    ev(bus, "cloth_f", le("js_bruno") + 0.04, -41)                             # Jason's pointing arm (after the word)
    ev(bus, "creak_short", ls("br_me") + 0.05, -42, semis=-2)                  # "ME?"
    ev(bus, "cloth_e", m("cut_ck6") + 0.05, -46)                               # Carrick's breath
    ev(bus, "creak_long", m("cut_br6") + 0.12, -38, semis=-4)                  # Bruno sinks back into his chair
    ev(bus, "cloth_b", m("cut_br6") + 0.2, -44)
    # Jim's paperwork: handled, then lowered
    ev(bus, "paper_handle", m("cut_jr1") - 0.05, -42, pan=-0.1)
    ev(bus, "paper_lower", ls("jr_bigger_issues") - 0.45, -38, pan=-0.1)
    # everyone turns to look at Jim
    ev(bus, "creak_small", m("cut_wide2") + 0.05, -42, pan=0.3, semis=-2)
    ev(bus, "creak_short", m("cut_wide2") + 0.28, -44, pan=-0.2, semis=-4)
    ev(bus, "cloth_c", m("cut_wide2") + 0.12, -44, pan=0.1)
    ev(bus, "creak_small", m("cut_br7") + 0.1, -45, semis=-3)                  # Bruno turns slowly
    # the smash cut back from Monaco: a dull punch, and Carrick puts his mug down
    ev(bus, "tom_hit", m("cut_ck8"), -27, semis=-6, lowpass=1100)
    ev(bus, "cup_down", m("cut_ck8") + 0.12, -33, pan=-0.05)
    ev(bus, "pen_click_b", le("js_no_left_back") + 0.06, -34, pan=0.05)        # Jason, firm
    ev(bus, "cloth_b", m("cut_execs") + 0.08, -43)                              # the three of them nod
    ev(bus, "pen_click_c", le("jr_good_meeting") + 0.12, -36, pan=0.2)          # Jim: meeting over
    ev(bus, "creak_small", le("om_positions") + 0.1, -44, semis=-2)              # Omar settles after "No."
    ev(bus, "creak_short", m("cut_br9") + 0.05, -45, semis=-3)                   # Bruno shifts for "Brilliant"
    # the title: the big boom
    bus.add(at_level(big_boom(1.0), -16), m("cut_title"))


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
