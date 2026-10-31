"""Clear the Air: the sets, props, inserts and captions, drawn in the house look (flat colours, the kits' dark ink
outline) for a portrait film (EP_RES=1080x1920). Text here is in screen px of that frame.

Sets (plate_image): the office from two angles, the same room and the same whiteboard on wheels.
  OF / OF2   documentary/ceo-office, the conversation's angle: CLEAR THE AIR / no leaks on the board (OF2: and the
             tick, RESOLVED)
  OW / OW2   aos/office, the wide angle with the door beside the board; OWD / OWD2 with the door open
Single props: can (Wilcox's blue aerosol and its two puffs), lanyard (Gary's: STANDARDS), card (UNITED BEHIND THE
MANAGER on Wilcox's tablet). World layers: door_jason (Wilcox in the doorway, six inches sideways), door_gary (Gary in
the open door), card_world (the tablet's text on Wilcox in a wide), puff_world (the last accidental spray).
Inserts: tick (RESOLVED), shake (the handshake), clip (Gary's checklist), stamp (SPECIAL MEASURES), end (ALL OR
SOMETHING). overlay: the United Road mark, the place caption and the captions of every line."""
import functools
import json
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from film import cards as C
from film.timeline import TL
from studio.film import ep
from studio.film.engine import OH, OW, RS

INK = (24, 18, 20, 255)
SKIN = (228, 176, 140, 255)
L = json.loads(ep.path("lines.json").read_text())


def m(k):
    return TL["marks"][k]


def fnt(path, px):
    return ImageFont.truetype(path, max(6, int(px)))


def layer():
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def comp(lay, im):
    a = C.premult(im)
    lay[:] = lay * (1 - a[..., 3:4]) + a


# ---------------------------------------------------------------- sets
@functools.lru_cache(maxsize=4)
def _up(name):
    from studio.episode.upscale import upscaled
    from studio.paths import BACKGROUNDS
    return upscaled(BACKGROUNDS / f"{name}.png", 4.0)[..., ::-1].copy()       # RGB uint8, 4x


QUAD_OF = [(1236, 141), (1399, 101), (1399, 414), (1236, 404)]     # the board's white face, 1x plate px
QUAD_OW = [(1043, 213), (1213, 202), (1212, 418), (1044, 416)]
DOOR = [(1339, 150), (1403, 147), (1403, 546), (1339, 548)]       # the door in the wide angle


def board(img4, quad, resolved=False):
    """the board wiped and written on in marker, warped onto its face in the 4x plate"""
    bw, bh = BW, BH
    im = Image.new("RGB", (bw, bh), (241, 242, 240))
    dr = ImageDraw.Draw(im)
    f1, f2, f3 = fnt(C.MARKER, 112), fnt(C.MARKER, 70), fnt(C.MARKER, 86)
    for k, (txt, y) in enumerate((("CLEAR", 70), ("THE AIR", 200))):
        w = dr.textlength(txt, font=f1)
        dr.text(((bw - w) / 2, y), txt, font=f1, fill=(28, 36, 70))
    dr.line([(60, 352), (bw - 60, 346)], fill=(196, 30, 36), width=7)
    w = dr.textlength("no leaks", font=f2)
    dr.text(((bw - w) / 2, 380), "no leaks", font=f2, fill=(196, 30, 36))
    dr.text((70, 540), "1. TALK", font=f2, fill=(28, 36, 70))
    dr.text((70, 640), "2. LISTEN", font=f2, fill=(28, 36, 70))
    dr.text((70, 740), "3. PHOTO", font=f2, fill=(28, 36, 70))
    if resolved:
        dr.line([(70, 880), (120, 935), (210, 830)], fill=(30, 140, 60), width=16, joint="curve")
        dr.text((235, 845), "RESOLVED", font=f3, fill=(30, 140, 60))
    src = np.float32([[0, 0], [bw, 0], [bw, bh], [0, bh]])
    dst = np.float32(quad) * 4
    T = cv2.getPerspectiveTransform(src, dst)
    h, w = img4.shape[:2]
    face = cv2.warpPerspective(np.asarray(im), T, (w, h), flags=cv2.INTER_AREA)
    msk = cv2.warpPerspective(np.full((bh, bw), 255, np.uint8), T, (w, h)).astype(np.float32)[..., None] / 255
    return (img4 * (1 - msk) + face * msk).astype(np.uint8)


BW, BH = 520, 980                                 # the board's own drawing, before it is warped onto the plate


def board_pt(quad, x, y):
    """a point of the board's drawing -> 1x plate px on its face"""
    T = cv2.getPerspectiveTransform(np.float32([[0, 0], [BW, 0], [BW, BH], [0, BH]]), np.float32(quad))
    v = T @ np.float64([x, y, 1.0])
    return v[0] / v[2], v[1] / v[2]


def door_open(img4):
    """the door in the wide angle standing open: a lit corridor beyond, the leaf swung back against the jamb"""
    out = img4.astype(np.float32)
    poly = (np.float32(DOOR) * 4).astype(np.int32)
    x0, y0 = poly[:, 0].min(), poly[:, 1].min()
    x1, y1 = poly[:, 0].max(), poly[:, 1].max()
    yy = np.linspace(0, 1, y1 - y0)[:, None]
    corridor = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
    corridor[:] = np.float32([196, 192, 184])[None, None, :] * (0.8 + 0.2 * yy)[:, :, None]
    corridor[int((y1 - y0) * 0.72):] = np.float32([150, 146, 140])                 # the corridor floor
    corridor[:, :int((x1 - x0) * 0.12)] *= 0.7
    msk = np.zeros(out.shape[:2], np.uint8)
    cv2.fillPoly(msk, [poly], 255)
    sub = msk[y0:y1, x0:x1].astype(np.float32)[..., None] / 255
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - sub) + corridor * sub
    leaf = np.int32([[x0 - 4, y0 - 6], [x0 + 70, y0 + 40], [x0 + 70, y1 - 40], [x0 - 4, y1 + 6]])
    cv2.fillPoly(out, [leaf], (40, 40, 46))
    cv2.polylines(out, [leaf], True, (14, 12, 14), 8, cv2.LINE_AA)
    return np.clip(out, 0, 255).astype(np.uint8)


