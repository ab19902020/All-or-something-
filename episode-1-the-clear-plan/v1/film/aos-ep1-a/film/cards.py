"""All or Something's on-screen graphics for Episode One, drawn in the look the opening already set (the Hull score
cards: Oswald on a dark bar, the score in a white box, a red rule, the dark red glow behind), plus the documentary
furniture the new scenes need: result cards, chapter cards, the paraphrase panel for real post-match positions, the
PARODY DIALOGUE corner label, and the whiteboard, tablet and laptop inserts. Everything is drawn at the output
resolution from a 1920 x 1080 layout (RS) and returned as RGB float 0..1 (full frames) or premultiplied RGBA layers.
Shared by both parts of the episode (aos-ep1-a and aos-ep1-b keep identical copies)."""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from studio.film.engine import OH, OW, RS
from studio.paths import FONTS

OSWALD, BEBAS, INTER = str(FONTS / "Oswald.ttf"), str(FONTS / "BebasNeue-Regular.ttf"), str(FONTS / "Inter.ttf")
MARKER = str(FONTS / "PermanentMarker-Regular.ttf")
RED = (218, 22, 30)
INK = (28, 36, 70)                      # whiteboard marker: dark blue-black
INK_RED = (196, 30, 36)


def sm(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


@functools.lru_cache(maxsize=128)
def font(path, size, weight=None):
    f = ImageFont.truetype(path, max(4, int(round(size * RS))))
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def S(v):
    return int(round(v * RS))


def premult(im):
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


def over(img, lay, k=1.0):
    return img * (1 - lay[..., 3:4] * k) + lay[..., :3] * k


def text_w(dr, s, f, track=0):
    return sum(dr.textlength(ch, font=f) for ch in s) + S(track) * max(0, len(s) - 1)


def draw_text(dr, xy, s, f, fill, track=0, anchor="l"):
    """text with letter spacing; anchor l / c / r on x; y is the top"""
    x, y = xy
    w = text_w(dr, s, f, track)
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    for ch in s:
        dr.text((x, y), ch, font=f, fill=fill)
        x += dr.textlength(ch, font=f) + S(track)
    return w


def wrap(dr, s, f, width):
    out, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=f) <= S(width) or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- backgrounds
@functools.lru_cache(maxsize=4)
def glow_bg(tint=(0.30, 0.05, 0.08)):
    """the score cards' ground: near black, a wide dark red band through the middle, a faint scanline texture"""
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    v = np.exp(-((yy - OH * 0.5) / (OH * 0.2)) ** 2) * (0.75 + 0.25 * np.exp(-((xx - OW * 0.5) / (OW * 0.6)) ** 2))
    img = np.float32([0.045, 0.045, 0.055]) + v[..., None] * np.float32(tint)
    img *= (1 - 0.06 * (np.sin(yy / max(1.0, 2.0 * RS)) > 0.6))[..., None]
    return img.astype(np.float32)


# ---------------------------------------------------------------- result cards
@functools.lru_cache(maxsize=64)
def _result_layer(home, hs, as_, away, top, foot, foot2):
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    x0, x1, y0, y1 = S(210), S(1710), S(420), S(645)
    dr.rectangle((x0, y0, x1, y1), fill=(24, 24, 28, 255))
    bx0, bx1 = S(780), S(1140)
    dr.rectangle((bx0, S(435), bx1, y1), fill=(236, 236, 236, 255))
    dr.rectangle((x0, S(654), x1, S(661)), fill=RED + (255,))
    fn = font(OSWALD, 118, 700)
    for name, cx in ((home, (x0 + bx0) / 2 + S(10)), (away, (bx1 + x1) / 2 - S(10))):
        size = 118
        while text_w(dr, name, font(OSWALD, size, 700)) > (bx0 - x0) - S(110) and size > 40:
            size -= 4
        f = font(OSWALD, size, 700)
        draw_text(dr, (cx, (y0 + y1) / 2 - f.getbbox("H")[3] / 2 - f.getbbox("H")[1] / 2 - S(2)), name, f,
                  (255, 255, 255, 255), anchor="c")
    fs = font(OSWALD, 168, 600)
    cy = (S(435) + y1) / 2
    for s, cx in ((hs, bx0 + S(62)), ("-", (bx0 + bx1) / 2), (as_, bx1 - S(62))):
        bb = fs.getbbox(s)
        dr.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), s, font=fs, fill=(18, 18, 20, 255))
    if top:
        draw_text(dr, (OW / 2, S(330)), top, font(OSWALD, 44, 500), (232, 232, 232, 255), track=4, anchor="c")
    if foot:
        draw_text(dr, (OW / 2, S(690)), foot, font(OSWALD, 44, 500), (205, 205, 205, 255), track=1, anchor="c")
    if foot2:
        draw_text(dr, (OW / 2, S(752)), foot2, font(OSWALD, 36, 400), (170, 170, 170, 255), track=1, anchor="c")
    return premult(im)


