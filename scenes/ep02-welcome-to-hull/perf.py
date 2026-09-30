"""The acting: per character, per frame face and body state, from the dialogue and the script's beats.

state(who, t, resolve) -> dict(vis, amp, blink, lookx, looky, brow, smile, tilt, nod, turn, lean, sink)
  * lip sync  - phones -> the mouth shapes (face.py), a frame early, closures held >= 2 frames; the jaw opens with
                the loudness of the line; nobody's mouth moves without their voice
  * blinks    - every 2.2-4.8 s, never in sync between characters, plus the blinks the script asks for
  * eyes      - on whoever is talking (a beat late), on the person being talked to while talking, or where a cue
                sends them (the lens, the board, the clipboard); `resolve` turns a target into a screen direction
  * face      - brows / smile from each line's delivery tag, easing in and out
  * head      - small nods on the stressed words, slow idle drift, the nods and turns the script names"""
import json, math, numpy as np, soundfile as sf
import face
from timeline import TL
from direction import m, ls, le, wt

FPS = 30
N = int(math.ceil(TL["total"] * FPS)) + 2
L = json.load(open("build/lines.json"))
WHO = ["ck", "sh", "br", "mg", "mn", "bs", "sl"]
SPK = {"carrick": "ck", "steve": "sh", "bruno": "br", "maguire": "mg", "mainoo": "mn", "narrator": "nar"}

# delivery tag, who the line is said to, stressed words (small nods)
META = {
    "ck_right_lads": ("motivational", "br", ["fresh", "clean"]),
    "ck_hull_come_up": ("serious", "br", ["aggressive", "physical", "set"]),
    "sh_practise": ("deadpan", "ck", ["practise", "defending"]),
    "ck_already": ("confident", "sh", ["already", "thursday"]),
    "sh_attacking": ("confused", "ck", ["attacking"]),
    "ck_same_corner": ("deadpan", "sh", ["same"]),
    "ck_kobbie": ("casual", "mn", ["bench"]),
    "mn_again": ("disbelieving", "ck", ["again"]),
    "ck_bought": ("awkward", "mn", ["bought"]),
    "mn_noticed": ("deadpan", "ck", ["noticed"]),
    "br_nine": ("frustrated", "ck", ["nine"]),
    "mg_striker": ("innocent", "ck", ["striker"]),
    "ck_come_on": ("energised", "br", ["hull", "come"]),
    "sh_wrong_door": ("deadpan", "ck", ["wrong"]),
    "ck_positives": ("positive", "br", ["positives"]),
    "br_possession": ("deadpan", "ck", ["seventy"]),
    "sh_excellent": ("encouraging", "br", ["excellent"]),
    "br_lost": ("flat", "sh", ["lost"]),
    "sh_less_excellent": ("deadpan", "br", ["less"]),
    "mg_both_goals": ("serious", "ck", ["both", "set"]),
    "ck_yep1": ("restrained", "mg", []),
    "mg_warned": ("helpful", "ck", ["warned", "before"]),
    "ck_yep2": ("quiet", "mg", []),
    "mg_twice": ("innocent", "ck", ["twice"]),
    "ck_aware": ("irritated", "mg", ["aware"]),
    "mn_came_on": ("annoyed", "ck", ["sixty", "two"]),
    "mn_plan": ("confused", "ck", ["exactly", "plan"]),
    "ck_impact": ("confident", "mn", ["impact"]),
    "mn_didnt_score": ("deadpan", "ck", ["score"]),
    "ck_nearly": ("awkward", "mn", ["nearly"]),
    "br_newly": ("frustrated", "ck", ["newly", "two", "no"]),
    "mg_shooting": ("defensive", "br", ["shooting"]),
    "br_centre_back": ("disbelieving", "mg", ["centre"]),
    "mg_nobody": ("matter", "br", ["nobody"]),
    "sh_good_news": ("positive", "br", ["good"]),
    "sh_ipswich": ("calm", "br", ["ipswich"]),
    "mn_ipswich": ("concerned", "sh", ["promoted", "well"]),
    "ck_good_meeting": ("deadpan", "cam", ["good"]),
    "br_saudi": ("exhausted", "cam", ["saudi", "still"]),
}
# delivery tag -> (brow: + raised / - lowered, smile: + / - frown)
TAG = dict(motivational=(0.3, 0.2), serious=(-0.3, -0.1), deadpan=(-0.12, -0.05), confident=(0.15, 0.3),
           confused=(0.8, -0.15), casual=(0.1, 0.25), disbelieving=(0.85, -0.2), awkward=(0.4, 0.15),
           frustrated=(-0.55, -0.3), innocent=(0.55, 0.1), energised=(0.45, 0.35), positive=(0.35, 0.3),
           encouraging=(0.45, 0.45), flat=(-0.2, -0.15), restrained=(-0.05, -0.1), helpful=(0.45, 0.15),
           quiet=(-0.35, -0.2), irritated=(-0.6, -0.25), annoyed=(-0.4, -0.25), defensive=(0.4, -0.12),
           matter=(0.25, 0.05), calm=(0.05, 0.05), concerned=(0.5, -0.3), exhausted=(0.2, -0.3))
