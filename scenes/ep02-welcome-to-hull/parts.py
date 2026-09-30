"""Cut every drawing the episode uses out of the 4x-upscaled character sheets (build/x4/).

Each part is a box on the 1x sheet. The matte is a flood fill of the paper from the box border on the 4x image
(floating range, so the panels' soft gradients fill but the ink outline stops it); inside the outline everything
is kept, so white eyes, collars and shoes stay solid. Only the components that reach the box's core are kept
(neighbouring drawings and labels are dropped).

Carrick's and Bruno's drawings from Episode 1 are cut the same way (their boxes are here too); a part that already
exists is only re-cut when named on the command line.

Output: build/parts/<name>.png (RGBA, 4x) and build/parts/meta.json {name: {sheet, box, off:[x, y], size:[w, h]}}:
a sheet coordinate (x, y) maps to part pixel ((x - off_x) * 4, (y - off_y) * 4). Check build/parts/check_*.jpg."""
import json, os, sys, numpy as np, cv2

S = {c: f"build/x4/{n}.png" for c, n in dict(
    ck="michael-carrick", br="bruno-fernandes", mn="kobbie-mainoo", mg="harry-maguire", sh="steve-holland",
    bs="benjamin-sesko", yt="yuri-tielemans", ls="luke-shaw", sl="senne-lammens").items()}
# name: (sheet, box x0, y0, x1, y1 in 1x sheet px)
P = {
    # Michael Carrick (no hero drawing: the front turnaround is his main body)
    "ck_front": ("ck", 30, 112, 228, 522), "ck_q34l": ("ck", 258, 112, 450, 522), "ck_q34r": ("ck", 686, 112, 866, 522),
    "ck_side": ("ck", 482, 112, 646, 532), "ck_back": ("ck", 893, 112, 1094, 532),
    "ck_g_explain": ("ck", 120, 1195, 282, 1352), "ck_g_talk": ("ck", 528, 1195, 672, 1352),
    "ck_g_crossed": ("ck", 28, 1195, 124, 1352), "ck_g_point": ("ck", 280, 1195, 430, 1352),
    "ck_walk": ("ck", 818, 1192, 946, 1370),
    # Bruno Fernandes
    "br_hero": ("br", 12, 108, 292, 818), "br_q34l": ("br", 462, 142, 594, 462), "br_q34r": ("br", 776, 142, 914, 462),
    "br_g_shrug": ("br", 973, 1088, 1104, 1218), "br_g_talk": ("br", 838, 1088, 977, 1218),
    "br_back": ("br", 926, 142, 1080, 468), "br_g_celebrate": ("br", 716, 1088, 840, 1218),
    # Kobbie Mainoo
    "mn_hero": ("mn", 12, 108, 274, 818), "mn_q34l": ("mn", 466, 142, 592, 464), "mn_q34r": ("mn", 783, 142, 905, 464),
    "mn_back": ("mn", 938, 142, 1066, 464), "mn_g_crossed": ("mn", 836, 1050, 912, 1176),
    # Harry Maguire (mg_hand: his open palm, raised into a close-up from below the frame)
    "mg_hero": ("mg", 6, 100, 295, 828), "mg_q34l": ("mg", 462, 140, 596, 468), "mg_q34r": ("mg", 770, 140, 910, 468),
    "mg_back": ("mg", 930, 140, 1082, 468), "mg_hand": ("mg", 458, 1088, 558, 1203),
    "mg_confused": ("mg", 697, 768, 813, 915), "mg_g_talk": ("mg", 834, 1086, 976, 1218),
    # Steve Holland
    "sh_hero": ("sh", 8, 120, 295, 858), "sh_q34l": ("sh", 465, 148, 603, 466), "sh_q34r": ("sh", 776, 148, 918, 466),
    # the rest of the squad, seated behind the dressing-room table
    "bs_hero": ("bs", 8, 100, 284, 833), "yt_hero": ("yt", 10, 115, 282, 828), "ls_hero": ("ls", 8, 120, 282, 822),
    "sl_hero": ("sl", 5, 112, 284, 857),
}

