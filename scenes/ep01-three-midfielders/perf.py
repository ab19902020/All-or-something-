"""The acting: per character, per frame face and body state, from the dialogue and the script's beats.

state(who, t, resolve) -> dict(vis, amp, blink, lookx, looky, brow, smile, tilt, nod, turn, lean, sink)
  * lip sync  - phones -> the mouth shapes (face.py), a frame early, closures held >= 2 frames; the jaw opens with
                the loudness of the line
  * blinks    - every 2.2-4.8 s, never in sync between characters, plus the blinks the script asks for
  * eyes      - on whoever is talking (a beat late), on the person being talked to while talking, or where a cue
                sends them (the lens, the paperwork); `resolve` turns a target into a screen direction for the shot
  * face      - brows / smile from each line's delivery tag, easing in and out
  * head      - small nods on the stressed words, slow idle drift, the nods and turns the script names
  * body      - Carrick leans in, Bruno sinks back"""
import json, math, numpy as np, soundfile as sf
import face
from timeline import TL
from direction import m, ls, le

FPS = 30
N = int(math.ceil(TL["total"] * FPS)) + 2
L = json.load(open("build/lines.json"))
WHO = ["ck", "js", "om", "br", "jr"]
SPK = {"carrick": "ck", "jason": "js", "omar": "om", "bruno": "br", "jim": "jr", "narrator": "nar"}

# delivery tag, who the line is said to, stressed words (small nods)
META = {
    "ck_two_things": ("calm", "js", ["two", "left", "striker"]),
    "js_sorted": ("confident", "ck", ["sorted"]),
    "ck_brilliant": ("relieved", "js", ["brilliant"]),
    "js_bought": ("casual", "ck", ["three"]),
    "ck_i_said": ("confused", "js", ["left", "striker"]),
    "om_yeah_but": ("obvious", "ck", ["three"]),
    "js_three_things": ("explaining", "ck", ["three", "two", "technically", "won"]),
    "om_positions": ("honest", "ck", ["positions", "no"]),
    "br_you_bought": ("stunned", "js", ["three"]),
    "ck_not_complaining": ("diplomatic", "js", ["complaining", "love", "great"]),
    "ck_whos_scoring": ("deadpan", "js", ["actually", "goals"]),
    "om_bruno": ("calm", "ck", []),
    "br_sorry_what": ("confused", "om", ["what"]),
    "om_efficient": ("matter", "ck", ["here", "technically", "efficient"]),
    "br_crossing": ("frustrated", "om", ["crossing", "ball"]),
    "js_bruno": ("confident", "br", ["bruno"]),
    "br_me": ("angry", "js", ["me", "corner"]),
    "br_midfielder": ("disbelieving", "js", ["midfielder"]),
    "js_perfect": ("deadpan_happy", "br", ["perfect", "loads"]),
    "br_brilliant": ("deadpan", "js", ["brilliant", "absolutely"]),
    "ck_left_back": ("concerned", "js", ["left"]),
    "js_luke": ("casual", "ck", ["luke"]),
    "ck_luke": ("disbelieving", "js", ["luke", "whole"]),
    "js_next_question": ("awkward", "ck", ["next"]),
    "jr_bigger_issues": ("detached", "ck", ["bigger", "britain"]),
    "br_monaco": ("deadpan", "jr", ["monaco"]),
    "jr_yes_monaco": ("defensive", "cam", ["yes", "monaco"]),
    "jr_perspective": ("smug", "cam", ["outside", "perspective"]),
    "ck_no_striker": ("sigh", "om", ["striker"]),
    "om_no_striker": ("confident", "ck", ["striker"]),
    "ck_no_left_back": ("deadpan", "js", ["left"]),
    "js_no_left_back": ("firm", "ck", ["left"]),
    "ck_but_three": ("confused", "js", ["three"]),
    "js_three_mids": ("proud", "ck", ["three"]),
    "om_three_mids": ("proud", "ck", ["three"]),
    "jr_good_meeting": ("smug", "ck", ["good"]),
    "br_sunshine": ("regretful", "cam", ["sunshine"]),
    "br_saudi": ("resigned", "cam", ["saudi"]),
}
# delivery tag -> (brow: + raised / - lowered, smile: + / - frown)
TAG = dict(honest=(0.35, -0.05), calm=(0.05, 0.0), confident=(0.15, 0.35), relieved=(0.5, 0.55), casual=(0.1, 0.3), confused=(0.8, -0.15),
           obvious=(0.45, 0.12), explaining=(0.4, 0.2), stunned=(1.0, -0.25), diplomatic=(0.3, 0.1),
           deadpan=(-0.12, -0.05), matter=(0.25, 0.1), frustrated=(-0.55, -0.3), angry=(-0.95, -0.4),
           disbelieving=(0.85, -0.2), deadpan_happy=(0.2, 0.45), concerned=(0.5, -0.3), awkward=(0.4, 0.15),
           detached=(-0.05, 0.0), defensive=(0.4, -0.12), smug=(-0.25, 0.6), sigh=(-0.1, -0.2), firm=(-0.3, 0.0),
           proud=(0.25, 0.5), regretful=(0.35, -0.35), resigned=(0.2, -0.28))
