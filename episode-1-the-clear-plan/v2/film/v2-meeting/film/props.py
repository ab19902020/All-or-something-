"""The meeting's screens, drawn in the house look:

  plate_image   the boardroom with its big screen in each state: "BC" CONNECTING... 3%, "BO" the objectives,
                "BE" CALL ENDED 0:41 ("B" and "SC" are the plate as drawn, the screen black)
  screen        the big screen's own shots (a world layer): the objectives scrolling, the incoming call, the two
                CAMERA OFF tiles (the one speaking lit green), CALL ENDED
  tablet        Wilcox's tablet, close: THE PLAN, connecting, the battery at 3%
  overlay       the parody notice over the open; Wilcox's buzzwords stamped on the picture as he says them"""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from film import cards as C
from film.timeline import TL
from studio.film.engine import OH, OW, RS
from studio.film.shots import Marks
from studio.film import ep

S = C.S
import json
L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

GX0, GY0, GX1, GY1 = 699, 201, 1040, 362            # the big screen's glass, 1x plate px
SW, SH = (GX1 - GX0) * 4, (GY1 - GY0) * 4           # its picture, at the plate's 4x
BG = (14, 16, 22)
GREEN = (60, 200, 110)


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


def F(path, size):
    return ImageFont.truetype(path, int(size))


def ctext(dr, cx, y, s, f, fill, track=0):
    w = sum(dr.textlength(ch, font=f) for ch in s) + track * max(0, len(s) - 1)
    x = cx - w / 2
    for ch in s:
        dr.text((x, y), ch, font=f, fill=fill)
        x += dr.textlength(ch, font=f) + track


# ---------------------------------------------------------------- the big screen's pictures (SW x SH, RGB uint8)
def _canvas():
    im = Image.new("RGB", (SW, SH), BG)
    return im, ImageDraw.Draw(im)


@functools.lru_cache(maxsize=4)
def scr_connecting(pct=3):
    im, dr = _canvas()
    ctext(dr, SW / 2, 130, "CONNECTING TO BOARDROOM DISPLAY...", F(C.BEBAS, 92), (236, 236, 236), 3)
    x0, x1, y = 230, SW - 230, 330
    dr.rounded_rectangle((x0, y, x1, y + 46), radius=23, fill=(44, 46, 54))
    dr.rounded_rectangle((x0, y, x0 + max(46, (x1 - x0) * pct / 100), y + 46), radius=23, fill=C.RED)
    ctext(dr, SW / 2, 420, f"{pct}%", F(C.BEBAS, 110), (230, 60, 60), 2)
    dr.rectangle((0, SH - 10, SW, SH), fill=C.RED)
    return np.asarray(im)


OBJ = ["WIN THE LEAGUE", "WIN THE CHAMPIONS LEAGUE", "WIN THE FA CUP", "WIN THE LEAGUE CUP", "SPEND LESS",
       "DEVELOP EVERYONE", "SELL TO BUY", "STAY AGILE", "DON'T COMPLAIN ABOUT THE SQUAD"]
ROW = 104


@functools.lru_cache(maxsize=1)
def _obj_list():
    """the bullets as one tall strip (RGBA)"""
    h = ROW * len(OBJ) + 40
    im = Image.new("RGBA", (SW, h), BG + (255,))
    dr = ImageDraw.Draw(im)
    f = F(C.BEBAS, 84)
    for i, s in enumerate(OBJ):
        y = 20 + i * ROW
        col = (255, 255, 255) if i < len(OBJ) - 1 else (246, 180, 40)
        dr.ellipse((150, y + 34, 176, y + 60), fill=C.RED)
        dr.text((210, y + 4), s, font=f, fill=col)
    return np.asarray(im)


def obj_shown(t):
    """how many bullets are up at t: one every 0.36 s, the last on Jim's "complain\""""
    n = 1 + int((t - m("cut_obj")) / 0.36)
    n = min(len(OBJ) - 1, max(0, n))
    if t >= wt("M29", "complain") - 0.05:
        n = len(OBJ)
    return n


