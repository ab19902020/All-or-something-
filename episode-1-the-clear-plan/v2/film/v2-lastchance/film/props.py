"""The door (The Handover's, episodes/the-handover/film/props.py): the boardroom door opening on a lit corridor, and
Ole walking into the doorway (his walk cycle, to the right, then he stops on the threshold, turns to them and
waves). Drawn in the house look from the plate's own door. And the episode's credits after the end title.

  plate_image("O")       the boardroom with the door open
  plate_image("D"/"DO")  the door's end of the room at 8x (closed / open): the closer shots by the door are filmed
                         in it at true scale, so Ole and Carrick are the size the room says they are. 1x "D px" are
                         half a plate px: d(x, y) = (2 (x - DX0), 2 (y - DY0))
  doorway(...)           the world layer of the wide door shot: the door shut, opening, open; Ole in it
  credits(...)           the episode's credits on black"""
import functools
import json
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

from film import cards as C
from studio.film import engine as E
from studio.film.cast import CAST
from studio.film.engine import OH, OW, RS
from studio.paths import BACKGROUNDS, BUILD, CHARACTERS
from film.timeline import TL

S = C.S
X0, Y0, X1, Y1 = 1158, 220, 1252, 466          # the door leaf, 1x plate px (hinge on the right)
VP = (836.0, 330.0)                            # the room's vanishing point
DEPTH = 564.0                                  # camera to the back wall, in plate px at the wall
OPEN_DEG = 80.0
OLE_H = 203.0                                  # Ole's height, head top to soles (plate px): a little shorter than
CARRICK_H = 216.0                              # Carrick (1.78 m against 1.88 m) and well inside the 2.1 m door
FLOOR = 466.0                                  # the threshold: where his feet are, walking in and standing
OLE_X = 1205.0                                 # the middle of the doorway
DX0, DY0, DX1, DY1 = 860, 110, 1460, 590       # the door's end of the room, filmed at 8x (plate "D")


def d(x, y):
    """plate px -> D px"""
    return (2.0 * (x - DX0), 2.0 * (y - DY0))


def m(k):
    return TL["marks"][k]


# ---------------------------------------------------------------- the plate, its door and the corridor
@functools.lru_cache(maxsize=1)
def base_plate():
    from studio.episode.upscale import upscaled
    return upscaled(BACKGROUNDS / "club/boardroom.png", 4.0)[..., ::-1].copy()      # RGB uint8, 4x


@functools.lru_cache(maxsize=1)
def corridor():
    """what is behind the door, 4x px over the leaf's box: a lit corridor wall (warm, brighter than the room), a
    dado rail, a skirting and floor, the right-hand jamb's inner face in shadow, and the light falling off at the
    sides. RGB float 0..1"""
    w, h = (X1 - X0) * 4, (Y1 - Y0) * 4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / w, yy / h
    top, low = np.float32([0.93, 0.87, 0.77]), np.float32([0.80, 0.72, 0.62])
    img = top + (low - top) * v[..., None]
    img *= (0.80 + 0.20 * np.exp(-((u - 0.45) / 0.42) ** 2))[..., None]               # the light, from the left
    img += np.float32([0.10, 0.08, 0.04]) * np.exp(-((u - 0.45) / 0.3) ** 2 - (v / 0.12) ** 2)[..., None]
    rail = (np.abs(v - 0.60) < 0.006)
    img[rail] = np.float32([0.45, 0.34, 0.26])
    img[v > 0.60] *= np.float32([0.93, 0.92, 0.92])
    floor = v > 0.935
    img[floor] = np.float32([0.42, 0.33, 0.27])
    img[np.abs(v - 0.935) < 0.004] = np.float32([0.16, 0.13, 0.12])
    jamb = u > 0.90                                                                    # the jamb's inner face
    img[jamb] = np.float32([0.38, 0.34, 0.31]) * (0.85 + 0.15 * (1 - v[jamb]))[:, None]
    img[np.abs(u - 0.90) < 0.006] = np.float32([0.12, 0.10, 0.10])
    img[:, :6] *= 0.55                                                                 # the left edge, in shadow
    return np.clip(img, 0, 1)