BASE = dict(ck=(0.1, 0.0), sh=(-0.15, -0.05), br=(-0.3, -0.1), mg=(0.0, -0.05), mn=(0.05, 0.05), bs=(0.0, 0.1),
            sl=(0.0, 0.1))
# a drawing's own mouth: Kobbie's sheet has him smiling, so everything he does is played a notch straighter
SMILE_BIAS = dict(mn=-0.7)


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
    "ck": [m("cut_ck3") + 0.62, m("cut_ck5") + 0.05, m("cut_ck9") + 0.1, m("cut_ck13") + 0.75, m("cut_ck11") + 0.12],
    "sh": [m("cut_sh1") + 0.3, m("cut_sh5") + 0.08, m("cut_sh7") + 0.3],
    "br": [m("cut_br3") + 0.05, m("cut_br7") + 0.55],
    "mg": [m("cut_mg5") + 0.3, m("cut_mg1") + 0.1],
    "mn": [m("cut_mn2") + 0.1, m("cut_mn6") + 0.1],
    "bs": [], "sl": [],
}
# no automatic blinks in these holds (looks into the lens, stares)
NOBLINK = {
    "ck": [(m("cut_ck14"), le("ck_good_meeting")), (m("cut_ck3"), m("cut_ck3") + 0.5)],
    "br": [(m("cut_br1") + 0.3, m("cut_ck4")), (ls("br_saudi") - 0.3, m("cut_black"))],
    "mn": [(m("cut_mn5"), m("cut_br5"))],
    "sh": [], "mg": [(m("cut_mg4"), m("cut_ck10"))], "bs": [], "sl": [],
}


def _blinks():
    out = {}
    for k, w in enumerate(WHO):
        rng = np.random.default_rng(200 + k)
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