@functools.lru_cache(maxsize=8)
def plate_image(k):
    if k in ("OF", "OF2"):
        return board(_up("documentary/ceo-office"), QUAD_OF, resolved=k == "OF2")
    if k in ("OW", "OW2", "OWD", "OWD2"):
        img = board(_up("aos/office"), QUAD_OW, resolved=k in ("OW2", "OWD2"))
        return door_open(img) if k.startswith("OWD") else img
    return None


# ---------------------------------------------------------------- people placed by hand
def draw_world_actor(img, s, t, M, sc, who, draw, eye, ed_p, mirror=False):
    """one actor in a world shot by hand (so it can move): eyes at `eye` (plate px), eye distance ed_p (plate px)"""
    from studio.film import engine as E
    from studio.film import render as R
    from studio.film.cast import CAST
    from film.perf import PERF
    d, info = CAST.get(draw)
    ex, ey = M[0, 0] * eye[0] + M[0, 2], M[1, 1] * eye[1] + M[1, 2]
    k = ed_p * sc / info["ed"]
    st = PERF.state(who, t, R.world_resolver(s, who, {who: ex}), s["t"]) if d.has_face and who in PERF.WHO else {}
    Ms = R.actor_matrix(info, ex, ey, k, mirror, st.get("lean", 0.0), st.get("sink", 0.0))
    lay = np.zeros((OH, OW, 4), np.float32)
    E.place(lay, d, R.face_state(st, info, mirror) if st else {}, Ms)
    return img * (1 - lay[..., 3:4]) + lay[..., :3], Ms


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def door_jason(img, s, t, M, sc):
    """Wilcox in the doorway; on `shuffle` he moves six inches sideways (towards the board) and stops, still mostly in
    the doorway"""
    from film.direction import DOOR_JASON
    who, draw, (x, y), ed_p = DOOR_JASON
    u = ease((t - m("shuffle")) / 0.55)
    x -= 24 * u
    y -= 4 * math.sin(math.pi * u)
    img, _ = draw_world_actor(img, s, t, M, sc, who, draw, (x, y), ed_p)
    return img


def door_gary(img, s, t, M, sc):
    """Gary, in the open door: suit, lanyard. He arrives with the bang: a quick step in from beside the door frame and
    a small settle, then stands there, inspecting"""
    from film.direction import DOOR_GARY
    who, draw, (x, y), ed_p = DOOR_GARY
    u = (t - s["t"]) / 0.28
    if u < 1:
        x += 34 * (1 - ease(u)) ** 2
        y -= 5 * math.sin(math.pi * max(0.0, u))
    else:
        y += 1.6 * math.sin(math.pi * min(1.0, (u - 1) / 1.2)) * math.exp(-(u - 1) * 0.8)      # the settle
    img, Ms = draw_world_actor(img, s, t, M, sc, who, draw, (x, y), ed_p)
    return lanyard_at(img, Ms, draw)


def jason_matrix(M, sc, eye, ed_p, draw):
    from studio.film import render as R
    from studio.film.cast import CAST
    d, info = CAST.get(draw)
    ex, ey = M[0, 0] * eye[0] + M[0, 2], M[1, 1] * eye[1] + M[1, 2]
    return R.actor_matrix(info, ex, ey, ed_p * sc / info["ed"])


def card_jason(img, s, t, M, sc):
    """the tablet's text on Wilcox standing behind them (the master's actor)"""
    from film.direction import JW, ED_J, J_CLIP
    return tablet_text(img, jason_matrix(M, sc, JW, ED_J, J_CLIP))


def can_jason(img, s, t, M, sc):
    """the can held up by Wilcox's face, behind them (the master's actor, in the phone pose: an advert)"""
    from film.direction import JW, ED_J, J_PHONE
    return C.over(img, can_layer(jason_matrix(M, sc, JW, ED_J, J_PHONE), t, [], J_PHONE))


def card_world(img, s, t, M, sc):
    """the tablet's text on Wilcox in a wide: drawn with him, from his tuple in the direction"""
    from film.direction import WIDE_JASON
    who, draw, eye, ed_p = WIDE_JASON
    img, Ms = draw_world_actor(img, s, t, M, sc, who, draw, eye, ed_p)
    up = ease((t - s["t"] - 0.35) / 0.4)
    return tablet_text(img, Ms, k=up)


def puff_world(img, s, t, M, sc):
    """Wilcox behind them, the can below the table: one tiny accidental spray"""
    from film.direction import END_JASON
    who, draw, eye, ed_p = END_JASON
    img, Ms = draw_world_actor(img, s, t, M, sc, who, draw, eye, ed_p)
    ex, ey = M[0, 0] * eye[0] + M[0, 2], M[1, 1] * eye[1] + M[1, 2]
    ed = ed_p * sc
    u = (t - m("psst3")) / 0.9
    if 0 <= u <= 1:
        im, dr = layer()
        for k in range(5):
            r = ed * (0.25 + 0.5 * u) * (1 + 0.25 * k)
            cx, cy = ex + ed * (1.6 + 0.35 * k + 0.9 * u), ey + ed * (3.6 - 0.25 * k - 1.2 * u)
            dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 205, 235, int(150 * (1 - u))))
        img = C.over(img, cv2.GaussianBlur(C.premult(im), (0, 0), 3))
    return img


# ---------------------------------------------------------------- Wilcox's tablet, Gary's lanyard
TABLET = [(104, 153), (170, 149), (140, 219), (76, 218)]          # the clipboard pose's tablet face, sheet px


def tablet_layer(Ms):
    """UNITED BEHIND THE MANAGER on the tablet face, warped from sheet px to the screen: premultiplied RGBA"""
    tw, th = 420, 520
    im = Image.new("RGBA", (tw, th), (16, 18, 24, 255))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, tw, 26), fill=(218, 22, 30, 255))
    f = fnt(C.BEBAS, 104)
    for i, w in enumerate(("UNITED", "BEHIND THE", "MANAGER")):
        ww = dr.textlength(w, font=f)
        dr.text(((tw - ww) / 2, 70 + i * 120), w, font=f, fill=(255, 255, 255, 255))
    dr.rectangle((tw / 2 - 90, 440, tw / 2 + 90, 448), fill=(218, 22, 30, 255))
    src = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]])
    dst = np.float32([[Ms[0, 0] * x + Ms[0, 2], Ms[1, 1] * y + Ms[1, 2]] for x, y in TABLET])
    T = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(C.premult(im), T, (OW, OH), flags=cv2.INTER_AREA)