@functools.lru_cache(maxsize=1)
def leaf():
    """the door leaf's picture (RGB uint8, 4x): the plate's door, with its bottom (hidden by the chairs) carried down
    from the plain panel above the glass"""
    big = base_plate()
    x0, x1, y0, y1 = X0 * 4, X1 * 4, Y0 * 4, Y1 * 4
    im = big[y0:y1, x0:x1].copy()
    plain = np.median(big[(Y0 + 6) * 4:(Y0 + 30) * 4, x0:x1].astype(np.float32), axis=0).astype(np.uint8)
    cut = (398 - Y0) * 4                       # the chair backs start at y 398
    im[cut:] = plain[None]
    return im


def opening(t):
    """0 (shut) .. 1 (open at OPEN_DEG): the latch, a tiny give, then the swing"""
    if t < m("swing"):
        return 0.0
    u = min(1.0, (t - m("swing")) / 0.75)
    return 1 - (1 - u) ** 3


def leaf_quad(a):
    """the leaf's corners (TL, TR, BR, BL; 1x plate px) open by a (0..1): turning on its right-hand hinge towards
    the camera"""
    th = math.radians(OPEN_DEG * a)
    xw = X1 - (X1 - X0) * math.cos(th)
    f = 1.0 / (1.0 - (X1 - X0) * math.sin(th) / DEPTH)
    px = VP[0] + (xw - VP[0]) * f
    return np.float32([[px, VP[1] + (Y0 - VP[1]) * f], [X1, Y0], [X1, Y1], [px, VP[1] + (Y1 - VP[1]) * f]])


def plate_image(k):
    if k in ("D", "DO"):
        return door_end(k)
    if k != "O":
        return None
    return open_plate()


@functools.lru_cache(maxsize=1)
def open_plate():
    big = base_plate().copy()
    big[Y0 * 4:Y1 * 4, X0 * 4:X1 * 4] = (corridor() * 255 + 0.5).astype(np.uint8)
    # the chairs in front of the doorway stay where they are
    from film.direction import CHAIR_A, CHAIR_B
    keep = np.zeros(big.shape[:2], np.uint8)
    for poly in (CHAIR_A, CHAIR_B):
        cv2.fillPoly(keep, [np.int32(np.float32(poly) * 4)], 1)
    big[keep > 0] = base_plate()[keep > 0]
    lf = leaf().astype(np.float32) / 255 * (1 - 0.35 * math.sin(math.radians(OPEN_DEG)))
    h, w = lf.shape[:2]
    H = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), leaf_quad(1.0) * 4)
    warped = cv2.warpPerspective(np.dstack([lf, np.ones((h, w), np.float32)]), H, (big.shape[1], big.shape[0]),
                                 flags=cv2.INTER_LINEAR, borderValue=0)
    al = np.ascontiguousarray(warped[..., 3])
    from film.direction import CHAIR_C
    cv2.fillPoly(al, [np.int32(np.float32(CHAIR_C) * 4)], 0)
    al = al[..., None]
    out = big.astype(np.float32) / 255 * (1 - al) + warped[..., :3] * al
    return (out * 255 + 0.5).astype(np.uint8)


def door_end(k):
    """the door's end of the room (DX0..DX1, DY0..DY1) at 8x, door shut ("D") or open ("DO"): Real-ESRGAN once more on
    the 4x plate brought down to 2x, cached in the episode's build folder -> RGB uint8 (its "4x" level is 8x)"""
    from studio.film import ep
    out = ep.path("plates", f"{k}.png")
    if out.exists():
        return cv2.imread(str(out))[..., ::-1].copy()
    from studio.episode.upscale import x4
    src = base_plate() if k == "D" else open_plate()
    crop = src[DY0 * 4:DY1 * 4, DX0 * 4:DX1 * 4]
    half = cv2.resize(crop, (crop.shape[1] // 2, crop.shape[0] // 2), interpolation=cv2.INTER_AREA)
    big = x4(np.ascontiguousarray(half[..., ::-1]))                        # BGR in, BGR out
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), big)
    return big[..., ::-1].copy()