# open mouths painted shut so the lip sync can drive them: (cx, cy, rx, ry) of the open mouth (1x sheet px);
# the gap is inpainted with the surrounding skin and a closed mouth line drawn across its upper third
CLOSE = {}
# paper enclosed by the drawing (e.g. between arm and body, or the legs and the sheet's floor shadow) to clear:
# seed points (1x sheet px)
HOLES = {"ck_front": [(123.9, 469.0)], "ck_walk": [(880.0, 1345.0)], "ck_q34r": [(770.0, 480.0)]}
INK = (22, 28, 45)          # BGR of the sheets' dark brown line work


def close_mouth(im, a, ox, oy, cx, cy, rx, ry):
    """paint an open mouth shut on a 4x part (BGR image, alpha)"""
    X, Y = (cx - ox) * 4, (cy - oy) * 4
    RX, RY = rx * 4 * 1.22, ry * 4 * 1.35
    m = np.zeros(im.shape[:2], np.uint8)
    cv2.ellipse(m, (int(X), int(Y)), (int(RX), int(RY)), 0, 0, 360, 255, -1)
    im[:] = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA)
    # a soft, slightly downturned closed-mouth line across the upper part of the old opening
    w = rx * 4 * 0.78
    yl = Y - ry * 4 * 0.25
    pts = np.array([[X - w, yl + 0.10 * w], [X - 0.45 * w, yl - 0.02 * w], [X, yl - 0.05 * w],
                    [X + 0.45 * w, yl - 0.02 * w], [X + w, yl + 0.10 * w]], np.float32)
    k = 8
    lay = np.zeros(im.shape[:2], np.float32)
    cv2.polylines(lay, [np.int32(np.round(pts * k))], False, 1.0, max(4, int(round(1.6 * 4))), cv2.LINE_AA, 3)
    lay = cv2.GaussianBlur(lay, (0, 0), 0.7)[..., None]
    im[:] = (im * (1 - lay) + np.float32(INK) * lay).astype(np.uint8)


def extend_down(im, a, frac):
    """continue the body below the cell edge: the torso's lowest wide row (arms and stray bits excluded) is held at
    its full width and repeated downwards, so the figure reaches out of the frame as a solid body"""
    H, W = a.shape
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.int16)
    # arms / hands are not torso: skin is orange-brown (hue 6-25) at any lightness, so dark skin counts too;
    # the red shirts sit at hue 0-5 / 170-180
    skin = (hsv[..., 0] >= 6) & (hsv[..., 0] <= 25) & (hsv[..., 1] > 60) & (hsv[..., 2] > 40)
    op = (a > 0.5) & ~skin
    op = cv2.morphologyEx(op.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, 9), np.uint8)) > 0
    rows = np.where(op.sum(1) > 0.05 * W)[0]
    if len(rows) == 0: return im, a
    r = rows.max()
    def main_run(y):
        v = op[y].astype(np.int8)
        d = np.diff(np.concatenate([[0], v, [0]]))
        st, en = np.where(d == 1)[0], np.where(d == -1)[0]
        if len(st) == 0: return None
        k = int(np.argmax(en - st)); return st[k], en[k]
    run = main_run(r)
    if run is None: return im, a
    # the body tapers into the cell's last rows: use the widest main run in the bottom 8 % instead
    best = (run[1] - run[0], r, run)
    for y in range(r, max(0, int(r - 0.08 * H)), -2):
        rr = main_run(y)
        if rr and rr[1] - rr[0] > best[0]: best = (rr[1] - rr[0], y, rr)
    _, ry, (x0, x1) = best
    inset = 3
    x0, x1 = x0 + inset, x1 - inset
    n = int(frac * H)
    band = im[ry - 2:ry + 1, x0:x1].astype(np.float32).mean(0)
    # a collar or zip line crossing the last row is not continued down the body: pixels much darker than the
    # cloth take the cloth's colour (a black tracksuit is dark all over, so nothing changes there)
    lum = band.mean(1)
    cloth = np.median(band[lum >= np.median(lum) * 0.6], 0)
    band[lum < np.median(lum) * 0.45] = cloth
    ext = np.zeros((n, W, 3), np.uint8); ext[:, x0:x1] = band.astype(np.uint8)
    ea = np.zeros((n, W), np.float32); ea[:, x0:x1] = 1.0
    # the ink outline down both sides
    ext[:, x0:x0 + 4] = INK; ext[:, x1 - 4:x1] = INK
    # rows between ry and the old bottom: fill the body run so there is no notch where it tapered
    im = im.copy(); a = a.copy()
    fill = (slice(ry, r + 1), slice(x0, x1))
    holes = a[fill] < 0.5
    blk = im[fill]; blk[holes] = band.astype(np.uint8)[None].repeat(r + 1 - ry, 0)[holes]
    im[fill] = blk
    a[fill] = np.maximum(a[fill], 1.0)
    im[ry:r + 1, x0:x0 + 4][holes[:, :4]] = INK
    im2 = np.concatenate([im[:r + 1], ext], 0)
    a2 = np.concatenate([a[:r + 1], ea], 0)
    return im2, a2