def tablet_text(img, Ms, k=1.0):
    return C.over(img, tablet_layer(Ms), k) if k > 0 else img


def card(lay, s, t, ex, ey, ed, st):
    """UNITED BEHIND THE MANAGER on the tablet of the drawing he is filmed in (from `card_up`, if given)"""
    from studio.film import render as R
    from studio.film.cast import CAST
    d, info = CAST.get(s["draw"])
    Ms = R.actor_matrix(info, ex, ey, ed / info["ed"], s.get("mirror", False), st.get("lean", 0.0),
                        st.get("sink", 0.0))
    k = 1.0 if not s.get("card_up") else ease((t - s["card_up"]) / 0.35)
    if k > 0:
        a = tablet_layer(Ms) * k
        lay[:] = lay * (1 - a[..., 3:4]) + a


def lanyard_layer(Ms, draw):
    """a plain blue lanyard round his neck, the card on his chest: STANDARDS (premultiplied RGBA)"""
    from studio.film.cast import CAST
    import json as _j
    from studio.paths import BUILD
    cid, name = draw.split(":")
    mk = _j.loads((BUILD / "film" / cid / "marks.json").read_text())[name]
    d, info = CAST.get(draw)
    nx, ny = mk["neck"] if mk.get("neck") else (info["anchor"][0], info["anchor"][1] + 2.6 * info["ed"])
    ed = mk["eyes"][1][0] - mk["eyes"][0][0] if mk.get("eyes") else info["ed"]      # the same size on any drawing

    def P(x, y):
        return Ms[0, 0] * x + Ms[0, 2], Ms[1, 1] * y + Ms[1, 2]
    k = Ms[1, 1]
    im, dr = layer()
    w = max(2, int(0.16 * ed * k))
    l0, r0 = P(nx - 0.95 * ed, ny - 0.1 * ed), P(nx + 0.95 * ed, ny - 0.1 * ed)
    bc = P(nx, ny + 1.55 * ed)
    dr.line([l0, bc], fill=(36, 90, 200, 255), width=w)
    dr.line([r0, bc], fill=(36, 90, 200, 255), width=w)
    cw, ch = 1.3 * ed * k, 0.92 * ed * k
    x0, y0 = bc[0] - cw / 2, bc[1]
    dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=max(2, int(0.12 * cw)), fill=(250, 250, 248, 255),
                         outline=INK, width=max(1, int(w * 0.5)))
    dr.rectangle((x0, y0, x0 + cw, y0 + ch * 0.28), fill=(36, 90, 200, 255))
    f = fnt(C.BEBAS, ch * 0.34)
    tw = dr.textlength("STANDARDS", font=f)
    dr.text((bc[0] - tw / 2, y0 + ch * 0.38), "STANDARDS", font=f, fill=(24, 24, 28, 255))
    f2 = fnt(C.INTER, ch * 0.13)
    tw = dr.textlength("INSPECTOR (SELF-APPOINTED)", font=f2)
    dr.text((bc[0] - tw / 2, y0 + ch * 0.76), "INSPECTOR (SELF-APPOINTED)", font=f2, fill=(80, 80, 86, 255))
    return C.premult(im)


def lanyard_at(img, Ms, draw):
    return C.over(img, lanyard_layer(Ms, draw))


def lanyard(lay, s, t, ex, ey, ed, st):
    from studio.film import render as R
    from studio.film.cast import CAST
    d, info = CAST.get(s["draw"])
    Ms = R.actor_matrix(info, ex, ey, ed / info["ed"], s.get("mirror", False), st.get("lean", 0.0),
                        st.get("sink", 0.0))
    a = lanyard_layer(Ms, s["draw"])
    lay[:] = lay * (1 - a[..., 3:4]) + a


CAN = {                                      # the can in his hand (sheet px): x0, y0, x1, y1, nozzle, spray way
    "jason-wilcox:phone": ((37, 30, 67, 104), "up", (-1.0, -0.6)),        # held up by his face, like an advert
    "jason-wilcox:point": ((201, 127, 229, 192), "finger", (1.0, -0.45)),  # at arm's length, finger on the nozzle
}


def can_layer(Ms, t, pssts, draw="jason-wilcox:phone"):
    """the blue air freshener (FRESH) in his hand; a puff from the nozzle on each psst"""
    def P(x, y):
        return Ms[0, 0] * x + Ms[0, 2], Ms[1, 1] * y + Ms[1, 2]
    k = abs(Ms[0, 0])
    (x0, y0, x1, y1), nozzle, (vx, vy) = CAN[draw]
    (ax, ay), (bx, by) = P(x0, y0), P(x1, y1)
    ax, bx = min(ax, bx), max(ax, bx)
    if Ms[0, 0] < 0:
        vx = -vx
    im, dr = layer()
    lw = max(2, int(1.6 * k))
    top = ay + 8 * k if nozzle == "up" else ay
    dr.rounded_rectangle((ax, top, bx, by), radius=int(4 * k), fill=(40, 110, 210, 255), outline=INK, width=lw)
    dr.rectangle((ax + lw, top + 22 * k, bx - lw, top + 44 * k), fill=(250, 250, 250, 255))
    f = fnt(C.BEBAS, 15 * k * (bx - ax) / (30 * k))
    tw = dr.textlength("FRESH", font=f)
    dr.text(((ax + bx) / 2 - tw / 2, top + 25 * k), "FRESH", font=f, fill=(40, 110, 210, 255))
    cx = (ax + bx) / 2
    if nozzle == "up":
        dr.rounded_rectangle((cx - 7 * k, ay, cx + 7 * k, ay + 10 * k), radius=int(2 * k), fill=(220, 220, 226, 255),
                             outline=INK, width=lw)
        nx, ny = cx - 4 * k * (1 if vx < 0 else -1), ay
    else:                                    # the cap is under his fingertip: the spray leaves just past it
        nx, ny = P(228, 121)
    out = C.premult(im)
    for pk in pssts:
        u = (t - pk) / 0.8
        if 0 <= u <= 1:
            im, dr = layer()
            for j in range(6):
                r = k * (5 + 22 * u) * (1 + 0.25 * j)
                px = nx + vx * k * (10 + 12 * j) * (0.5 + u)
                py = ny + vy * k * (10 + 12 * j) * (0.5 + u)
                dr.ellipse((px - r, py - r, px + r, py + r), fill=(160, 210, 240, int(150 * (1 - u) ** 0.8)))
            puff = cv2.GaussianBlur(C.premult(im), (0, 0), max(1.0, 3 * k))
            out = out * (1 - puff[..., 3:4]) + puff
    return out


