"""Part B's sets, props and inserts, drawn in the house look (flat colours, the kit's dark ink outline).

Sets made from the library's (plate_image):
  CW / CW2  the opening's dressing room with its reds taken out (the away room at Como: neutral, cold) and a standing
            whiteboard painted in by the left wall: COMPACT before the match, PRESS / TOGETHER after half-time
  CD        the board corner of the dressing room, neutralised the same way (Carrick's singles)
  CS        a stand turned Como blue (the touchline singles)
  BN        the boardroom at night

Inserts: the Leeds card and the office hands (one tiny clap, the dust, the blue mug), the white mug, the Como cards,
the boards (COMPACT, the half-time rewrite, the tactics cartoon, the arrows), the pen's click, Maguire and the cap,
the laptop (CLEAR PLAN - FINAL - FINAL 2; A PLAN), the dark mug, the credits.
World layers: gather (Carrick last out of the room), movers (everyone for the door, and back), corridor (Bruno one way,
Carrick the other, the board rolling through). Single props: mic (the reporter's), mics (the press-room desk).
overlay: the paraphrase cards, the PARODY DIALOGUE label, the lens lowered."""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

from film import cards as C
from film.timeline import TL
from studio.film.engine import OH, OW, RS

S = C.S
SKIN, INK = (228, 176, 140, 255), (24, 18, 20, 255)


def m(k):
    return TL["marks"][k]


def plate_view(k, cx, cy, z, blur=0.0):
    from studio.film import render as R
    P = R.plate(k)
    cx, cy = P.clamp(cx, cy, z)
    img = P.render(cx, cy, z)
    if blur > 0:
        img = cv2.GaussianBlur(img, (0, 0), blur * RS)
    return img


def zoom(img, z, fx=0.5, fy=0.5):
    if abs(z - 1) < 1e-3:
        return img
    M = cv2.getRotationMatrix2D((OW * fx, OH * fy), 0, z)
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def lw():
    return max(2, S(6))


def poly(dr, pts, fill, w=None):
    pts = [(S(x), S(y)) for x, y in pts]
    dr.polygon(pts, fill=fill)
    dr.line(pts + [pts[0]], fill=INK, width=w or lw(), joint="curve")


def layer():
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


# ---------------------------------------------------------------- sets
@functools.lru_cache(maxsize=4)
def _up(name):
    from studio.episode.upscale import upscaled
    from studio.paths import BACKGROUNDS
    return upscaled(BACKGROUNDS / f"{name}.png", 4.0)[..., ::-1].copy()       # RGB uint8, 4x


def neutral(img):
    """take the club's reds out: saturated red becomes a cold slate grey (the wood, orange, is left alone), and
    everything is a touch cooler"""
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    dh = np.minimum(h, 180 - h)                                  # distance from red (OpenCV hue 0..180)
    red = np.clip(1 - (dh - 3) / 5, 0, 1) * np.clip((s - 100) / 60, 0, 1)
    red = cv2.GaussianBlur(red.astype(np.float32), (0, 0), 3)
    hsv[..., 0] = h * (1 - red) + 108 * red
    hsv[..., 1] = s * (1 - red) + s * 0.2 * red
    hsv[..., 2] = v * (1 - 0.15 * red)
    out = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    out = out * np.float32([0.97, 0.99, 1.03])
    return np.clip(out, 0, 255).astype(np.uint8)


def blue(img):
    """a red stand turned Como blue"""
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s = hsv[..., 0], hsv[..., 1]
    red = (((h < 12) | (h > 168)) & (s > 60)).astype(np.float32)
    red = cv2.GaussianBlur(red, (0, 0), 2)
    hsv[..., 0] = h * (1 - red) + 108 * red
    hsv[..., 1] = s * (1 - 0.25 * red)
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB)


def painted_board(img, words):
    """a standing whiteboard on wheels painted into a 4x plate by the left wall (plate px 300-540 x 255-560)"""
    k = 4
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 300 * k, 255 * k, 540 * k, 470 * k
    ink = (20, 20, 24)
    for lx in (x0 + 30 * k, x1 - 30 * k):                                  # the legs and the wheels
        dr.rectangle((lx - 4 * k, y1, lx + 4 * k, 600 * k), fill=(70, 72, 78), outline=ink, width=2 * k)
        dr.ellipse((lx - 9 * k, 594 * k, lx + 9 * k, 610 * k), fill=(30, 30, 34))
    dr.rectangle((x0 + 30 * k, 560 * k, x1 - 30 * k, 566 * k), fill=(70, 72, 78), outline=ink, width=2 * k)
    dr.rectangle((x0, y0, x1, y1), fill=(225, 228, 230), outline=ink, width=4 * k)
    dr.rectangle((x0 + 6 * k, y0 + 6 * k, x1 - 6 * k, y1 - 6 * k), fill=(242, 243, 242))
    f = C.ImageFont.truetype(C.MARKER, 34 * k)
    y = y0 + 22 * k
    for text, col in words:
        tw = dr.textlength(text, font=f)
        dr.text(((x0 + x1) / 2 - tw / 2, y), text, font=f, fill=col)
        y += 46 * k
    for i in range(5):                                                      # magnets: red facing blue
        dr.ellipse((x0 + (40 + 30 * i) * k, y1 - 50 * k, x0 + (52 + 30 * i) * k, y1 - 38 * k), fill=(200, 30, 36))
        dr.ellipse((x0 + (40 + 30 * i) * k, y1 - 30 * k, x0 + (52 + 30 * i) * k, y1 - 18 * k), fill=(30, 80, 190))
    return np.asarray(im)