def result_card(t, t0, home, hs, as_, away, top="", foot="", foot2="", flip=None):
    """a score card: (home hs - as away), with a dated line above and the scorers below. flip = (t, hs, as, foot):
    the score changes there (a lead becoming a draw)"""
    img = glow_bg().copy()
    u = t - t0
    if flip and t >= flip[0]:
        hs, as_, foot = flip[1], flip[2], flip[3] if len(flip) > 3 else foot
    lay = _result_layer(home, str(hs), str(as_), away, top, foot, foot2)
    k = sm(u / 0.25)
    dy = int((1 - sm(u / 0.35)) * S(18))
    if dy:
        lay = np.roll(lay, dy, 0)
    img = over(img, lay, k)
    if flip and 0 <= t - flip[0] < 0.25:                     # the change lands: a flash on the score box
        f = 1 - (t - flip[0]) / 0.25
        img[S(435):S(645), S(780):S(1140)] += 0.35 * f
    return np.clip(img, 0, 1)


# ---------------------------------------------------------------- chapter cards
@functools.lru_cache(maxsize=32)
def _chapter_layer(a, b, c):
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    fa = font(BEBAS, 150)
    draw_text(dr, (OW / 2, S(372)), a, fa, (255, 255, 255, 255), track=8, anchor="c")
    w = text_w(dr, a, fa, 8)
    dr.rectangle((OW / 2 - min(w, S(900)) / 2, S(552), OW / 2 + min(w, S(900)) / 2, S(559)), fill=RED + (255,))
    if b:
        draw_text(dr, (OW / 2, S(586)), b, font(INTER, 40, 600), (230, 230, 230, 255), track=3, anchor="c")
    if c:
        draw_text(dr, (OW / 2, S(650)), c, font(INTER, 30, 500), (160, 160, 160, 255), track=1, anchor="c")
    return premult(im)


def chapter_card(t, t0, a, b="", c="", base=None):
    img = glow_bg((0.16, 0.03, 0.05)).copy() if base is None else base
    k = sm((t - t0) / 0.35)
    return np.clip(over(img, _chapter_layer(a, b, c), k), 0, 1)


# ---------------------------------------------------------------- overlays: paraphrase panel, parody label
@functools.lru_cache(maxsize=16)
def _para_layer(title, body, footer):
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    x0, x1 = S(170), OW - S(170)
    fb = font(INTER, 46, 500)
    lines = wrap(dr, body, fb, 1500)
    h = S(150) + len(lines) * S(66) + S(120)
    y0 = (OH - h) // 2
    dr.rectangle((x0, y0, x1, y0 + h), fill=(10, 10, 12, 222))
    dr.rectangle((x0, y0, x0 + S(10), y0 + h), fill=RED + (255,))
    draw_text(dr, (x0 + S(60), y0 + S(42)), title, font(BEBAS, 66), (255, 255, 255, 255), track=3)
    y = y0 + S(140)
    for ln in lines:
        dr.text((x0 + S(60), y), ln, font=fb, fill=(240, 240, 240, 255))
        y += S(66)
    ff = font(INTER, 26, 500)
    for k, ln in enumerate(wrap(dr, footer, ff, 1500)):
        dr.text((x0 + S(60), y + S(38) + k * S(36)), ln, font=ff, fill=(165, 165, 165, 255))
    return premult(im)


def paraphrase(img, t, t0, t1, title, body, footer):
    """a real post-match position, paraphrased (no quotation marks), the picture behind dimmed"""
    k = sm((t - t0) / 0.4) * (1 - sm((t - (t1 - 0.35)) / 0.35))
    img = img * (1 - 0.55 * k)
    return over(img, _para_layer(title, body, footer), k)