BASE = dict(ck=(0.1, 0.0), js=(0.22, 0.32), om=(0.0, 0.0), br=(-0.3, -0.1), jr=(-0.1, 0.0))


def sm(x):
    x = np.clip(x, 0.0, 1.0); return x * x * (3 - 2 * x)


def ramp(t, a, b, fin=0.15, fout=0.3):
    """0 -> 1 over [a, a + fin], 1 until b, back to 0 over [b, b + fout]"""
    return float(sm((t - a) / max(fin, 1e-3)) * (1 - sm((t - b) / max(fout, 1e-3))))


# ---------------------------------------------------------------- lip sync: per-frame visemes and jaw amplitude
def _speech():
    ev = {w: [] for w in WHO}
    amp = {w: np.zeros(N, np.float32) for w in WHO}
    talking = {w: np.zeros(N, bool) for w in WHO}
    for lid, v in TL["lines"].items():
        who = SPK[v["speaker"]]
        if who not in ev or L[lid].get("missing"): continue
        ev[who] += face.viseme_events(L[lid]["phones"], v["start"])
        y, sr = sf.read(f"build/lines/{lid}.wav", dtype="float32")
        if y.ndim > 1: y = y.mean(1)
        hop = sr // FPS
        rms = np.array([np.sqrt(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y), hop)])
        if L[lid].get("missing"): rms = np.full(len(rms), 0.08)
        ref = np.percentile(rms, 90) + 1e-6
        a = np.clip(0.55 + 0.55 * rms / ref, 0.5, 1.15)
        f0 = int(round(v["start"] * FPS))
        for k, val in enumerate(a):
            if 0 <= f0 + k < N: amp[who][f0 + k] = val
        talking[who][max(0, f0):min(N, int(round(v["end"] * FPS)))] = True
    vis = {w: face.track(ev[w], N, FPS) for w in WHO}
    for w in WHO: amp[w][amp[w] == 0] = 1.0
    return vis, amp, talking


VIS, AMP, TALK = _speech()

# ---------------------------------------------------------------- blinks
FORCED = {
    "ck": [m("cut_ck2") + 0.14, m("cut_ck5") + 0.2, m("cut_ck7") + 0.12, m("cut_ck10") + 0.22],
    "js": [m("cut_js_nod") + 0.3, ls("js_next_question") - 0.12],
    "om": [m("cut_om2") + 0.1],
    "br": [m("cut_br8") + 0.25, m("br_pause") + 0.1],
    "jr": [m("cut_jr2") + 0.12, m("cut_monaco") + 0.2],
}
# no automatic blinks in these holds (a look into the lens, a freeze)
NOBLINK = {
    "ck": [(m("cut_ck3") + 0.2, m("cut_br1"))],
    "js": [(m("cut_js7"), ls("js_next_question") - 0.2)],
    "br": [(m("cut_br1") + 0.8, ls("br_you_bought") + 0.3), (m("cut_br8") + 0.5, m("br_pause"))],
    "jr": [],
    "om": [],
}


