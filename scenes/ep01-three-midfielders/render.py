"""Render Episode 1, "Three Midfielders": 1080 x 1920 (9:16), 30 fps.

  python3 render.py still 3.5 12 40          -> build/stills/still_<t>.jpg (single frames)
  python3 render.py chunk A B out.mp4        -> frames [A, B) encoded without audio (for parallel rendering)
  EP_RES=540x960 python3 render.py ...       -> quick low-res previews
Each frame: the shot at that time (direction.py) -> the set, the characters with their face / body state
(perf.py) and the furniture in front of them -> grade -> graphics -> vignette and grain."""
import os, sys, math, subprocess, numpy as np, cv2
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
        return D.EYES[who].get(g, (0.0, 0.0, 0.0))
    return res


# eyelines inside the world shots: (viewer, target) -> (lookx, looky, turn) on screen
W_EYES = {("ck", "js"): (-0.25, 0.15, -0.05), ("ck", "om"): (0.35, 0.15, 0.1), ("ck", "br"): (-0.95, 0.1, -0.45),
          ("ck", "jr"): (-0.85, 0.25, -0.4), ("br", "ck"): (0.8, -0.05, 0.3), ("br", "jr"): (-0.9, 0.3, -0.5),
          ("br", "js"): (-0.35, 0.3, -0.1), ("br", "om"): (0.1, 0.3, 0.05), ("jr", "ck"): (0.8, -0.1, 0.25),
          ("jr", "br"): (0.9, -0.1, 0.3), ("jr", "js"): (0.4, 0.2, 0.1), ("jr", "om"): (0.6, 0.2, 0.15)}
V_EYES = {("js", "ck"): (0.0, -0.05, 0.0), ("om", "ck"): (0.05, -0.05, 0.0), ("jr", "ck"): (-0.6, 0.0, -0.2),
          ("js", "om"): (-0.9, 0.05, -0.35), ("om", "js"): (0.9, 0.05, 0.35), ("js", "jr"): (0.9, 0.1, 0.3),
          ("om", "jr"): (0.9, 0.1, 0.3), ("jr", "js"): (-0.8, 0.05, -0.3), ("jr", "om"): (-0.9, 0.05, -0.35)}


def world_resolver(s, who):
    tab = W_EYES if s["plate"] == "W" else V_EYES if s["plate"] == "V" else {}     # others: to the lens
    def res(g):
        if g == "cam": return (0.0, 0.0, 0.0)
        if g == "down": return (0.1, 0.85, 0.05)
        if isinstance(g, tuple) and g[0] == "dir": return g[1:]
        return tab.get((who, g), (0.0, 0.05, 0.0))
    return res


# ---------------------------------------------------------------- Jason's three fingers
_HAND = {}