# ---------------------------------------------------------------- Ole
@functools.lru_cache(maxsize=8)
def walk_frame(i):
    """walk-0i (1..6), upscaled 4x and cached in build/film/ole-gunnar-solskjaer/ -> (premultiplied RGBA float,
    4x px per sheet px)"""
    out = BUILD / "film" / "ole-gunnar-solskjaer" / f"walk-{i:02d}.png"
    if not out.exists():
        from studio.film.art import upscale_rgba
        src = np.asarray(Image.open(CHARACTERS / "ole-gunnar-solskjaer" / "reference" / f"walk-{i:02d}.png").convert("RGBA"))
        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(upscale_rgba(src)).save(out)
    a = np.asarray(Image.open(out)).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    return a


def _warp(dst, pm, A):
    lay = cv2.warpAffine(pm, A, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return lay


def _ole_state(t, t0):
    from film.direction import EYES
    from film.perf import PERF

    def res(g):
        if g == "cam":
            return (0.0, 0.0, 0.0)
        if g == "down":
            return (0.08, 0.85, 0.0)
        if isinstance(g, tuple) and g[0] == "dir":
            return g[1:]
        return EYES["ole"].get(g, (0.0, 0.05, 0.0))
    st = PERF.state("ole", t, res, t0)
    return st


def ole_layer(t, s, M):
    """Ole in the doorway at time t (premultiplied RGBA float, screen) and whether he is still in the corridor
    (clipped to the doorway). One size throughout: OLE_H tall, his feet on the threshold"""
    ta, tb = m("walk"), m("stop")
    if t < ta:
        return None, True
    if t < tb:                                    # walking in from the left, the cycle at 9 frames a second
        u = (t - ta) / (tb - ta)
        x = (X0 - 62) + (OLE_X - (X0 - 62)) * (1 - (1 - u) ** 1.6)
        k = int((t - ta) * 9) % 6 + 1
        pm = walk_frame(k)
        s4 = OLE_H * 0.985 / (269 * 4)            # plate px per 4x walk px: the walk frames are 269 sheet px tall at
        ys, xs = np.nonzero(pm[..., 3] > 0.5)     # their tallest, a walking man 1.5 % under his standing height
        cx4, by4 = (xs.min() + xs.max()) / 2, ys.max()
        A = np.float32([[s4 * M[0, 0], 0, 0], [0, s4 * M[1, 1], 0]])
        A[0, 2] = M[0, 0] * (x - cx4 * s4) + M[0, 2]
        A[1, 2] = M[1, 1] * (FLOOR - by4 * s4) + M[1, 2]
        return _warp(None, pm, A), True
    # stopped on the threshold, turned to them: the wave
    from studio.film.cast import feet
    key = "ole-gunnar-solskjaer:wave"
    d_, info = CAST.get(key)
    st = _ole_state(t, s["t"])
    l0 = info["look0"]
    st = dict(st, lookx=max(-1.2, min(1.2, st["lookx"] + l0[0])), looky=max(-0.8, min(1.0, st["looky"] + l0[1])),
              turn=max(-0.9, min(0.9, st["turn"])))
    kp = OLE_H / CAST.spec("ole-gunnar-solskjaer")["drawings"]["wave"]["stand_h"]      # plate px per sheet px
    fx, fy = feet(key)
    kk = kp * M[0, 0]                             # screen px per sheet px
    ex = M[0, 0] * OLE_X + M[0, 2]
    ey = M[1, 1] * FLOOR + M[1, 2]
    Ms = np.float64([[kk, 0, ex - kk * fx], [0, kk, ey - kk * fy]])
    lay = np.zeros((OH, OW, 4), np.float32)
    E.place(lay, d_, st, Ms)
    return lay, False


def doorway(img, s, t, M, sc):
    """the door shots' own layer, under the actors: the door shut (the plate), opening, open, and Ole"""
    a = opening(t)
    if a <= 0 and t < m("walk"):
        return img
    M = np.float32(M)
    # the corridor in the doorway
    cor = corridor()
    A = np.float32([[M[0, 0] / 4, 0, M[0, 0] * X0 + M[0, 2]], [0, M[1, 1] / 4, M[1, 1] * Y0 + M[1, 2]]])
    c = cv2.warpAffine(np.dstack([cor, np.ones(cor.shape[:2], np.float32)]), A, (OW, OH), flags=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    img = img * (1 - c[..., 3:4]) + c[..., :3] * c[..., 3:4]
    # a little of the corridor's light falls into the room
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    gx, gy = M[0, 0] * 1205 + M[0, 2], M[1, 1] * 470 + M[1, 2]
    glow = np.exp(-(((xx - gx) / (150 * M[0, 0])) ** 2 + ((yy - gy) / (90 * M[0, 0])) ** 2)) * (1 - c[..., 3]) * a
    img = img + glow[..., None] * np.float32([0.10, 0.08, 0.05])
    # Ole
    lay, inside = ole_layer(t, s, M)
    if lay is not None:
        if inside:                                # still in the corridor: only the doorway shows him
            lay = lay * c[..., 3:4]
        img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    # the leaf, swinging in (darker as it turns from the light)
    if a > 0:
        lf = leaf().astype(np.float32) / 255 * (1 - 0.35 * math.sin(math.radians(OPEN_DEG * a)))
        h, w = lf.shape[:2]
        q = leaf_quad(a)
        scr = np.float32([[M[0, 0] * x + M[0, 2], M[1, 1] * y + M[1, 2]] for x, y in q])
        H = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), scr)
        wl = cv2.warpPerspective(np.dstack([lf, np.ones((h, w), np.float32)]), H, (OW, OH), flags=cv2.INTER_LINEAR,
                                 borderValue=0)
        img = img * (1 - wl[..., 3:4]) + wl[..., :3] * wl[..., 3:4]
    return img


