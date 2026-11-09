"""WHY UNITED ARE FAILING: a 60-second portrait tactical breakdown, every frame drawn from scratch (no cut-outs).
python3 make.py frames  -> renders video.mp4 (silent) ; python3 make.py audio -> mix.wav ; python3 make.py still T"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FONTS = "/home/user/src/anim-handover/library/fonts"
W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f"{D}/words.json"))
TIMES = {x[0]: (x[1], x[2]) for x in json.load(open(f"{D}/vo_times.json"))}
TOTAL = 60.0

BG = (10, 12, 18)
RED = (218, 30, 46)
RED_D = (120, 14, 24)
WHITE = (245, 245, 247)
GREY = (150, 154, 166)
AMBER = (255, 184, 28)
PITCH = (14, 52, 40)
LINE = (58, 112, 90)


def wt(lid, word, occ=1):
    """the time a word is spoken (its start)"""
    n = 0
    for w, s, e in WORDS[lid]:
        if w == word:
            n += 1
            if n == occ:
                return s
    raise KeyError((lid, word))


def ls(lid):
    return TIMES[lid][0]


# ---------------------------------------------------------------- easing
def clamp(u):
    return min(1.0, max(0.0, u))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def back(u, s=1.7):
    u = clamp(u)
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def appear(t, t0, d=0.25):
    return out((t - t0) / d)


def window(t, a, b, fin=0.2, fout=0.25):
    return out((t - a) / fin) * (1 - ease((t - b) / fout))


# ---------------------------------------------------------------- fonts
_F = {}


def font(name, px, wght=None):
    key = (name, int(px), wght)
    if key not in _F:
        path = {"bebas": "BebasNeue-Regular.ttf", "inter": "Inter.ttf", "oswald": "Oswald.ttf",
                "marker": "PermanentMarker-Regular.ttf"}[name]
        f = ImageFont.truetype(f"{FONTS}/{path}", max(6, int(px)))
        if wght:
            try:
                axes = f.get_variation_axes()
                f.set_variation_by_axes([wght if a["name"] in (b"Weight", "Weight") else a["default"] for a in axes])
            except Exception:
                pass
        _F[key] = f
    return _F[key]


def text(dr, xy, s, f, fill, anchor="mm", alpha=1.0, stroke=0, stroke_fill=(0, 0, 0)):
    if alpha <= 0.01:
        return
    a = int(255 * clamp(alpha))
    dr.text(xy, s, font=f, fill=fill + (a,), anchor=anchor, stroke_width=stroke,
            stroke_fill=stroke_fill + (a,))


def scaled_text(lay, xy, s, f, fill, k, alpha=1.0, anchor="mm"):
    """text drawn at scale k about its anchor point (a slam)"""
    if alpha <= 0.01 or k <= 0.01:
        return
    l, t_, r, b = f.getbbox(s)
    tw, th = r - l + 40, b - t_ + 40
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20 - l, 20 - t_), s, font=f, fill=fill + (int(255 * clamp(alpha)),))
    im = im.resize((max(1, int(tw * k)), max(1, int(th * k))), Image.BICUBIC)
    x, y = xy
    if anchor == "mm":
        x, y = x - im.width / 2, y - im.height / 2
    lay.alpha_composite(im, (int(x), int(y)))


# ---------------------------------------------------------------- the background
def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.zeros((H, W, 3), np.float32)
    g[:] = np.float32(BG)
    glow = np.exp(-(((xx - W * 0.5) / (W * 0.9)) ** 2 + ((yy - H * 0.32) / (H * 0.5)) ** 2))
    g += glow[..., None] * np.float32([38, 8, 14])
    v = 1 - 0.45 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)
    g *= np.clip(v, 0.35, 1)[..., None]
    rng = np.random.default_rng(3)
    g += rng.normal(0, 2.2, (H, W, 1)).astype(np.float32)
    # a faint grid: an analyst's screen
    for x in range(0, W, 60):
        g[:, x:x + 1] += 5
    for y in range(0, H, 60):
        g[y:y + 1, :] += 5
    return np.clip(g, 0, 255).astype(np.uint8)


BGIMG = None


# ---------------------------------------------------------------- the pitch
PX0, PY0, PW, PH = 150, 470, 780, 1060          # the pitch's rectangle on screen (vertical, attacking up)


def pp(x, y, box=None):
    """pitch coordinates (x 0..1 across, y 0..1 from our goal up to theirs) -> screen"""
    bx, by, bw, bh = box or (PX0, PY0, PW, PH)
    return bx + x * bw, by + (1 - y) * bh


def draw_pitch(dr, a, box=None):
    bx, by, bw, bh = box or (PX0, PY0, PW, PH)
    A = int(255 * a)
    dr.rounded_rectangle((bx - 14, by - 14, bx + bw + 14, by + bh + 14), radius=18, fill=PITCH + (int(235 * a),))
    for k in range(10):                                     # mown stripes
        if k % 2:
            y0 = by + k * bh / 10
            dr.rectangle((bx, y0, bx + bw, y0 + bh / 10), fill=(18, 60, 46, int(235 * a)))
    lc = LINE + (A,)
    lw = 4
    dr.rectangle((bx, by, bx + bw, by + bh), outline=lc, width=lw)
    dr.line((bx, by + bh / 2, bx + bw, by + bh / 2), fill=lc, width=lw)
    r = bw * 0.13
    dr.ellipse((bx + bw / 2 - r, by + bh / 2 - r, bx + bw / 2 + r, by + bh / 2 + r), outline=lc, width=lw)
    for top in (True, False):
        y0 = by if top else by + bh
        s = 1 if top else -1
        dr.rectangle((bx + bw * 0.2, min(y0, y0 + s * bh * 0.16), bx + bw * 0.8, max(y0, y0 + s * bh * 0.16)),
                     outline=lc, width=lw)
        dr.rectangle((bx + bw * 0.37, min(y0, y0 + s * bh * 0.055), bx + bw * 0.63, max(y0, y0 + s * bh * 0.055)),
                     outline=lc, width=lw)


SHAPES = {
    "4231": {"GK": (0.5, 0.05), "LB": (0.13, 0.27), "LCB": (0.37, 0.21), "RCB": (0.63, 0.21), "RB": (0.87, 0.27),
             "DM1": (0.38, 0.41), "DM2": (0.62, 0.41), "LW": (0.15, 0.63), "AM": (0.5, 0.6), "RW": (0.85, 0.63),
             "ST": (0.5, 0.8)},
    "316": {"GK": (0.5, 0.07), "LB": (0.2, 0.33), "LCB": (0.5, 0.29), "RCB": (0.8, 0.33), "RB": (0.64, 0.64),
            "DM1": (0.5, 0.47), "DM2": (0.36, 0.66), "LW": (0.1, 0.82), "AM": (0.5, 0.79), "RW": (0.9, 0.82),
            "ST": (0.5, 0.92)},
    "fbhigh": {"GK": (0.5, 0.05), "LB": (0.1, 0.62), "LCB": (0.38, 0.22), "RCB": (0.62, 0.22), "RB": (0.9, 0.62),
               "DM1": (0.4, 0.52), "DM2": (0.6, 0.52), "LW": (0.15, 0.78), "AM": (0.5, 0.72), "RW": (0.85, 0.78),
               "ST": (0.5, 0.88)},
}
SIX = ["RB", "DM2", "LW", "AM", "RW", "ST"]
ROLE = {"GK": "GK", "LB": "LB", "LCB": "CB", "RCB": "CB", "RB": "RB", "DM1": "DM", "DM2": "DM", "LW": "LW",
        "AM": "AM", "RW": "RW", "ST": "ST"}


def shape_at(a, b, u):
    A, B = SHAPES[a], SHAPES[b]
    k = ease(u)
    return {p: (A[p][0] + (B[p][0] - A[p][0]) * k, A[p][1] + (B[p][1] - A[p][1]) * k) for p in A}


def draw_players(dr, pos, a, rings=(), dim=(), r=30, box=None, labels=True):
    for p, (x, y) in pos.items():
        X, Y = pp(x, y, box)
        al = a * (0.35 if p in dim else 1.0)
        A = int(255 * al)
        if p in rings:
            dr.ellipse((X - r - 12, Y - r - 12, X + r + 12, Y + r + 12), outline=AMBER + (A,), width=6)
        col = (40, 40, 48) if p == "GK" else RED
        dr.ellipse((X - r, Y - r, X + r, Y + r), fill=col + (A,), outline=WHITE + (A,), width=4)
        if labels:
            text(dr, (X, Y + 1), ROLE[p], font("bebas", r * 0.95), WHITE, alpha=al)


def arrow(dr, p0, p1, col, a, w=8, head=26, dash=None, u=1.0):
    """an arrow from p0 towards p1, drawn to fraction u of its length"""
    if u <= 0 or a <= 0:
        return
    x0, y0 = p0
    x1, y1 = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
    A = int(255 * a)
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 2:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    if dash:
        n = int(L // (dash * 2))
        for k in range(n + 1):
            a0, a1 = k * dash * 2, min(L - head * 0.6, k * dash * 2 + dash)
            if a1 > a0:
                dr.line((x0 + ux * a0, y0 + uy * a0, x0 + ux * a1, y0 + uy * a1), fill=col + (A,), width=w)
    else:
        dr.line((x0, y0, x1 - ux * head * 0.6, y1 - uy * head * 0.6), fill=col + (A,), width=w)
    nx, ny = -uy, ux
    dr.polygon([(x1, y1), (x1 - ux * head + nx * head * 0.55, y1 - uy * head + ny * head * 0.55),
                (x1 - ux * head - nx * head * 0.55, y1 - uy * head - ny * head * 0.55)], fill=col + (A,))


# ---------------------------------------------------------------- the frame furniture
CHAPTERS = [(0.0, "THE TABLE"), (ls("V03"), "THE SHAPE"), (ls("V05"), "THE PROOF"), (ls("V08"), "THE OWNERS"),
            (ls("V11"), "THE VERDICT")]


def furniture(dr, t):
    # the progress bar and the title strip
    dr.rectangle((0, 0, W, 10), fill=(40, 42, 52, 255))
    dr.rectangle((0, 0, int(W * clamp(t / TOTAL)), 10), fill=RED + (255,))
    text(dr, (60, 120), "WHY UNITED ARE FAILING", font("bebas", 58), WHITE, anchor="lm")
    text(dr, (60, 172), "A TACTICAL BREAKDOWN", font("inter", 26, 700), GREY, anchor="lm")
    ch = [c for c in CHAPTERS if c[0] <= t + 0.01][-1]
    k = appear(t, ch[0], 0.3)
    f = font("bebas", 40)
    tw = dr.textlength(ch[1], font=f)
    dr.rounded_rectangle((W - 60 - tw - 36, 96, W - 60, 148), radius=8, fill=RED + (int(255 * k),))
    text(dr, (W - 60 - 18, 123), ch[1], f, WHITE, anchor="rm", alpha=k)
    # the brand, small, at the foot
    text(dr, (W / 2, 1830), "UNITED ROAD", font("bebas", 40), (200, 200, 206), alpha=0.85)


# ---------------------------------------------------------------- the scenes
def s_table(lay, dr, t):
    """0-9: 18TH, the relegation zone; eight points from ten; eight without a win"""
    a_out = 1 - ease((t - (ls("V03") - 0.25)) / 0.25)
    if a_out <= 0:
        return 0.0
    shake = 0.0
    t18 = wt("V01", "eighteenth")
    text(dr, (W / 2, 330), "MANCHESTER UNITED", font("bebas", 96), WHITE, alpha=appear(t, 0.35) * a_out)
    if t >= t18 - 0.05:
        u = (t - t18 + 0.05) / 0.22
        k = 2.4 - 1.4 * back(u, 2.2) if u < 1 else 1.0
        scaled_text(lay, (W / 2, 640), "18TH", font("bebas", 430), RED, k, alpha=clamp(u * 2) * a_out)
        shake = max(0.0, 1 - (t - t18) / 0.35) * 14
    tz = wt("V01", "relegation")
    if t >= tz - 0.1:
        k = out((t - tz + 0.1) / 0.25)
        y = 880
        dr.rectangle((W / 2 - 400 * k, y - 50, W / 2 + 400 * k, y + 50), fill=RED + (int(255 * a_out),))
        text(dr, (W / 2, y + 2), "RELEGATION ZONE", font("bebas", 86), WHITE, alpha=k * a_out)
    # the record: P10 W1 D5 L4, 8 PTS, GD -5
    tp = wt("V02", "eight")
    if t >= tp - 0.1:
        k = appear(t, tp - 0.1, 0.3) * a_out
        pts = int(round(8 * ease((t - tp) / 0.5)))
        y = 1080
        dr.rounded_rectangle((90, y - 70, 990, y + 70), radius=16, fill=(24, 26, 34, int(240 * k)),
                             outline=(60, 62, 74, int(255 * k)), width=3)
        cols = [("P", "10"), ("W", "1"), ("D", "5"), ("L", "4"), ("GD", "-5"), ("PTS", str(pts))]
        for i, (h, v) in enumerate(cols):
            x = 170 + i * 148
            text(dr, (x, y - 30), h, font("inter", 26, 700), GREY, alpha=k)
            text(dr, (x, y + 22), v, font("bebas", 74), AMBER if h == "PTS" else WHITE, alpha=k)
    # eight without a win: the form strip
    tw_ = wt("V02", "eight", 2)
    form = [("EVE", "D"), ("MCI", "L"), ("FUL", "D"), ("TOT", "D"), ("LEE", "D"), ("BOU", "L"), ("CHE", "L"),
            ("AVL", "D")]
    if t >= tw_ - 0.1:
        text(dr, (W / 2, 1265), "PREMIER LEAGUE GAMES WITHOUT A WIN", font("inter", 30, 800), GREY,
             alpha=appear(t, tw_) * a_out)
        for i, (opp, r) in enumerate(form):
            ti = tw_ + 0.12 * i
            k = back((t - ti) / 0.22) if t > ti else 0
            if k <= 0:
                continue
            x = 120 + i * 120
            y = 1380
            sz = 50 * k
            col = (200, 40, 50) if r == "L" else (110, 112, 124)
            dr.rounded_rectangle((x - sz, y - sz, x + sz, y + sz), radius=12, fill=col + (int(255 * a_out),))
            text(dr, (x, y - 8), r, font("bebas", 64), WHITE, alpha=a_out)
            text(dr, (x, y + 70), opp, font("inter", 22, 700), GREY, alpha=a_out)
        tn = wt("V02", "win")
        if t > tn:
            k = back((t - tn) / 0.25) * a_out
            scaled_text(lay, (W / 2, 1520), "8 WITHOUT A WIN", font("bebas", 120), AMBER, max(0.01, k), alpha=clamp(k))
    return shake


def s_shape(lay, dr, t):
    """9-21.4: the 4-2-3-1 becomes a 3-1-6; six ahead, one holding; lose it: the canyon"""
    a0, a1 = ls("V03") - 0.2, ls("V05") - 0.25
    a = window(t, a0, a1)
    if a <= 0:
        return
    draw_pitch(dr, a)
    tb = wt("V03", "becomes")
    tf = wt("V03", "four")
    pos = shape_at("4231", "316", (t - tb) / 0.9)
    # the shape's name
    label = "4-2-3-1" if t < tb + 0.45 else "3-1-6"
    lk = appear(t, tf - 0.1) if t < tb + 0.45 else appear(t, tb + 0.45, 0.2)
    text(dr, (W / 2, 330), label, font("bebas", 150), WHITE, alpha=a * lk)
    sub = "OUT OF POSSESSION" if t < tb + 0.45 else "WITH THE BALL"
    text(dr, (W / 2, 420), sub, font("inter", 30, 800), AMBER, alpha=a * lk)
    t6 = wt("V04", "six")
    t1 = wt("V04", "one")
    tl = wt("V04", "lose")
    tc = wt("V04", "canyon")
    rings = []
    if t6 - 0.05 <= t < t1:
        rings = SIX
    elif t1 - 0.05 <= t < tl:
        rings = ["DM1"]
    dim = []
    # the canyon: between the six and the back three
    if t >= tc - 0.15:
        k = out((t - tc + 0.15) / 0.35) * a
        ya, yb = pp(0, 0.6)[1], pp(0, 0.36)[1]
        band = Image.new("RGBA", (PW, int(yb - ya)), RED + (int(110 * k),))
        bd = ImageDraw.Draw(band)
        for x in range(-int(yb - ya), PW, 34):                  # hatching
            bd.line((x, int(yb - ya), x + int(yb - ya), 0), fill=RED + (int(80 * k),), width=8)
        lay.alpha_composite(band, (PX0, int(ya)))
        dr.line((PX0, ya, PX0 + PW, ya), fill=RED + (int(255 * k),), width=4)
        dr.line((PX0, yb, PX0 + PW, yb), fill=RED + (int(255 * k),), width=4)
        scaled_text(lay, (W / 2, (ya + yb) / 2), "THE CANYON", font("bebas", 120), WHITE,
                    max(0.01, back((t - tc) / 0.3)), alpha=k)
    draw_players(dr, pos, a, rings=rings, dim=dim)
    # lose it: the ball goes, the counters run through the gap
    if t >= tl - 0.05:
        bx, by = pp(0.5, 0.79)
        k = appear(t, tl - 0.05, 0.15) * a
        dr.ellipse((bx - 18 + 60, by - 18 - 50, bx + 18 + 60, by + 18 - 50), fill=WHITE + (int(255 * k),),
                   outline=(20, 20, 20, int(255 * k)), width=3)
        sz = 26
        cx, cy = bx + 60, by - 50
        if t > tl + 0.15:
            k2 = appear(t, tl + 0.15, 0.12) * a
            dr.line((cx - sz, cy - sz, cx + sz, cy + sz), fill=AMBER + (int(255 * k2),), width=9)
            dr.line((cx - sz, cy + sz, cx + sz, cy - sz), fill=AMBER + (int(255 * k2),), width=9)
        for i, (x0, x1) in enumerate(((0.3, 0.38), (0.62, 0.55), (0.48, 0.5))):
            ts = tl + 0.45 + 0.15 * i
            if t > ts:
                arrow(dr, pp(x0, 0.74), pp(x1, 0.3 if i < 2 else 0.24), AMBER, a, w=9, dash=18,
                      u=out((t - ts) / 0.7))


def s_villa(lay, dr, t):
    """21.4-28.2: Villa: two down inside four minutes; full-backs high, the centre-backs alone"""
    a = window(t, ls("V05") - 0.2, ls("V07") - 0.2)
    if a <= 0:
        return
    text(dr, (W / 2, 300), "UNITED 4-4 VILLA", font("bebas", 110), WHITE, alpha=a * appear(t, ls("V05") - 0.2))
    text(dr, (W / 2, 372), "OLD TRAFFORD · 8 NOV 2026", font("inter", 28, 700), GREY, alpha=a * appear(t, ls("V05")))
    # the clock: 0' to 4', two goals
    tt = wt("V05", "two")
    y = 470
    x0, x1 = 120, 960
    k = appear(t, tt - 0.4, 0.3) * a
    dr.rounded_rectangle((x0, y - 12, x1, y + 12), radius=12, fill=(40, 42, 52, int(255 * k)))
    run = clamp((t - tt + 0.3) / 1.4)
    dr.rounded_rectangle((x0, y - 12, x0 + (x1 - x0) * run, y + 12), radius=12, fill=RED + (int(255 * k),))
    for m_, lab, tg in ((1, "0-1  1'", tt - 0.25), (4, "0-2  4'", wt("V05", "four"))):
        xm = x0 + (x1 - x0) * (m_ / 4.4)
        if t > tg:
            kk = back((t - tg) / 0.25)
            dr.ellipse((xm - 22 * kk, y - 22 * kk, xm + 22 * kk, y + 22 * kk), fill=WHITE + (int(255 * a),))
            text(dr, (xm, y + 62), lab, font("bebas", 56), AMBER, alpha=a * clamp(kk))
    # the pitch, smaller: full-backs high, the centre-backs alone
    box = (265, 700, 550, 700)
    tf = wt("V05", "full")
    tc = wt("V05", "two", 2)
    if t > tf - 0.4:
        ka = appear(t, tf - 0.4, 0.3) * a
        draw_pitch(dr, ka, box)
        pos = shape_at("4231", "fbhigh", (t - tf) / 0.6)
        draw_players(dr, pos, ka, rings=(["LB", "RB"] if t < tc else ["LCB", "RCB"]), r=24, box=box)
        if t > tf:
            for p in ("LB", "RB"):
                X, Y = pp(*SHAPES["4231"][p], box)
                arrow(dr, (X, Y), pp(*SHAPES["fbhigh"][p], box), WHITE, ka * 0.8, w=6, head=20, u=out((t - tf) / 0.6))
        if t > tc:
            for i, (sx, ex) in enumerate(((0.3, 0.42), (0.72, 0.58))):
                arrow(dr, pp(sx, 0.62, box), pp(ex, 0.12, box), AMBER, ka, w=8, head=24, dash=16,
                      u=out((t - tc - 0.1 * i) / 0.8))
            text(dr, (W / 2, 1470), "TWO CENTRE-BACKS. ALONE.", font("bebas", 74), AMBER,
                 alpha=appear(t, tc + 0.3) * a)
    # the stat card: 26 shots, 3.09 xG conceded
    ts = wt("V05", "two", 2) + 0.9
    if t > ts:
        k = back((t - ts) / 0.3)
        y0 = 584
        dr.rounded_rectangle((90, y0 - 4, 990, y0 + 88), radius=14, fill=(24, 26, 34, int(240 * a)))
        text(dr, (300, y0 + 42), "26 SHOTS", font("bebas", 64), WHITE, alpha=a * clamp(k))
        text(dr, (760, y0 + 42), "3.09 xG CONCEDED", font("bebas", 64), RED, alpha=a * clamp(k))


def s_thirty(lay, dr, t):
    a = window(t, ls("V07") - 0.15, ls("V08") - 0.2)
    if a <= 0:
        return 0.0
    t30 = wt("V07", "thirty")
    n = int(round(30 * out((t - t30) / 0.7)))
    k = back((t - t30) / 0.35)
    scaled_text(lay, (W / 2, 720), str(n), font("bebas", 620), RED, max(0.01, k), alpha=a * clamp(k))
    text(dr, (W / 2, 1060), "GOALS CONCEDED · ALL COMPETITIONS", font("inter", 34, 800), WHITE, alpha=a * appear(t, t30 + 0.3))
    tm = wt("V07", "more")
    if t > tm:
        kk = out((t - tm) / 0.3)
        dr.rectangle((W / 2 - 430 * kk, 1150, W / 2 + 430 * kk, 1290), fill=AMBER + (int(255 * a),))
        text(dr, (W / 2, 1222), "MOST IN EUROPE'S TOP 5 LEAGUES", font("bebas", 72), (14, 14, 18), alpha=a * kk)
        text(dr, (W / 2, 1340), "per Opta, 8 Nov 2026", font("inter", 26, 600), GREY, alpha=a * kk)
    return max(0.0, 1 - (t - t30) / 0.3) * 10 if t > t30 else 0.0


def s_owners(lay, dr, t):
    """33.6-47.8: upstairs. 2005, borrowed money; twenty years on, still paying; under a third; the fans"""
    a = window(t, ls("V08") - 0.15, ls("V10") - 0.2)
    if a <= 0:
        return
    tu = wt("V08", "upstairs")
    # the camera tilts up: the pitch slides away below, the boardroom comes down
    k = out((t - (ls("V08") - 0.15)) / 0.5)
    ku = 1 - ease((t - (ls("V09") - 0.3)) / 0.25)
    text(dr, (W / 2, 330 + 60 * (1 - k)), "LOOK UPSTAIRS", font("bebas", 140), WHITE, alpha=a * appear(t, tu - 0.1) * ku)
    arrow(dr, (W / 2, 520), (W / 2, 430), RED, a * appear(t, tu) * ku, w=12, head=34, u=1)
    t05 = wt("V08", "two")
    if t < ls("V09") - 0.1:
        if t > t05 - 0.2:
            kk = back((t - t05 + 0.2) / 0.3)
            scaled_text(lay, (W / 2, 700), "2005", font("bebas", 300), AMBER, max(0.01, kk), alpha=a * clamp(kk))
        tb = wt("V08", "borrowed")
        if t > tb - 0.1:
            text(dr, (W / 2, 880), "THE GLAZERS' TAKEOVER", font("bebas", 70), WHITE, alpha=a * appear(t, tb - 0.1))
            text(dr, (W / 2, 950), "funded by borrowing, loaded onto the club", font("inter", 32, 600), GREY,
                 alpha=a * appear(t, tb + 0.2))
        ty = wt("V08", "twenty")
        if t > ty - 0.1:
            kt = out((t - ty + 0.1) / 1.2)
            y = 1160
            dr.line((140, y, 140 + 800 * kt, y), fill=WHITE + (int(255 * a),), width=6)
            for frac, lab in ((0.0, "2005"), (1.0, "2026")):
                if kt >= frac:
                    x = 140 + 800 * frac
                    dr.ellipse((x - 14, y - 14, x + 14, y + 14), fill=AMBER + (int(255 * a),))
                    text(dr, (x, y + 52), lab, font("bebas", 54), WHITE, alpha=a)
            text(dr, (W / 2, y - 50), "21 SEASONS", font("inter", 28, 800), GREY, alpha=a * kt)
        tp = wt("V08", "paying")
        if t > tp - 0.1:
            kk = back((t - tp + 0.1) / 0.25)
            stamp = Image.new("RGBA", (760, 170), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp)
            sd.rounded_rectangle((6, 6, 754, 164), radius=14, outline=RED + (int(255 * a),), width=10)
            sd.text((380, 88), "STILL PAYING", font=font("bebas", 120), fill=RED + (int(255 * a),), anchor="mm")
            stamp = stamp.rotate(-6, expand=True, resample=Image.BICUBIC)
            stamp = stamp.resize((max(1, int(stamp.width * kk)), max(1, int(stamp.height * kk))), Image.BICUBIC)
            lay.alpha_composite(stamp, (int(W / 2 - stamp.width / 2), int(1430 - stamp.height / 2)))
    else:
        # who owns it: the Glazers, the majority; INEOS, under a third; and the fans turning on both
        tr = ls("V09")
        ko = appear(t, tr - 0.1, 0.3)
        cx, cy, R = W / 2, 820, 270
        to = wt("V09", "owns")
        sweep = 360 * out((t - to + 0.2) / 0.8) if t > to - 0.2 else 0
        dr.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(70, 72, 84, int(255 * a * ko)), width=70)
        if sweep > 0:
            dr.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + sweep * 0.71, fill=(110, 112, 124, int(255 * a)),
                   width=70)
            if sweep > 360 * 0.71:
                dr.arc((cx - R, cy - R, cx + R, cy + R), -90 + 360 * 0.71, -90 + sweep, fill=RED + (int(255 * a),),
                       width=70)
        text(dr, (cx, cy - 30), "~29%", font("bebas", 150), RED, alpha=a * appear(t, to + 0.5))
        text(dr, (cx, cy + 70), "INEOS / RATCLIFFE", font("inter", 30, 800), WHITE, alpha=a * appear(t, to + 0.5))
        text(dr, (W / 2, 340), "RATCLIFFE", font("bebas", 120), WHITE, alpha=a * appear(t, tr - 0.1))
        text(dr, (W / 2, 450), "RUNS THE FOOTBALL", font("bebas", 74), AMBER, alpha=a * appear(t, wt("V09", "runs")))
        text(dr, (W / 2, 1150), "GLAZER FAMILY: THE MAJORITY", font("bebas", 64), (190, 192, 204),
             alpha=a * appear(t, to + 0.7))
        tf = wt("V09", "fans")
        if t > tf - 0.1:
            # the crowd, row by row, turning red
            for row in range(2):
                for i in range(10):
                    x = 132 + i * 91 + (row % 2) * 45
                    y = 1290 + row * 105
                    flip = clamp((t - tf - 0.04 * i - 0.08 * row) / 0.15)
                    col = tuple(int(c0 + (c1 - c0) * flip) for c0, c1 in zip((90, 92, 104), RED))
                    kk = a * appear(t, tf - 0.1 + 0.02 * i)
                    dr.ellipse((x - 18, y - 46, x + 18, y - 10), fill=col + (int(255 * kk),))
                    dr.rounded_rectangle((x - 30, y - 6, x + 30, y + 40), radius=16, fill=col + (int(255 * kk),))
            text(dr, (W / 2, 1500), "TURNING ON BOTH", font("bebas", 80), WHITE, alpha=a * appear(t, wt("V09", "both")))


def s_banner(lay, dr, t):
    a = window(t, ls("V10") - 0.15, ls("V11") - 0.2)
    if a <= 0:
        return
    text(dr, (W / 2, 330), "OLD TRAFFORD · SUNDAY", font("bebas", 70), GREY, alpha=a * appear(t, ls("V10")))
    # the banner: a hand-painted sheet, swaying a little
    k = out((t - ls("V10")) / 0.45)
    bw, bh = 960, 560
    ban = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(ban)
    bd.rectangle((0, 0, bw, bh), fill=(236, 232, 222, 255))
    for y in range(0, bh, 7):                                   # the cloth's weave
        bd.line((0, y, bw, y), fill=(226, 222, 212, 255), width=2)
    f = font("marker", 74)
    l1 = wt("V10", "we")
    l2 = wt("V10", "we", 2)
    if t > l1 - 0.1:
        r1 = clamp((t - l1 + 0.1) / 0.9)
        for j, s in enumerate(("WE DON'T WANT", "A NEW STADIUM")):
            rr = clamp(r1 * 2 - j)
            if rr > 0:
                tmp = Image.new("RGBA", (bw, 110), (0, 0, 0, 0))
                ImageDraw.Draw(tmp).text((bw / 2, 55), s, font=f, fill=(30, 30, 34, 255), anchor="mm")
                ban.alpha_composite(tmp.crop((0, 0, int(bw * rr), 110)), (0, 40 + j * 110))
    if t > l2 - 0.1:
        r2 = clamp((t - l2 + 0.1) / 0.8)
        for j, s in enumerate(("WE WANT THE", "OWNERS OUT")):
            rr = clamp(r2 * 2 - j)
            if rr > 0:
                tmp = Image.new("RGBA", (bw, 110), (0, 0, 0, 0))
                ImageDraw.Draw(tmp).text((bw / 2, 55), s, font=f, fill=RED + (255,), anchor="mm")
                ban.alpha_composite(tmp.crop((0, 0, int(bw * rr), 110)), (0, 300 + j * 110))
    ban = ban.rotate(1.6 * math.sin(t * 1.7), expand=True, resample=Image.BICUBIC)
    if k > 0:
        ban = ban.resize((ban.width, max(1, int(ban.height * k))), Image.BICUBIC)
        sh = Image.new("RGBA", ban.size, (0, 0, 0, int(140 * a)))
        lay.alpha_composite(sh, (int(W / 2 - ban.width / 2) + 14, 520 + 18))
        ban.putalpha(ban.getchannel("A").point(lambda v: int(v * a)))
        lay.alpha_composite(ban, (int(W / 2 - ban.width / 2), 520))
    text(dr, (W / 2, 1230), "Fans' banner, United v Aston Villa", font("inter", 28, 600), GREY, alpha=a * k)


def s_verdict(lay, dr, t):
    t0 = ls("V11")
    a = window(t, t0 - 0.15, TOTAL + 1)
    if a <= 0:
        return
    tc = wt("V11", "coach")
    text(dr, (W / 2, 330), "IT ISN'T ONE COACH", font("bebas", 120), WHITE, alpha=a * appear(t, t0))
    if t > tc:
        k = out((t - tc) / 0.25)
        dr.rectangle((W / 2 - 300 * k, 410, W / 2 + 300 * k, 418), fill=RED + (int(255 * a),))
    ts = wt("V11", "shape")
    tst = wt("V11", "structure")
    # the two layers: the shape (a pitch) and the structure (the ownership above it)
    if t > ts - 0.15:
        k = appear(t, ts - 0.15, 0.3) * a
        box = (330, 1000, 420, 440)
        draw_pitch(dr, k, box)
        draw_players(dr, SHAPES["316"], k, r=18, box=box, labels=False)
        text(dr, (W / 2, 1520), "THE SHAPE", font("bebas", 110), WHITE, alpha=k)
    if t > tst - 0.15:
        k = appear(t, tst - 0.15, 0.3) * a
        cx, cy, R = W / 2, 690, 150
        dr.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(110, 112, 124, int(255 * k)), width=46)
        dr.arc((cx - R, cy - R, cx + R, cy + R), -90 + 360 * 0.71, 270, fill=RED + (int(255 * k),), width=46)
        text(dr, (W / 2, 900), "THE STRUCTURE", font("bebas", 110), AMBER, alpha=k)
    te = TIMES["V11"][1] + 0.35
    if t > te:
        k = appear(t, te, 0.35)
        dr.rectangle((0, 0, W, H), fill=(6, 7, 10, int(235 * k)))
        scaled_text(lay, (W / 2, 860), "WHY UNITED", font("bebas", 190), WHITE, 1.0, alpha=k)
        scaled_text(lay, (W / 2, 1040), "ARE FAILING", font("bebas", 190), RED, 1.0, alpha=k)
        text(dr, (W / 2, 1200), "THE SHAPE  ·  THE STRUCTURE", font("inter", 32, 800), GREY, alpha=k)
        text(dr, (W / 2, 1420), "Stats: Premier League, Opta, Goal, NBC Sports · to 8 Nov 2026",
             font("inter", 24, 600), (120, 122, 134), alpha=k)


def frame(t):
    global BGIMG
    if BGIMG is None:
        BGIMG = make_bg()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    shake = s_table(lay, dr, t)
    s_shape(lay, dr, t)
    s_villa(lay, dr, t)
    shake = max(shake, s_thirty(lay, dr, t))
    s_owners(lay, dr, t)
    s_banner(lay, dr, t)
    s_verdict(lay, dr, t)
    furniture(dr, t)
    img = Image.fromarray(BGIMG).convert("RGBA")
    img.alpha_composite(lay)
    out_ = np.asarray(img.convert("RGB"))
    if shake > 0.5:
        import cv2
        dx, dy = shake * math.sin(t * 91), shake * math.cos(t * 77)
        out_ = cv2.warpAffine(out_, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    return out_


def render(path, a=0.0, b=TOTAL):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n0, n1 = int(round(a * FPS)), int(round(b * FPS))
    for i in range(n0, n1):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{n1}", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for tt in sys.argv[2:]:
            Image.fromarray(frame(float(tt))).save(f"{D}/still_{float(tt):05.2f}.jpg", quality=90)
    elif cmd == "frames":
        a = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        b = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
        render(sys.argv[4] if len(sys.argv) > 4 else f"{D}/video.mp4", a, b)