# explicit gaze cues: (t0, t1, target); targets: a character, "cam", "down", "board", ("dir", lx, ly, turn)
AWAY = ("dir", 0.55, 0.35, 0.15)          # Carrick pretending not to notice / looking away
GAZE = {
    "ck": [(m("cut_ck3"), m("cut_ck3") + 0.5, "board"), (m("cut_ck3") + 0.5, ls("ck_same_corner"), "sh"),
           (m("cut_ck4"), m("cut_ck4") + 0.1, "sh"),
           (m("cut_ck6"), m("clap") - 0.12, AWAY),
           (m("cut_ck11"), ls("ck_impact") - 0.08, ("dir", 0.45, -0.55, 0.12)),      # thinks it through, seriously
           (m("cut_ck13") + 0.72, m("cut_sh6"), ("dir", -0.6, 0.45, -0.2)),          # ...looks away
           (m("cut_ck14") + 0.15, m("ck_exit"), "cam"),
           (m("cut_ck7") + 0.68, m("cut_ck7") + 0.92, ("dir", 0.85, 0.05, 0.3)),        # at the door: everyone...
           (m("cut_ck7") + 0.92, m("cut_ck7") + 1.14, ("dir", 0.2, 0.05, 0.05)),
           (m("cut_post_wide"), ls("ck_positives"), ("dir", 0.0, 0.25, 0.0)),
           (m("chant") + 1.15, m("chant") + 2.55, ("dir", 0.25, 0.1, 0.05))],       # staring at the pitch
    "sh": [(m("cut_sh1"), m("cut_sh1") + 0.3, "down"),                                # clipboard -> Carrick
           (m("cut_sh3"), m("cut_sh3") + 0.35, ("dir", 0.95, 0.0, 0.4)),               # watching him go
           (m("cut_sh5"), m("cut_sh5") + 0.3, "down"),
           (m("cut_sh6"), ls("sh_good_news") + 0.1, "down"),
           (ls("sh_ipswich") - 0.1, le("sh_ipswich") - 0.3, "down")],                   # reads it off the clipboard
    "br": [(m("cut_br1"), m("cut_br1") + 0.35, "ck"), (m("cut_br1") + 0.35, m("cut_ck4"), "cam"),
           (m("cut_br3"), m("cut_br3") + 0.22, "down"),
           (m("cut_br7"), m("cut_br7") + 0.45, ("dir", 0.95, -0.1, 0.4)),             # watches Carrick go
           (m("cut_br7") + 0.45, m("cut_black"), "cam"),
           (m("cut_silence"), m("cut_br3"), "down"),
           (m("chant") + 3.85, m("cut_post_wide"), ("dir", 0.6, -0.2, 0.2))],          # shouting at the ref
    "mg": [(m("cut_mg5") + 0.25, m("cut_mn3"), ("dir", -0.35, 0.5, -0.1)),
           (m("cut_silence"), m("cut_br3"), ("dir", 0.1, 0.4, 0.0)),
           (m("chant") + 2.55, m("chant") + 3.0, ("dir", -0.6, -0.15, -0.15)),          # lost: which way...
           (m("chant") + 3.0, m("chant") + 3.45, ("dir", 0.6, -0.1, 0.15)),
           (m("chant") + 3.45, m("chant") + 3.85, ("dir", -0.2, 0.2, -0.05))],
    "mn": [(m("cut_mn3"), m("mn_look"), ("dir", -0.2, 0.3, -0.05)),                   # arms folded, not looking
           (m("cut_mn5"), m("cut_br5"), "cam"),
           (m("cut_silence"), m("cut_br3"), ("dir", -0.3, 0.3, -0.1))],
    "bs": [], "sl": [],
}
# the lineups: everyone turns to Carrick, slowly and not together (t0 offsets per character)
for w, dt in (("mn", 0.05), ("br", 0.28), ("mg", 0.45), ("bs", 0.6), ("sl", 0.7)):
    GAZE[w] += [(m("cut_wide2") + dt, m("cut_ck6"), "ck")]
for w, dt in (("mg", 0.0), ("br", 0.1), ("mn", 0.18)):
    GAZE[w] += [(m("cut_hope"), m("cut_hope") + dt, "down"), (m("cut_hope") + dt, m("cut_sh7"), "sh"),
                (m("cut_turn"), m("cut_turn") + 0.12 + 1.5 * dt, "sh"), (m("cut_turn") + 0.12 + 1.5 * dt, m("cut_ck14"), "ck")]
# the Tigers ending's reactions
T0 = m("cut_tigers")
GAZE["mg"] += [(T0, T0 + 3.3, "cam")]
GAZE["mn"] += [(T0, T0 + 3.3, ("dir", 0.5, 0.1, 0.15))]
GAZE["sh"] += [(T0, T0 + 3.3, "down")]
GAZE["br"] += [(T0, T0 + 3.3, ("dir", -0.2, 0.55, -0.05))]


