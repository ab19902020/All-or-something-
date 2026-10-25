"""Hull and the month: inserts and props, drawn in the house look (flat colours, the kit's dark ink outline):

  hull1, hull2   the match broadcast (the episode's animated wides, clock and score graphics corrected to the real
                 minutes: 17' and 38'), from clips/ (frames)
  card_hull      FULL TIME: HULL 2-0 UNITED

  board_hull     the tactics board after Hull: SET PIECES wiped (it stays faintly there), BASICS written over it
  board_reset    the same board after the break: a printed RESET sheet taped over BASICS; a corner lets go
  card_*         the result cards (cards.py: the opening's own score-card design)
  tab_dna        Wilcox's tablet: THE PLAN, NOW WITH EUROPEAN DNA (moved out of somebody's way)
  tab_charge     the tablet on a desk, charging, alone
  lacey_shirt    Lacey's shirt on its hook, still arranged neatly, his name above it
  calendar       the wall calendar: September, then October
  mug            the white mug on an office sill; the camera racks to Carrington beyond, and the hedge
  flashes        press flashes in an empty mixed zone (a world-shot layer)
  overlay        the tablet Wilcox moves into the documentary camera's shot (the shot carries `tablet`)"""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

from film import cards as C
from film.timeline import TL
from studio.film.engine import OH, OW, RS

S = C.S


def m(k):
    return TL["marks"][k]


import json as _json
from studio.film import ep as _ep
from studio.film.shots import Marks as _Marks
T = _Marks(TL, _json.loads(_ep.path("lines.json").read_text()))
CLIPS = _ep.DIR / "clips"


@functools.lru_cache(maxsize=64)
def _clip_frame(name, i):
    import glob
    fs = sorted(glob.glob(str(CLIPS / name / "*.jpg")))
    im = cv2.imread(fs[max(0, min(len(fs) - 1, i))])[..., ::-1]
    if im.shape[1] != OW or im.shape[0] != OH:
        im = cv2.resize(im, (OW, OH), interpolation=cv2.INTER_AREA)
    return im.astype(np.float32) / 255


def hull1(s, t):
    return _clip_frame("hull1", int((t - s["t"]) * 30 + 0.5)).copy()


def hull2(s, t):
    return _clip_frame("hull2", int((t - s["t"]) * 30 + 0.5)).copy()


def card_hull(s, t):
    return C.result_card(t, s["t"], "HULL", 2, 0, "UNITED", top="22 AUGUST 2026  |  PREMIER LEAGUE  |  FULL TIME",
                         foot="AJAYI 17'  ·  MENDY 38'", foot2="SECOND HALF: GOALLESS")


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


# ---------------------------------------------------------------- the tactics board
FORMATION = [(1240, 300), (1420, 300), (1600, 300), (1330, 470), (1510, 470), (1250, 640), (1420, 660), (1600, 640),
             (1330, 820), (1510, 820)]


def board_base(t, magnets=True):
    img = C.board_surface().copy()
    if magnets:
        for x, y in FORMATION:
            img = C.magnet(img, x, y, 30, (205, 30, 36))
    return img


def board_hull(s, t):
    """SET PIECES (underlined twice), the wipe, the ghost, BASICS written over it, the push in on both words"""
    t0, tw, tb, tp = s["t"], m("wipe"), m("write_basics"), m("board_push")
    img = board_base(t)
    wiped = min(1.0, max(0.0, (t - tw) / 1.0))
    if wiped < 1:                                          # the words as written before kick-off, wiped left to right
        lay = C._marker_text("SET PIECES", 170, C.INK_RED, 4.0)
        img2 = C.paste(img.copy(), lay, S(250), S(300))
        if wiped > 0:
            cut = int(S(250) + wiped * lay.shape[1])
            img2[:, :cut] = img[:, :cut]
        img = img2
        img = C.arrow(img, (270, 560), (1000, 520), t, -1, 0, C.INK_RED, 8) if wiped == 0 else img
    if wiped > 0:
        img = C.ghost(img, "SET PIECES", 250, 300, 170, rot=4.0, amount=0.26 * min(1.0, wiped * 1.4))
    if 0 < t - tw < 1.25:                                  # the eraser in a hand, sweeping across
        u = (t - tw) / 1.0
        x = 220 + 900 * min(1.0, u)
        img = eraser(img, x, 380 + 30 * math.sin(u * 9))
    img = C.write(img, "BASICS", 330, 400, 200, t, tb, 1.5, C.INK, rot=2.0)
    if tb - 0.2 < t < tb + 2.0:                            # the hand writing it
        u = min(1.0, max(0.0, (t - tb) / 1.5))
        img = C.hand_marker(img, 380 + 720 * u, 560 + 18 * math.sin(u * 20), k=min(1.0, (t - tb + 0.2) / 0.2)
                            * min(1.0, (tb + 2.0 - t) / 0.3))
    z = 1.0 + 0.12 * C.sm((t - tp) / 2.2) if t > tp else 1.0
    return zoom(img, z, 0.36, 0.45)