@functools.lru_cache(maxsize=8)
def plate_image(k):
    if k == "CW":
        return painted_board(neutral(_up("aos/locker-room-wide")), [("COMPACT", (40, 46, 70))])
    if k == "CW2":
        return painted_board(neutral(_up("aos/locker-room-wide")),
                             [("COMPACT", (150, 156, 170)), ("PRESS", (40, 46, 70)), ("TOGETHER", (196, 30, 36))])
    if k == "CD":
        return neutral(_up("documentary/locker-room"))
    if k == "CS":
        return blue(_up("stadiums/red-seated"))
    if k == "BN":
        b = _up("club/boardroom").astype(np.float32) / 255
        lum = b.mean(2, keepdims=True)
        b = (lum + (b - lum) * 0.6) * np.float32([0.42, 0.46, 0.62]) * 0.75
        return (np.clip(b, 0, 1) * 255).astype(np.uint8)
    return None


# ---------------------------------------------------------------- people who move
def draw_actors(img, s, t, M, sc, acts):
    """actors in a world shot at positions that change with t: [(who, drawing, (x, y) feet, height px, mirror)]"""
    from studio.film import engine as E
    from studio.film import render as R
    from studio.film.cast import CAST
    from film.perf import PERF
    full = [(w, d, xy, 0.0, mi, {"stand": h}) for w, d, xy, h, mi in acts]
    pos = {a[0]: M[0, 0] * R.stand_at(a)[0] + M[0, 2] for a in full}
    lay = np.zeros((OH, OW, 4), np.float32)
    for a in sorted(full, key=lambda a: a[2][1]):
        who, draw, _, _, mirror = a[:5]
        d, info = CAST.get(draw)
        px, py, ed_p = R.stand_at(a)
        ex, ey = M[0, 0] * px + M[0, 2], M[1, 1] * py + M[1, 2]
        k = ed_p * sc / info["ed"]
        st = PERF.state(who, t, R.world_resolver(s, who, pos), s["t"]) if d.has_face and who in PERF.WHO else {}
        Ms = R.actor_matrix(info, ex, ey, k, mirror, st.get("lean", 0.0), st.get("sink", 0.0))
        E.place(lay, d, R.face_state(st, info, mirror) if st else {}, Ms)
    return img * (1 - lay[..., 3:4]) + lay[..., :3]


def walk(p0, p1, t, t0, t1, bob=6.0):
    """a position along a walk from p0 to p1 between t0 and t1, with a small step bob (plate px)"""
    u = min(1.0, max(0.0, (t - t0) / max(1e-3, t1 - t0)))
    e = u * u * (3 - 2 * u)
    x, y = p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e
    if 0 < u < 1:
        y -= bob * abs(math.sin((t - t0) * math.pi * 3.4))
    return x, y


def movers(img, s, t, M, sc):
    """the pen clicks; everyone goes for the door (the back left); Carrick's line; they shuffle back"""
    from film.direction import GO, HEIGHT, px_per_m
    acts = []
    for who, draw, a, b in GO:
        if t < m("cut_hold"):
            x, y = walk(a, b, t, m("cut_go") + 0.06, m("cut_go") + 0.75, 5.0)
        else:
            x, y = walk(b, a, t, m("cut_hold") + 0.7, m("cut_hold") + 2.0, 4.0)
        acts.append((who, draw, (x, y), HEIGHT.get(who, 1.8) * px_per_m(y), False))
    return draw_actors(img, s, t, M, sc, acts)


def gather(img, s, t, M, sc):
    """the dressing room after Leeds: the last of them gone; Carrick walks out towards the door, back to us"""
    from film.direction import C_BACK, HEIGHT, px_per_m
    x, y = walk((880, 660), (520, 528), t, s["t"] + 0.3, s["end"] + 0.4, 4.0)
    return draw_actors(img, s, t, M, sc, [("carrick", C_BACK, (x, y), HEIGHT["carrick"] * px_per_m(y), False)])


# the corridor: the far doors' floor at y 640 (2.1 m doors 295 px tall there); camera 1.6 m up
def cpx(y):
    return (y - 416.0) / 1.6


def corridor(img, s, t, M, sc):
    """Bruno walks towards us and out of the frame on the left; Carrick walks away to the far doors; their steps
    overlap and stop; then the tactics board rolls through the middle, its reverse to us"""
    from film.direction import DRAW, C_BACK
    t0 = s["t"]
    acts = []
    bx, by = walk((760, 690), (180, 1000), t, t0 + 0.2, t0 + 3.0, 7.0)
    acts.append(("bruno", DRAW["bruno"], (bx, by), 1.79 * cpx(by), False))
    cx, cy = walk((1060, 760), (1430, 642), t, t0 + 0.1, t0 + 3.2, 5.0)
    if t < t0 + 3.25:
        acts.append(("carrick", C_BACK, (cx, cy), 1.76 * cpx(cy), False))
    img = draw_actors(img, s, t, M, sc, acts)
    if t >= m("board_roll"):
        u = (t - m("board_roll")) / 3.6
        x = 1900 - 2300 * u
        img = rolling_board(img, M, x, 790, t)
    return img