@functools.lru_cache(maxsize=4)
def _label_layer(text):
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = font(INTER, 26, 700)
    w = text_w(dr, text, f, 3)
    x1, y0 = OW - S(64), S(56)
    dr.rectangle((x1 - w - S(44), y0, x1, y0 + S(52)), fill=(12, 12, 14, 200))
    dr.rectangle((x1 - w - S(44), y0, x1 - w - S(36), y0 + S(52)), fill=RED + (255,))
    draw_text(dr, (x1 - S(18), y0 + S(11)), text, f, (255, 255, 255, 255), track=3, anchor="r")
    return premult(im)


def label(img, t, t0, t1, text="PARODY DIALOGUE"):
    k = sm((t - t0) / 0.25) * (1 - sm((t - (t1 - 0.25)) / 0.25))
    return over(img, _label_layer(text), k)


@functools.lru_cache(maxsize=8)
def _disclaimer_layer(text):
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = font(INTER, 28, 600)
    w = text_w(dr, text, f, 2)
    y = OH - S(92)
    dr.rectangle((OW / 2 - w / 2 - S(26), y - S(12), OW / 2 + w / 2 + S(26), y + S(46)), fill=(10, 10, 12, 190))
    draw_text(dr, (OW / 2, y), text, f, (236, 236, 236, 255), track=2, anchor="c")
    return premult(im)


def disclaimer(img, t, t0, t1, text="ANIMATED PARODY — PRIVATE SCENES AND DIALOGUE ARE FICTIONALISED"):
    k = sm((t - t0) / 0.3) * (1 - sm((t - (t1 - 0.3)) / 0.3))
    return over(img, _disclaimer_layer(text), k)