def eraser(img, x, y):
    """a board eraser (felt under a grey block) in a hand"""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    X, Y, ink, w = S(x), S(y), (24, 18, 20, 255), max(2, S(6))
    dr.rounded_rectangle((X - S(90), Y - S(40), X + S(90), Y + S(40)), radius=S(10), fill=(90, 92, 100, 255),
                         outline=ink, width=w)
    dr.rectangle((X - S(90), Y + S(26), X + S(90), Y + S(40)), fill=(40, 40, 46, 255))
    skin = (228, 176, 140, 255)
    fist = [(X - S(60), Y - S(36)), (X + S(50), Y - S(52)), (X + S(96), Y - S(110)), (X + S(40), Y - S(150)),
            (X - S(40), Y - S(130)), (X - S(80), Y - S(80))]
    dr.polygon(fist, fill=skin)
    dr.line(fist + [fist[0]], fill=ink, width=w, joint="curve")
    sleeve = [(X + S(40), Y - S(150)), (X + S(96), Y - S(110)), (X + S(200), Y - S(230)), (X + S(130), Y - S(280))]
    dr.polygon(sleeve, fill=(26, 30, 44, 255))
    dr.line(sleeve + [sleeve[0]], fill=ink, width=w)
    return C.over(img, C.premult(im))


def board_reset(s, t):
    """BASICS (SET PIECES ghosting under it) with a printed RESET sheet taped over it; at `tape` a corner lets go"""
    img = board_base(t)
    img = C.ghost(img, "SET PIECES", 250, 300, 170, rot=4.0, amount=0.26)
    img = C.write(img, "BASICS", 330, 400, 200, t, -1, 0, C.INK, rot=2.0)
    a = 0.0
    if t > m("tape"):
        u = (t - m("tape")) / 0.55
        a = (1 - math.cos(min(1.0, u) * math.pi)) / 2 * 34 + (2.5 * math.sin((t - m("tape")) * 7) * math.exp(-u)
                                                              if u > 1 else 0.0)
    img = sheet(img, "RESET", (300, 330, 1060, 780), a)
    z = 1.0 + 0.05 * C.sm((t - s["t"]) / (s["end"] - s["t"]))
    return zoom(img, z, 0.35, 0.5)