def _blinks():
    out = {}
    for k, w in enumerate(WHO):
        rng = np.random.default_rng(100 + k)
        t, ts = rng.uniform(0.4, 2.5), []
        while t < TL["total"]:
            if not any(a <= t <= b for a, b in NOBLINK[w]): ts.append(t)
            t += rng.uniform(2.2, 4.8)
        ts += FORCED[w]
        ts.sort()
        clean = []
        for x in ts:                                        # forced blinks win over nearby automatic ones
            if clean and x - clean[-1] < 0.5:
                if x in FORCED[w]: clean[-1] = x
                continue
            clean.append(x)
        out[w] = clean
    return out


BLINKS = _blinks()
BLINK_SHAPE = [0.45, 0.95, 1.0, 0.7, 0.3]


def blink(w, t):
    f = t * FPS
    for b in BLINKS[w]:
        k = f - b * FPS
        if 0 <= k < len(BLINK_SHAPE):
            i = int(k); u = k - i
            nx = BLINK_SHAPE[i + 1] if i + 1 < len(BLINK_SHAPE) else 0.0
            return BLINK_SHAPE[i] * (1 - u) + nx * u
    return 0.0


# ---------------------------------------------------------------- where each one looks
def speaker_at(t, lag=0.2):
    """the character whose line is current (or was the last one) at time t - lag"""
    best = None
    for lid, v in TL["lines"].items():
        who = SPK[v["speaker"]]
        if who not in WHO: continue
        if v["start"] + lag <= t: best = (who, lid)
    return best


# explicit gaze cues: (t0, t1, target); targets: a character, "cam", "down", "downleft", ("dir", lx, ly, turn)
GAZE = {
    "ck": [(m("cut_ck3") + 0.05, m("cut_br1"), "cam"),
           (m("cut_ck5"), m("cut_br5"), ("dir", 0.35, 0.35, 0.08)),
           (m("cut_ck10"), m("cut_ck10") + 0.22, "jr"), (m("cut_ck10") + 0.22, m("cut_ck10") + 0.42, "js"),
           (m("cut_ck10") + 0.42, ls("ck_but_three") + 0.1, "om"),
           (m("cut_wide2"), m("cut_br7"), "jr")],
    "js": [(m("cut_js7") + 0.3, m("cut_js7") + 0.58, "om"), (m("cut_js7") + 0.58, ls("js_next_question") + 0.2, "cam"),
           (m("cut_wide2"), m("cut_br7"), "jr")],
    "om": [(ls("om_efficient"), le("om_efficient"), "br"), (m("cut_wide2"), m("cut_br7"), "jr"),
           (ls("om_positions") + 0.9, ls("om_positions") + 1.35, ("dir", -0.3, 0.55, -0.05))],
    "br": [(m("cut_br1"), m("cut_br1") + 0.42, "ck"), (m("cut_br1") + 0.42, m("cut_br1") + 0.85, "js"),
           (m("cut_br1") + 0.85, ls("br_you_bought") + 0.35, "cam"),
           (m("cut_br6") + 0.1, m("cut_jr1"), ("dir", -0.25, 0.45, -0.05)),
           (m("cut_wide2"), le("br_monaco") + 0.5, "jr"),
           (m("cut_br8"), m("cut_black"), "cam")],
    "jr": [(m("cut_wide") - 0.1, m("cut_js1"), "down"), (m("cut_jr1"), ls("jr_bigger_issues") + 0.05, "down"),
           (m("cut_wide2"), m("cut_br7"), ("dir", 0.2, 0.2, 0.05)),
           (m("cut_jr2") + 1.05, m("cut_jr2") + 1.32, ("dir", -0.75, 0.1, -0.12)),   # the glitch: busted
           (m("cut_jr2") + 1.32, m("cut_monaco"), "cam"),
           (m("cut_jr2"), m("cut_monaco"), "br")],
}


