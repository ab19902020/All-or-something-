"""On-screen graphics and the picture finish: the opening text over the MKM Stadium, the full-time score, the goal
scoreboards, the Tigers-ending scoreboard, the title card, Steve's clipboard, the ball, colour grades, vignette and
grain. Everything is drawn at the output resolution (layout in 1080 x 1920 px, scaled by RS)."""
import math, functools, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from engine import OW, OH, RS

BEBAS, INTER, MONT = "fonts/BebasNeue-Regular.ttf", "fonts/Inter.ttf", "fonts/Montserrat.ttf"
RED, AMBER = (218, 22, 30), (246, 160, 30)


def sm(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


@functools.lru_cache(maxsize=64)
def font(path, size, weight=None):
    f = ImageFont.truetype(path, int(round(size)))
    if weight is not None:
        try: f.set_variation_by_axes([weight])
        except Exception: pass
    return f


def premult(im):
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


@functools.lru_cache(maxsize=32)
def text_layer(lines, key=0):
    """lines: ((text, font path, size, weight, tracking px, y, colour rgb), ...) centred -> premult RGBA float"""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for text, fp, size, weight, track, y, col in lines:
        f = font(fp, size * RS, weight)
        widths = [dr.textlength(ch, font=f) for ch in text]
        total = sum(widths) + track * RS * (len(text) - 1)
        x = (OW - total) / 2
        for ch, w in zip(text, widths):
            dr.text((x, y * RS), ch, font=f, fill=tuple(col) + (255,))
            x += w + track * RS
    return premult(im)


def shadow_of(layer, blur, offset, strength):
    a = cv2.GaussianBlur(layer[..., 3], (0, 0), blur * RS)
    a = np.roll(np.roll(a, int(offset[1] * RS), 0), int(offset[0] * RS), 1)
    return a * strength


def over(img, layer, alpha=1.0):
    return img * (1 - layer[..., 3:4] * alpha) + layer[..., :3] * alpha


def scaled(layer, s, cx, cy):
    if abs(s - 1) < 1e-3: return layer
    M = cv2.getRotationMatrix2D((cx, cy), 0, s)
    return cv2.warpAffine(layer, M, (OW, OH), flags=cv2.INTER_LINEAR)


# ---------------------------------------------------------------- opening text over the MKM Stadium
EXT_TEXT = (("HULL", BEBAS, 230, None, 16, 230, (255, 255, 255)),
            ("OPENING DAY", BEBAS, 96, None, 9, 496, (255, 255, 255)))


def ext_text(img, t, t0, t1):
    k = sm((t - t0 - 0.05) / 0.35)
    if k <= 0: return img
    lay = text_layer(EXT_TEXT)
    # a slow drift upwards while it holds
    dy = int(round((1 - k) * 18 * RS + (t - t0) * 4 * RS))
    lay = np.roll(lay, -dy, 0)
    sh = shadow_of(lay, 12, (0, 6), 0.6)
    img = img * (1 - sh[..., None] * k)
    # a thin amber rule between the lines: Hull's colours
    y = int((476 - (t - t0) * 4) * RS) - (int((1 - k) * 18 * RS))
    w = int(300 * RS * k)
    img[y:y + max(2, int(5 * RS)), OW // 2 - w // 2:OW // 2 + w // 2] = np.float32(AMBER) / 255
    return over(img, lay, k)


# ---------------------------------------------------------------- full time
@functools.lru_cache(maxsize=2)
def score_layer():
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    S = RS
    ft = font(INTER, 56 * S, 700)
    txt = "FULL TIME"
    tw = dr.textlength(txt, font=ft)
    dr.text(((OW - tw) / 2, 540 * S), txt, font=ft, fill=(236, 236, 236, 255))
    dr.rectangle((OW / 2 - 70 * S, 622 * S, OW / 2 + 70 * S, 630 * S), fill=RED + (255,))
    rows = (("HULL CITY", "2", AMBER, 700), ("MANCHESTER UNITED", "0", RED, 1010))
    fn, fs = font(BEBAS, 96 * S), font(BEBAS, 300 * S)
    for name, sc, col, y in rows:
        dr.rectangle((70 * S, (y + 30) * S, 88 * S, (y + 250) * S), fill=col + (255,))
        dr.text((116 * S, (y + 84) * S), name, font=fn, fill=(255, 255, 255, 255))
        w = dr.textlength(sc, font=fs)
        dr.text((OW - 90 * S - w, (y - 10) * S), sc, font=fs, fill=(255, 255, 255, 255))
    dr.rectangle((70 * S, 978 * S, OW - 70 * S, 982 * S), fill=(90, 90, 96, 255))
    return premult(im)


def score_card(t, t0):
    """black; the score slams in (a punch of scale, a knock of the frame), then holds dead still"""
    u = t - t0
    img = np.zeros((OH, OW, 3), np.float32)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    g = np.exp(-(((xx - OW / 2) / (OW * 0.7)) ** 2 + ((yy - OH * 0.5) / (OH * 0.35)) ** 2))
    img += g[..., None] * np.float32([0.07, 0.07, 0.08])
    s = 1.0 + 0.16 * math.exp(-u * 16.0)
    lay = scaled(score_layer(), s, OW / 2, OH * 0.47)
    dy = int(10 * RS * math.exp(-u * 20) * math.cos(u * 60))
    if dy: lay = np.roll(lay, dy, 0)
    return over(img, lay)


# ---------------------------------------------------------------- the goals: a broadcast scoreboard
@functools.lru_cache(maxsize=4)
def board_layer(n, big=False):
    """HULL n-0 MAN UTD: a broadcast score bug, drawn once"""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    S = RS * (1.0 if big else 0.86)
    w, h = 1180 * S, 160 * S
    x0, y0 = (OW - w) / 2, (1180 if not big else 820) * RS
    dr.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=int(18 * S), fill=(14, 14, 18, 235))
    dr.rectangle((x0 + 24 * S, y0 + 22 * S, x0 + 38 * S, y0 + h - 22 * S), fill=AMBER + (255,))
    dr.rectangle((x0 + w - 38 * S, y0 + 22 * S, x0 + w - 24 * S, y0 + h - 22 * S), fill=RED + (255,))
    ft, fs = font(BEBAS, 110 * S), font(BEBAS, 132 * S)
    dr.text((x0 + 62 * S, y0 + 22 * S), "HULL", font=ft, fill=(255, 255, 255, 255))
    t2 = "MAN UTD" if not big else "UNITED"
    wt = dr.textlength(t2, font=ft)
    dr.text((x0 + w - 62 * S - wt, y0 + 22 * S), t2, font=ft, fill=(255, 255, 255, 255))
    sc = f"{n}-0"
    cw = 270 * S
    dr.rectangle((x0 + (w - cw) / 2, y0, x0 + (w + cw) / 2, y0 + h), fill=(245, 245, 245, 255))
    ws = dr.textlength(sc, font=fs)
    dr.text((x0 + (w - ws) / 2, y0 + 8 * S), sc, font=fs, fill=(14, 14, 18, 255))
    if not big:
        fl = font(INTER, 34 * S, 700)
        lab = "GOAL"
        wl = dr.textlength(lab, font=fl)
        dr.rounded_rectangle(((OW - wl) / 2 - 22 * S, y0 - 70 * S, (OW + wl) / 2 + 22 * S, y0 - 14 * S),
                             radius=int(8 * S), fill=AMBER + (255,))
        dr.text(((OW - wl) / 2, y0 - 66 * S), lab, font=fl, fill=(14, 14, 18, 255))
    return premult(im)


def goal_board(img, t, t0, n):
    u = t - t0
    k = sm((u - 0.08) / 0.12)
    if k <= 0: return img
    lay = board_layer(n)
    s = 1.0 + 0.12 * math.exp(-max(0.0, u - 0.08) * 14.0)
    lay = scaled(lay, s, OW / 2, 1255 * RS)
    sh = shadow_of(lay, 14, (0, 8), 0.45)
    img = img * (1 - sh[..., None] * k)
    return over(img, lay, k)


def tigers_board(img, t, t0):
    """the Tigers ending's scoreboard flash: HULL 2-0 UNITED, big"""
    u = t - t0
    lay = board_layer(2, True)
    s = 1.0 + 0.14 * math.exp(-u * 16.0)
    lay = scaled(lay, s, OW / 2, 915 * RS)
    sh = shadow_of(lay, 16, (0, 10), 0.5)
    img = img * (1 - sh[..., None])
    return over(img, lay)


# ---------------------------------------------------------------- the ball
@functools.lru_cache(maxsize=1)
def ball_sprite():
    """a football in the sheets' style: white, black patches, an ink outline (premult RGBA, 256 px)"""
    n = 256
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((8, 8, n - 8, n - 8), fill=(250, 250, 248, 255), outline=(22, 22, 26, 255), width=10)
    c = n / 2
    def pent(cx, cy, r, rot):
        return [(cx + r * math.cos(rot + i * 2 * math.pi / 5), cy + r * math.sin(rot + i * 2 * math.pi / 5)) for i in range(5)]
    dr.polygon(pent(c, c, 34, -math.pi / 2), fill=(26, 26, 30, 255))
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        dr.polygon(pent(c + 88 * math.cos(a), c + 88 * math.sin(a), 26, a + math.pi), fill=(26, 26, 30, 255))
    a = premult(im)
    return cv2.GaussianBlur(a, (0, 0), 0.8)


def ball(img, trail):
    """trail: [(x, y, diameter px), ...] newest first; older copies fade (motion blur)"""
    sp = ball_sprite()
    for j, (x, y, d) in reversed(list(enumerate(trail))):
        if d < 2: continue
        k = d / sp.shape[0]
        M = np.float32([[k, 0, x - k * sp.shape[1] / 2], [0, k, y - k * sp.shape[0] / 2]])
        lay = cv2.warpAffine(sp, M, (OW, OH), flags=cv2.INTER_AREA)
        img = over(img, lay, 1.0 if j == 0 else 0.35 * (1 - j / len(trail)))
    return img


# ---------------------------------------------------------------- Steve's clipboard
@functools.lru_cache(maxsize=4)
def clipboard_sprite(w):
    """a clipboard seen from behind: brown hardboard, the steel clip over its top edge, the paper's edge showing
    (premult RGBA, w px wide)"""
    w = int(w); h = int(w * 1.3)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    lw = max(3, int(w * 0.018))
    dr.rounded_rectangle((10 + w * 0.06, 10 + h * 0.035, 10 + w * 0.94, 10 + h * 0.08), radius=int(w * 0.01),
                         fill=(246, 244, 236, 255), outline=(40, 34, 30, 255), width=max(2, lw // 2))
    dr.rounded_rectangle((10, 10 + h * 0.05, 10 + w, 10 + h), radius=int(w * 0.05), fill=(150, 104, 62, 255),
                         outline=(34, 26, 22, 255), width=lw)
    dr.rounded_rectangle((10 + w * 0.05, 10 + h * 0.10, 10 + w * 0.95, 10 + h * 0.97), radius=int(w * 0.04),
                         outline=(128, 88, 52, 255), width=max(2, lw // 2))
    cw = w * 0.36
    dr.rounded_rectangle((10 + (w - cw) / 2, 10, 10 + (w + cw) / 2, 10 + h * 0.10), radius=int(w * 0.03),
                         fill=(186, 190, 198, 255), outline=(40, 40, 46, 255), width=lw)
    dr.line((10 + (w - cw) / 2 + lw * 2, 10 + h * 0.045, 10 + (w + cw) / 2 - lw * 2, 10 + h * 0.045),
            fill=(236, 238, 242, 255), width=max(2, lw // 2))
    a = premult(im)
    return cv2.GaussianBlur(a, (0, 0), 0.6)


def clipboard(img, cx, ytop, ed):
    """held low in front of him, tilted, its top edge at ytop (screen px); the rest runs out of the frame"""
    sp = clipboard_sprite(round(2.6 * ed / 8) * 8)
    M = cv2.getRotationMatrix2D((sp.shape[1] / 2, 0), -9, 1.0)
    M[0, 2] += cx + 0.35 * ed - sp.shape[1] / 2
    M[1, 2] += ytop
    lay = cv2.warpAffine(sp, M, (OW, OH), flags=cv2.INTER_LINEAR)
    sh = shadow_of(lay, 10, (0, -6), 0.25)
    img = img * (1 - sh[..., None])
    return over(img, lay)


# ---------------------------------------------------------------- title card
TITLE = (("ALL OR", BEBAS, 250, None, 12, 590, (255, 255, 255)),
         ("SOMETHING", BEBAS, 250, None, 12, 810, (255, 255, 255)))
TAG = (("NEW SEASON. SAME CORNERS.", BEBAS, 96, None, 6, 1120, (236, 236, 236)),)


def title_card(t, t0):
    u = t - t0
    img = np.zeros((OH, OW, 3), np.float32)
    # dark red glow behind the title, pulsing once on the boom
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    g = np.exp(-(((xx - OW / 2) / (OW * 0.55)) ** 2 + ((yy - OH * 0.40) / (OH * 0.22)) ** 2))
    boom = 0.55 + 0.45 * math.exp(-u * 2.2)
    img += g[..., None] * np.float32([0.30, 0.02, 0.03]) * boom
    s = 1.0 + 0.10 * math.exp(-u * 7.0)                                # punches in on the boom
    lay = scaled(text_layer(TITLE), s, OW / 2, OH * 0.40)
    img = over(img, lay)
    # red rule
    y = int(1080 * RS); w = int(560 * RS * sm(u / 0.35))
    img[y:y + int(8 * RS), OW // 2 - w // 2:OW // 2 + w // 2] = np.float32(RED) / 255
    img = over(img, text_layer(TAG), sm((u - 0.3) / 0.3))
    return img


# ---------------------------------------------------------------- grades, finish
def grade(img, kind, t=0.0):
    if kind == "sunny":                                  # opening day in Hull: bright, warm, a touch filmic
        l = img.mean(2, keepdims=True)
        img = l + (img - l) * 1.05
        img = (img - 0.5) * 1.04 + 0.5
        img = img * np.float32([1.03, 1.0, 0.96]) + 0.01
    elif kind == "room":                                 # the dressing room: warm lights, a little contrast
        l = img.mean(2, keepdims=True)
        img = l + (img - l) * 0.94
        img = (img - 0.5) * 1.06 + 0.5
        img *= np.float32([1.02, 1.0, 0.975])
    elif kind == "pitch":                                # the match: punchy, like a broadcast replay
        l = img.mean(2, keepdims=True)
        img = l + (img - l) * 1.08
        img = (img - 0.5) * 1.1 + 0.5
    return img


@functools.lru_cache(maxsize=2)
def _vignette():
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    r = np.sqrt(((xx - OW / 2) / (OW * 0.62)) ** 2 + ((yy - OH / 2) / (OH * 0.62)) ** 2)
    return (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)


def finish(img, frame):
    img = img * _vignette()
    rng = np.random.default_rng(frame)
    g = rng.standard_normal((OH // 2, OW // 2)).astype(np.float32)
    g = cv2.resize(g, (OW, OH), interpolation=cv2.INTER_LINEAR)
    img = img + g[..., None] * 0.009
    return np.clip(img, 0, 1)


# ---------------------------------------------------------------- documentary captions
@functools.lru_cache(maxsize=16)
def caption_layer(kind, a, b):
    """a caption drawn once (premultiplied RGBA float, full frame)"""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    S = RS
    if kind == "name":                                    # lower third: red bar, name, role
        x, y = int(64 * S), int(1262 * S)
        fn, fr = font(BEBAS, 84 * S), font(INTER, 40 * S, 600)
        wn = dr.textlength(a, font=fn); wr = dr.textlength(b, font=fr)
        w = int(max(wn, wr) + 64 * S)
        dr.rectangle((x - int(22 * S), y - int(14 * S), x + w, y + int(146 * S)), fill=(12, 12, 14, 170))
        dr.rectangle((x - int(22 * S), y - int(14 * S), x - int(12 * S), y + int(146 * S)), fill=RED + (255,))
        dr.text((x + int(8 * S), y - int(6 * S)), a, font=fn, fill=(255, 255, 255, 255))
        dr.text((x + int(10 * S), y + int(88 * S)), b, font=fr, fill=(215, 215, 215, 255))
    elif kind == "place":                                 # location slug, top left
        x, y = int(64 * S), int(150 * S)
        fn, fr = font(BEBAS, 76 * S), font(INTER, 36 * S, 600)
        w = int(max(dr.textlength(a, font=fn), dr.textlength(b, font=fr)) + 48 * S)
        dr.rectangle((x - int(24 * S), y - int(16 * S), x + w, y + int(160 * S)), fill=(12, 12, 14, 175))
        dr.text((x, y), a, font=fn, fill=(255, 255, 255, 255))
        dr.rectangle((x, y + int(88 * S), x + int(96 * S), y + int(94 * S)), fill=RED + (255,))
        dr.text((x, y + int(106 * S)), b, font=fr, fill=(240, 240, 240, 255))
    elif kind == "match":                                 # the minute and the moment, broadcast style
        fm, fe = font(BEBAS, 110 * S), font(BEBAS, 110 * S)
        wm = dr.textlength(a, font=fm); wev = dr.textlength(b, font=fe)
        x, y = int(OW - 64 * S - (wm + wev + 104 * S)), int(1500 * S)
        dr.rectangle((x, y, x + wm + 44 * S, y + 136 * S), fill=AMBER + (255,))
        dr.text((x + 22 * S, y + 10 * S), a, font=fm, fill=(14, 14, 18, 255))
        dr.rectangle((x + wm + 44 * S, y, x + wm + wev + 104 * S, y + 136 * S), fill=(14, 14, 18, 225))
        dr.text((x + wm + 74 * S, y + 10 * S), b, font=fe, fill=(255, 255, 255, 255))
    elif kind in ("epilogue", "epilogue2"):             # closing captions, centred on black
        f = font(INTER, 56 * S, 500)
        txt = a or b
        tw = dr.textlength(txt, font=f)
        y = int((860 if kind == "epilogue" else 960) * S)
        dr.text(((OW - tw) / 2, y), txt, font=f, fill=(236, 236, 236, 255))
    return premult(im)


def captions(img, t, caps):
    for t0, t1, kind, a, b in caps:
        if not (t0 <= t < t1): continue
        k = sm((t - t0) / 0.22) * (1 - sm((t - (t1 - 0.2)) / 0.2))
        if kind == "match": k = sm((t - t0) / 0.08)                        # snaps on, held to the cut
        lay = caption_layer(kind, a, b)
        dx = int(round((1 - sm((t - t0) / 0.3)) * -36 * RS)) if kind in ("name", "place") else 0
        if kind.startswith("epilogue"): k = sm((t - t0) / 0.45)            # held until the cut
        if dx: lay = np.roll(lay, dx, 1)
        if not kind.startswith("epilogue"):
            sh = shadow_of(lay, 8, (0, 4), 0.35)
            img = img * (1 - sh[..., None] * k)
        img = img * (1 - lay[..., 3:4] * k) + lay[..., :3] * k
    return img