def sheet(img, text, box, droop):
    """a printed A4 sheet (landscape) taped at its corners; droop: the top-right corner's tape gone, the sheet
    swinging down about its top-left corner by `droop` degrees"""
    x0, y0, x1, y1 = box
    w, h = S(x1 - x0), S(y1 - y0)
    im = Image.new("RGBA", (w + S(40), h + S(40)), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    o = S(20)
    dr.rectangle((o, o, o + w, o + h), fill=(250, 250, 248, 255), outline=(150, 150, 150, 255), width=max(1, S(2)))
    f = C.font(C.BEBAS, 300)
    tw = dr.textlength(text, font=f)
    bb = f.getbbox(text)
    dr.text((o + (w - tw) / 2, o + (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=(20, 20, 24, 255))
    dr.rectangle((o, o + h - S(26), o + w, o + h - S(12)), fill=C.RED + (255,))
    lay = C.premult(im)
    # the sheet's own shadow, then the sheet (rotated about its top-left corner)
    M = cv2.getRotationMatrix2D((o, o), -droop, 1.0)
    M[0, 2] += S(x0) - o
    M[1, 2] += S(y0) - o
    warped = cv2.warpAffine(lay, M, (OW, OH), flags=cv2.INTER_LINEAR, borderValue=0)
    sh = cv2.GaussianBlur(warped[..., 3], (0, 0), 7 * RS)
    sh = np.roll(np.roll(sh, S(8), 0), S(6), 1)
    img = img * (1 - 0.3 * sh[..., None])
    img = C.over(img, warped)
    # tape: three corners held (the top-right one has let go once the sheet droops)
    corners = [(x0, y0), (x0, y1), (x1, y1)] + ([] if droop > 0.5 else [(x1, y0)])
    for cx, cy in corners:
        px, py = S(cx), S(cy)
        if droop > 0.5 and (cx, cy) != (x0, y0):
            r = math.radians(-droop)
            dx, dy = px - S(x0), py - S(y0)
            px, py = S(x0) + dx * math.cos(r) - dy * math.sin(r), S(y0) + dx * math.sin(r) + dy * math.cos(r)
            if (cx, cy) == (x1, y1) or (cx, cy) == (x0, y1):
                if droop > 12:
                    continue                                   # the bottom tapes went with it
        tape = Image.new("RGBA", (S(120), S(44)), (236, 230, 200, 200))
        tl = C.premult(tape.rotate(35 if (cx == x0) == (cy == y0) else -35, expand=True))
        img = C.paste(img, tl, px - tl.shape[1] // 2, py - tl.shape[0] // 2, 0.85)
    if droop > 0.5:                                            # the loose tape still on the board, top right
        tape = Image.new("RGBA", (S(120), S(44)), (236, 230, 200, 200))
        tl = C.premult(tape.rotate(-35, expand=True))
        img = C.paste(img, tl, S(x1 + 30) - tl.shape[1] // 2, S(y0 - 10) - tl.shape[0] // 2, 0.7)
    return img


# ---------------------------------------------------------------- result cards
def card_ips(s, t):
    return C.result_card(t, s["t"], "UNITED", 5, 2, "IPSWICH", top="30 AUGUST 2026  |  PREMIER LEAGUE",
                         foot="FERNANDES 40', 61' PEN, 68'  ·  GREAVES OG 56'  ·  MBEUMO 82'",
                         foot2="IPSWICH: DAVIS 29', AKPOM 90+1'")


def card_eve(s, t):
    return C.result_card(t, s["t"], "EVERTON", 1, 2, "UNITED", top="6 SEPTEMBER 2026  |  PREMIER LEAGUE",
                         foot="88'  ŠEŠKO", flip=(m("flip_eve"), 2, 2, "90+6'  MAITLAND-NILES"),
                         foot2="UNITED: MBEUMO 46', ŠEŠKO 88'   ·   EVERTON: GEORGE 83', MAITLAND-NILES 90+6'"
                         if t >= m("flip_eve") else "")


def card_sab(s, t):
    return C.result_card(t, s["t"], "UNITED", 4, 0, "SABAH", top="10 SEPTEMBER 2026  |  EUROPE",
                         foot="CUNHA 27'  ·  FERNANDES 42'  ·  ŠEŠKO 45'  ·  MARTÍNEZ 68'")


def card_city(s, t):
    return C.result_card(t, s["t"], "UNITED", 0, 1, "MAN CITY", top="13 SEPTEMBER 2026  |  PREMIER LEAGUE",
                         foot="HAALAND 60'")


def card_bri(s, t):
    return C.result_card(t, s["t"], "UNITED", 2, 0, "BRIGHTON", top="16 SEPTEMBER 2026  |  LEAGUE CUP",
                         foot="LACEY 8'  ·  MOUNT 10'",
                         flip=(m("flip_bri"), 2, 3, "KOSTOULAS 45+1'  ·  GROSS 65'  ·  DE CUYPER 69'"),
                         foot2="UNITED OUT OF THE LEAGUE CUP" if t >= m("flip_bri") + 0.6 else "")


def card_ful(s, t):
    return C.result_card(t, s["t"], "FULHAM", 1, 1, "UNITED", top="20 SEPTEMBER 2026  |  PREMIER LEAGUE",
                         foot="MARTÍNEZ OG 63'  ·  CUNHA 89'")


def card_tot(s, t):
    ft = T.wt("R39", "ninety") + 0.1
    return C.result_card(t, s["t"], "UNITED", 1, 0, "TOTTENHAM", top="10 OCTOBER 2026  |  PREMIER LEAGUE",
                         foot="MBEUMO 73'", flip=(ft, 1, 1, "SOLANKE 90+2'"),
                         foot2="UNITED: MBEUMO 73'" if t >= ft else "")


def card_atl(s, t):
    return C.result_card(t, s["t"], "ATLÉTICO", 1, 0, "UNITED", top="13 OCTOBER 2026  |  EUROPE",
                         foot="1'  BARRIOS", flip=(T.wt("R41", "lasted"), 2, 0, "BARRIOS 1'  ·  LOOKMAN 79'"))


def card_leeds(s, t):
    return C.chapter_card(t, s["t"], "LEEDS WEEK", "A FICTIONALISED CARRINGTON DETOUR",
                          "Animated parody: the private scenes that follow are invented.")


# ---------------------------------------------------------------- the tablet
def plan_screen(lines, accent=C.RED):
    return C.slide(lines, accent=accent)


def tab_dna(s, t):
    """the tablet, close: THE PLAN, NOW WITH EUROPEAN DNA. At 1.6 s it is moved away to the left, out of somebody's
    way (Martínez, trying to get into the shot)"""
    u = t - s["t"]
    bg = plate_view("W", 700, 330, 2.2, 7.0) * 0.8
    scr = plan_screen((("THE PLAN", 150, (255, 255, 255), 230), ("NOW WITH", 90, (210, 210, 210), 450),
                       ("EUROPEAN DNA", 170, (246, 180, 40), 560)))
    dx = -1400 * C.sm((u - 1.55) / 0.45)
    dy = 6 * math.sin(u * 1.3)
    img = C.device_frame(bg.copy(), (360 + dx, 120 + dy, 1560 + dx, 900 + dy), scr)
    img = fingers(img, 1560 + dx, 470 + dy, side="R")
    img = fingers(img, 360 + dx, 520 + dy, side="L")
    return img


def fingers(img, x, y, side="R", down=False):
    """two drawn fingertips and a thumb gripping a device's edge at (x, y) (1920 layout); down: the forearm runs
    down out of the bottom of the frame (a device held up close to the lens) instead of out to the side"""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    ink, w, skin = (24, 18, 20, 255), max(2, S(5)), (228, 176, 140, 255)
    sg = 1 if side == "R" else -1
    for k in range(3):                                   # fingertips curled over the edge, overlapping
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
    if down:                                             # wrist to the bottom edge, widening towards the lens
        sleeve = [(S(x + 140 * sg), S(y - 40)), (S(x + 300 * sg), S(y + 60)), (S(x + 420 * sg), S(1120)),
                  (S(x + 170 * sg), S(1120)), (S(x + 200 * sg), S(y + 220))]
    dr.polygon(sleeve, fill=(32, 34, 44, 255))
    dr.line(sleeve + [sleeve[0]], fill=ink, width=w)
    return C.over(img, C.premult(im))


def tab_charge(s, t):
    """the tablet face up on a desk, plugged in, alone: THE PLAN, 4 %"""
    u = t - s["t"]
    bg = plate_view("OF", 620, 300, 1.9, 9.0) * 0.72
    img = bg.copy()
    # the desk top: warm wood, in perspective, filling the lower half
    yy = np.arange(OH, dtype=np.float32)[:, None]
    desk = (yy > OH * 0.52).astype(np.float32)
    wood = np.float32([0.42, 0.25, 0.14]) * (0.8 + 0.2 * (yy / OH))[..., None]
    grain = (np.sin(np.arange(OW, dtype=np.float32)[None, :] * 0.02 + yy * 0.3) * 0.03)[..., None]
    img = img * (1 - desk[..., None]) + (wood + grain) * desk[..., None]
    img[int(OH * 0.52):int(OH * 0.52) + S(4)] *= 0.5
    scr = plan_screen((("THE PLAN", 160, (255, 255, 255), 300), ("CHARGING", 80, (200, 200, 200), 520),
                       ("4%", 110, (230, 60, 60), 640)))
    tab = np.zeros((OH, OW, 3), np.float32)
    tab = C.device_frame(tab, (560, 300, 1360, 800), scr)
    msk = np.zeros((OH, OW), np.float32)
    cv2.rectangle(msk, (S(560), S(300)), (S(1360), S(800)), 1.0, -1)
    src = np.float32([[S(560), S(300)], [S(1360), S(300)], [S(1360), S(800)], [S(560), S(800)]])
    dst = np.float32([[S(560), S(560)], [S(1360), S(560)], [S(1600), S(1000)], [S(320), S(1000)]])
    H = cv2.getPerspectiveTransform(src, dst)
    tw = cv2.warpPerspective(tab, H, (OW, OH))
    mw = cv2.warpPerspective(msk, H, (OW, OH))
    sh = cv2.GaussianBlur(mw, (0, 0), 14 * RS)
    img = img * (1 - 0.45 * np.roll(sh, S(14), 0)[..., None])
    img = img * (1 - mw[..., None]) + tw * mw[..., None]
    # the cable, to the edge of the frame
    pts = np.int32([[S(1300 + 200 * k / 20 + 10 * math.sin(k)), S(760 + 300 * (k / 20) ** 2)] for k in range(21)])
    pts = np.int32([[S(1430 + 200 * k / 20 + 10 * math.sin(k)), S(940 + 160 * (k / 20) ** 2)] for k in range(21)])
    cv2.polylines(img, [pts], False, (0.92, 0.92, 0.92), max(2, S(9)), cv2.LINE_AA)
    cv2.polylines(img, [pts], False, (0.1, 0.1, 0.1), max(1, S(2)), cv2.LINE_AA)
    # the charging light breathing
    k = 0.5 + 0.5 * math.sin(u * 3.0)
    cv2.circle(img, (S(1440), S(930)), S(7), (0.2 + 0.6 * k, 0.9 * k + 0.1, 0.25), -1, cv2.LINE_AA)
    return zoom(img, 1.0 + 0.03 * u / max(0.1, s["end"] - s["t"]))


def overlay(img, t, s):
    """Wilcox moves his tablet into the foreground of the documentary camera's shot (THE PLAN: IT'S WORKING)"""
    if not s.get("tablet"):
        return img
    t0, a, b = s["tablet"]
    u = t - t0
    x = 2150 - 900 * C.sm((u - 0.15) / 0.7)
    if x >= 2100:
        return img
    scr = plan_screen(((a, 170, (255, 255, 255), 260), (b, 120, (90, 220, 120), 520)))
    lay = np.zeros((OH, OW, 3), np.float32)
    msk = np.zeros((OH, OW), np.float32)
    box = (x, 140, x + 1100, 980)
    lay = C.device_frame(lay, box, scr)
    cv2.rectangle(msk, (S(box[0]), S(box[1])), (S(box[2]), S(box[3])), 1.0, -1)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.2 * RS)                      # close to the lens: a touch soft
    img = img * (1 - msk[..., None]) + lay * msk[..., None]
    return fingers(img, x, 520, side="L", down=True)


# ---------------------------------------------------------------- Lacey's shirt
def lacey_shirt(s, t):
    """the wall of shirts, close on one still hanging as it was before the match; LACEY on the plate above it"""
    u = (t - s["t"]) / max(0.1, s["end"] - s["t"])
    z = 6.0 + 0.4 * C.sm(u)
    img = plate_view("W", 1335, 300, z, 0.0)
    from studio.film import render as R
    P = R.plate("W")
    cx, cy = P.clamp(1335, 300, z)
    M = P.M(cx, cy, z)
    sc = M[0, 0]
    px, py = M[0, 0] * 1340 + M[0, 2], M[1, 1] * 238 + M[1, 2]       # the name plate above the hook
    w, h = 74 * sc / RS, 15 * sc / RS
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rectangle((px - w / 2 * RS, py - h / 2 * RS, px + w / 2 * RS, py + h / 2 * RS), fill=(26, 26, 30, 255),
                 outline=(150, 120, 60, 255), width=max(2, S(4)))
    f = C.font(C.OSWALD, h * 0.72, 600)
    C.draw_text(dr, (px, py - h * 0.48 * RS), "LACEY", f, (238, 238, 238, 255), track=3, anchor="c")
    return C.over(img, C.premult(im))


# ---------------------------------------------------------------- the calendar
def _cal_page(month, days, first, hi=None):
    w, h = 900, 760
    im = Image.new("RGB", (w, h), (250, 250, 247))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, w, 150), fill=C.RED)
    f = C.ImageFont.truetype(C.BEBAS, 120)
    tw = dr.textlength(month, font=f)
    dr.text(((w - tw) / 2, 14), month, font=f, fill=(255, 255, 255))
    fd = C.ImageFont.truetype(C.OSWALD, 40)
    for k, d in enumerate("MTWTFSS"):
        dr.text((60 + k * 118, 168), d, font=fd, fill=(120, 120, 120))
    for day in range(1, days + 1):
        i = first + day - 1
        x, y = 50 + (i % 7) * 118, 230 + (i // 7) * 100
        dr.text((x + 10, y), str(day), font=fd, fill=(40, 40, 40))
        if hi and day in hi:
            dr.ellipse((x - 6, y - 6, x + 76, y + 70), outline=(200, 30, 36), width=6)
    return np.asarray(im).astype(np.float32) / 255


def calendar(s, t):
    """September flips up and over to October (a top-hinged page), the dressing room behind"""
    u = t - s["t"]
    bg = plate_view("W", 1000, 300, 2.6, 8.0) * 0.75
    sep = _cal_page("SEPTEMBER 2026", 30, 1, hi=(6, 10, 13, 16, 20))
    octo = _cal_page("OCTOBER 2026", 31, 3, hi=(10, 13, 18))
    img = bg.copy()
    x0, y0, w, h = S(510), S(170), S(900), S(760)
    img[y0 + S(10):y0 + h + S(10), x0 + S(10):x0 + w + S(10)] *= 0.55          # its shadow on the wall
    img[y0:y0 + h, x0:x0 + w] = cv2.resize(octo, (w, h), interpolation=cv2.INTER_AREA)
    flip = C.sm((u - 0.9) / 0.8)
    if flip < 1:
        ph = int(h * math.cos(flip * math.pi / 2) + 1)
        pg = cv2.resize(sep, (w, max(1, ph)), interpolation=cv2.INTER_AREA) * (1 - 0.35 * flip)
        img[y0:y0 + ph, x0:x0 + w] = pg
    # the spiral binding
    for k in range(14):
        cx = x0 + S(40) + k * (w - S(80)) // 13
        cv2.circle(img, (cx, y0 + S(8)), S(12), (0.25, 0.25, 0.28), max(2, S(5)), cv2.LINE_AA)
    return img


# ---------------------------------------------------------------- the mug, Carrington, the hedge
def mug(s, t):
    """a white mug on an office windowsill, sharp; the camera racks focus to Carrington beyond the glass: the hedge,
    and a pair of binoculars rising out of it"""
    u = (t - s["t"]) / max(0.1, s["end"] - s["t"])
    rack = C.sm((u - 0.3) / 0.35)
    bg = plate_view("CQ", 900, 520, 1.6, 9.0 * (1 - rack) + 0.01)
    img = bg.copy()
    # the binoculars: two dark lenses rising out of the hedge line (plate px 1210, 560 at this zoom)
    b = C.sm((u - 0.62) / 0.25)
    if b > 0:
        bx, by = S(1240), S(640 - 40 * b)
        for dx in (-S(22), S(22)):
            cv2.circle(img, (bx + dx, by), S(17), (0.06, 0.07, 0.06), -1, cv2.LINE_AA)
            cv2.circle(img, (bx + dx - S(4), by - S(5)), S(5), (0.75, 0.8, 0.85), -1, cv2.LINE_AA)
        img[by + S(10):S(660), bx - S(40):bx + S(40)] = img[by + S(10):S(660), bx - S(40):bx + S(40)] * 0.6 \
            + np.float32([0.10, 0.22, 0.08]) * 0.4
    # the window frame: dark mullions
    img[:, :S(70)] = img[:, :S(70)] * 0.15
    img[:S(56)] = img[:S(56)] * 0.15
    img[:, S(1240) + S(800):] *= 0.15
    # the sill and the mug (sharp first, then soft)
    fg = np.zeros((OH, OW, 4), np.float32)
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    ink, w = (24, 18, 20, 255), max(2, S(7))
    dr.rectangle((0, S(860), OW, OH), fill=(236, 232, 224, 255))
    dr.line([(0, S(860)), (OW, S(860))], fill=ink, width=w)
    mx, my = S(560), S(560)
    dr.ellipse((mx + S(250), my + S(80), mx + S(420), my + S(250)), outline=ink, width=S(34))
    dr.ellipse((mx + S(250), my + S(80), mx + S(420), my + S(250)), outline=(250, 250, 250, 255), width=S(20))
    dr.rectangle((mx, my, mx + S(300), my + S(300)), fill=(250, 250, 250, 255))
    dr.ellipse((mx, my + S(250), mx + S(300), my + S(330)), fill=(250, 250, 250, 255))
    dr.line([(mx, my), (mx, my + S(290))], fill=ink, width=w)
    dr.line([(mx + S(300), my), (mx + S(300), my + S(290))], fill=ink, width=w)
    dr.arc((mx, my + S(250), mx + S(300), my + S(330)), 0, 180, fill=ink, width=w)
    dr.ellipse((mx, my - S(40), mx + S(300), my + S(40)), fill=(230, 228, 222, 255), outline=ink, width=w)
    dr.ellipse((mx + S(22), my - S(26), mx + S(278), my + S(26)), fill=(150, 104, 66, 255))
    fg = C.premult(im)
    blur = 0.4 + 10 * rack
    fg = cv2.GaussianBlur(fg, (0, 0), blur * RS)
    return C.over(img, fg)


# ---------------------------------------------------------------- the mixed zone's flashes
def flashes(img, s, t, M, sc):
    """press flashes going off along the barrier of an empty mixed zone"""
    rng = np.random.default_rng(int(t * 30))
    out = img
    for k in range(3):
        if rng.random() < 0.22:
            x, y = rng.uniform(OW * 0.15, OW * 0.85), rng.uniform(OH * 0.35, OH * 0.6)
            yy, xx = np.ogrid[0:OH, 0:OW]
            g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * (S(120)) ** 2))).astype(np.float32)
            out = out + g[..., None] * 0.9 + 0.06
    return np.clip(out, 0, 1)


def card_intl(s, t):
    return C.chapter_card(t, s["t"], "INTERNATIONAL BREAK", "GET AWAY. RESET. COME BACK FRESH.",
                          "Five points from five league games. Out of the League Cup.")


def lights_off(img, s, t, M, sc):
    """the empty dressing room; the ceiling lights go off a bank at a time (the far wall first), leaving the exit sign"""
    u = t - s["t"]
    k = sum(1 for tk in (0.9, 1.6, 2.3) if u > tk)
    dim = [1.0, 0.72, 0.48, 0.26][k]
    out = img * dim
    if k:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        gx, gy = M[0, 0] * 478 + M[0, 2], M[1, 1] * 250 + M[1, 2]                 # the door, its exit light
        g = np.exp(-(((xx - gx) / (90 * M[0, 0])) ** 2 + ((yy - gy) / (40 * M[0, 0])) ** 2))
        out = out + g[..., None] * np.float32([0.05, 0.25, 0.08]) * (1 - dim)
    return out