def scr_objectives(t):
    im, dr = _canvas()
    dr.rectangle((0, 0, SW, 120), fill=(26, 26, 32))
    dr.rectangle((0, 116, SW, 124), fill=C.RED)
    ctext(dr, SW / 2, 14, "2026/27 OBJECTIVES", F(C.BEBAS, 96), (255, 255, 255), 4)
    a = np.asarray(im).copy()
    strip = _obj_list()
    n = obj_shown(t)
    view0, view1 = 132, SH - 12                      # the list's window
    vis = view1 - view0
    bottom = 20 + n * ROW                             # the strip's y below the last bullet up
    off = max(0, bottom - vis)                        # scrolls up so the newest bullet is in view
    # ease the scroll
    k = (t - m("cut_obj")) % 0.36 / 0.36
    if t < wt("M29", "complain") - 0.05 and n < len(OBJ) - 1 and off > 0:
        off = max(0, off - int(ROW * (1 - C.sm(k * 2.5))))
    seg = strip[off:off + vis].copy()
    seg[max(0, bottom - off):] = BG + (255,)          # bullets not up yet
    a[view0:view0 + len(seg)] = seg[..., :3]
    return a


@functools.lru_cache(maxsize=1)
def scr_objectives_final():
    return scr_objectives(TL["total"] + 99)


def _tile(dr, box, name, initials, lit):
    x0, y0, x1, y1 = box
    dr.rounded_rectangle(box, radius=18, fill=(34, 36, 44), outline=GREEN if lit else (60, 62, 72),
                         width=12 if lit else 3)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 30
    dr.ellipse((cx - 92, cy - 92, cx + 92, cy + 92), fill=(88, 92, 110))
    ctext(dr, cx, cy - 66, initials, F(C.BEBAS, 120), (240, 240, 240), 2)
    dr.text((x0 + 26, y1 - 66), name, font=F(C.INTER, 36), fill=(236, 236, 236))
    # CAMERA OFF: a small camera with a slash, top right
    cx2, cy2 = x1 - 120, y0 + 50
    dr.rounded_rectangle((cx2 - 40, cy2 - 22, cx2 + 18, cy2 + 22), radius=6, outline=(220, 70, 70), width=6)
    dr.polygon([(cx2 + 18, cy2 - 4), (cx2 + 46, cy2 - 20), (cx2 + 46, cy2 + 20), (cx2 + 18, cy2 + 4)],
               outline=(220, 70, 70), width=6)
    dr.line((cx2 - 50, cy2 - 34, cx2 + 54, cy2 + 34), fill=(220, 70, 70), width=7)
    dr.text((x0 + 26, y0 + 22), "CAMERA OFF", font=F(C.INTER, 30), fill=(200, 200, 205))


def speaking(t, who):
    ids = {"joel": ("M37", "M39", "M41"), "avram": ("M38", "M40")}[who]
    return any(ls(i) - 0.02 <= t <= le(i) + 0.05 for i in ids)


def scr_call(t):
    im, dr = _canvas()
    if t < m("cut_call"):                             # ringing
        u = t - m("chime")
        ctext(dr, SW / 2, 110, "INCOMING VIDEO CALL", F(C.BEBAS, 92), (236, 236, 236), 4)
        for k, (nm, ini) in enumerate((("JOEL GLAZER", "JG"), ("AVRAM GLAZER", "AG"))):
            cx = SW / 2 + (k * 2 - 1) * 230
            r = 92 + 18 * (0.5 + 0.5 * math.sin(u * 9))
            dr.ellipse((cx - r - 14, 330 - r - 14, cx + r + 14, 330 + r + 14), outline=GREEN, width=6)
            dr.ellipse((cx - 92, 330 - 92, cx + 92, 330 + 92), fill=(88, 92, 110))
            ctext(dr, cx, 330 - 66, ini, F(C.BEBAS, 120), (240, 240, 240), 2)
            ctext(dr, cx, 448, nm, F(C.INTER, 34), (220, 220, 225))
        return np.asarray(im)
    if t >= m("ended"):
        return scr_ended()
    _tile(dr, (40, 40, SW / 2 - 20, SH - 110), "Joel Glazer", "JG", speaking(t, "joel"))
    _tile(dr, (SW / 2 + 20, 40, SW - 40, SH - 110), "Avram Glazer", "AG", speaking(t, "avram"))
    # the call's toolbar
    for k in range(4):
        cx = SW / 2 + (k - 1.5) * 96
        dr.ellipse((cx - 30, SH - 92, cx + 30, SH - 32), fill=(200, 50, 50) if k == 3 else (60, 62, 72))
    return np.asarray(im)


