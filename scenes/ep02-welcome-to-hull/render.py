"""Render Episode 2, "Welcome to Hull": 1080 x 1920 (9:16), 30 fps.

  python3 render.py still 3.5 12 40          -> build/stills/still_<t>.jpg (single frames)
  python3 render.py chunk A B out.mp4        -> frames [A, B) encoded without audio (for parallel rendering)
  EP_RES=540x960 python3 render.py ...       -> quick low-res previews
Each frame: the shot at that time (direction.py) -> the set, the characters with their face / body state
(perf.py), their props and the furniture in front of them -> grade -> graphics -> vignette and grain."""
import os, sys, math, subprocess, functools, numpy as np, cv2
import engine as E
from engine import OW, OH, FPS, RS
import direction as D, perf, graphics as G
from cast import CAST

_PL = {}


def plate(k):
    if k not in _PL:
        _PL[k] = E.Plate(f"build/x4/{D.PLATES[k]}.png", D.OCCL.get(k))
    return _PL[k]


def drift(t, s, amt):
    """handheld documentary camera: slow, small wander (screen px)"""
    k = s["i"] * 1.37
    dx = (5.0 * math.sin(t * 0.9 + k) + 2.5 * math.sin(t * 2.1 + 2 * k)) * RS * amt
    dy = (4.0 * math.sin(t * 0.7 + 3 * k) + 2.0 * math.sin(t * 1.9 + k)) * RS * amt
    return dx, dy


def shake(t, amt):
    """a rougher handheld shake (celebrations, shouting): per-frame jitter, smoothed over 2 frames"""
    f = int(t * FPS)
    r0, r1 = np.random.default_rng(f), np.random.default_rng(f + 1)
    u = t * FPS - f
    a, b = r0.uniform(-1, 1, 2), r1.uniform(-1, 1, 2)
    v = a * (1 - u) + b * u
    return float(v[0] * amt * RS), float(v[1] * amt * RS)


def zoom_about(P, cx, cy, z, f, F):
    """the view (cx, cy, z) zoomed by f about screen point F"""
    s = P.scale(z)
    px, py = cx + (F[0] - OW / 2) / s, cy + (F[1] - OH / 2) / s
    s2 = s * f
    return px - (F[0] - OW / 2) / s2, py - (F[1] - OH / 2) / s2, z * f


def face_state(st, info, mirror):
    """perf state -> the drawing's own face parameters (look offset for the drawing, mirrored when flipped)"""
    lx, ly = st["lookx"], st["looky"]
    l0 = info["look0"]
    sg = -1.0 if mirror else 1.0
    out = dict(st)
    out["lookx"] = max(-1.2, min(1.2, sg * lx + l0[0]))
    out["looky"] = max(-0.8, min(1.0, ly + l0[1]))
    out["turn"] = max(-0.9, min(0.9, sg * st["turn"]))
    out["tilt"] = sg * st["tilt"]
    return out


def actor_matrix(info, ex, ey, k, mirror=False, lean=0.0, sink=0.0, ed=None):
    """sheet px -> screen px: the drawing's anchor (between the eyes) at (ex, ey), k screen px per sheet px"""
    ax, ay = info["anchor"]
    k2 = k * (1 + 0.07 * lean - 0.05 * sink)
    ed_s = (ed if ed else info["ed"] * k)
    ey = ey + ed_s * (0.25 * lean + 0.55 * sink)
    sx = -k2 if mirror else k2
    return np.float64([[sx, 0, ex - sx * ax], [0, k2, ey - k2 * ay]])


# ---------------------------------------------------------------- gaze resolution per shot
def single_resolver(s):
    who = s["who"]
    def res(g):
        if g == "cam": return (0.0, 0.0, 0.0)
        if g == "down": return (0.05, 0.85, 0.0)
        if isinstance(g, tuple) and g[0] == "dir": return g[1:]
        return D.EYES.get(who, {}).get(g, (0.0, 0.05, 0.0))
    return res


def world_resolver(s, who, pos):
    """inside a wide or a lineup: towards where the target is on screen (pos: who -> screen x), Carrick and Steve
    screen right of the players"""
    def res(g):
        if g == "cam": return (0.0, 0.0, 0.0)
        if g == "down": return (0.08, 0.85, 0.0)
        if isinstance(g, tuple) and g[0] == "dir": return g[1:]
        if g in pos and who in pos:
            dx = pos[g] - pos[who]
            if abs(dx) < 1: return (0.0, 0.05, 0.0)
            sgn = 1.0 if dx > 0 else -1.0
            return (0.9 * sgn, 0.05, 0.35 * sgn)
        if g in ("ck", "sh", "board"): return (0.9, -0.1, 0.35)
        return (0.0, 0.05, 0.0)
    return res