def rolling_board(img, M, x, y, t):
    """a whiteboard on wheels at plate x (its middle), its wheels on the floor at plate y; its reverse says the
    opening's four words; a pair of legs walks behind it"""
    h = 1.85 * cpx(y)
    w = 1.25 * cpx(y)
    X = lambda v: M[0, 0] * v + M[0, 2]
    Y = lambda v: M[1, 1] * v + M[1, 2]
    im, dr = layer()
    wob = 2.0 * math.sin(t * 9)
    bx0, bx1 = X(x - w / 2), X(x + w / 2)
    top, bot = Y(y - h), Y(y - h * 0.33)
    fy = Y(y)
    # the legs behind it (grey trousers, black shoes)
    for k, dx in enumerate((-0.12, 0.08)):
        ph = math.sin(t * 7 + k * math.pi) * 0.06
        lx = X(x + (dx + ph) * w)
        dr.rectangle((lx - 0.06 * w * M[0, 0], bot, lx + 0.06 * w * M[0, 0], fy - 0.04 * h * M[1, 1]),
                     fill=(92, 94, 104, 255), outline=INK, width=lw())
        dr.ellipse((lx - 0.1 * w * M[0, 0], fy - 0.07 * h * M[1, 1], lx + 0.12 * w * M[0, 0], fy),
                   fill=(18, 18, 20, 255))
    for lx in (bx0 + 0.12 * (bx1 - bx0), bx1 - 0.12 * (bx1 - bx0)):
        dr.rectangle((lx - S(5), bot, lx + S(5), fy - S(10)), fill=(80, 82, 88, 255), outline=INK, width=lw() // 2)
        dr.ellipse((lx - S(13), fy - S(20), lx + S(13), fy + S(4)), fill=(22, 22, 26, 255))
    dr.rectangle((bx0, top + wob, bx1, bot + wob), fill=(236, 238, 238, 255), outline=INK, width=lw())
    f = C.font(C.MARKER, (bot - top) / RS * 0.13)
    words = ["CLARITY", "ALIGNMENT", "SUSTAINABILITY", "AGILITY"]
    for i, wd in enumerate(words):
        tw = dr.textlength(wd, font=f)
        dr.text(((bx0 + bx1) / 2 - tw / 2, top + wob + (bot - top) * (0.1 + 0.21 * i)), wd, font=f,
                fill=(40, 46, 70, 255))
    return C.over(img, C.premult(im))


# ---------------------------------------------------------------- the office inserts
def office_bg(cx=900, cy=300, z=2.4):
    return plate_view("OF", cx, cy, z, 8.0) * 0.85


def sleeve_track(dr, pts):
    poly(dr, pts, (26, 26, 30, 255))


def hand(dr, cx, cy, r, ang=0.0, fill=SKIN):
    """a flat cartoon hand (palm and four fingers together, thumb) centred at (cx, cy), r = its half length"""
    ca, sa = math.cos(ang), math.sin(ang)
    base = [(-0.55, -0.45), (0.35, -0.55), (0.95, -0.35), (1.0, 0.15), (0.6, 0.55), (-0.45, 0.6), (-0.7, 0.1)]
    pts = [(cx + r * (x * ca - y * sa), cy + r * (x * sa + y * ca)) for x, y in base]
    poly(dr, pts, fill)
    for f in (-0.15, 0.15):
        a = (cx + r * (0.35 * ca - f * sa), cy + r * (0.35 * sa + f * ca))
        b = (cx + r * (0.9 * ca - f * sa), cy + r * (0.9 * sa + f * ca))
        dr.line([(S(a[0]), S(a[1])), (S(b[0]), S(b[1]))], fill=(196, 140, 108, 255), width=max(1, S(4)))


def capsule(cx, cy, L, Wd, ang, n=28):
    """a rounded capsule (a finger, a thumb, a palm) centred at (cx, cy), L long, Wd wide, along angle ang"""
    pts = []
    r = Wd / 2
    hl = max(0.0, L / 2 - r)
    for k in range(n + 1):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((hl + r * math.cos(a), r * math.sin(a)))
    for k in range(n + 1):
        a = math.pi / 2 + math.pi * k / n
        pts.append((-hl + r * math.cos(a), r * math.sin(a)))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def fill(dr, pts, col, w=None):
    poly(dr, pts, col, w)


def open_hand(dr, cx, cy, size, ang, mirror=False, cuff=(26, 26, 30, 255), stripe=(200, 30, 36, 255)):
    """an open cartoon hand seen from the side (fingers together, thumb up), the wrist at (cx, cy), pointing along
    ang; a tracksuit cuff behind the wrist"""
    ca, sa = math.cos(ang), math.sin(ang)
    sg = -1 if mirror else 1
    P = lambda u, v: (cx + u * size * ca - sg * v * size * sa, cy + u * size * sa + sg * v * size * ca)
    fill(dr, capsule(*P(-0.55, 0.0), 0.9 * size, 0.62 * size, ang), cuff)
    if stripe:
        fill(dr, capsule(*P(-0.55, -0.24), 0.9 * size, 0.08 * size, ang), stripe, w=1)
    fill(dr, capsule(*P(0.35, 0.02), 1.05 * size, 0.5 * size, ang), SKIN)                    # palm and fingers
    for k in (-0.1, 0.06):                                                                   # the finger lines
        a, b = P(0.45, k), P(0.82, k)
        dr.line([(S(a[0]), S(a[1])), (S(b[0]), S(b[1]))], fill=(196, 140, 108, 255), width=max(1, S(3)))
    fill(dr, capsule(*P(0.18, -0.3), 0.42 * size, 0.2 * size, ang - sg * 0.7), SKIN)       # the thumb


def fist(dr, cx, cy, size, ang, mirror=False, sleeve=None):
    """a closed cartoon fist round something, its middle at (cx, cy): the palm, four knuckled fingers curled
    across the front, the thumb over them"""
    ca, sa = math.cos(ang), math.sin(ang)
    sg = -1 if mirror else 1
    P = lambda u, v: (cx + u * size * ca - sg * v * size * sa, cy + u * size * sa + sg * v * size * ca)
    if sleeve:
        fill(dr, capsule(*P(-0.95, 0.0), 1.2 * size, 0.72 * size, ang), sleeve)
    fill(dr, capsule(*P(-0.15, 0.0), 1.0 * size, 0.85 * size, ang), SKIN)
    for k in range(4):                                                                       # the fingers
        fill(dr, capsule(*P(0.28, -0.3 + 0.2 * k), 0.42 * size, 0.24 * size, ang), SKIN, w=max(2, S(4)))
    fill(dr, capsule(*P(0.08, -0.42), 0.5 * size, 0.22 * size, ang + sg * 0.35), SKIN)     # the thumb


def clap(s, t):
    """Wilcox's hands (his tracksuit cuffs): they come together once, softly, and stop"""
    u = t - s["t"]
    img = office_bg()
    gap = 150 - 140 * math.sin(min(1.0, max(0.0, (u - 0.25) / 0.4)) * math.pi)
    im, dr = layer()
    open_hand(dr, 960 - gap / 2 - 250, 600, 300, -0.25, mirror=False)
    open_hand(dr, 960 + gap / 2 + 250, 600, 300, math.pi + 0.25, mirror=True)
    return C.over(img, C.premult(im))


def brush(s, t):
    """the clap turned into brushing dust off his track trousers"""
    u = t - s["t"]
    img = office_bg(700, 420, 2.6)
    im, dr = layer()
    poly(dr, [(560, 300), (1360, 300), (1440, 1080), (480, 1080)], (24, 24, 28, 255))     # the thigh
    dr.rectangle((S(1300), S(300), S(1330), OH), fill=(200, 30, 36, 255))                # the stripe
    x = 900 + 140 * math.sin(u * 7.5)
    sleeve_track(dr, [(x + 60, 300), (x + 300, 140), (x + 420, 320), (x + 160, 470)])
    hand(dr, x, 560, 150, ang=math.pi / 2 + 0.2)
    return C.over(img, C.premult(im))


def desk_top(img, y0=560):
    yy = np.arange(OH, dtype=np.float32)[:, None]
    desk = (yy > S(y0)).astype(np.float32)
    wood = np.float32([0.46, 0.28, 0.15]) * (0.85 + 0.15 * (yy / OH))[..., None]
    img = img * (1 - desk[..., None]) + wood * desk[..., None]
    img[S(y0):S(y0) + S(4)] *= 0.45
    return img


def mug_shape(dr, x, y, w, h, body, inside=(150, 104, 66, 255)):
    """a mug, its rim at y (top), w wide, h tall (1920 layout px), its handle on the right"""
    dr.ellipse((S(x + w * 0.8), S(y + h * 0.25), S(x + w * 1.35), S(y + h * 0.8)), outline=INK, width=S(w * 0.12))
    dr.ellipse((S(x + w * 0.8), S(y + h * 0.25), S(x + w * 1.35), S(y + h * 0.8)), outline=body, width=S(w * 0.07))
    dr.rectangle((S(x), S(y), S(x + w), S(y + h)), fill=body)
    dr.ellipse((S(x), S(y + h - w * 0.13), S(x + w), S(y + h + w * 0.13)), fill=body)
    dr.line([(S(x), S(y)), (S(x), S(y + h))], fill=INK, width=lw())
    dr.line([(S(x + w), S(y)), (S(x + w), S(y + h))], fill=INK, width=lw())
    dr.arc((S(x), S(y + h - w * 0.13), S(x + w), S(y + h + w * 0.13)), 0, 180, fill=INK, width=lw())
    dr.ellipse((S(x), S(y - w * 0.13), S(x + w), S(y + w * 0.13)), fill=tuple(int(c * 0.9) for c in body[:3]) + (255,),
               outline=INK, width=lw())
    dr.ellipse((S(x + w * 0.07), S(y - w * 0.09), S(x + w * 0.93), S(y + w * 0.09)), fill=inside)


def bluemug(s, t):
    """Berrada's hand (a navy suit cuff) slides a sky-blue mug off the desk and out of the frame"""
    u = t - s["t"]
    img = desk_top(office_bg(1200, 300, 2.4), 600)
    dx = -1300 * C.sm((u - 0.35) / 0.9)
    im, dr = layer()
    mug_shape(dr, 860 + dx, 520, 200, 230, (110, 186, 232, 255))
    poly(dr, [(1080 + dx, 640), (1300 + dx, 560), (1920, 520), (1920, 760), (1120 + dx, 760)], (30, 34, 58, 255))
    dr.rectangle((S(1080 + dx), S(640)), fill=None) if False else None
    poly(dr, [(1060 + dx, 650), (1110 + dx, 640), (1135 + dx, 760), (1085 + dx, 768)], (245, 245, 245, 255))
    fist(dr, 1050 + dx, 690, 120, math.pi + 0.1, mirror=True)
    return C.over(img, C.premult(im))


def whitemug(s, t):
    """the white mug, alone on an otherwise empty table"""
    u = (t - s["t"]) / max(0.1, s["end"] - s["t"])
    img = desk_top(office_bg(880, 260, 2.2) * 0.8, 640)
    im, dr = layer()
    mug_shape(dr, 840, 520, 230, 260, (250, 250, 250, 255))
    img = C.over(img, C.premult(im))
    return zoom(img, 1.0 + 0.05 * u, 0.5, 0.6)


# ---------------------------------------------------------------- cards
def card_leeds(s, t):
    return C.result_card(t, s["t"], "LEEDS", 0, 1, "UNITED", top="18 OCTOBER 2026  |  PREMIER LEAGUE",
                         foot="35'  MBEUMO", flip=(m("flip_leeds"), 1, 1, "MBEUMO 35'  ·  CALVERT-LEWIN 51'"))


def card_como(s, t):
    return C.chapter_card(t, s["t"], "COMO", "21 OCTOBER 2026", "Europe. An away night by the lake.")


def goal_card(s, t, minute, scorer, hs, as_, foot2=""):
    return C.result_card(t, s["t"], "COMO", hs, as_, "UNITED", top=f"{minute}  |  {scorer}", foot="", foot2=foot2)


def card_g1(s, t):
    return goal_card(s, t, "2'", "NICO PAZ", 1, 0)


def card_ht(s, t):
    return C.result_card(t, s["t"], "COMO", 1, 0, "UNITED", top="HALF-TIME", foot="PAZ 2'")


def card_g2(s, t):
    return goal_card(s, t, "49'", "DOUVIKAS", 2, 0)


def card_g3(s, t):
    return goal_card(s, t, "57'", "PAZ", 3, 0)


def card_g4(s, t):
    return goal_card(s, t, "76'", "RAMÓN", 4, 0)


def card_g5(s, t):
    return C.result_card(t, s["t"], "COMO", 4, 1, "UNITED", top="90+1'  |  ZIRKZEE", foot="")


def card_ft(s, t):
    return C.result_card(t, s["t"], "COMO", 4, 1, "UNITED", top="FULL TIME  |  21 OCTOBER 2026",
                         foot="PAZ 2', 57'  ·  DOUVIKAS 49'  ·  RAMÓN 76'", foot2="UNITED: ZIRKZEE 90+1'")


# ---------------------------------------------------------------- boards
RED_M, BLUE_M = (205, 30, 36), (30, 80, 190)
COMPACT_RED = [(700, 560), (820, 560), (940, 560), (1060, 560), (760, 680), (880, 680), (1000, 680), (820, 800),
               (940, 800), (880, 900)]
BLUE_FACE = [(760, 300), (940, 260), (1120, 300), (850, 400), (1030, 400)]


def board_compact(s, t):
    """COMPACT, in a pen that is almost dry; the red magnets packed in a block, the blue ones facing them"""
    u = t - s["t"]
    img = C.board_surface().copy()
    lay = C._marker_text("COMPACT", 150, C.INK, -2.0).copy()
    rng = np.random.default_rng(5)
    dry = cv2.resize(rng.random((24, 120)).astype(np.float32), (lay.shape[1], lay.shape[0]))
    lay *= (0.35 + 0.65 * (dry > 0.42))[..., None]
    img = C.paste(img, lay, S(170), S(120))
    for x, y in COMPACT_RED:
        img = C.magnet(img, x + 300, y - 40, 30, RED_M)
    for x, y in BLUE_FACE:
        img = C.magnet(img, x + 300, y + 20, 30, BLUE_M)
    return zoom(img, 1.0 + 0.04 * u / max(0.1, s["end"] - s["t"]), 0.45, 0.45)


def board_ht(s, t):
    """half-time: COMPACT crossed out, PRESS written; a hesitation; TOGETHER under it"""
    img = C.board_surface().copy()
    lay = C._marker_text("COMPACT", 150, C.INK, -2.0)
    img = C.paste(img, lay, S(170), S(120), 0.7)
    if t > s["t"] + 0.25:
        img = C.arrow(img, (180, 230), (180 + 700 * C.sm((t - s["t"] - 0.25) / 0.4), 205), t, -1, 0, C.INK_RED, 12) \
            if False else img
        u = C.sm((t - s["t"] - 0.25) / 0.4)
        msk = np.zeros((OH, OW), np.float32)
        cv2.line(msk, (S(190), S(235)), (S(190 + 680 * u), S(205)), 1.0, S(14), cv2.LINE_AA)
        img = img * (1 - msk[..., None]) + np.float32(C.INK_RED) / 255 * msk[..., None]
    img = C.write(img, "PRESS", 230, 330, 170, t, m("w_press"), 1.0, C.INK, rot=1.5)
    img = C.write(img, "TOGETHER", 180, 560, 170, t, m("w_together"), 1.4, C.INK_RED, rot=-1.0)
    for x, y in COMPACT_RED:
        img = C.magnet(img, x + 420, y - 40, 26, RED_M)
    if m("w_press") - 0.2 < t < m("w_press") + 1.2:
        u = (t - m("w_press")) / 1.0
        img = C.hand_marker(img, 280 + 480 * min(1, max(0, u)), 470, k=1.0)
    elif m("w_together") - 0.2 < t < m("w_together") + 1.6:
        u = (t - m("w_together")) / 1.4
        img = C.hand_marker(img, 240 + 760 * min(1, max(0, u)), 700, k=1.0)
    elif m("w_press") + 1.2 <= t <= m("w_together") - 0.2:                     # the hesitation: the hand hovers
        img = C.hand_marker(img, 760 + 6 * math.sin(t * 5), 600, k=1.0)
    return img


def tactic(s, t):
    """the tactics cartoon (a whiteboard pitch): two red magnets step forward to press; the rest stay behind; a blue
    one runs into the space between them; the ball follows; an arrow to goal"""
    u = t - s["t"]
    img = C.board_surface().copy()
    # pitch lines (the halfway line, the box and the goal at the bottom)
    msk = np.zeros((OH, OW), np.float32)
    cv2.rectangle(msk, (S(260), S(120)), (S(1660), S(1000)), 1.0, max(2, S(6)))
    cv2.line(msk, (S(260), S(140)), (S(1660), S(140)), 1.0, max(2, S(4)))
    cv2.rectangle(msk, (S(700), S(780)), (S(1220), S(1000)), 1.0, max(2, S(6)))
    cv2.rectangle(msk, (S(860), S(990)), (S(1060), S(1040)), 1.0, max(2, S(8)))
    img = img * (1 - 0.8 * msk[..., None]) + np.float32([0.15, 0.17, 0.25]) * 0.8 * msk[..., None]
    reds = [(600, 520), (820, 520), (1100, 520), (1320, 520), (700, 700), (920, 700), (1150, 700), (1350, 700),
            (860, 860), (1060, 860)]
    press = C.sm((u - 0.3) / 0.7)
    for i, (x, y) in enumerate(reds):
        if i in (1, 2):                                   # the two who go
            y -= 230 * press
        img = C.magnet(img, x, y, 30, RED_M)
    run = C.sm((u - 1.1) / 0.9)
    bx, by = 960, 300 + 420 * run
    img = C.magnet(img, bx, by, 30, BLUE_M)
    img = C.magnet(img, 1240, 300, 30, BLUE_M)
    img = C.magnet(img, 700, 280, 30, BLUE_M)
    ball = C.sm((u - 1.6) / 0.6)
    cx, cy = 1240 + (bx - 1240) * ball, 330 + (by + 30 - 330) * ball
    cv2.circle(img, (S(cx), S(cy)), S(12), (0.05, 0.05, 0.05), -1, cv2.LINE_AA)
    cv2.circle(img, (S(cx), S(cy)), S(8), (0.97, 0.97, 0.97), -1, cv2.LINE_AA)
    img = C.arrow(img, (960, 760), (960, 960), t, s["t"] + 2.4, 0.5, C.INK_RED, 10)
    return img


def board_arrows(s, t):
    """his board: an arrow for everyone; only two magnets went along theirs"""
    img = C.board_surface().copy()
    reds = [(600, 640), (820, 640), (1100, 640), (1320, 640), (700, 820), (920, 820), (1150, 820), (1350, 820),
            (860, 960), (1060, 960)]
    for i, (x, y) in enumerate(reds):
        img = C.arrow(img, (x, y - 40), (x, y - 290), t, -1, 0, C.INK, 8)
    for i, (x, y) in enumerate(reds):
        if i in (1, 2):
            y -= 300
        img = C.magnet(img, x, y, 30, RED_M)
    u = (t - s["t"]) / max(0.1, s["end"] - s["t"])
    return zoom(img, 1.0 + 0.05 * u)


# ---------------------------------------------------------------- the pen, the cap
def pen_hand(img, x, y, press):
    """a click pen held upright, close: the thumb comes down on its button (press 0..1); an index finger round the
    barrel; the tracksuit sleeve at the bottom right"""
    im, dr = layer()
    top = y - 330
    fill(dr, [(x - 34, top + 40), (x + 34, top + 40), (x + 34, y + 620), (x - 34, y + 620)], (34, 42, 74, 255))
    fill(dr, [(x + 30, top + 60), (x + 52, top + 60), (x + 52, top + 300), (x + 30, top + 300)], (196, 198, 206, 255))
    by = top - 10 + 26 * press                                     # the button
    fill(dr, [(x - 18, by - 40), (x + 18, by - 40), (x + 18, top + 42), (x - 18, top + 42)], (210, 212, 220, 255))
    fill(dr, capsule(x - 30, y + 260, 230, 92, 0.08), SKIN)                     # the index finger round it
    fill(dr, capsule(x + 300, y + 420, 620, 300, -1.0), (26, 26, 30, 255))       # the sleeve
    fill(dr, capsule(x + 170, y + 170, 520, 260, -1.05), SKIN)                   # the hand
    tip = (x + 6, by - 50)
    ang = math.atan2(tip[1] - (y + 140), tip[0] - (x + 300))
    L = math.hypot(tip[0] - (x + 300), tip[1] - (y + 140))
    fill(dr, capsule((tip[0] + x + 300) / 2, (tip[1] + y + 140) / 2, L, 120, ang), SKIN)      # the thumb
    nx, ny = tip[0] + 40 * math.cos(ang + math.pi), tip[1] + 40 * math.sin(ang + math.pi)
    fill(dr, capsule(nx, ny, 70, 64, ang), (240, 200, 176, 255), w=max(2, S(3)))           # its nail
    return C.over(img, C.premult(im))


def pen_click(s, t):
    u = t - s["t"]
    img = plate_view("CD", 500, 330, 2.6, 8.0) * 0.8
    press = 1.0 if 0.32 < u < 0.45 else 0.0
    return pen_hand(img, 900, 520, press)


def pen_click2(s, t):
    u = t - s["t"]
    img = plate_view("CS", 900, 330, 2.2, 9.0) * 0.85
    press = 1.0 if 0.40 < u < 0.52 else 0.0
    return pen_hand(img, 960, 540, press)


def cap(s, t):
    """Maguire's big hands, still trying to make the dry marker work: the cap comes off in his hand"""
    u = t - s["t"]
    img = plate_view("CW2", 1000, 380, 2.8, 8.0) * 0.85
    im, dr = layer()
    pull = C.sm((u - 0.75) / 0.12)
    jig = 6 * math.sin(u * 30) * (1 - pull) * (u < 0.75)
    fill(dr, [(470, 500 + jig), (1160, 500 + jig), (1160, 610 + jig), (470, 610 + jig)], (244, 244, 244, 255))
    dr.text((S(620), S(522 + jig)), "DRY WIPE", font=C.font(C.OSWALD, 54, 600), fill=(40, 46, 70, 255))
    cx = 1160 + 300 * pull
    fill(dr, [(cx - 10, 488 + jig), (cx + 210, 488 + jig), (cx + 230, 555 + jig), (cx + 210, 622 + jig),
              (cx - 10, 622 + jig)], (34, 42, 74, 255))
    fist(dr, 520, 560 + jig, 230, 0.0, mirror=False, sleeve=None)
    fist(dr, cx + 120, 560 + jig, 230, math.pi, mirror=True, sleeve=None)
    fill(dr, capsule(130, 640, 420, 230, 0.35), (200, 24, 30, 255))             # his sleeves, at the edges
    fill(dr, capsule(cx + 520, 650, 420, 230, math.pi - 0.35), (200, 24, 30, 255))
    return C.over(img, C.premult(im))


# ---------------------------------------------------------------- single props: microphones
def mic(lay, s, t, ex, ey, ed, st):
    """the reporter's microphone, in from frame left at mouth height (no reporter in shot)"""
    u = C.sm((t - s["t"] - 0.1) / 0.5)
    im, dr = layer()
    x1 = -200 + (ex / RS - 2.6 * ed / RS + 200) * u
    y = ey / RS + 2.0 * ed / RS
    if x1 < -60:                                                  # still out of the frame
        return
    if x1 - 70 > 0:
        dr.rectangle((0, S(y - 18), S(x1 - 70), S(y + 18)), fill=(40, 40, 44, 255), outline=INK, width=lw())
    dr.rounded_rectangle((S(x1 - 120), S(y - 50), S(x1 - 40), S(y + 50)), radius=S(12), fill=(200, 24, 30, 255),
                         outline=INK, width=lw())
    dr.ellipse((S(x1 - 60), S(y - 46), S(x1 + 30), S(y + 46)), fill=(30, 30, 34, 255), outline=INK, width=lw())
    a = C.premult(im)
    lay[:] = lay * (1 - a[..., 3:4]) + a


def mics(lay, s, t, ex, ey, ed, st):
    """the press-room desk's microphones in front of him, below the chin"""
    im, dr = layer()
    y = ey / RS + 4.2 * ed / RS
    for k, dx in enumerate((-2.2, -0.9, 0.7, 2.0)):
        x = ex / RS + dx * ed / RS
        dr.line([(S(x), S(y + 120)), (S(x + (k - 1.5) * 16), S(y - 30 * (k % 2)))], fill=INK, width=S(14))
        dr.line([(S(x), S(y + 120)), (S(x + (k - 1.5) * 16), S(y - 30 * (k % 2)))], fill=(40, 40, 44, 255), width=S(8))
        dr.ellipse((S(x + (k - 1.5) * 16 - 26), S(y - 30 * (k % 2) - 40), S(x + (k - 1.5) * 16 + 26),
                    S(y - 30 * (k % 2) + 10)), fill=(28, 28, 32, 255), outline=INK, width=lw())
    a = C.premult(im)
    lay[:] = lay * (1 - a[..., 3:4]) + a


# ---------------------------------------------------------------- the clear plan
def laptop(s, t):
    """the presentation on the laptop in the dark boardroom: the file name grows (FINAL, FINAL 2); the word CLEAR is
    taken out of the title; A PLAN; then the lid comes down"""
    u = t - s["t"]
    bg = plate_view("BN", 836, 470, 2.0, 7.0) * 0.6
    name0, name1 = "CLEAR PLAN", "CLEAR PLAN - FINAL - FINAL 2"
    k = int(len(name0) + (len(name1) - len(name0)) * C.sm((t - m("type1")) / 1.4)) if t > m("type1") else len(name0)
    fname = name1[:k] + ".pptx"
    title = "A CLEAR PLAN"
    if t > m("type2"):
        n = int(6 * min(1.0, (t - m("type2")) / 0.9))                  # backspace "CLEAR "
        title = "A " + "CLEAR "[n:] + "PLAN"
    w, h = 1600, 1000
    scr = Image.new("RGB", (w, h), (238, 238, 240))
    dr = ImageDraw.Draw(scr)
    dr.rectangle((0, 0, w, 70), fill=(196, 72, 40))
    f = C.ImageFont.truetype(C.INTER, 36)
    tw = dr.textlength(fname, font=f)
    dr.text(((w - tw) / 2, 14), fname, font=f, fill=(255, 255, 255))
    dr.rectangle((140, 160, w - 140, h - 80), fill=(16, 16, 20))
    ft = C.ImageFont.truetype(C.BEBAS, 190)
    tw = dr.textlength(title, font=ft)
    dr.text(((w - tw) / 2, 420), title, font=ft, fill=(255, 255, 255))
    if int(u * 2) % 2 == 0 and m("type2") < t < m("aplan"):
        cx = (w + tw) / 2 + 10
        dr.rectangle((cx, 440, cx + 8, 600), fill=(255, 255, 255))
    dr.rectangle((140, h - 100, w - 140, h - 80), fill=C.RED)
    scr = np.asarray(scr).astype(np.float32) / 255
    lid = C.sm((t - m("lid")) / 0.6) if t > m("lid") else 0.0
    img = bg.copy()
    # the keyboard deck
    im, dr2 = layer()
    poly(dr2, [(330, 860), (1590, 860), (1760, 1040), (160, 1040)], (60, 62, 70, 255))
    img = C.over(img, C.premult(im))
    if lid < 0.98:
        top = 80 + 780 * lid
        sc = cv2.resize(scr, (S(1240), max(1, S(780 * (1 - lid)))), interpolation=cv2.INTER_AREA)
        lay = np.zeros((OH, OW, 3), np.float32)
        box = (340, top, 1580, 860)
        lay = C.device_frame(lay, box, cv2.resize(sc, (S(1240) - 2 * S(26), max(1, S(780 * (1 - lid)) - 2 * S(26)))),
                             radius=14)
        msk = np.zeros((OH, OW), np.float32)
        cv2.rectangle(msk, (S(340), S(top)), (S(1580), S(860)), 1.0, -1)
        img = img * (1 - msk[..., None]) + lay * msk[..., None]
        glow = (1 - lid) * 0.12
        img = img + glow * np.float32([0.6, 0.7, 1.0])
    else:
        im, dr2 = layer()
        poly(dr2, [(340, 840), (1580, 840), (1600, 870), (320, 870)], (70, 72, 80, 255))
        img = C.over(img, C.premult(im))
    zz = 1.0 + (0.18 * C.sm((t - m("aplan")) / 1.2) if t > m("aplan") else 0.0) * (1 - lid)
    return zoom(np.clip(img, 0, 1), zz, 0.5, 0.48)


def mug_dark(s, t):
    """the dark boardroom; only the white mug catches the light"""
    u = t - s["t"]
    img = plate_view("BN", 836, 520, 2.4, 9.0) * 0.28
    im, dr = layer()
    mug_shape(dr, 860, 560, 200, 230, (236, 238, 244, 255), inside=(70, 50, 36, 255))
    lay = C.premult(im)
    img = C.over(img, lay)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    g = np.exp(-(((xx - S(960)) / S(420)) ** 2 + ((yy - S(680)) / S(330)) ** 2))
    img = img * (0.55 + 0.6 * g[..., None])
    return np.clip(img, 0, 1)


CREDITS = [
    ("ALL OR SOMETHING", "BEBAS", 120, (255, 255, 255)),
    ("EPISODE ONE: THE CLEAR PLAN", "BEBAS", 70, (236, 236, 236)),
    ("", None, 30, None),
    ("An animated parody. Real results; the private scenes and dialogue are fictionalised.", "INTER", 34, (210, 210, 210)),
    ("", None, 30, None),
    ("THE CAST (ALL PARODY)", "BEBAS", 56, (255, 255, 255)),
    ("Michael Carrick  ·  Bruno Fernandes  ·  Harry Maguire  ·  Lisandro Martínez", "INTER", 32, (200, 200, 200)),
    ("Matheus Cunha  ·  Benjamin Šeško  ·  Mason Mount  ·  Shea Lacey (off camera)", "INTER", 32, (200, 200, 200)),
    ("Kobbie Mainoo  ·  Joshua Zirkzee  ·  Jason Wilcox  ·  Omar Berrada", "INTER", 32, (200, 200, 200)),
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
    """the credits on black, rolling up slowly; no next-week tease"""
    roll, H = _credit_roll()
    dur = s["end"] - s["t"]
    u = (t - s["t"]) / max(0.1, dur)
    if H <= 960:                                                  # it fits: one card, centred
        y0 = (OH - S(H)) / 2 - S(80)
    else:
        y0 = S(1080 * 0.18) - u * max(0, S(H) - S(820))
    img = np.zeros((OH, OW, 3), np.float32)
    return C.paste(img, roll, 0, int(y0 + S(80)), C.sm((t - s["t"]) / 0.6))


# ---------------------------------------------------------------- over the picture
PARA1 = ("AFTER THE MATCH — BRUNO FERNANDES",
         "Fernandes questioned the staff's decision to sit off Como rather than press man-to-man. He said it gave "
         "the opposition confidence.",
         "Paraphrase of post-match TNT Sports interview, reported by Reuters / RTÉ, 21 October 2026.")
PARA2 = ("CARRICK'S RESPONSE",
         "Carrick said United partly pressed man-to-man after half-time and conceded. He argued that any system "
         "still requires players to run and recover.",
         "Paraphrase of post-match remarks reported by Sky Sports, 22 October 2026.")


def overlay(img, t, s):
    if s.get("tilt_down"):                                        # the operator lowers the lens, too late
        t0, a = s["tilt_down"]
        if t > t0:
            u = C.sm((t - t0) / 0.6) * a
            M = np.float32([[1, 0, 0], [0, 1, -u * 300 * RS]])
            img = cv2.warpAffine(img, M, (OW, OH), borderMode=cv2.BORDER_REPLICATE)
            img = cv2.GaussianBlur(img, (0, 0), 0.1 + 4 * u * RS)
    if m("cut_par1") <= t < m("cut_b05"):
        img = C.paraphrase(img, t, m("cut_par1"), m("cut_b05"), *PARA1)
    if m("cut_par2") <= t < m("cut_c08"):
        img = C.paraphrase(img, t, m("cut_par2"), m("cut_c08"), *PARA2)
    if m("cut_b05") <= t < m("cut_par2"):
        img = C.label(img, t, m("cut_b05"), m("cut_par2"))
    if m("cut_c08") <= t < m("cut_corr"):
        img = C.label(img, t, m("cut_c08"), m("cut_corr"))
    return img


def lake(s, t):
    """dissolving in from the white mug: a hotel breakfast cup by a window on the lake, mountains across the water"""
    u = t - s["t"]
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    sky = np.float32([0.62, 0.78, 0.92]) + (yy / OH)[..., None] * np.float32([0.25, 0.14, 0.02])
    img = sky.copy()
    rng = np.random.default_rng(7)

    def ridge(y0, amp, col, seed, freq):
        r = np.random.default_rng(seed)
        ph = r.uniform(0, 6, 4)
        x = np.arange(OW, dtype=np.float32) / RS
        h = y0 - amp * (0.55 * np.sin(x * freq + ph[0]) + 0.3 * np.sin(x * freq * 2.3 + ph[1]) + 0.15 * np.sin(x * freq * 5 + ph[2]))
        return (yy / RS > h[None, :]), col
    for y0, amp, col, seed, f in ((470, 120, (0.52, 0.60, 0.72), 1, 0.004), (540, 90, (0.38, 0.48, 0.58), 2, 0.006),
                                  (600, 50, (0.24, 0.38, 0.30), 3, 0.009)):
        msk, c = ridge(y0, amp, c if False else col, seed, f)
        img[msk] = np.float32(c)
    water = yy / RS > 640
    img[water] = (np.float32([0.20, 0.42, 0.60]) + (yy[water] / OH)[:, None] * np.float32([0.05, 0.08, 0.1]))
    sp = (rng.random((OH, OW)) > 0.9985) & water
    img[sp] = 0.95
    img = cv2.GaussianBlur(img, (0, 0), 1.2 * RS)
    # far shore: little villas
    for k in range(9):
        x = 160 + k * 190 + rng.uniform(-30, 30)
        cv2.rectangle(img, (S(x), S(612)), (S(x + 34), S(638)), (0.93, 0.86, 0.72), -1)
        cv2.rectangle(img, (S(x - 2), S(604)), (S(x + 36), S(612)), (0.62, 0.30, 0.22), -1)
    # the window: frame and mullion
    img[:, :S(90)] = np.float32([0.88, 0.86, 0.82]); img[:, -S(90):] = np.float32([0.88, 0.86, 0.82])
    img[:S(60)] = np.float32([0.88, 0.86, 0.82]); img[:, S(940):S(980)] = np.float32([0.88, 0.86, 0.82])
    # the breakfast table, the cup and saucer
    tab = yy / RS > 820
    img[tab] = np.float32([0.97, 0.96, 0.93])
    img[(yy / RS > 818) & (yy / RS < 824)] = 0.4
    im, dr = layer()
    dr.ellipse((S(700), S(880), S(1220), S(980)), fill=(250, 250, 250, 255), outline=INK, width=lw())
    mug_shape(dr, 820, 760, 260, 170, (250, 250, 250, 255), inside=(120, 78, 46, 255))
    img = C.over(img, C.premult(im))
    img = zoom(np.clip(img, 0, 1), 1.0 + 0.04 * u / max(0.1, s["end"] - s["t"]), 0.5, 0.7)
    if u < 0.5:                                      # the dissolve from the white mug
        prev = whitemug(dict(t=s["t"] - 2.0, end=s["t"]), s["t"] - 0.001)
        k = u / 0.5
        img = prev * (1 - k) + img * k
    return img
