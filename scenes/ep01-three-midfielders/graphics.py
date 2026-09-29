"""On-screen graphics and the picture finish: the opening text over Carrington, the title card, Jim's paperwork,
drizzle for the grey Manchester exterior, colour grades, vignette and grain. Everything is drawn at the output
resolution (layout in 1080 x 1920 px, scaled by RS)."""
import math, functools, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from engine import OW, OH, RS

BEBAS, INTER, MONT = "fonts/BebasNeue-Regular.ttf", "fonts/Inter.ttf", "fonts/Montserrat.ttf"


def sm(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


@functools.lru_cache(maxsize=64)
def font(path, size, weight=None):
    f = ImageFont.truetype(path, int(round(size)))
    if weight is not None:
        try: f.set_variation_by_axes([weight])
        except Exception: pass
    return f


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
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


def shadow_of(layer, blur, offset, strength):
    a = cv2.GaussianBlur(layer[..., 3], (0, 0), blur * RS)
    a = np.roll(np.roll(a, int(offset[1] * RS), 0), int(offset[0] * RS), 1)
    return a * strength


def over(img, layer, alpha=1.0):
    return img * (1 - layer[..., 3:4] * alpha) + layer[..., :3] * alpha


# ---------------------------------------------------------------- opening text over Carrington
EXT_TEXT = (("MANCHESTER", BEBAS, 168, None, 10, 560, (255, 255, 255)),
            ("TRANSFER DEADLINE DAY", BEBAS, 92, None, 7, 758, (255, 255, 255)))


def ext_text(img, t, t0, t1):
    k = sm((t - t0 - 0.05) / 0.35)
    if k <= 0: return img
    lay = text_layer(EXT_TEXT)
    # a slow drift upwards while it holds
    dy = int(round((1 - k) * 18 * RS + (t - t0) * 4 * RS))
    lay = np.roll(lay, -dy, 0)
    sh = shadow_of(lay, 10, (0, 6), 0.55)
    img = img * (1 - sh[..., None] * k)
    # a thin red rule between the lines
    y = int((737 - (t - t0) * 4) * RS) - (int((1 - k) * 18 * RS))
    w = int(300 * RS * k)
    img[y:y + max(2, int(5 * RS)), OW // 2 - w // 2:OW // 2 + w // 2] = (0.84, 0.07, 0.10)
    return over(img, lay, k)


# ---------------------------------------------------------------- title card
TITLE = (("ALL OR", BEBAS, 250, None, 12, 610, (255, 255, 255)),
         ("SOMETHING", BEBAS, 250, None, 12, 830, (255, 255, 255)))
TAG = (("Everything except what the manager", INTER, 44, 500, 0, 1150, (225, 225, 225)),
       ("actually asked for.", INTER, 44, 500, 0, 1210, (225, 225, 225)))


def title_card(t, t0):
    u = t - t0
    img = np.zeros((OH, OW, 3), np.float32)
    # dark red glow behind the title, pulsing once on the boom
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    g = np.exp(-(((xx - OW / 2) / (OW * 0.55)) ** 2 + ((yy - OH * 0.40) / (OH * 0.22)) ** 2))
    boom = 0.55 + 0.45 * math.exp(-u * 2.2)
    img += g[..., None] * np.float32([0.30, 0.02, 0.03]) * boom
    s = 1.0 + 0.10 * math.exp(-u * 7.0)                                # punches in on the boom
    lay = text_layer(TITLE)
    if abs(s - 1) > 1e-3:
        M = cv2.getRotationMatrix2D((OW / 2, OH * 0.40), 0, s)
        lay = cv2.warpAffine(lay, M, (OW, OH), flags=cv2.INTER_LINEAR)
    img = over(img, lay)
    # red rule
    y = int(1080 * RS); w = int(560 * RS * sm(u / 0.35))
    img[y:y + int(8 * RS), OW // 2 - w // 2:OW // 2 + w // 2] = (0.86, 0.06, 0.09)
    img = over(img, text_layer(TAG), sm((u - 0.35) / 0.4))
    return img


# ---------------------------------------------------------------- Jim's paperwork
@functools.lru_cache(maxsize=2)
def paper_sprite():
    """a stapled A4 report, drawn in the sheets' style (ink outline, flat colour)"""
    w, h = int(640 * RS), int(860 * RS)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    lw = max(2, int(5 * RS))
    dr.rounded_rectangle((10, 10, w, h), radius=int(10 * RS), fill=(250, 249, 244, 255), outline=(35, 28, 22, 255), width=lw)
    f1 = font(MONT, 38 * RS, 800); f2 = font(INTER, 26 * RS, 600)
    dr.text((50 * RS, 60 * RS), "INEOS", font=f1, fill=(200, 20, 30, 255))
    dr.text((50 * RS, 115 * RS), "BRITAIN: THE BIGGER ISSUES", font=f2, fill=(40, 40, 45, 255))
    y = 180 * RS
    rng = np.random.default_rng(7)
    while y < h - 60 * RS:
        L = rng.uniform(0.55, 0.95) * (w - 110 * RS)
        dr.rounded_rectangle((50 * RS, y, 50 * RS + L, y + 9 * RS), radius=int(4 * RS), fill=(150, 150, 158, 255))
        y += 34 * RS if rng.uniform() > 0.18 else 60 * RS
    dr.line((w - 70 * RS, 22 * RS, w - 30 * RS, 50 * RS), fill=(120, 120, 128, 255), width=max(2, int(5 * RS)))
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


def paper(img, t, t_lower):
    """held up in front of him, then lowered out of frame"""
    u = sm((t - t_lower) / 0.4)
    if u >= 1: return img
    sp = paper_sprite()
    ang = -5 + 3 * u
    cx, cy = OW * 0.52, OH * 0.83 + u * 900 * RS
    M = cv2.getRotationMatrix2D((sp.shape[1] / 2, sp.shape[0] / 2), ang, 1.0)
    M[0, 2] += cx - sp.shape[1] / 2; M[1, 2] += cy - sp.shape[0] / 2
    lay = cv2.warpAffine(sp, M, (OW, OH), flags=cv2.INTER_LINEAR)
    sh = shadow_of(lay, 14, (8, 10), 0.35)
    img = img * (1 - sh[..., None])
    return over(img, lay)


# ---------------------------------------------------------------- weather, grades, finish
def drizzle(img, t, strength=1.0):
    """fine diagonal drizzle streaks, drawn at half resolution"""
    h, w = OH // 2, OW // 2
    lay = np.zeros((h, w), np.float32)
    rng = np.random.default_rng(11)
    n = 420
    x0 = rng.uniform(-0.2, 1.2, n) * w; y0 = rng.uniform(0, 1, n) * h
    sp = rng.uniform(0.9, 1.4, n); ln = rng.uniform(10, 22, n) * RS
    for i in range(n):
        y = (y0[i] + t * 900 * RS * sp[i] / 2) % (h + 40) - 20
        x = x0[i] + (y - y0[i]) * 0.18
        cv2.line(lay, (int(x), int(y)), (int(x + ln[i] * 0.18), int(y + ln[i])), 1.0, 1, cv2.LINE_AA)
    lay = cv2.resize(cv2.GaussianBlur(lay, (0, 0), 0.6), (OW, OH))
    return img * (1 - 0.18 * strength * lay[..., None]) + 0.82 * 0.18 * strength * lay[..., None]


def grey_sky(img):
    """turn the blue sky into Manchester grey: desaturate the blues, flatten the light"""
    hsv = cv2.cvtColor(np.clip(img, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    sky = np.clip((s - 0.18) / 0.2, 0, 1) * np.exp(-((h - 212) / 22) ** 2) * np.clip((v - 0.45) / 0.2, 0, 1)
    sky = cv2.GaussianBlur(sky.astype(np.float32), (0, 0), 3 * RS)
    grey = np.float32([0.70, 0.72, 0.75])
    lum = img.mean(2, keepdims=True)
    out = img * (1 - sky[..., None]) + (grey * (0.82 + 0.25 * lum)) * sky[..., None]
    # overcast: less saturation and contrast, a touch cooler, shadows lifted
    l2 = out.mean(2, keepdims=True)
    out = l2 + (out - l2) * 0.55
    out = 0.1 + out * 0.82
    out *= np.float32([0.97, 0.99, 1.03])
    return out


def grade(img, kind, t=0.0):
    if kind == "grey":
        img = grey_sky(img)
        img = drizzle(img, t, 0.9)
    elif kind == "board":
        l = img.mean(2, keepdims=True)
        img = l + (img - l) * 0.93
        img = (img - 0.5) * 1.06 + 0.5
        img *= np.float32([1.01, 1.0, 0.985])
    elif kind == "monaco":
        l = img.mean(2, keepdims=True)
        img = l + (img - l) * 1.12
        img = img * np.float32([1.04, 1.01, 0.95]) + 0.015
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
        dr.rectangle((x - int(22 * S), y - int(14 * S), x - int(12 * S), y + int(146 * S)), fill=(218, 22, 30, 255))
        dr.text((x + int(8 * S), y - int(6 * S)), a, font=fn, fill=(255, 255, 255, 255))
        dr.text((x + int(10 * S), y + int(88 * S)), b, font=fr, fill=(215, 215, 215, 255))
    elif kind == "place":                                 # location slug, top left
        x, y = int(64 * S), int(150 * S)
        fn, fr = font(BEBAS, 76 * S), font(INTER, 36 * S, 600)
        w = int(max(dr.textlength(a, font=fn), dr.textlength(b, font=fr)) + 48 * S)
        dr.rectangle((x - int(24 * S), y - int(16 * S), x + w, y + int(160 * S)), fill=(12, 12, 14, 175))
        dr.text((x, y), a, font=fn, fill=(255, 255, 255, 255))
        dr.rectangle((x, y + int(88 * S), x + int(96 * S), y + int(94 * S)), fill=(218, 22, 30, 255))
        dr.text((x, y + int(106 * S)), b, font=fr, fill=(240, 240, 240, 255))
    elif kind == "stats":                                 # the transfer tally
        cols = [("STRIKERS", "0"), ("LEFT-BACKS", "0"), ("MIDFIELDERS", "3")]
        y = int(1440 * S)
        fh, fl, fnum = font(INTER, 30 * S, 600), font(INTER, 30 * S, 600), font(BEBAS, 150 * S)
        title = "DEADLINE DAY SIGNINGS"
        wt = dr.textlength(title, font=fh)
        dr.rectangle((int(40 * S), y - int(30 * S), OW - int(40 * S), y + int(270 * S)), fill=(12, 12, 14, 185))
        dr.rectangle((int(40 * S), y - int(30 * S), OW - int(40 * S), y - int(22 * S)), fill=(218, 22, 30, 255))
        dr.text(((OW - wt) / 2, y), title, font=fh, fill=(200, 200, 200, 255))
        cw = (OW - 80 * S) / 3
        for i, (lab, num) in enumerate(cols):
            cx = 40 * S + cw * (i + 0.5)
            wn = dr.textlength(num, font=fnum); wl = dr.textlength(lab, font=fl)
            col = (255, 255, 255, 255) if num != "3" else (240, 200, 60, 255)
            dr.text((cx - wn / 2, y + int(44 * S)), num, font=fnum, fill=col)
            dr.text((cx - wl / 2, y + int(206 * S)), lab, font=fl, fill=(230, 230, 230, 255))
    arr = np.asarray(im).astype(np.float32) / 255.0
    arr[..., :3] *= arr[..., 3:4]
    return arr


def captions(img, t, caps):
    for t0, t1, kind, a, b in caps:
        if not (t0 <= t < t1): continue
        k = sm((t - t0) / 0.22) * (1 - sm((t - (t1 - 0.2)) / 0.2))
        lay = caption_layer(kind, a, b)
        dx = int(round((1 - sm((t - t0) / 0.3)) * -36 * RS)) if kind != "stats" else 0
        if dx: lay = np.roll(lay, dx, 1) if dx > -OW else lay
        if kind == "stats":                                # the numbers land one by one
            pass
        sh = shadow_of(lay, 8, (0, 4), 0.35)
        img = img * (1 - sh[..., None] * k)
        img = img * (1 - lay[..., 3:4] * k) + lay[..., :3] * k
    return img