def can(lay, s, t, ex, ey, ed, st):
    from studio.film import render as R
    from studio.film.cast import CAST
    d, info = CAST.get(s["draw"])
    Ms = R.actor_matrix(info, ex, ey, ed / info["ed"], s.get("mirror", False), st.get("lean", 0.0),
                        st.get("sink", 0.0))
    a = can_layer(Ms, t, s.get("pssts", []), s["draw"])
    lay[:] = lay * (1 - a[..., 3:4]) + a


# ---------------------------------------------------------------- inserts
def plate_view(k, cx, cy, z, blur=0.0):
    from studio.film import render as R
    P = R.plate(k)
    cx, cy = P.clamp(cx, cy, z)
    img = P.render(cx, cy, z)
    if blur > 0:
        img = cv2.GaussianBlur(img, (0, 0), blur)
    return img, P.M(cx, cy, z)


def sleeve(dr, pts, base, stripes=None, w=6):
    dr.polygon(pts, fill=base)
    dr.line(pts + [pts[0]], fill=INK, width=w, joint="curve")
    for (a, b) in stripes or []:
        dr.line([a, b], fill=(200, 28, 34, 255), width=int(w * 2.2))


def tick(s, t):
    """close on the board: a hand in a black tracksuit sleeve ticks it and RESOLVED appears"""
    z = 9.0
    img, M = plate_view("OF", 1318, 262, z)
    u = (t - s["t"]) / max(0.1, s["end"] - s["t"])

    def P(x, y):
        return M[0, 0] * x + M[0, 2], M[1, 1] * y + M[1, 2]
    a, b, c = (P(*board_pt(QUAD_OF, x, y)) for x, y in ((70, 880), (120, 935), (210, 830)))   # where OF2 has it
    path = [a, b, c]
    k = ease((u - 0.1) / 0.35)
    im, dr = layer()
    pts = [a] if k <= 0 else ([a, (a[0] + (b[0] - a[0]) * min(1, 2 * k), a[1] + (b[1] - a[1]) * min(1, 2 * k))] +
                              ([(b[0] + (c[0] - b[0]) * (2 * k - 1), b[1] + (c[1] - b[1]) * (2 * k - 1))] if k > 0.5 else []))
    if len(pts) > 1:
        dr.line(pts, fill=(30, 140, 60, 255), width=int(0.022 * OW), joint="curve")
    rk = ease((u - 0.5) / 0.3)
    if rk > 0:
        x0, y0 = P(*board_pt(QUAD_OF, 235, 845))
        x1b, _ = P(*board_pt(QUAD_OF, 235 + 300, 845))
        f = fnt(C.MARKER, (x1b - x0) / 300 * 86)                       # the size OF2's RESOLVED has on screen
        tw = dr.textlength("RESOLVED", font=f)
        rev = int(tw * rk)
        tmp = Image.new("RGBA", (int(tw) + 10, int(0.13 * OW)), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((0, 0), "RESOLVED", font=f, fill=(30, 140, 60, 255))
        tmp = tmp.crop((0, 0, max(1, rev), tmp.size[1]))
        im.alpha_composite(tmp, (int(x0), int(y0)))
    img = C.over(img, C.premult(im))
    # the hand with the marker, following the pen
    rx, ry = P(*board_pt(QUAD_OF, 235, 845))
    pen = pts[-1] if k < 1 else (rx + (P(*board_pt(QUAD_OF, 520, 845))[0] - rx) * rk, ry + 0.04 * OW)
    hx, hy = pen
    im, dr = layer()
    S = OW / 1080
    sleeve(dr, [(hx + 60 * S, hy + 70 * S), (hx + 520 * S, hy + 380 * S), (hx + 520 * S, hy + 700 * S),
                (hx + 10 * S, hy + 220 * S)], (26, 26, 30, 255),
           [((hx + 120 * S, hy + 130 * S), (hx + 520 * S, hy + 420 * S))], int(6 * S))
    dr.ellipse((hx - 30 * S, hy - 10 * S, hx + 110 * S, hy + 120 * S), fill=SKIN, outline=INK, width=int(6 * S))
    dr.line([(hx, hy), (hx + 60 * S, hy + 50 * S)], fill=(30, 140, 60, 255), width=int(22 * S))
    dr.line([(hx, hy), (hx + 60 * S, hy + 50 * S)], fill=INK, width=int(4 * S))
    return C.over(img, C.premult(im))


HANDS = {"carrick": "michael-carrick/kit/casual/hands", "bruno": "bruno-fernandes/kit/home/hands"}


@functools.lru_cache(maxsize=8)
def kit_hand(who, part, rot, scale):
    """one drawing off the character's kit hand sheet (house style), rotated (degrees, anticlockwise) and scaled
    to screen px: premultiplied float RGBA, and where its wrist is (x, y, height) in that image"""
    import yaml
    from studio.episode.upscale import x4
    from studio.paths import CHARACTERS
    base = CHARACTERS / HANDS[who]
    im = np.array(Image.open(f"{base}.png").convert("RGBA"))
    x, y = yaml.safe_load(open(f"{base}.yaml"))["parts"][part][0]
    n, lab, st, _ = cv2.connectedComponentsWithStats((im[..., 3] > 20).astype(np.uint8), 8)
    X, Y, W, H, _ = st[lab[y, x]]
    pad = 8
    crop = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)
    crop[pad:pad + H, pad:pad + W] = im[Y:Y + H, X:X + W]
    crop[pad:pad + H, pad:pad + W, 3] *= (lab[Y:Y + H, X:X + W] == lab[y, x])
    rgb = x4(cv2.cvtColor(crop[..., :3], cv2.COLOR_RGB2BGR))[..., ::-1]
    al = cv2.resize(crop[..., 3], (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC)
    big = Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), "RGBA").rotate(rot, expand=True,
                                                                                 resample=Image.BICUBIC)
    k = scale / 4
    big = big.resize((int(big.width * k), int(big.height * k)), Image.LANCZOS)
    a = np.asarray(big, np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    side = 0 if rot < 0 else -1                                # the wrist: the first / last opaque columns
    cols = np.nonzero(a[..., 3].max(0) > 0.5)[0]
    c = cols[0] + 6 if side == 0 else cols[-1] - 6
    rows = np.nonzero(a[:, c, 3] > 0.5)[0]
    return a, (float(c), float(rows.mean()), float(rows[-1] - rows[0]))


@functools.lru_cache(maxsize=8)
def kit_hand_pts(who, part, rot, scale):
    """a kit hand drawn upright (wrist at the bottom), rotated `rot` degrees anticlockwise and scaled: premultiplied
    RGBA, its wrist (x, y, width) and its fingertip (x, y) in that image"""
    import yaml
    from studio.episode.upscale import x4
    from studio.paths import CHARACTERS
    base = CHARACTERS / HANDS[who]
    im = np.array(Image.open(f"{base}.png").convert("RGBA"))
    x, y = yaml.safe_load(open(f"{base}.yaml"))["parts"][part][0]
    n, lab, st, _ = cv2.connectedComponentsWithStats((im[..., 3] > 20).astype(np.uint8), 8)
    X, Y, W, H, _ = st[lab[y, x]]
    pad = 8
    crop = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)
    crop[pad:pad + H, pad:pad + W] = im[Y:Y + H, X:X + W]
    mine = lab[Y:Y + H, X:X + W] == lab[y, x]
    crop[pad:pad + H, pad:pad + W, 3] *= mine
    xs = np.nonzero(mine[-4:].any(0))[0]                       # the wrist: the bottom rows
    wrist = (pad + (xs[0] + xs[-1]) / 2, pad + H - 2, xs[-1] - xs[0])
    top = np.nonzero(mine[2])[0]                               # the fingertip: the top rows
    tip = (pad + top.mean(), pad + 2)
    rgb = x4(cv2.cvtColor(crop[..., :3], cv2.COLOR_RGB2BGR))[..., ::-1]
    al = cv2.resize(crop[..., 3], (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC)
    big = Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), "RGBA")
    c0 = (big.width / 2, big.height / 2)
    big = big.rotate(rot, expand=True, resample=Image.BICUBIC)
    c1 = (big.width / 2, big.height / 2)
    k = scale / 4
    big = big.resize((int(big.width * k), int(big.height * k)), Image.LANCZOS)
    a = np.asarray(big, np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def tr(px, py):                                           # sheet px -> the rotated, scaled image
        dx, dy = px * 4 - c0[0], py * 4 - c0[1]
        return ((ca * dx + sa * dy + c1[0]) * k, (-sa * dx + ca * dy + c1[1]) * k)
    return a, (*tr(*wrist[:2]), wrist[2] * scale), tr(*tip)


def fingers(lay, s, t, ex, ey, ed, st):
    """two pointing fingers jab into the frame at him, together: Carrick's (black club tracksuit, red stripe) from
    the bottom left, Bruno's (bare forearm, red kit sleeve) from the bottom right"""
    t0 = s.get("jab", s["t"] + 0.15)
    u = (t - t0) / 0.17
    if u <= 0:
        return
    k = 1.0 + 0.09 * math.sin(math.pi * min(1.0, u)) if u < 1 else 1.0         # a little overshoot, then still
    go = 1 - (1 - min(1.0, u)) ** 3
    lw = max(2, int(9 * OW / 1080))
    for who, part, rot, aim, sleeve_col in (("carrick", "point_R", -38, (-1.3, 1.45), (30, 30, 34, 255)),
                                            ("bruno", "point_L", 38, (2.35, 1.1), None)):   # either side of the tablet
        tall = 2.3 * ed
        a, (wx, wy, ww), (tx, ty) = kit_hand_pts(who, part, rot, round(tall / (207 if who == "carrick" else 157), 3))
        dx, dy = tx - wx, ty - wy
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n                                 # the way the finger points
        gx, gy = ex + aim[0] * ed, ey + aim[1] * ed             # where the fingertip stops: just short of him
        travel = (1 - go) * 2.2 * ed - (k - 1) * 1.5 * ed
        ox, oy = gx - tx - ux * travel, gy - ty - uy * travel   # the hand image's top-left
        im, dr = layer()
        W0, H0 = ox + wx, oy + wy                               # the wrist on screen
        far = (W0 - ux * 3.2 * OH, H0 - uy * 3.2 * OH)
        nx, ny = -uy, ux
        h0, h1 = ww * 0.62, ww * 1.1

        def quad(a0, a1, w0, w1):
            p0 = (W0 - ux * a0, H0 - uy * a0)
            p1 = (W0 - ux * a1, H0 - uy * a1)
            return [(p0[0] + nx * w0, p0[1] + ny * w0), (p1[0] + nx * w1, p1[1] + ny * w1),
                    (p1[0] - nx * w1, p1[1] - ny * w1), (p0[0] - nx * w0, p0[1] - ny * w0)]
        L = 3.2 * OH
        if sleeve_col:                                          # Carrick: the tracksuit sleeve to the cuff
            q = quad(-0.15 * ww, L, h0 * 1.1, h1 * 1.4)
            dr.polygon(q, fill=sleeve_col)
            dr.line(q + [q[0]], fill=INK, width=lw, joint="curve")
            dr.line([(W0 - ux * 0.5 * ww + nx * h0 * 0.55, H0 - uy * 0.5 * ww + ny * h0 * 0.55),
                     (far[0] + nx * h1 * 0.8, far[1] + ny * h1 * 0.8)], fill=(205, 30, 36, 255), width=int(lw * 1.6))
            c = quad(-0.15 * ww, 0.35 * ww, h0 * 1.15, h0 * 1.2)
            dr.polygon(c, fill=(46, 46, 52, 255))
            dr.line(c + [c[0]], fill=INK, width=lw, joint="curve")
        else:                                                   # Bruno: the bare forearm, then the kit sleeve
            q = quad(-0.1 * ww, L, h0, h1 * 1.2)
            dr.polygon(q, fill=hand_skin("bruno"))
            dr.line(q + [q[0]], fill=INK, width=lw, joint="curve")
            sv = quad(1.7 * ww, L, h1 * 1.25, h1 * 1.5)
            dr.polygon(sv, fill=(205, 28, 36, 255))
            dr.line(sv + [sv[0]], fill=INK, width=lw, joint="curve")
            dr.line([sv[0], sv[3]], fill=(250, 250, 250, 255), width=int(lw * 2.2))
        arm = C.premult(im)
        lay[:] = lay * (1 - arm[..., 3:4]) + arm
        x0, y0 = int(round(ox)), int(round(oy))
        H, W = a.shape[:2]
        ys, xs = max(0, y0), max(0, x0)
        ye, xe = min(OH, y0 + H), min(OW, x0 + W)
        if ye > ys and xe > xs:
            hh = a[ys - y0:ye - y0, xs - x0:xe - x0]
            lay[ys:ye, xs:xe] = lay[ys:ye, xs:xe] * (1 - hh[..., 3:4]) + hh


def hand_skin(who):
    """the skin colour the kit hand is painted in, for the forearm"""
    a, _ = kit_hand(who, "thumbs_up_R", 0, 1.0)
    al = a[..., 3]
    rgb = a[..., :3] / np.maximum(al[..., None], 1e-3)
    ok = (al > 0.95) & (rgb.mean(2) > 0.55)
    return tuple(int(round(v * 255)) for v in np.median(rgb[ok], 0)) + (255,)


def shake(s, t):
    """the handshake over the desk, framed below the chest, with the two characters' own kit hands: Carrick's from
    the left in his black club tracksuit, his thumb over the top; Bruno's from the right, bare forearm under the red
    kit sleeve; two firm pumps"""
    S = OW / 1080
    u = t - s["t"]
    push = 1.0 + 0.03 * ease(u / 1.4)
    img, _ = plate_view("OF", 760, 560, 9.0 * push, blur=9)
    img = img * 0.82
    dy = 30 * S * math.sin(u * 2 * math.pi * 2.0) * (1 - ease((u - 0.8) / 0.4))
    cx, cy = 0.5 * OW, 0.44 * OH + dy
    lw = int(9 * S)
    ch, (cwx, cwy, cwh) = kit_hand("carrick", "thumbs_up_R", -90, 3.0 * S * push)
    bh, (bwx, bwy, bwh) = kit_hand("bruno", "thumbs_up_L", 90, 3.55 * S * push)
    c0 = (cx - 100 * S - ch.shape[1] / 2, cy + 22 * S - ch.shape[0] / 2)      # top-left of each hand
    b0 = (cx + 86 * S - bh.shape[1] / 2, cy - 18 * S - bh.shape[0] / 2)
    skin_b = hand_skin("bruno")
    im, dr = layer()

    def limb(wx, wy, wh, fx, fy, fw, fill):
        """a forearm from the wrist (x, y, height) out to (fx, fy) off screen, fw wide there"""
        dx, dy_ = fx - wx, fy - wy
        n = math.hypot(dx, dy_)
        nx, ny = -dy_ / n, dx / n
        h0, h1 = wh * 0.55, fw / 2
        pts = [(wx + nx * h0, wy + ny * h0), (fx + nx * h1, fy + ny * h1), (fx - nx * h1, fy - ny * h1),
               (wx - nx * h0, wy - ny * h0)]
        dr.polygon(pts, fill=fill)
        dr.line(pts + [pts[0]], fill=INK, width=lw, joint="curve")
        return (nx, ny), pts
    # Bruno: the bare forearm, the red kit sleeve with its white trim at the frame's edge
    bwx2, bwy2 = b0[0] + bwx, b0[1] + bwy
    fx, fy = OW + 240 * S, cy + 560 * S
    (nx, ny), _ = limb(bwx2 - 20 * S, bwy2, bwh * 1.1, fx, fy, 330 * S, skin_b)
    sx0, sy0 = bwx2 + (fx - bwx2) * 0.62, bwy2 + (fy - bwy2) * 0.62
    sl = [(sx0 + nx * 190 * S, sy0 + ny * 190 * S), (fx + nx * 220 * S, fy + ny * 220 * S),
          (fx - nx * 220 * S, fy - ny * 220 * S), (sx0 - nx * 190 * S, sy0 - ny * 190 * S)]
    dr.polygon(sl, fill=(205, 28, 36, 255))
    dr.line(sl + [sl[0]], fill=INK, width=lw, joint="curve")
    dr.line([sl[0], sl[3]], fill=(250, 250, 250, 255), width=int(22 * S))
    dr.line([(sl[0][0] + (sl[1][0] - sl[0][0]) * 0.06, sl[0][1] + (sl[1][1] - sl[0][1]) * 0.06),
             (sl[3][0] + (sl[2][0] - sl[3][0]) * 0.06, sl[3][1] + (sl[2][1] - sl[3][1]) * 0.06)], fill=INK, width=lw)
    # Carrick: the tracksuit sleeve to the cuff, the club's red piping down it
    cwx2, cwy2 = c0[0] + cwx, c0[1] + cwy
    fx, fy = -240 * S, cy + 580 * S
    (nx, ny), pts = limb(cwx2 + 40 * S, cwy2, cwh * 1.25, fx, fy, 400 * S, (30, 30, 34, 255))
    k0, k1 = 0.16, 1.0
    q = [(pts[0][0] + (pts[1][0] - pts[0][0]) * k0 - nx * 28 * S, pts[0][1] + (pts[1][1] - pts[0][1]) * k0 - ny * 28 * S),
         (pts[0][0] + (pts[1][0] - pts[0][0]) * k1 - nx * 40 * S, pts[0][1] + (pts[1][1] - pts[0][1]) * k1 - ny * 40 * S)]
    dr.line(q, fill=(205, 30, 36, 255), width=int(14 * S))
    cuff = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * 0.12, pts[0][1] + (pts[1][1] - pts[0][1]) * 0.12),
            (pts[3][0] + (pts[2][0] - pts[3][0]) * 0.12, pts[3][1] + (pts[2][1] - pts[3][1]) * 0.12), pts[3]]
    dr.polygon(cuff, fill=(46, 46, 52, 255))
    dr.line(cuff + [cuff[0]], fill=INK, width=lw, joint="curve")
    a = C.premult(im)
    out = C.over(img, a)
    # the hands: Bruno's behind, Carrick's in front with the thumb over the top
    for h, (x0, y0) in ((bh, b0), (ch, c0)):
        x0, y0 = int(round(x0)), int(round(y0))
        H, W = h.shape[:2]
        ys, xs = max(0, y0), max(0, x0)
        ye, xe = min(OH, y0 + H), min(OW, x0 + W)
        hh = h[ys - y0:ye - y0, xs - x0:xe - x0]
        out[ys:ye, xs:xe] = out[ys:ye, xs:xe] * (1 - hh[..., 3:4]) + hh[..., :3]
    return out