def target(w, t):
    for a, b, g in GAZE[w]:
        if a <= t < b: return g
    for lid, v in TL["lines"].items():                     # talking: to the person the line is for
        if SPK[v["speaker"]] == w and v["start"] - 0.1 <= t < v["end"] + 0.25:
            return META[lid][1]
    sp = speaker_at(t)
    if sp and sp[0] != w:
        return sp[0]
    return "ck" if w != "ck" else "js"


# ---------------------------------------------------------------- brows / smile
def expression(w, t):
    b, s = BASE[w]
    for lid, v in TL["lines"].items():
        if SPK[v["speaker"]] != w: continue
        k = ramp(t, v["start"] - 0.12, v["end"], 0.15, 0.45)
        if k > 0:
            tb, ts = TAG[META[lid][0]]
            b, s = b + (tb - b) * k, s + (ts - s) * k
    for a, bb, cb, cs, fin in EXPR.get(w, []):
        k = ramp(t, a, bb, fin, 0.3)
        if k > 0: b, s = b + (cb - b) * k, s + (cs - s) * k
    return b, s


# reactions outside their own lines: (t0, t1, brow, smile, ease-in)
EXPR = {
    "ck": [(m("cut_ck3"), m("cut_br1"), 0.25, -0.05, 0.5), (m("cut_ck5"), m("cut_br5"), 0.05, -0.35, 0.1),
           (m("cut_ck7"), ls("ck_luke"), 0.35, -0.1, 0.3), (m("cut_wide2"), m("cut_br7"), 0.3, -0.1, 0.2),
           (m("cut_ck10"), ls("ck_but_three"), 0.3, -0.15, 0.2)],
    "js": [(m("cut_js_nod"), m("cut_ck4"), 0.25, 0.55, 0.1), (m("cut_js7"), ls("js_next_question"), 0.35, 0.3, 0.05),
           (m("cut_execs"), m("cut_br8"), 0.2, 0.45, 0.2)],
    "om": [(m("cut_execs"), m("cut_br8"), 0.15, 0.35, 0.2),
           (le("om_positions") - 0.1, m("cut_br1"), 0.2, 0.0, 0.2)],
    "br": [(m("cut_br1"), ls("br_you_bought"), 0.4, -0.2, 0.3), (m("cut_br6"), m("cut_jr1"), 0.1, -0.3, 0.3),
           (m("cut_br7"), m("cut_jr2"), -0.35, -0.12, 0.4),                        # the stare
           (ls("br_brilliant"), le("br_brilliant") + 0.3, -0.25, -0.18, 0.1),
           (m("cut_br8"), m("cut_black"), -0.12, -0.22, 0.3)],
    "jr": [(m("cut_jr2"), m("cut_monaco"), 0.0, 0.05, 0.3), (m("jr_nod") - 0.1, m("cut_br8"), 0.0, 0.25, 0.2)],
}


# ---------------------------------------------------------------- head motion
def _emph():
    """(t, strength) of every stressed word, per character"""
    out = {w: [] for w in WHO}
    for lid, v in TL["lines"].items():
        w = SPK[v["speaker"]]
        if w not in WHO: continue
        stress = META[lid][2]
        for wd in L[lid]["words"]:
            if wd["w"] in stress:
                out[w].append((v["start"] + wd["s"] + 0.03, 1.0))
    return out