def cut(name, spec):
    sh, x0, y0, x1, y1 = spec[:5]
    big = SHEETS[sh]
    X0, Y0, X1, Y1 = x0 * 4, y0 * 4, x1 * 4, y1 * 4
    im = big[Y0:Y1, X0:X1].copy()
    h, w = im.shape[:2]
    ff = cv2.GaussianBlur(im, (3, 3), 0)
    mask = np.zeros((h + 2, w + 2), np.uint8)
    flags = 4 | cv2.FLOODFILL_MASK_ONLY | (255 << 8)
    # seeds: every light pixel on the box border
    border = np.concatenate([np.stack([np.arange(w), np.zeros(w, int)], 1), np.stack([np.arange(w), np.full(w, h - 1)], 1),
                             np.stack([np.zeros(h, int), np.arange(h)], 1), np.stack([np.full(h, w - 1), np.arange(h)], 1)])
    g = cv2.cvtColor(ff, cv2.COLOR_BGR2GRAY)
    for x, y in border[::7]:
        if g[y, x] > 200 and mask[y + 1, x + 1] == 0:
            cv2.floodFill(ff, mask, (int(x), int(y)), 0, (3, 3, 3), (3, 3, 3), flags)
    paper = mask[1:-1, 1:-1] > 0
    fig = (~paper).astype(np.uint8)
    fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fig, 8)
    cx0, cy0, cx1, cy1 = int(0.3 * w), int(0.15 * h), int(0.7 * w), int(0.85 * h)
    core = set(np.unique(lab[cy0:cy1, cx0:cx1])) - {0}
    keep = np.isin(lab, [k for k in core if st[k, cv2.CC_STAT_AREA] > 0.002 * w * h])
    # fill enclosed holes (paper-coloured regions fully inside the figure are part of it)
    keep8 = keep.astype(np.uint8)
    inv = 1 - keep8
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv, 4)
    for k in range(1, n2):
        xx, yy, ww, hh, a = st2[k]
        if xx > 0 and yy > 0 and xx + ww < w and yy + hh < h and a < 0.02 * w * h:
            keep8[lab2 == k] = 1
    # soft edge: the outline's anti-aliasing is kept, then a 1 px feather
    keep8 = cv2.erode(keep8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))   # 2 px inside the outline
    a = cv2.GaussianBlur(keep8.astype(np.float32), (0, 0), 0.9)
    a = np.clip((a - 0.25) / 0.5, 0, 1)
    for hx, hy in HOLES.get(name, []):
        # start from the nearest paper-coloured pixel, so a seed that lands on the drawing never floods it
        sx, sy = int((hx - x0) * 4), int((hy - y0) * 4)
        r = 60
        win = g[max(0, sy - r):sy + r, max(0, sx - r):sx + r]
        ys_, xs_ = np.nonzero(win > 222)
        if len(ys_) == 0: continue
        k = int(np.argmin((ys_ + max(0, sy - r) - sy) ** 2 + (xs_ + max(0, sx - r) - sx) ** 2))
        sx, sy = int(xs_[k] + max(0, sx - r)), int(ys_[k] + max(0, sy - r))
        hole = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(ff, hole, (sx, sy), 0, (6, 6, 6), (6, 6, 6), flags)
        hm = (cv2.dilate(hole[1:-1, 1:-1], np.ones((3, 3), np.uint8)) > 0) & (g > 150)   # light pixels only
        a[hm] = 0
    if name in CLOSE:
        close_mouth(im, a, x0, y0, *CLOSE[name])
    if name in EXTEND:
        im, a = extend_down(im, a, EXTEND[name])
        h, w = a.shape
    ys, xs = np.where(a > 0.02)
    bx0, by0, bx1, by1 = max(0, xs.min() - 8), max(0, ys.min() - 8), min(w, xs.max() + 9), min(h, ys.max() + 9)
    rgba = np.dstack([im, (a * 255).astype(np.uint8)])[by0:by1, bx0:bx1]
    cv2.imwrite(f"build/parts/{name}.png", rgba)
    return dict(sheet=sh, box=[x0, y0, x1, y1], off=[x0 + int(bx0) / 4, y0 + int(by0) / 4], size=[int(bx1 - bx0), int(by1 - by0)])