@functools.lru_cache(maxsize=1)
def scr_ended():
    im, dr = _canvas()
    ctext(dr, SW / 2, 150, "CALL ENDED", F(C.BEBAS, 170), (240, 240, 240), 6)
    ctext(dr, SW / 2, 380, "0:41", F(C.BEBAS, 120), (170, 170, 178), 4)
    return np.asarray(im)


def screen_picture(t):
    if t < m("cut_ck8"):
        return scr_objectives(t)
    return scr_call(t)


# ---------------------------------------------------------------- the room with its screen in each state
@functools.lru_cache(maxsize=1)
def base_plate():
    from studio.episode.upscale import upscaled
    from studio.paths import BACKGROUNDS
    return upscaled(BACKGROUNDS / "club/boardroom.png", 4.0)[..., ::-1].copy()       # RGB uint8, 4x


def lit(pic):
    """a screen picture as the room sees it: a touch of glass sheen"""
    p = pic.astype(np.float32) / 255
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    p = p + (np.clip(1 - np.abs((xx / SW - 0.3) + (yy / SH) * 0.5 - 0.4) / 0.1, 0, 1) * 0.05)[..., None]
    return np.clip(p, 0, 1)


def plate_image(k):
    pics = {"BC": lambda: scr_connecting(3), "BO": scr_objectives_final, "BE": scr_ended}
    if k not in pics:
        return None if k != "SC" else base_plate()
    big = base_plate().copy()
    big[GY0 * 4:GY1 * 4, GX0 * 4:GX1 * 4] = (lit(pics[k]()) * 255 + 0.5).astype(np.uint8)
    return big


def screen(img, s, t, M, sc):
    """the big screen's own shots: its picture at t, warped onto the glass"""
    M = np.float32(M)
    pic = lit(screen_picture(t))
    A = np.float32([[M[0, 0] / 4, 0, M[0, 0] * GX0 + M[0, 2]], [0, M[1, 1] / 4, M[1, 1] * GY0 + M[1, 2]]])
    c = cv2.warpAffine(np.dstack([pic, np.ones(pic.shape[:2], np.float32)]), A, (OW, OH), flags=cv2.INTER_AREA,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return img * (1 - c[..., 3:4]) + c[..., :3] * c[..., 3:4]


# ---------------------------------------------------------------- Wilcox's tablet
def fingers(img, x, y, side="R"):
    """two drawn fingertips and a thumb gripping a device's edge at (x, y) (1920 layout), the black sleeve beyond"""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    ink, w, skin = (24, 18, 20, 255), max(2, S(5)), (228, 176, 140, 255)
    sg = 1 if side == "R" else -1
    for k in range(3):
        cy = y + k * 56
        box = (S(x - 40) if sg > 0 else S(x - 18), S(cy), S(x + 18) if sg > 0 else S(x + 40), S(cy + 58))
        dr.ellipse(box, fill=skin, outline=ink, width=w)
        nx = x - 22 * sg
        dr.arc((S(nx - 12), S(cy + 14), S(nx + 12), S(cy + 40)), 90 if sg > 0 else 270, 270 if sg > 0 else 90,
               fill=(196, 140, 108, 255), width=max(1, S(3)))
    hand = [(S(x + 20 * sg), S(y - 20)), (S(x + 140 * sg), S(y - 40)), (S(x + 200 * sg), S(y + 220)),
            (S(x + 20 * sg), S(y + 200))]
    dr.polygon(hand, fill=skin)
    dr.line(hand + [hand[0]], fill=ink, width=w)
    sleeve = [(S(x + 140 * sg), S(y - 40)), (S(x + 330 * sg), S(y - 60)), (S(x + 360 * sg), S(y + 250)),
              (S(x + 200 * sg), S(y + 220))]
    dr.polygon(sleeve, fill=(22, 22, 26, 255))
    dr.line(sleeve + [sleeve[0]], fill=ink, width=w)
    return C.over(img, C.premult(im))


def tab_screen(t):
    """the tablet's picture (1548 x 728 layout px): THE PLAN, connecting; the battery at 3%, flashing on "three"""
    w, h = 1548, 728
    im = Image.new("RGB", (w, h), (16, 16, 20))
    dr = ImageDraw.Draw(im)
    # status bar: the battery, top right
    flash = t >= wt("M06", "three") - 0.05 and int((t - wt("M06", "three")) * 4) % 2 == 0
    bc = (235, 50, 50) if not flash else (255, 120, 120)
    dr.rounded_rectangle((w - 190, 24, w - 70, 74), radius=8, outline=(230, 230, 230), width=5)
    dr.rectangle((w - 70, 38, w - 58, 60), fill=(230, 230, 230))
    dr.rectangle((w - 182, 32, w - 176, 66), fill=bc)
    dr.text((w - 330, 18), "3%", font=F(C.BEBAS, 64), fill=bc)
    dr.text((40, 22), "09:58", font=F(C.INTER, 40), fill=(200, 200, 200))
    ctext(dr, w / 2, 150, "THE PLAN", F(C.BEBAS, 190), (255, 255, 255), 6)
    ctext(dr, w / 2, 400, "CONNECTING TO BOARDROOM DISPLAY...", F(C.BEBAS, 64), (200, 200, 205), 2)
    # the spinner
    cx, cy, r = w / 2, 560, 46
    a0 = (t * 360 * 1.3) % 360
    dr.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 270, fill=(218, 22, 30), width=12)
    dr.rectangle((0, h - 14, w, h), fill=C.RED)
    return np.asarray(im).astype(np.float32) / 255