EMPH = _emph()
# explicit nods: (t, count, amplitude %), head shakes: (t, count, amplitude)
NODS = {"js": [(m("cut_js_nod") + 0.05, 2, 4.5), (ls("js_perfect") + 0.1, 3, 3.5), (ls("js_three_mids"), 1, 3.0),
               (m("cut_execs") + 0.1, 1, 2.5)],
        "om": [(ls("om_three_mids"), 1, 3.0), (m("cut_execs") + 0.12, 1, 2.2)],
        "jr": [(m("jr_nod") + 0.05, 1, 2.6), (m("cut_execs") + 0.15, 1, 1.6)],
        "ck": [(m("cut_ck6") + 0.05, 1, -2.0)],
        "br": []}
TURN = {   # head moves that aren't eyelines: (t0, t1, turn, tilt deg)
    "ck": [(m("cut_ck2") + 0.1, ls("ck_i_said"), 0.08, -1.2)],
    "br": [(m("cut_br6") + 0.1, m("cut_jr1"), -0.05, 2.5),
           (m("cut_br7") + 0.05, m("cut_jr2"), -0.18, -1.5)],        # the slow turn to Jim
    "om": [(ls("om_yeah_but"), le("om_yeah_but"), 0.0, 3.0)],
    "js": [(m("cut_js7"), m("cut_js7") + 0.3, 0.0, 0.0)],
}


def bump(u):
    """a nod: down then back (u in 0..1)"""
    return math.sin(math.pi * min(1.0, max(0.0, u))) if 0 <= u <= 1 else 0.0


def head(w, t):
    k = WHO.index(w)
    tilt = 1.1 * math.sin(t * 0.61 + k * 1.7) + 0.5 * math.sin(t * 1.37 + k)
    nod = 0.6 * math.sin(t * 0.83 + k * 2.3)
    turn = 0.02 * math.sin(t * 0.47 + k)
    for te, s in EMPH[w]:
        nod += 2.2 * s * bump((t - te) / 0.3)
    for tn, cnt, a in NODS.get(w, []):
        for c in range(cnt):
            nod += a * bump((t - tn - c * 0.36) / 0.34)
    for a, b, tu, ti in TURN.get(w, []):
        r = ramp(t, a, b, 0.25, 0.3)
        turn += tu * r; tilt += ti * r
    if TALK[w][min(N - 1, int(t * FPS))]:
        tilt += 0.8 * math.sin(t * 2.3 + k)
    return tilt, nod, turn


def body(w, t):
    lean = sink = 0.0
    if w == "ck":
        lean = ramp(t, m("ck_lean") + 0.02, m("cut_om2"), 0.32, 0.01)
    if w == "br":
        sink = ramp(t, m("cut_br6") + 0.12, m("cut_jr1") + 5, 0.62, 0.01)
    return lean, sink


def state(w, t, resolve, t0=0.0):
    """face + body state; resolve(target) -> (lookx, looky, turn) for the current shot, which started at t0"""
    f = min(N - 1, max(0, int(round(t * FPS))))
    # eyes: stateless smoothing of the resolved targets over the last few frames (saccade ~ 60 ms, head ~ 180 ms),
    # never reaching back across the cut
    lx = ly = tu = 0.0; wsum_e = wsum_h = 0.0
    for j in range(8):
        tt = max(t0, t - j / FPS)
        gx, gy, gt = resolve(target(w, tt))
        we = math.exp(-j / 1.8); wh = math.exp(-j / 5.0)
        lx += gx * we; ly += gy * we; wsum_e += we
        tu += gt * wh; wsum_h += wh
    lx /= wsum_e; ly /= wsum_e; tu /= wsum_h
    brow, smile = expression(w, t)
    tilt, nod, turn = head(w, t)
    lean, sink = body(w, t)
    b = blink(w, t)
    if w == "br" and sink > 0: b = max(b, 0.35 * sink)          # sinking back: heavy lids
    return dict(vis=VIS[w][f], amp=float(AMP[w][f]), blink=b, lookx=lx, looky=ly, brow=brow, smile=smile,
                tilt=tilt, nod=nod, turn=turn + tu, lean=lean, sink=sink)