CHECK = [("Doorway", "OBSTRUCTED", False), ("Air", "FRESHENED", True), ("Communication", "TELEVISED", False),
         ("Who's in charge", "?", False)]


def clipboard(t, t0, stamp=None):
    S = OW / 1080
    img, _ = plate_view("OW2", 1150, 470, 5.5, blur=10)
    img = img * 0.6
    im, dr = layer()
    x0, y0, x1, y1 = 120 * S, 300 * S, 960 * S, 1560 * S
    dr.rounded_rectangle((x0, y0, x1, y1), radius=int(28 * S), fill=(150, 104, 62, 255), outline=INK, width=int(8 * S))
    dr.rectangle((x0 + 50 * S, y0 + 70 * S, x1 - 50 * S, y1 - 40 * S), fill=(250, 250, 246, 255), outline=(170, 170, 170, 255))
    dr.rounded_rectangle((x0 + 260 * S, y0 - 30 * S, x1 - 260 * S, y0 + 90 * S), radius=int(16 * S),
                         fill=(200, 202, 208, 255), outline=INK, width=int(7 * S))
    f1, f2, f3 = fnt(C.BEBAS, 72 * S), fnt(C.INTER, 40 * S), fnt(C.MARKER, 52 * S)
    dr.text((x0 + 90 * S, y0 + 120 * S), "STANDARDS INSPECTION", font=f1, fill=(24, 24, 28, 255))
    dr.text((x0 + 90 * S, y0 + 200 * S), "Carrington  ·  Manager's office", font=f2, fill=(90, 90, 96, 255))
    u = t - t0
    for i, (what, verdict, ok) in enumerate(CHECK):
        y = y0 + 330 * S + i * 190 * S
        dr.text((x0 + 90 * S, y), what, font=f2, fill=(24, 24, 28, 255))
        dr.line([(x0 + 90 * S, y + 120 * S), (x1 - 90 * S, y + 120 * S)], fill=(200, 200, 205, 255), width=int(3 * S))
        k = ease((u - 0.15 - 0.33 * i) / 0.25)
        if k > 0:
            col = (30, 140, 60, 255) if ok else (196, 30, 36, 255)
            tmp = Image.new("RGBA", (int(560 * S), int(90 * S)), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), verdict + ("  ✓" if ok else ""), font=f3, fill=col)
            if not ok and verdict != "?":
                td.line([(int(470 * S), int(10 * S)), (int(540 * S), int(70 * S))], fill=col, width=int(9 * S))
                td.line([(int(540 * S), int(10 * S)), (int(470 * S), int(70 * S))], fill=col, width=int(9 * S))
            tmp = tmp.crop((0, 0, max(1, int(tmp.size[0] * k)), tmp.size[1]))
            im.alpha_composite(tmp, (int(x0 + 330 * S), int(y + 30 * S)))
    img = C.over(img, C.premult(im))
    if stamp is not None:
        k = ease((t - stamp) / 0.12)
        if k > 0:
            sc = 1.6 - 0.6 * k
            st = Image.new("RGBA", (int(900 * S), int(300 * S)), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((10 * S, 10 * S, 890 * S, 290 * S), radius=int(24 * S), outline=(200, 24, 32, 255),
                                 width=int(16 * S))
            f = fnt(C.BEBAS, 132 * S)
            for i, w in enumerate(("SPECIAL", "MEASURES")):
                tw = sd.textlength(w, font=f)
                sd.text(((900 * S - tw) / 2, 22 * S + i * 120 * S), w, font=f, fill=(200, 24, 32, 255))
            st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
            st = st.resize((max(1, int(st.size[0] * sc)), max(1, int(st.size[1] * sc))))
            lay = C.premult(st)
            img = C.paste(img, lay * min(1.0, 0.2 + k), int(OW / 2 - st.size[0] / 2), int(0.52 * OH - st.size[1] / 2))
    return img


def clip(s, t):
    """Gary's checklist, filled in without looking up: a hand in a black jacket sleeve writing"""
    img = clipboard(t, s["t"])
    S = OW / 1080
    i = min(3, int((t - s["t"] - 0.15) / 0.33)) if t > s["t"] + 0.15 else 0
    hx = 330 * S + 380 * S * ease(((t - s["t"] - 0.15) % 0.33) / 0.25)
    hy = 300 * S + 330 * S + i * 190 * S + 60 * S
    im, dr = layer()
    sleeve(dr, [(hx + 60 * S, hy + 70 * S), (hx + 420 * S, hy + 330 * S), (hx + 380 * S, hy + 470 * S),
                (hx + 10 * S, hy + 170 * S)], (24, 24, 28, 255), None, int(7 * S))
    dr.ellipse((hx - 50 * S, hy - 20 * S, hx + 100 * S, hy + 130 * S), fill=SKIN, outline=INK, width=int(7 * S))
    dr.line([(hx - 30 * S, hy - 10 * S), (hx + 40 * S, hy + 60 * S)], fill=(30, 30, 34, 255), width=int(16 * S))
    return C.over(img, C.premult(im))


def stamp(s, t):
    return clipboard(t, s["t"] - 2.0, stamp=s["t"] + 0.08)


def end(s, t):
    S = OW / 1080
    img = np.zeros((OH, OW, 3), np.float32)
    im, dr = layer()
    k = ease((t - s["t"] - 0.25) / 0.4)
    f1, f2, f3 = fnt(C.BEBAS, 150 * S), fnt(C.BEBAS, 78 * S), fnt(C.INTER, 30 * S)
    for i, w in enumerate(("ALL OR", "SOMETHING")):
        tw = dr.textlength(w, font=f1)
        dr.text((CAP_X - tw / 2, 0.36 * OH + i * 150 * S), w, font=f1, fill=(255, 255, 255, int(255 * k)))
    dr.rectangle((CAP_X - 140 * S, 0.36 * OH + 330 * S, CAP_X + 140 * S, 0.36 * OH + 338 * S), fill=(218, 22, 30, int(255 * k)))
    tw = dr.textlength("CLEAR THE AIR", font=f2)
    dr.text((CAP_X - tw / 2, 0.36 * OH + 370 * S), "CLEAR THE AIR", font=f2, fill=(236, 236, 236, int(255 * k)))
    for i, w in enumerate(("A United Road Original", "Fictional AI-animated football satire.", "Voices are AI clones.")):
        tw = dr.textlength(w, font=f3)
        dr.text((CAP_X - tw / 2, 0.36 * OH + 500 * S + i * 46 * S), w, font=f3, fill=(170, 170, 176, int(255 * k)))
    return C.over(img, C.premult(im))


# ---------------------------------------------------------------- over the picture
CAP_Y = 0.70                                     # the captions' centre, as a fraction of the height
# the phone's safe area (x 90-900 at 1080 wide: the app's buttons sit down the right): captions and the opening
# mark are centred in it, the captions no wider than it
CAP_X, CAP_W = 495 * OW / 1080, 0.72


def wrap(text, f, dr, maxw):
    """one line if it fits, else two balanced ones (no orphaned last word); None if two lines can't hold it"""
    if dr.textlength(text, font=f) <= maxw:
        return [text]
    words = text.split()
    best = min(range(1, len(words)), key=lambda i: max(dr.textlength(" ".join(words[:i]), font=f),
                                                        dr.textlength(" ".join(words[i:]), font=f)))
    lines = [" ".join(words[:best]), " ".join(words[best:])]
    return lines if max(dr.textlength(ln, font=f) for ln in lines) <= maxw else None


@functools.lru_cache(maxsize=64)
def cap_font(px):
    f = fnt(C.INTER, px)
    try:
        f.set_variation_by_axes([32, 800])                 # optical size (display), weight (extra bold)
    except Exception:
        pass
    return f


def caption(text, dr):
    """the caption's font and lines: 58 px (at 1080 wide), smaller only if two lines can't hold it"""
    S = OW / 1080
    for px in (58, 54, 50, 46, 42):
        f = cap_font(int(px * S))
        lines = wrap(text, f, dr, CAP_W * OW - 14 * S)
        if lines:
            return f, lines, px * S
    return f, [text], px * S


SPLIT = {"A01": 8, "A02": 11}     # the two long lines, captioned in two parts: the second from this word (a sentence)


@functools.lru_cache(maxsize=1)
def captions():
    """[(start, end, text)]: one caption a line, from 50 ms before it to 250 ms after (never over the next one)"""
    out = []
    for lid, v in sorted(TL["lines"].items(), key=lambda kv: kv[1]["start"]):
        words = L[lid]["text"].split()
        if lid in SPLIT:
            k = SPLIT[lid]
            tk = v["start"] + L[lid]["words"][k]["s"] - 0.05
            out += [[v["start"] - 0.05, tk, " ".join(words[:k])], [tk, v["end"] + 0.25, " ".join(words[k:])]]
        else:
            out.append([v["start"] - 0.05, v["end"] + 0.25, L[lid]["text"]])
    for a, b in zip(out, out[1:]):
        a[1] = min(a[1], b[0])
    return [tuple(c) for c in out]


def caption_now(t):
    for a, b, text in captions():
        if a <= t < b:
            return text
    return None


def overlay(img, t, s):
    S = OW / 1080
    if s.get("fingers"):                     # over the desk too: the two of them reach in from the camera's side
        lay = np.zeros((OH, OW, 4), np.float32)
        fingers(lay, s, t, s["eye"][0] * RS, s["eye"][1] * RS, s["ed"] * RS * s["push"][0], None)
        img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    im, dr = layer()
    # the United Road mark, small, at the opening
    if t < 3.4:
        k = ease(t / 0.4) * (1 - ease((t - 3.0) / 0.4))
        f = fnt(C.BEBAS, 40 * S)
        tw = dr.textlength("UNITED ROAD ORIGINAL", font=f)
        dr.rectangle((CAP_X - tw / 2 - 18 * S, 196 * S, CAP_X + tw / 2 + 18 * S, 252 * S), fill=(218, 22, 30, int(230 * k)))
        dr.text((CAP_X - tw / 2, 202 * S), "UNITED ROAD ORIGINAL", font=f, fill=(255, 255, 255, int(255 * k)))
    # the place
    if 0.6 < t < 4.6:
        k = ease((t - 0.6) / 0.35) * (1 - ease((t - 4.2) / 0.4))
        f1, f2 = fnt(C.BEBAS, 64 * S), fnt(C.INTER, 30 * S)
        dr.rectangle((92 * S, 290 * S, 100 * S, 400 * S), fill=(218, 22, 30, int(255 * k)))
        dr.text((118 * S, 286 * S), "CARRINGTON", font=f1, fill=(255, 255, 255, int(255 * k)))
        dr.text((120 * S, 360 * S), "The manager's office. Private.", font=f2, fill=(230, 230, 230, int(255 * k)))
    return C.over(img, C.premult(im))