# ---------------------------------------------------------------- props
@functools.lru_cache(maxsize=1)
def arm_sprite():
    """Harry's raised hand (props.py): premultiplied RGBA float, wrist point, palm width (part px)"""
    import json
    m = json.load(open("build/parts/meta.json"))["mg_arm"]
    p = cv2.imread("build/parts/mg_arm.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    p = p[..., [2, 1, 0, 3]].copy()
    p[..., :3] *= p[..., 3:4]
    return p, tuple(m["wrist"]), m["palm"]


def raised_hand(lay, s, t, ex, ey, ed):
    """Harry's hand, up beside his face from below the frame: up on the first shot, held, lowered slowly on the
    last (the tiny zoom)"""
    t2, t5 = D.m("cut_mg2"), D.m("cut_mg5")
    if s["t"] == t2:
        h = D.ease((t - t2 - 0.04) / 0.34)
    elif s["t"] == t5:
        h = 1 - D.ease((t - t5 - 0.18) / 0.8)
    else:
        h = 1.0
    if h <= 0: return
    p, (wx, wy), palm = arm_sprite()
    k = 1.32 * ed / palm
    ang = math.radians(-16)                       # fingers up, leaning out a little
    tx = ex - 2.35 * ed
    ty = ey + 2.55 * ed + (1 - h) * 3.6 * ed
    c, sn = math.cos(ang), math.sin(ang)
    A = np.float64([[k * c, -k * sn, 0], [k * sn, k * c, 0]])
    A[:, 2] = np.float64([tx, ty]) - A[:, :2] @ np.float64([wx, wy])
    E.warp_into(lay, p, A.astype(np.float32))


def feet_shadow(img, x, y, w, strength=0.42):
    sh = np.zeros((OH, OW), np.float32)
    cv2.ellipse(sh, (int(x), int(y)), (max(1, int(w / 2)), max(1, int(w * 0.09))), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    sh = cv2.GaussianBlur(sh, (0, 0), max(1.0, w * 0.06))
    return img * (1 - strength * sh[..., None])


# standing drawings: feet centre (sheet px) and the shadow's width
FEET = {"ck_walk": (884, 1360, 105), "ck_front": (128, 516, 190), "sh_hero": (152, 848, 250), "ck_side": (566, 526, 150),
        "ck_back": (994, 526, 185)}


# ---------------------------------------------------------------- shots
def render_single(s, t, extra_dx=0.0):
    u = (t - s["t"]) / max(1e-3, s["end"] - s["t"])
    p = s["push"][0] + (s["push"][1] - s["push"][0]) * D.ease(u)
    if s.get("punch") and t >= s["punch"][0]:          # a snap punch-in on the punchline (3 frames)
        p *= 1 + (s["punch"][1] - 1) * D.ease((t - s["punch"][0]) / 0.1)
    dx, dy = drift(t, s, s["drift"])
    if s.get("shake"):
        sx, sy = shake(t, 9.0); dx += sx; dy += sy
    ex, ey = s["eye"][0] * RS, s["eye"][1] * RS
    EDS = s["ed"] * RS                                          # his eye distance on this output
    # Carrick's clap: his shoulders jolt in and the camera takes a small knock (3 frames)
    jolt = 0.0
    if s.get("clap") is not None:
        jolt = perf.bump((t - s["clap"]) / 0.12)
        dy += 5 * RS * jolt
    # Bruno stands up: he rises out of the bench, the camera tilts up after him
    rise = 0.0
    if s.get("rise"):
        r0, rd = s["rise"]
        rise = D.ease((t - r0) / rd)
    F = (ex, ey)
    # the set behind: blurred, zooms less than the character (parallax)
    pk, cx, cy, z, blur = s["bg"]
    P = plate(pk)
    cx, cy, z = zoom_about(P, cx, cy, z, p ** 0.35, F)
    sc = P.scale(z)
    cy = cy - rise * 0.45 * EDS / sc                            # the tilt up follows him
    cx, cy = P.clamp(cx - dx * 0.6 / sc, cy - dy * 0.6 / sc, z)
    bg = P.render(cx, cy, z)
    if blur > 0: bg = cv2.GaussianBlur(bg, (0, 0), blur * RS)
    q = s.get("quiet", 0.0) * G.sm((t - s["t"] - 0.2) / 1.2)
    if q > 0:                                                    # the button: the room goes quiet behind him
        l = bg.mean(2, keepdims=True)
        bg = (l + (bg - l) * (1 - 0.55 * q)) * (1 - 0.32 * q)
    # the character
    draw, mirror = s["draw"], False
    exit_u = 0.0
    if s.get("exit") is not None and t >= s["exit"]:             # Carrick turns and walks straight out
        draw = "ck_side"
        exit_u = (t - s["exit"]) / 0.55
    d, info = CAST.get(draw)
    st = perf.state(s["who"], t, single_resolver(s), s["t"])
    k = EDS * p / info["ed"]
    ex2 = ex + dx + extra_dx
    ey2 = ey + dy - rise * 1.0 * EDS * p + rise * 0.45 * EDS
    if exit_u > 0:
        ex2 += (exit_u ** 1.6) * 1.35 * OW
        ey2 -= abs(math.sin(math.pi * exit_u * 3.2)) * 0.18 * EDS
    kk = k * (1 + 0.012 * jolt)
    Ms = actor_matrix(info, ex2, ey2 - 3 * RS * jolt, kk, mirror, st["lean"], st["sink"])
    lay = np.zeros((OH, OW, 4), np.float32)
    E.place(lay, d, face_state(st, info, mirror), Ms)
    if s.get("hand"):
        raised_hand(lay, s, t, ex2, ey2, EDS * p)
    if exit_u > 0:                                               # moving fast: a little motion blur
        n = int(6 + 30 * min(1.0, exit_u)) | 1
        lay = cv2.filter2D(lay, -1, np.ones((1, n), np.float32) / n)
    img = bg * (1 - lay[..., 3:4]) + lay[..., :3]
    if s.get("clipboard"):
        # Steve's clipboard, held low in front of him (its back to us); lifted a little when he reads it
        down = max(0.0, st["looky"]) if st["looky"] > 0.4 else 0.0
        top = 4.35 if not s["fg"] else 3.75                       # behind a counter: held up where we see it
        img = G.clipboard(img, ex + dx, ey + dy + (top - 0.35 * down) * EDS * p, EDS * p)
    # the table in front of him
    if s["fg"] and s.get("table", 1) > 0:
        fk, mname, fcx, edge, fz, fblur = s["fg"]
        P2 = plate(fk)
        fz2 = fz * p ** 1.1
        s2 = P2.scale(fz2)
        ty = ey + s["table"] * EDS * p + dy * 1.15
        # never below the drawing's own bottom edge (a body must not end in mid-air above the table)
        bottom = Ms[1, 1] * (d.oy + d.size(1.0)[1] / d.S) + Ms[1, 2]
        ty = min(ty, bottom - 10 * RS)
        fcy = edge - (ty - OH / 2) / s2
        fcx2 = fcx - dx * 1.15 / s2
        fimg = P2.render(fcx2, fcy, fz2)
        msk = P2.mask(mname, fcx2, fcy, fz2)
        if fblur > 0:
            fimg = cv2.GaussianBlur(fimg, (0, 0), fblur * RS)
            msk = cv2.GaussianBlur(msk, (0, 0), max(0.8, fblur * 0.5) * RS)
        if q > 0: fimg = fimg * (1 - 0.25 * q)
        img = img * (1 - msk[..., None]) + fimg * msk[..., None]
    return G.grade(img, s["grade"], t)


def cam_at(s, t):
    if s.get("cams"):
        ks = s["cams"]
        k = max([i for i, (tk, _) in enumerate(ks) if tk <= t] or [0])
        if k == 0 and t < ks[0][0]: return ks[0][1]
        if k + 1 < len(ks):                                 # glide between framings
            u = D.ease((t - ks[k][0]) / max(1e-3, ks[k + 1][0] - ks[k][0]))
            return tuple(a + (b - a) * u for a, b in zip(ks[k][1], ks[k + 1][1]))
        return ks[k][1]
    u = D.ease((t - s["t"]) / max(1e-3, s["end"] - s["t"]), s["ease"])
    return tuple(a + (b - a) * u for a, b in zip(s["cam0"], s["cam1"]))


def moving_actor(a, t):
    """a keyframed actor at time t -> (who, drawing, (x, y), ed, mirror, bob px)"""
    ks = a["keys"]
    i = max([j for j, k in enumerate(ks) if k[0] <= t] or [0])
    k0 = ks[i]
    k1 = ks[i + 1] if i + 1 < len(ks) else k0
    _, dr, (x0, y0), e0, mi = k0
    _, dr1, (x1, y1), e1, _ = k1
    if dr1 == dr and k1[0] > k0[0]:
        u = min(1.0, max(0.0, (t - k0[0]) / (k1[0] - k0[0])))
    else:
        u = 0.0
    x, y, ed = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, e0 + (e1 - e0) * u
    moving = abs(x1 - x0) + abs(y1 - y0) > 0.5 and 0 < u < 1 and dr1 == dr
    if any(a0 <= t < a1 for a0, a1 in a.get("still", [])): moving = False
    bob = abs(math.sin(math.pi * (t - ks[0][0]) / 0.28)) * 0.32 * ed * a.get("bob", 0.0) if moving else 0.0
    return a["who"], dr, (x, y - bob), ed, mi, (y if moving else None)


def render_world(s, t):
    P = plate(s["plate"])
    cx, cy, z = cam_at(s, t)
    dx, dy = drift(t, s, s["drift"])
    sc = P.scale(z)
    cx, cy = P.clamp(cx - dx / sc, cy - dy / sc, z)
    bg = P.render(cx, cy, z)
    if s["blur"] > 0: bg = cv2.GaussianBlur(bg, (0, 0), s["blur"] * RS)
    M = P.M(cx, cy, z)
    img = bg.copy()
    # where everyone is on screen (for eyelines)
    pos = {}
    for kind, val in s["layers"]:
        if kind != "actors": continue
        for a in val:
            if isinstance(a, dict): pos[a["who"]] = M[0, 0] * moving_actor(a, t)[2][0] + M[0, 2]
            else: pos[a[0]] = M[0, 0] * a[2][0] + M[0, 2]
    for kind, val in s["layers"]:
        if kind == "occl":
            msk = P.mask(val, cx, cy, z)[..., None]
            img = img * (1 - msk) + bg * msk
            continue
        lay = np.zeros((OH, OW, 4), np.float32)
        for a in val:
            ground = None
            if isinstance(a, dict):
                who, draw, (px, py), ed_p, mirror, ground = moving_actor(a, t)
            else:
                who, draw, (px, py), ed_p, mirror = a
            d, info = CAST.get(draw)
            ex, ey = M[0, 0] * px + M[0, 2], M[1, 1] * py + M[1, 2]
            k = ed_p * sc / info["ed"]
            if isinstance(a, dict) and a.get("shadow") and draw in FEET:     # walking: his shadow on the floor
                fx, fy, fw = FEET[draw]
                ax, ay = info["anchor"]
                gy = ey if ground is None else M[1, 1] * ground + M[1, 2]
                sx = ex + ((ax - fx) if mirror else (fx - ax)) * k
                img = feet_shadow(img, sx, gy + (fy - ay) * k, fw * k)
            st = perf.state(who, t, world_resolver(s, who, pos) if d.has_face else (lambda g: (0, 0, 0)), s["t"])
            Ms = actor_matrix(info, ex, ey, k, mirror, 0.0, 0.0)
            E.place(lay, d, face_state(st, info, mirror), Ms)
        img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    img = G.grade(img, s["grade"], t)
    if s.get("text") == "ext":
        img = G.ext_text(img, t, s["t"], s["end"])
    return img


def render_group(s, t):
    fx, fy, z = cam_at(s, t)
    dx, dy = drift(t, s, s["drift"])
    def S(x, y): return ((x - fx) * z * RS + OW / 2 + dx, (y - fy) * z * RS + OH / 2 + dy)
    # the set behind: blurred, moving less than the characters (parallax)
    pk, cx, cy, zz, blur = s["bg"]
    P = plate(pk)
    s0 = P.scale(zz) / RS
    zb = zz * z ** 0.35
    cxb = cx + (fx - 540) * 0.35 / s0 - dx * 0.6 / P.scale(zb)
    cyb = cy + (fy - 960) * 0.35 / s0 - dy * 0.6 / P.scale(zb)
    cxb, cyb = P.clamp(cxb, cyb, zb)
    img = P.render(cxb, cyb, zb)
    if blur > 0: img = cv2.GaussianBlur(img, (0, 0), blur * RS)
    pos = {who: S(px, py)[0] for who, _, (px, py), _, _ in s["actors"]}
    # the characters, back to front
    lay = np.zeros((OH, OW, 4), np.float32)
    for who, draw, (px, py), ed, mirror in s["actors"]:
        d, info = CAST.get(draw)
        ex, ey = S(px, py)
        st = perf.state(who, t, world_resolver(s, who, pos), s["t"])
        Ms = actor_matrix(info, ex, ey, ed * z * RS / info["ed"], mirror)
        E.place(lay, d, face_state(st, info, mirror), Ms)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    # the table in front of them
    if s["fg"]:
        fk, mname, fcx, edge, fz, fblur = s["fg"]
        P2 = plate(fk)
        fz2 = fz * z ** 1.1
        s2 = P2.scale(fz2)
        ty = S(0, s["table_y"])[1] + dy * 0.15
        fcy = edge - (ty - OH / 2) / s2
        fcx2 = fcx + (fx - 540) * RS * 1.1 / P2.scale(fz) - dx * 1.15 / s2
        fimg = P2.render(fcx2, fcy, fz2)
        msk = P2.mask(mname, fcx2, fcy, fz2)
        if fblur > 0:
            fimg = cv2.GaussianBlur(fimg, (0, 0), fblur * RS)
            msk = cv2.GaussianBlur(msk, (0, 0), max(0.8, fblur * 0.5) * RS)
        img = img * (1 - msk[..., None]) + fimg * msk[..., None]
    return G.grade(img, s["grade"], t)


# ---------------------------------------------------------------- the match
def render_corner(s, t):
    """a corner swung in from the flag: the pitch plate with a push, the ball's arc into the box"""
    P = plate("PITCH")
    u = (t - s["t"]) / max(1e-3, s["end"] - s["t"])
    cx, cy, z = (380 + 40 * D.ease(u), 930 - 50 * D.ease(u), 1.12 + 0.1 * D.ease(u))
    dx, dy = drift(t, s, 0.6)
    sc = P.scale(z)
    cx, cy = P.clamp(cx - dx / sc, cy - dy / sc, z)
    img = P.render(cx, cy, z)
    M = P.M(cx, cy, z)
    # the ball: whipped in from beside the flag, curling up and across into the goalmouth, smaller as it goes
    tk = s["t"] + (0.55 if s["n"] == 1 else 0.12)
    fl = 1.0 if s["n"] == 1 else 0.85
    v = (t - tk) / fl
    if 0 <= v <= 1.05:
        def at(v):
            v = min(1.0, max(0.0, v))
            x0, y0, x1, y1 = 178, 1466, 592, 742               # 1x plate px: the corner arc -> the six-yard box
            x = x0 + (x1 - x0) * v + 40 * math.sin(math.pi * v)
            y = y0 + (y1 - y0) * v - 260 * math.sin(math.pi * v)
            return M[0, 0] * x + M[0, 2], M[1, 1] * y + M[1, 2], (40 - 28 * v) * sc
        img = G.ball(img, [at(v - j * 0.018) for j in range(6)])
    return G.grade(img, "pitch", t)


def render_goal(s, t):
    """the net bulges off screen: the Hull end on its feet (a rough handheld push on the stand), the score"""
    P = plate("PITCH")
    u = (t - s["t"]) / max(1e-3, s["end"] - s["t"])
    cx, cy, z = 470, 300 - 10 * D.ease(u), 2.1 + 0.25 * D.ease(u)
    dx, dy = shake(t, 14.0)
    sc = P.scale(z)
    cx, cy = P.clamp(cx - dx / sc, cy - dy / sc, z)
    img = P.render(cx, cy, z)
    img = cv2.GaussianBlur(img, (0, 0), 1.2 * RS)
    img = G.grade(img, "pitch", t)
    return G.goal_board(img, t, s["t"], s["n"])


def render_tigers(s, t):
    """the Tigers song over the pitch: the scoreboard, then the reactions, fast"""
    t0 = s["t"]
    u = t - t0
    k = max([i for i, (tt, _) in enumerate(D.TIGERS) if tt <= u] or [0])
    t1 = t0 + D.TIGERS[k][0]
    t2 = t0 + D.TIGERS[k + 1][0] if k + 1 < len(D.TIGERS) else s["end"]
    kind = D.TIGERS[k][1]
    base = dict(i=s["i"] * 7 + k, t=t1, end=t2, kind="single", grade="pitch", table=0, fg=None, punch=None,
                bg=("PITCH", 470, 330, 1.9, 6.0))
    if kind == "board":
        P = plate("PITCH")
        z = 1.25 + 0.1 * D.ease((t - t1) / (t2 - t1))
        img = G.grade(P.render(330, 620, z), "pitch", t)
        return G.tigers_board(img, t, t1)
    if kind == "mg":
        sh = dict(base, who="mg", draw="mg_hero", ed=190, eye=(540, 720), push=(1.0, 1.06), drift=0.3)
    elif kind == "mn":
        sh = dict(base, who="mn", draw="mn_g_crossed", ed=185, eye=(560, 740), push=(1.0, 1.05), drift=0.3)
    elif kind == "sh":
        sh = dict(base, who="sh", draw="sh_hero", ed=150, eye=(540, 640), push=(1.0, 1.05), drift=0.3, clipboard=True)
    elif kind == "br":
        sh = dict(base, who="br", draw="br_hero", ed=190, eye=(540, 760), push=(1.0, 1.05), drift=0.3)
    else:                                                        # Carrick walking away down the touchline
        P = plate("PITCH")
        img = P.render(470, 520, 1.5)
        img = cv2.GaussianBlur(img, (0, 0), 4.0 * RS)
        v = (t - t1) / max(1e-3, t2 - t1)
        d, info = CAST.get("ck_back")
        ed = (150 - 60 * v) * RS
        ex, ey = OW * 0.5 + 40 * RS * v, OH * (0.40 - 0.08 * v) - abs(math.sin(math.pi * v * 3.5)) * 0.2 * ed
        k = ed / info["ed"]
        img = feet_shadow(img, ex, ey + (526 - info["anchor"][1]) * k, 185 * k)
        lay = np.zeros((OH, OW, 4), np.float32)
        E.place(lay, d, {}, actor_matrix(info, ex, ey, k))
        img = img * (1 - lay[..., 3:4]) + lay[..., :3]
        return G.grade(img, "pitch", t)
    return render_single(sh, t)


def render_frame(f):
    t = f / FPS
    s = D.shot_at(t)
    kind = s["kind"]
    if kind == "black":
        img = G.captions(np.zeros((OH, OW, 3), np.float32), t, D.CAPTIONS)
    elif kind == "title":
        img = G.title_card(t, s["t"])
    elif kind == "score":
        img = G.score_card(t, s["t"])
    elif kind == "corner":
        img = render_corner(s, t)
    elif kind == "goal":
        img = render_goal(s, t)
    elif kind == "tigers":
        img = render_tigers(s, t)
    elif kind == "single":
        img = render_single(s, t)
    elif kind == "group":
        img = render_group(s, t)
    else:
        img = render_world(s, t)
    # whip pan: the camera swings across the cut (the outgoing shot leaves to the left, the new one arrives from
    # the right), with a directional motion blur; the frame edge is extended, never wrapped round
    for tw in D.WHIPS:
        a = 1 - abs(t - tw) * FPS / 3.0
        if a > 0:
            n = max(3, int(110 * RS * a)) | 1
            ker = np.ones((1, n), np.float32) / n
            img = cv2.filter2D(img, -1, ker, borderType=cv2.BORDER_REFLECT)
            sh = (t - tw) * FPS * 70 * RS
            z = 1 + 2.2 * abs(sh) / OW                           # zoom just enough that no edge shows
            img = cv2.warpAffine(img, np.float32([[z, 0, OW / 2 * (1 - z) + sh], [0, z, OH / 2 * (1 - z)]]),
                                 (OW, OH), borderMode=cv2.BORDER_REPLICATE)
    if kind not in ("black", "title", "score"):
        img = G.captions(img, t, D.CAPTIONS)
        img = G.finish(img, f)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def main():
    cmd = sys.argv[1]
    if cmd == "still":
        os.makedirs("build/stills", exist_ok=True)
        for a in sys.argv[2:]:
            t = float(a)
            img = render_frame(int(round(t * FPS)))
            cv2.imwrite(f"build/stills/still_{t:06.2f}.jpg", img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
            print("still", t)
    elif cmd == "chunk":
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                              "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            p.stdin.write(render_frame(f).tobytes())
            if (f - a) % 60 == 0: print(f"frame {f}/{b}", flush=True)
        p.stdin.close(); p.wait()


if __name__ == "__main__":
    main()