# ---------------------------------------------------------------- the credits
CREDITS = [
    ("ALL OR SOMETHING", "BEBAS", 120, (255, 255, 255)),
    ("EPISODE ONE: THE CLEAR PLAN", "BEBAS", 70, (236, 236, 236)),
    ("", None, 30, None),
    ("An animated parody. Real results; the private scenes and dialogue are fictionalised.", "INTER", 34, (210, 210, 210)),
    ("", None, 30, None),
    ("THE CAST (ALL PARODY)", "BEBAS", 56, (255, 255, 255)),
    ("Michael Carrick  ·  Bruno Fernandes  ·  Harry Maguire  ·  Lisandro Martínez", "INTER", 32, (200, 200, 200)),
    ("Matheus Cunha  ·  Benjamin Šeško  ·  Mason Mount  ·  Shea Lacey (off camera)", "INTER", 32, (200, 200, 200)),
    ("Kobbie Mainoo  ·  Joshua Zirkzee  ·  Jason Wilcox  ·  Omar Berrada  ·  Ole Gunnar Solskjær", "INTER", 32,
     (200, 200, 200)),
    ("Sir Jim Ratcliffe  ·  Joel Glazer  ·  Avram Glazer  ·  The Narrator  ·  The Producer", "INTER", 32, (200, 200, 200)),
    ("", None, 30, None),
    ("Every voice: Fish Audio, cloned from the show's own character recordings. Not the real people.", "INTER", 32,
     (200, 200, 200)),
    ("Results: mufcinfo.com, soccerbase.com, manutd.com. Como interviews paraphrased from Reuters, RTÉ, Sky Sports.",
     "INTER", 30, (200, 200, 200)),
]


@functools.lru_cache(maxsize=1)
def _credit_roll():
    h = 1100
    im = Image.new("RGBA", (OW, S(h)), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    y = 0
    for text, fn, size, col in CREDITS:
        if text:
            f = C.font({"BEBAS": C.BEBAS, "INTER": C.INTER}[fn], size, 500 if fn == "INTER" else None)
            C.draw_text(dr, (OW / 2, S(y)), text, f, col + (255,), track=2 if fn == "BEBAS" else 0, anchor="c")
        y += size * 1.45
    return C.premult(im), y


def credits(s, t):
    """the credits on black, one card, centred; no next-week tease"""
    roll, H = _credit_roll()
    y0 = (OH - S(H)) / 2 - S(80)
    img = np.zeros((OH, OW, 3), np.float32)
    return C.paste(img, roll, 0, int(y0 + S(80)), C.sm((t - s["t"]) / 0.6))