# ---------------------------------------------------------------- the whiteboard
@functools.lru_cache(maxsize=2)
def board_surface(seed=3):
    """an off-white whiteboard filling the frame: a soft light falloff, old ghosting, the aluminium frame along the
    top and left edges"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    img = np.float32([0.95, 0.955, 0.95]) * (0.93 + 0.07 * np.exp(-(((xx - OW * 0.4) / (OW * 0.7)) ** 2
                                                                    + ((yy - OH * 0.3) / (OH * 0.9)) ** 2)))[..., None]
    smudge = cv2.GaussianBlur(rng.random((OH // 8, OW // 8)).astype(np.float32), (0, 0), 6)
    smudge = cv2.resize(smudge, (OW, OH))
    img -= (smudge - smudge.mean())[..., None] * 0.12
    # the frame: brushed aluminium along the top, a dark gap where it meets the board
    fh = S(46)
    grad = np.linspace(0.82, 0.55, fh, dtype=np.float32)[:, None, None]
    img[:fh] = grad * np.float32([0.92, 0.93, 0.95])
    img[fh:fh + S(4)] = 0.25
    img[:, :S(30)] = np.linspace(0.55, 0.8, S(30), dtype=np.float32)[None, :, None] * np.float32([0.92, 0.93, 0.95])
    img[:, S(30):S(33)] = 0.25
    return np.clip(img, 0, 1).astype(np.float32)


@functools.lru_cache(maxsize=64)
def _marker_text(text, size, color, rot=0.0):
    """marker writing as a tight premultiplied RGBA image"""
    f = font(MARKER, size)
    dr = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dr.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + S(20), bb[3] - bb[1] + S(20)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((S(10) - bb[0], S(10) - bb[1]), text, font=f, fill=tuple(color) + (255,))
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = premult(im)
    # marker ink is a little uneven
    a[..., 3] *= 0.92
    a[..., :3] *= 0.92
    return a


def paste(img, lay, x, y, k=1.0, reveal=1.0):
    """premultiplied layer at (x, y) screen px (top-left); reveal 0..1 uncovers it left to right (writing)"""
    h, w = lay.shape[:2]
    x, y = int(x), int(y)
    x0, y0, x1, y1 = max(0, x), max(0, y), min(OW, x + w), min(OH, y + h)
    if x1 <= x0 or y1 <= y0 or k <= 0:
        return img
    sub = lay[y0 - y:y1 - y, x0 - x:x1 - x].copy()
    if reveal < 1.0:
        cut = int(w * max(0.0, reveal)) - (x0 - x)
        sub[:, max(0, cut):] = 0
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - sub[..., 3:4] * k) + sub[..., :3] * k
    return img


def write(img, text, x, y, size, t, t0, dur, color=INK, rot=0.0, k=1.0):
    """marker text written from t0 over dur seconds (x, y: top-left, 1920 px layout)"""
    if t < t0:
        return img
    return paste(img, _marker_text(text, size, color, rot), S(x), S(y), k, sm((t - t0) / max(dur, 1e-3)) if dur else 1.0)


def ghost(img, text, x, y, size, rot=0.0, amount=0.22):
    """a word wiped off but still there: a faint, smeared grey"""
    lay = _marker_text(text, size, (120, 130, 150), rot).copy()
    lay = cv2.GaussianBlur(lay, (0, 0), 2.2 * RS)
    return paste(img, lay, S(x), S(y), amount)


def magnet(img, x, y, r, color, k=1.0):
    """a round board magnet with a highlight and a soft shadow (1920 layout px)"""
    X, Y, R = S(x), S(y), S(r)
    pad = R * 2
    yy, xx = np.mgrid[-pad:pad, -pad:pad].astype(np.float32)
    d = np.sqrt(xx ** 2 + yy ** 2)
    sh = np.clip(1 - np.sqrt((xx - R * 0.18) ** 2 + (yy - R * 0.28) ** 2) / (R * 1.15), 0, 1) ** 1.5 * 0.35
    a = np.clip(R - d + 0.5, 0, 1)
    rim = np.clip(R - d + 0.5, 0, 1) - np.clip(R * 0.86 - d + 0.5, 0, 1)
    col = np.float32(color) / 255
    hl = np.clip(1 - np.sqrt((xx + R * 0.35) ** 2 + (yy + R * 0.38) ** 2) / (R * 0.45), 0, 1) * 0.55
    rgb = col * (1 - 0.35 * (d / max(R, 1)))[..., None] + hl[..., None]
    rgb = rgb * (1 - rim[..., None] * 0.6)
    y0, x0 = Y - pad, X - pad
    ys, xs = slice(max(0, y0), min(OH, Y + pad)), slice(max(0, x0), min(OW, X + pad))
    oy, ox = ys.start - y0, xs.start - x0
    hh, ww = ys.stop - ys.start, xs.stop - xs.start
    if hh <= 0 or ww <= 0:
        return img
    shs = sh[oy:oy + hh, ox:ox + ww][..., None] * k
    img[ys, xs] = img[ys, xs] * (1 - shs)
    aa = a[oy:oy + hh, ox:ox + ww][..., None] * k
    img[ys, xs] = img[ys, xs] * (1 - aa) + np.clip(rgb[oy:oy + hh, ox:ox + ww], 0, 1) * aa
    return img


def arrow(img, p0, p1, t, t0, dur, color=INK, width=9):
    """a marker arrow drawn from p0 to p1 (1920 layout px) between t0 and t0 + dur"""
    if t < t0:
        return img
    u = sm((t - t0) / max(dur, 1e-3)) if dur else 1.0
    x0, y0 = p0
    x1, y1 = x0 + (p1[0] - x0) * u, y0 + (p1[1] - y0) * u
    lay = np.zeros((OH, OW, 3), np.float32)
    msk = np.zeros((OH, OW), np.float32)
    cv2.line(msk, (S(x0), S(y0)), (S(x1), S(y1)), 1.0, max(1, S(width)), cv2.LINE_AA)
    if u > 0.85:
        ang = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            hx, hy = x1 + 38 * math.cos(ang + da), y1 + 38 * math.sin(ang + da)
            cv2.line(msk, (S(x1), S(y1)), (S(hx), S(hy)), 1.0, max(1, S(width)), cv2.LINE_AA)
    col = np.float32(color) / 255 * 0.92
    return img * (1 - msk[..., None] * 0.92) + col * msk[..., None] * 0.92


def hand_marker(img, x, y, k=1.0, cap=True):
    """a drawn hand holding a marker, its nib at (x, y) (1920 layout px): flat skin, the kit's dark ink outline"""
    if k <= 0:
        return img
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    X, Y = S(x), S(y)
    ink, w = (24, 18, 20, 255), max(2, S(6))
    # the marker, from the nib down and to the right
    body = [(X, Y), (X + S(26), Y + S(10)), (X + S(150), Y + S(132)), (X + S(124), Y + S(158)), (X + S(6), Y + S(30))]
    dr.polygon(body, fill=(36, 40, 60, 255), outline=ink)
    dr.line(body + [body[0]], fill=ink, width=w)
    dr.polygon([(X, Y), (X + S(18), Y + S(4)), (X + S(6), Y + S(20))], fill=(20, 20, 30, 255))
    # the hand round it: a fist, thumb on top
    skin, shade = (228, 176, 140, 255), (200, 146, 112, 255)
    fist = [(X + S(70), Y + S(60)), (X + S(130), Y + S(50)), (X + S(196), Y + S(100)), (X + S(214), Y + S(178)),
            (X + S(176), Y + S(236)), (X + S(108), Y + S(226)), (X + S(66), Y + S(160)), (X + S(52), Y + S(100))]
    dr.polygon(fist, fill=skin)
    dr.line(fist + [fist[0]], fill=ink, width=w, joint="curve")
    for k2 in range(3):
        a = (X + S(66 + 12 * k2), Y + S(118 + 32 * k2))
        b = (X + S(120 + 10 * k2), Y + S(140 + 30 * k2))
        dr.line([a, b], fill=shade[:3] + (255,), width=max(2, S(4)))
    thumb = [(X + S(58), Y + S(70)), (X + S(102), Y + S(52)), (X + S(126), Y + S(70)), (X + S(98), Y + S(92)),
             (X + S(64), Y + S(98))]
    dr.polygon(thumb, fill=skin)
    dr.line(thumb + [thumb[0]], fill=ink, width=w, joint="curve")
    # the sleeve: the club's dark tracksuit
    sleeve = [(X + S(176), Y + S(236)), (X + S(214), Y + S(178)), (X + S(330), Y + S(260)), (X + S(300), Y + S(330))]
    dr.polygon(sleeve, fill=(26, 30, 44, 255))
    dr.line(sleeve + [sleeve[0]], fill=ink, width=w)
    return over(img, premult(im), k)