def target(w, t):
    for a, b, g in GAZE[w]:
        if a <= t < b: return g
    for lid, v in TL["lines"].items():                     # talking: to the person the line is for
        if SPK[v["speaker"]] == w and v["start"] - 0.1 <= t < v["end"] + 0.25:
            return META[lid][1]
    sp = speaker_at(t)
    if sp and sp[0] != w:
        return sp[0]
    return "ck" if w != "ck" else "sh"


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
    return b, s + SMILE_BIAS.get(w, 0.0)


# reactions outside their own lines: (t0, t1, brow, smile, ease-in)
EXPR = {
    "ck": [(m("cut_ck2"), ls("ck_already"), 0.35, -0.2, 0.15),                       # slightly offended
           (m("cut_ck3"), ls("ck_same_corner"), 0.2, -0.05, 0.3),
           (m("cut_ck6"), m("clap"), 0.1, -0.1, 0.1),
           (m("cut_ck9"), le("ck_yep2") + 0.2, -0.45, -0.3, 0.25),                   # his expression tightens
           (m("cut_ck13"), m("cut_ck13") + 0.45, 0.55, 0.0, 0.12),                    # about to say something...
           (m("cut_ck13") + 0.45, m("cut_sh6"), -0.1, -0.25, 0.3),                    # ...no
           (m("cut_ck14"), ls("ck_good_meeting"), -0.05, -0.08, 0.3),
           (m("chant") + 1.15, m("chant") + 2.55, 0.2, -0.3, 0.2)],
    "sh": [(m("cut_sh3"), ls("sh_wrong_door"), -0.2, -0.05, 0.2)],
    "br": [(m("cut_br1"), m("cut_ck4"), 0.25, -0.2, 0.3),
           (m("cut_br7"), m("cut_black"), 0.1, -0.3, 0.4),
           (m("chant") + 3.85, m("cut_post_wide"), -0.9, -0.4, 0.1),
           (T0, T0 + 3.3, 0.3, -0.35, 0.1)],
    "mg": [(m("cut_mg2") - 0.1, ls("mg_both_goals"), 0.4, 0.0, 0.2),
           (m("cut_mg5"), m("cut_mn3"), 0.35, -0.12, 0.2),
           (T0, T0 + 3.3, -0.05, -0.05, 0.1),
           (m("chant") + 2.55, m("chant") + 3.85, 0.85, -0.2, 0.1)],
    "mn": [(m("cut_mn5"), m("cut_br5"), -0.1, -0.12, 0.3),
           (m("cut_mn1") - 0.1, ls("mn_again"), 0.5, -0.1, 0.1)],
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
# explicit nods: (t, count, amplitude %)
NODS = {"ck": [(m("cut_ck8") + 0.02, 1, 3.5), (m("cut_ck12") + 0.02, 1, 3.0), (m("cut_ck13") + 0.05, 1, -3.0)],
        "sh": [], "br": [], "mg": [(m("cut_mg4") + 0.05, 1, 1.5)], "mn": [], "bs": [], "sl": []}
TURN = {   # head moves that aren't eyelines: (t0, t1, turn, tilt deg)
    "ck": [(m("cut_ck4"), le("ck_kobbie"), -0.1, 0.0), (m("cut_ck13") + 0.6, m("cut_sh6"), -0.12, -1.5)],
    "br": [(m("cut_br1") + 0.3, m("cut_ck4"), 0.0, -1.5), (m("cut_br7") + 0.4, m("cut_black"), 0.0, -2.0)],
    "mn": [(m("cut_mn1"), le("mn_again"), 0.0, 3.0), (m("cut_mn6"), le("mn_ipswich"), 0.0, -3.0)],
    "mg": [(m("cut_mg1"), le("mg_striker"), 0.0, 2.5), (m("cut_mg4"), le("mg_twice"), 0.0, 3.0)],
    "sh": [],
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
    return 0.0, 0.0


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
    return dict(vis=VIS[w][f], amp=float(AMP[w][f]), blink=b, lookx=lx, looky=ly, brow=brow, smile=smile,
                tilt=tilt, nod=nod, turn=turn + tu, lean=lean, sink=sink)