# waist-up gesture drawings stop at the sheet's cell edge: the torso is continued downwards (last rows repeated)
# so the body always runs out of the frame instead of ending in mid-air
EXTEND = {"br_g_shrug": 0.5, "br_g_talk": 0.5, "br_g_celebrate": 0.5, "ck_g_explain": 0.4, "ck_g_talk": 0.4,
          "ck_g_crossed": 0.4, "ck_g_point": 0.4, "mn_g_crossed": 0.5, "mg_g_talk": 0.5, "mg_confused": 0.35}
# drawings seen large on screen get a second 4x AI upscale (then halved): 8 part px per sheet px
X8 = ["ck_front", "ck_g_explain", "ck_g_point", "br_g_shrug", "br_g_talk", "br_g_celebrate", "mn_g_crossed",
      "mg_hand", "mg_confused", "mg_g_talk"]


def second_pass(name):
    """4x part -> 8x: Real-ESRGAN on the colour (over a neutral grey, so the edge isn't pulled towards white),
    the alpha resized; the 16x result is halved to 8x"""
    import upscale
    p = cv2.imread(f"build/parts/{name}.png", cv2.IMREAD_UNCHANGED)
    a = p[..., 3:4].astype(np.float32) / 255
    rgb = (p[..., :3].astype(np.float32) * a + 128 * (1 - a)).astype(np.uint8)
    big = upscale.upscale(rgb[..., ::-1].copy(), "RealESRGAN_x4plus_anime_6B")[..., ::-1]
    h, w = p.shape[0] * 2, p.shape[1] * 2
    big = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA)
    al = cv2.resize(p[..., 3], (w, h), interpolation=cv2.INTER_CUBIC)
    al = np.clip((al.astype(np.float32) - 128) * 1.6 + 128, 0, 255).astype(np.uint8)     # keep the edge crisp
    cv2.imwrite(f"build/parts/{name}.png", np.dstack([big, al]))


def check(names, out):
    tiles = []
    for n in names:
        p = cv2.imread(f"build/parts/{n}.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
        mag = np.zeros_like(p[..., :3]); mag[:] = (1, 0, 1)
        c = p[..., :3] * p[..., 3:4] + mag * (1 - p[..., 3:4])
        s = 600 / p.shape[0]
        tiles.append(cv2.resize((c * 255).astype(np.uint8), None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
    cv2.imwrite(out, np.hstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    os.makedirs("build/parts", exist_ok=True)
    only = sys.argv[1:]
    meta = json.load(open("build/parts/meta.json")) if os.path.exists("build/parts/meta.json") else {}
    SHEETS = {}
    done = []
    for name, spec in P.items():
        if only and not any(name.startswith(o) for o in only): continue
        if not only and name in meta and os.path.exists(f"build/parts/{name}.png"): continue
        if spec[0] not in SHEETS:
            if not os.path.exists(S[spec[0]]): print("no 4x sheet yet:", S[spec[0]]); continue
            SHEETS[spec[0]] = cv2.imread(S[spec[0]])
        meta[name] = cut(name, spec)
        if name in X8:
            second_pass(name)
            meta[name]["scale"] = 8
            meta[name]["size"] = [meta[name]["size"][0] * 2, meta[name]["size"][1] * 2]
        print(name, meta[name]["size"], flush=True)
        done.append(name)
        json.dump(meta, open("build/parts/meta.json", "w"), indent=1)
    for c in S:
        ns = [n for n in P if n.startswith(c + "_") and n in meta and os.path.exists(f"build/parts/{n}.png")]
        if ns and any(n in done for n in ns): check(ns, f"build/parts/check_{c}.jpg")