# ---------------------------------------------------------------- devices: tablet, laptop
def device_frame(img, box, screen, bezel=(18, 18, 22), radius=28):
    """a tablet/laptop screen: a rounded black bezel round `screen` (an RGB float image the size of the inner box)"""
    x0, y0, x1, y1 = [S(v) for v in box]
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((x0, y0, x1, y1), radius=S(radius), fill=bezel + (255,), outline=(6, 6, 8, 255),
                         width=max(2, S(5)))
    img = over(img, premult(im))
    m = S(26)
    sh, sw = y1 - y0 - 2 * m, x1 - x0 - 2 * m
    if sh <= 0 or sw <= 0:
        return img
    scr = cv2.resize(screen, (sw, sh), interpolation=cv2.INTER_AREA)
    # glass: a soft diagonal reflection
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    scr = scr + (np.clip(1 - np.abs((xx / sw - 0.25) + (yy / sh) * 0.6 - 0.45) / 0.12, 0, 1) * 0.06)[..., None]
    X0, Y0 = x0 + m, y0 + m                                     # the screen's place, clipped to the frame
    a0, b0 = max(0, X0), max(0, Y0)
    a1, b1 = min(OW, X0 + sw), min(OH, Y0 + sh)
    if a1 > a0 and b1 > b0:
        img[b0:b1, a0:a1] = scr[b0 - Y0:b1 - Y0, a0 - X0:a1 - X0]
    return img


@functools.lru_cache(maxsize=16)
def slide(lines, w=1600, h=1000, bg=(16, 16, 20), accent=RED):
    """a presentation slide (RGB float h x w): lines = ((text, size, colour, y), ...) centred"""
    im = Image.new("RGB", (w, h), bg)
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, h - 18, w, h), fill=accent)
    for text, size, col, y in lines:
        f = ImageFont.truetype(BEBAS, size)
        tw = dr.textlength(text, font=f)
        dr.text(((w - tw) / 2, y), text, font=f, fill=col)
    return np.asarray(im).astype(np.float32) / 255