def hand3(lay, s, t, ex, ey, ed, ty):
    """raised on a tracksuit sleeve from behind the table: up on "It's three things", beats on "three" / "two",
    down after "won" (drawn into the character layer, so the table in front still covers the sleeve)"""
    if "d" not in _HAND: _HAND["d"] = E.Drawing("js_hand3", "js_hand3")
    d = _HAND["d"]
    a, b = perf.ls("js_three_things"), perf.le("js_three_things")
    h = G.sm((t - a + 0.12) / 0.26) * (1 - G.sm((t - b + 0.25) / 0.3))
    if h <= 0: return
    words = {w["w"]: a + w["s"] for w in perf.L["js_three_things"]["words"]}
    beat = sum(0.06 * perf.bump((t - words[w]) / 0.28) for w in ("three", "two") if w in words)
    kh = 3.4 * ed / 138
    cx = ex - 1.12 * ed
    cy = ey + 3.95 * ed + (1 - h) * 2.6 * ed - beat * ed
    ang = math.radians(-7)
    # the sleeve: from the cuff down behind the table, leaning out towards the elbow
    w0 = 34 * kh
    top = np.float32([[-w0 / 2, 0], [w0 / 2, 0]])
    bot = np.float32([[w0 * 0.72 - 0.42 * ed, 2.4 * ed], [-w0 * 0.72 - 0.42 * ed, 2.4 * ed]])
    poly = np.concatenate([top, bot])
    R = np.float32([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    poly = poly @ R.T + np.float32([cx, cy])
    sl = np.zeros((OH, OW), np.float32)
    cv2.fillPoly(sl, [np.int32(np.round(poly * 8))], 1.0, cv2.LINE_AA, 3)
    ink = np.zeros((OH, OW), np.float32)
    cv2.polylines(ink, [np.int32(np.round(poly[[1, 2]] * 8)), np.int32(np.round(poly[[3, 0]] * 8))], False, 1.0,
                  max(2, int(4.5 * RS * ed / 138)), cv2.LINE_AA, 3)
    red = np.zeros((OH, OW), np.float32)
    for f in (0.16, 0.28):                                   # the red stripes down the outside of the sleeve
        p0 = poly[0] + (poly[1] - poly[0]) * f; p1 = poly[3] + (poly[2] - poly[3]) * f
        cv2.line(red, tuple(np.int32(np.round(p0 * 8))), tuple(np.int32(np.round(p1 * 8))), 1.0,
                 max(2, int(4 * RS * ed / 138)), cv2.LINE_AA, 3)
    col = np.float32([0.10, 0.13, 0.24])                    # his navy club tracksuit
    rgb = col * sl[..., None]
    rgb = rgb * (1 - red[..., None] * sl[..., None]) + np.float32([0.78, 0.07, 0.10]) * (red * sl)[..., None]
    a_ = np.clip(sl + ink, 0, 1)
    rgb = rgb * (1 - ink[..., None]) + np.float32([0.04, 0.04, 0.05]) * ink[..., None]
    lay[..., :3] = rgb + lay[..., :3] * (1 - a_[..., None])
    lay[..., 3] = a_ + lay[..., 3] * (1 - a_)
    # the hand, its cuff over the sleeve's top
    ax, ay = 1068.0, 1131.0                                  # cuff bottom centre on the sheet
    Mh = np.float64([[kh * math.cos(ang), -kh * math.sin(ang), 0], [kh * math.sin(ang), kh * math.cos(ang), 0]])
    Mh[:, 2] = np.float64([cx, cy]) - Mh[:, :2] @ np.float64([ax, ay])
    E.place(lay, d, {}, Mh)


# standing drawings: feet centre (sheet px) and the shadow's width
FEET = {"jr_hero": (163, 783, 250)}


# ---------------------------------------------------------------- shots
def render_single(s, t):
    u = (t - s["t"]) / max(1e-3, s["end"] - s["t"])
    p = s["push"][0] + (s["push"][1] - s["push"][0]) * D.ease(u)
    if s.get("punch") and t >= s["punch"][0]:          # a snap punch-in on the punchline (3 frames)
        p *= 1 + (s["punch"][1] - 1) * D.ease((t - s["punch"][0]) / 0.1)
    dx, dy = drift(t, s, s["drift"])
    ex, ey = s["eye"]
    F = (ex, ey)
    # the set behind: blurred, zooms less than the character (parallax)
    pk, cx, cy, z, blur = s["bg"]
    P = plate(pk)
    cx, cy, z = zoom_about(P, cx, cy, z, p ** 0.35, F)
    sc = P.scale(z)
    cx, cy = P.clamp(cx - dx * 0.6 / sc, cy - dy * 0.6 / sc, z)
    bg = P.render(cx, cy, z)
    if blur > 0: bg = cv2.GaussianBlur(bg, (0, 0), blur * RS)
    q = s.get("quiet", 0.0) * G.sm((t - s["t"] - 0.2) / 1.2)
    if q > 0:                                                    # the button: the room goes quiet behind him
        l = bg.mean(2, keepdims=True)
        bg = (l + (bg - l) * (1 - 0.55 * q)) * (1 - 0.32 * q)
    # the character
    d, info = CAST.get(s["draw"])
    st = perf.state(s["who"], t, single_resolver(s), s["t"])
    k = s["ed"] * p / info["ed"]
    Ms = actor_matrix(info, ex + dx, ey + dy, k, False, st["lean"], st["sink"])
    lay = np.zeros((OH, OW, 4), np.float32)
    E.place(lay, d, face_state(st, info, False), Ms)
    if s.get("hand3"):
        hand3(lay, s, t, ex + dx, ey + dy, s["ed"] * p, ey + s["table"] * s["ed"] * p + dy * 1.15)
    img = bg * (1 - lay[..., 3:4]) + lay[..., :3]
    # the table in front of him
    if s["fg"]:
        fk, mname, fcx, edge, fz, fblur = s["fg"]
        P2 = plate(fk)
        fz2 = fz * p ** 1.1
        s2 = P2.scale(fz2)
        ty = ey + s["table"] * s["ed"] * p + dy * 1.15
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
    if s.get("paper"):
        img = G.paper(img, t, perf.ls("jr_bigger_issues") - 0.32)
    return G.grade(img, s["grade"], t)


def cam_at(s, t):
    if s.get("cams"):
        ks = s["cams"]
        k = max([i for i, (tk, _) in enumerate(ks) if tk <= t] or [0])
        if k == 0 or t - ks[k][0] >= 0.2: return ks[k][1]
        u = D.ease((t - ks[k][0]) / 0.2)                    # a quick punch between framings
        return tuple(a + (b - a) * u for a, b in zip(ks[k - 1][1], ks[k][1]))
    u = D.ease((t - s["t"]) / max(1e-3, s["end"] - s["t"]), s["ease"])
    return tuple(a + (b - a) * u for a, b in zip(s["cam0"], s["cam1"]))


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
    for kind, val in s["layers"]:
        if kind == "occl":
            msk = P.mask(val, cx, cy, z)[..., None]
            img = img * (1 - msk) + bg * msk
            continue
        lay = np.zeros((OH, OW, 4), np.float32)
        for who, draw, (px, py), ed_p, mirror in val:
            d, info = CAST.get(draw)
            ex, ey = M[0, 0] * px + M[0, 2], M[1, 1] * py + M[1, 2]
            k = ed_p * sc / info["ed"]
            if draw in FEET:                                   # standing: a soft contact shadow on the floor
                fx, fy, fw = FEET[draw]
                ax, ay = info["anchor"]
                sx, sy = ex + (fx - ax) * k, ey + (fy - ay) * k
                sh = np.zeros((OH, OW), np.float32)
                cv2.ellipse(sh, (int(sx), int(sy)), (int(fw * k / 2), int(fw * k * 0.09)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
                sh = cv2.GaussianBlur(sh, (0, 0), max(1.0, fw * k * 0.06))
                img = img * (1 - 0.45 * sh[..., None])
            st = perf.state(who, t, world_resolver(s, who) if d.has_face else (lambda g: (0, 0, 0)), s["t"])
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
    def S(x, y): return ((x - fx) * z + OW / 2 + dx, (y - fy) * z + OH / 2 + dy)
    # the set behind: blurred, moving less than the characters (parallax)
    pk, cx, cy, zz, blur = s["bg"]
    P = plate(pk)
    s0 = P.scale(zz)
    zb = zz * z ** 0.35
    cxb = cx + (fx - OW / 2) * 0.35 / s0 - dx * 0.6 / P.scale(zb)
    cyb = cy + (fy - OH / 2) * 0.35 / s0 - dy * 0.6 / P.scale(zb)
    cxb, cyb = P.clamp(cxb, cyb, zb)
    img = P.render(cxb, cyb, zb)
    if blur > 0: img = cv2.GaussianBlur(img, (0, 0), blur * RS)
    # the characters, back to front
    lay = np.zeros((OH, OW, 4), np.float32)
    for who, draw, (px, py), ed, mirror in s["actors"]:
        d, info = CAST.get(draw)
        ex, ey = S(px, py)
        st = perf.state(who, t, world_resolver(dict(plate="V"), who), s["t"])
        Ms = actor_matrix(info, ex, ey, ed * z / info["ed"], mirror)
        E.place(lay, d, face_state(st, info, mirror), Ms)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    # the table in front of them
    fk, mname, fcx, edge, fz, fblur = s["fg"]
    P2 = plate(fk)
    fz2 = fz * z ** 1.1
    s2 = P2.scale(fz2)
    ty = S(0, s["table_y"])[1] + dy * 0.15
    fcy = edge - (ty - OH / 2) / s2
    fcx2 = fcx + (fx - OW / 2) * 1.1 / P2.scale(fz) - dx * 1.15 / s2
    fimg = P2.render(fcx2, fcy, fz2)
    msk = P2.mask(mname, fcx2, fcy, fz2)
    if fblur > 0:
        fimg = cv2.GaussianBlur(fimg, (0, 0), fblur * RS)
        msk = cv2.GaussianBlur(msk, (0, 0), max(0.8, fblur * 0.5) * RS)
    img = img * (1 - msk[..., None]) + fimg * msk[..., None]
    return G.grade(img, s["grade"], t)


def render_frame(f):
    t = f / FPS
    s = D.shot_at(t)
    if s["kind"] == "black":
        img = np.zeros((OH, OW, 3), np.float32)
    elif s["kind"] == "title":
        img = G.title_card(t, s["t"])
    elif s["kind"] == "single":
        img = render_single(s, t)
    elif s["kind"] == "group":
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
    if s["kind"] in ("single", "world", "group"):
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