def tablet(s, t):
    u = t - s["t"]
    bg = plate_view("B", 840, 540, 2.6, 9.0) * 0.78
    dy = 7 * math.sin(u * 1.4) + 3 * math.sin(u * 3.1)
    dx = 5 * math.sin(u * 0.9)
    img = C.device_frame(bg.copy(), (360 + dx, 150 + dy, 1560 + dx, 930 + dy), tab_screen(t))
    img = fingers(img, 1560 + dx, 470 + dy, side="R")
    img = fingers(img, 360 + dx, 520 + dy, side="L")
    return zoom(img, 1.0 + 0.04 * C.sm(u / max(0.1, s["end"] - s["t"])))


# ---------------------------------------------------------------- full-frame graphics
@functools.lru_cache(maxsize=8)
def _word_layer(word):
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = C.font(C.BEBAS, 150)
    w = C.text_w(dr, word, f, 8)
    y = OH - S(300)
    dr.rectangle((OW / 2 - w / 2 - S(40), y - S(10), OW / 2 + w / 2 + S(40), y + S(160)), fill=(10, 10, 12, 205))
    dr.rectangle((OW / 2 - w / 2 - S(40), y + S(150), OW / 2 + w / 2 + S(40), y + S(160)), fill=C.RED + (255,))
    C.draw_text(dr, (OW / 2, y), word, f, (255, 255, 255, 255), track=8, anchor="c")
    return C.premult(im)


def overlay(img, t, s):
    if t < 5.2:
        img = C.disclaimer(img, t, 0.4, 4.8)
    words = s.get("words")
    if words:
        cur = None
        for i, (tw, wd) in enumerate(words):
            if t >= tw:
                cur = (tw, wd)
        if cur and cur[1]:
            u = t - cur[0]
            k = 1.0 + 0.25 * (1 - C.sm(u / 0.12))           # stamped: a quick scale-down onto the frame
            lay = _word_layer(cur[1])
            if k > 1.001:
                Mx = cv2.getRotationMatrix2D((OW / 2, OH - S(220)), 0, k)
                lay = cv2.warpAffine(lay, Mx, (OW, OH))
            img = C.over(img, lay, min(1.0, u / 0.06))
    return img
