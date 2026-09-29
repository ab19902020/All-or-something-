"""Cut every drawing the episode uses out of the 4x-upscaled character sheets (build/x4/).

Each part is a box on the 1x sheet. The matte is a flood fill of the paper from the box border on the 4x image
(floating range, so the panels' soft gradients fill but the ink outline stops it); inside the outline everything
is kept, so white eyes, collars and shoes stay solid. Only the components that reach the box's core are kept
(neighbouring drawings and labels are dropped).

Output: build/parts/<name>.png (RGBA, 4x) and build/parts/meta.json {name: {sheet, box, off:[x, y], size:[w, h]}}:
a sheet coordinate (x, y) maps to part pixel ((x - off_x) * 4, (y - off_y) * 4). Check build/parts/check_*.jpg."""
import json, os, sys, numpy as np, cv2

S = {c: f"build/x4/{n}.png" for c, n in dict(ck="michael-carrick", js="jason-wilcox", om="omar-berrada",
                                           br="bruno-fernandes", jr="jim-ratcliffe").items()}
# name: (sheet, box x0, y0, x1, y1 in 1x sheet px[, core box to keep components from])
P = {
    # Michael Carrick (no hero drawing: the front turnaround is his main body)
    "ck_front": ("ck", 30, 112, 228, 522), "ck_q34l": ("ck", 258, 112, 450, 522), "ck_q34r": ("ck", 686, 112, 866, 522),
    "ck_g_explain": ("ck", 120, 1195, 282, 1352), "ck_g_talk": ("ck", 528, 1195, 672, 1352),
    "ck_g_crossed": ("ck", 28, 1195, 124, 1352),
    # Jason Wilcox
    "js_hero": ("js", 22, 98, 302, 752), "js_q34l": ("js", 478, 132, 604, 470), "js_q34r": ("js", 776, 132, 912, 470),
    "js_g_explain": ("js", 283, 1208, 437, 1372), "js_g_point": ("js", 128, 1208, 287, 1372),
    "js_back": ("js", 942, 132, 1092, 470), "js_hand3": ("js", 1040, 1046, 1106, 1137),
    "js_g_three": ("js", 283, 1208, 437, 1372),          # explaining pose, right hand swapped for three fingers
    # Omar Berrada
    "om_hero": ("om", 18, 106, 322, 850), "om_q34l": ("om", 506, 138, 628, 472), "om_q34r": ("om", 796, 138, 924, 472),
    "om_g_explain": ("om", 133, 1203, 307, 1382), "om_back": ("om", 946, 138, 1094, 472),
    # Bruno Fernandes
    "br_hero": ("br", 12, 108, 292, 818), "br_q34l": ("br", 462, 142, 594, 462), "br_q34r": ("br", 776, 142, 914, 462),
    "br_g_shrug": ("br", 973, 1088, 1104, 1218), "br_g_talk": ("br", 838, 1088, 977, 1218),
    # Jim Ratcliffe
    "jr_hero": ("jr", 12, 106, 302, 790), "jr_q34l": ("jr", 492, 150, 618, 488), "jr_q34r": ("jr", 792, 150, 918, 488),
}

# open mouths painted shut so the lip sync can drive them: (cx, cy, rx, ry) of the open mouth (1x sheet px);
# the gap is inpainted with the surrounding skin and a closed mouth line drawn across its upper third
CLOSE = {"js_g_explain": (364.5, 1290.5, 10.5, 6.2), "js_g_three": (364.5, 1290.5, 10.5, 6.2), "js_g_point": (223.0, 1291.0, 11.5, 6.6),
         "om_g_explain": (224.0, 1278.5, 8.6, 3.2)}
# paper enclosed by the drawing (e.g. between arm and body) to clear: seed points (1x sheet px)
HOLES = {"jr_hero": [(142.0, 704.2)], "js_hero": [(154.7, 664.9)], "ck_front": [(123.9, 469.0)],
         "jr_q34l": [(554.1, 443.9)]}       # the gap between the legs (closed off by the sheet's floor shadow)
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
    lay = np.zeros((im.shape[0] * 1, im.shape[1] * 1), np.float32)
    cv2.polylines(lay, [np.int32(np.round(pts * k))], False, 1.0, max(4, int(round(1.6 * 4))) * 1, cv2.LINE_AA, 3)
    lay = cv2.GaussianBlur(lay, (0, 0), 0.7)[..., None]
    im[:] = (im * (1 - lay) + np.float32(INK) * lay).astype(np.uint8)


def three_fingers(im, a, ox, oy):
    """Jason's open 'palm out' hand -> three fingers up (thumb, index, middle): the ring and little fingers are
    folded away above the knuckles and the knuckle edge is inked"""
    P = lambda x, y: ((x - ox) * 4, (y - oy) * 4)
    gone = np.float32([P(1080.6, 1040), P(1106, 1040), P(1106, 1083.6), P(1099.4, 1084.8), P(1089, 1082.8), P(1080.6, 1084.4)])
    m = np.zeros(a.shape, np.uint8)
    cv2.fillPoly(m, [np.int32(np.round(gone))], 1)
    a[m > 0] = 0
    # the folded knuckles: skin under an inked arc from the middle finger's base to the palm's edge
    arc = []
    for u in np.linspace(0, 1, 24):
        x = (1 - u) ** 2 * 1080.6 + 2 * (1 - u) * u * 1090.2 + u ** 2 * 1098.0
        y = (1 - u) ** 2 * 1084.4 + 2 * (1 - u) * u * 1077.6 + u ** 2 * 1086.2
        arc.append(P(x, y))
    arc = np.float32(arc)
    skin = np.median(im[int(P(0, 1092)[1]):int(P(0, 1098)[1]), int(P(1072, 0)[0]):int(P(1088, 0)[0])].reshape(-1, 3), 0)
    fill = np.concatenate([arc[:-2], np.float32([P(1096.6, 1085.6), P(1096.6, 1086.4), P(1080.6, 1086.0)])])
    fm = np.zeros(a.shape, np.uint8)
    cv2.fillPoly(fm, [np.int32(np.round(fill))], 1)
    im[fm > 0] = skin.astype(np.uint8)
    a[fm > 0] = 1.0
    lay = np.zeros(a.shape, np.float32)
    cv2.polylines(lay, [np.int32(np.round(arc * 8))], False, 1.0, 7, cv2.LINE_AA, 3)
    lay = cv2.GaussianBlur(lay, (0, 0), 0.7)
    im[:] = (im * (1 - lay[..., None]) + np.float32(INK) * lay[..., None]).astype(np.uint8)
    a[:] = np.maximum(a, lay)


# Jason Wilcox restyle. His sheet reads as Mark Goldbridge (the same swept-up brown hair, scowl and hoodie), so he
# gets the look from his Clear Plan sheet: short silver hair trimmed to a neat dome, grey stubble, a navy club
# tracksuit and a less angry brow. All in sheet px: dome = (cx, cy, a, b) of the new skull outline; stubble =
# (centre x, upper lip y, y at the jaw sides, half width, chin y); body = y below which dark cloth turns navy;
# creases = boxes whose dark lines are painted out; brows = (inner end x, y, radius, lift) warps
JASON = {
    "js_hero": dict(dome=(157, 236, 88, 119), stubble=(154, 284, 270, 64, 338), body=330,
                    creases=[(144.5, 206, 150.5, 219.5), (154.5, 206, 160.5, 219.5)],
                    brows=[(146.5, 222, 20, 3.0), (159.5, 222, 20, 3.0)]),
    "js_g_point": dict(dome=(229, 1266, 37.5, 45), stubble=(227, 1285, 1279, 30, 1306), body=1303,
                       creases=[], brows=[(219, 1263, 9, 1.6), (226.5, 1263, 9, 1.6)]),
    "js_back": dict(dome=(1020, 216, 46.5, 68), stubble=None, body=238, creases=[], brows=[], hair_to=250),
    "js_g_three": dict(dome=(358, 1268, 36, 49), stubble=(364, 1284.5, 1279, 26, 1306), body=1302,
                       creases=[], brows=[(359, 1264, 9, 1.6), (367, 1262, 9, 1.6)]),
    "js_hand3": dict(dome=None, stubble=None, body=1110, creases=[], brows=[]),
}
NAVY = (1.55, 0.85, 0.62)          # BGR gain on the cloth's own brightness -> navy


def restyle_jason(name, im, a, x0, y0):
    J = JASON[name]
    H, W = a.shape
    P = lambda x, y: ((x - x0) * 4.0, (y - y0) * 4.0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = im.astype(np.float32)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    S, V = hsv[..., 1].astype(np.float32), hsv[..., 2].astype(np.float32)
    b_, g_, r_ = f[..., 0], f[..., 1], f[..., 2]
    skin = (r_ > g_ + 15) & (g_ > b_ + 10) & (S > 105) & (V > 165)        # light-brown hair stays out of it
    # 1. navy tracksuit: dark neutral cloth below the collar
    by = P(0, J["body"])[1]
    dark = (a > 0.05) & (S < 70) & (V < 125) & (yy > by)
    lum = f.mean(2)
    f[dark] = np.clip(np.stack([lum * NAVY[0], lum * NAVY[1], lum * NAVY[2]], -1)[dark], 0, 255)
    # 2. the scowl: crease lines painted out, inner brow ends lifted
    for bx0, by0, bx1, by1 in J["creases"]:
        (X0, Y0), (X1, Y1) = P(bx0, by0), P(bx1, by1)
        m = np.zeros((H, W), np.uint8)
        box = (slice(int(Y0), int(Y1)), slice(int(X0), int(X1)))
        m[box] = (V[box] < 150).astype(np.uint8)
        m = cv2.dilate(m, np.ones((3, 3), np.uint8))
        f = cv2.inpaint(np.clip(f, 0, 255).astype(np.uint8), m, 5, cv2.INPAINT_TELEA).astype(np.float32)
    if J["brows"]:
        mx, my = xx.copy(), yy.copy()
        for bx, byy, r, lift in J["brows"]:
            X, Y = P(bx, byy)
            R = r * 4
            w = np.clip(1 - ((xx - X) / R) ** 2 - ((yy - Y) / (R * 0.45)) ** 2, 0, 1) ** 1.5
            my = my + lift * 4 * w
        f = cv2.remap(f, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # 3. hair: silver, trimmed to a neat dome
    if J["dome"]:
        cx, cy, ax, bx = J["dome"]
        CX, CY = P(cx, cy); AX, BX = ax * 4, bx * 4
        hy = P(0, J["hair_to"])[1] if "hair_to" in J else CY + 0.15 * BX
        hairc = (a > 0.3) & (S < 118) & (V > 55) & (V < 205) & ~skin & (yy < hy)
        # the strand lines split the hair into pieces: join them, keep the blob that reaches the top of the head
        # (not the brows), then take back the hair-coloured pixels inside it
        joined = cv2.morphologyEx(hairc.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(joined, 8)
        keep = [k for k in range(1, n) if st[k, cv2.CC_STAT_TOP] < CY - 0.72 * BX and st[k, cv2.CC_STAT_AREA] > 2000]
        blob = cv2.dilate(np.isin(lab, keep).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        hair = blob & ~skin & (a > 0.3) & (V > 45) & (S < 160) & (yy < hy + 12)
        v = V[hair]
        sil = 98 + np.clip((v - 60) / 150, 0, 1) * 132
        f[hair] = np.stack([sil * 1.03, sil * 0.99, sil * 0.95], -1)
        # fit the dome's width to the head itself where the trim starts, so its outline joins the head's sides
        yt = int(CY - 0.18 * BX)
        if 0 <= yt < H:
            row = a[yt] > 0.5
            c0 = int(np.clip(CX, 0, W - 1))
            if row[c0]:
                l_ = c0
                while l_ > 0 and row[l_ - 1]: l_ -= 1
                r_ = c0
                while r_ < W - 1 and row[r_ + 1]: r_ += 1
                if r_ - l_ > 0.6 * AX:
                    CX, AX = (l_ + r_) / 2, (r_ - l_) / 2 / np.sqrt(1 - 0.18 ** 2)
        e = ((xx - CX) / AX) ** 2 + ((yy - CY) / BX) ** 2
        top = yy < CY - 0.18 * BX
        band = np.abs(xx - CX) < 1.14 * AX                 # the head's own columns (not a raised hand beside it)
        a[(e > 1.0) & top & band] = 0
        # gaps between the old tufts that are now inside the dome become hair
        fill = (e <= 1.0) & top & band & (a < 0.6) & ~skin
        f[fill] = np.median(f[hair], 0) if hair.any() else f[fill]
        a[fill] = 1.0
        # the new outline along the dome
        ts = np.linspace(np.pi * 1.02, np.pi * 1.98, 400)
        px, py = CX + AX * np.cos(ts), CY + BX * np.sin(ts)
        # only where the dome actually borders the hair (just inside it), never floating beside the head
        nx, ny = np.cos(ts) / AX, np.sin(ts) / BX
        nl = np.sqrt(nx ** 2 + ny ** 2); nx, ny = nx / nl, ny / nl
        qx, qy = px - nx * 14, py - ny * 14
        on = [(0 <= int(x) < W and 0 <= int(y) < H and y < CY - 0.12 * BX and 0 <= int(u_) < W and 0 <= int(v_) < H
               and a[int(v_), int(u_)] > 0.5) for x, y, u_, v_ in zip(px, py, qx, qy)]
        ink = np.zeros((H, W), np.float32)
        run = []
        for ok, x, y in zip(on + [False], list(px) + [0], list(py) + [0]):
            if ok: run.append((x, y)); continue
            if len(run) > 3:
                cv2.polylines(ink, [np.int32(np.round(np.float32(run) * 8))], False, 1.0, 11, cv2.LINE_AA, 3)
            run = []
        ink = cv2.GaussianBlur(ink, (0, 0), 0.8)
        f = f * (1 - ink[..., None]) + np.float32(INK) * ink[..., None]
        a[:] = np.maximum(a, ink)
    # 4. grey stubble on the jaw, chin and upper lip
    if J["stubble"]:
        scx, ylip, yside, hw, ychin = J["stubble"]
        SCX, YL = P(scx, ylip); YS = P(0, yside)[1]; HW = hw * 4; YC = P(0, ychin)[1]
        u = (xx - SCX) / HW
        ytop = YL - (YL - YS) * np.clip(u * u, 0, 1)
        sk = skin & (a > 0.5)
        m = np.clip((yy - ytop) / 20, 0, 1) * np.clip((1.12 - np.abs(u)) / 0.2, 0, 1) * (yy < YC + 10)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5) * sk
        rng = np.random.default_rng(3)
        dots = cv2.GaussianBlur((rng.random((H, W)) > 0.8).astype(np.float32), (0, 0), 0.8)
        dots = np.clip((dots - 0.16) * 3, 0, 1)
        t = (m * 0.30)[..., None]
        f = f * (1 - t) + np.float32([150, 150, 158]) * t
        dd = (dots * m * 0.28)[..., None]
        f = f * (1 - dd) + np.float32([96, 98, 106]) * dd
    im[:] = np.clip(f, 0, 255).astype(np.uint8)


def three_finger_arm(im, a, x0, y0):
    """js_g_three: paint out the palm-up right hand of the explaining pose and put the three-finger hand (js_hand3)
    on that wrist, fingers up and tilted out, its cuff tucked into the sleeve"""
    P = lambda x, y: ((x - x0) * 4.0, (y - y0) * 4.0)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # the old hand: everything left of the hoodie's edge between the thumb tip and the top of the sleeve
    X1 = P(316.5, 0)[0]
    Ya, Yb = P(0, 1302)[1], P(0, 1343.5)[1]
    a[(xx < X1) & (yy > Ya) & (yy < Yb)] = 0
    m = json.load(open("build/parts/meta.json"))["js_hand3"]
    hp = cv2.imread("build/parts/js_hand3.png", cv2.IMREAD_UNCHANGED).astype(np.float32)
    K = m.get("scale", 4); hox, hoy = m["off"]
    s_, ang = 0.6, np.radians(12)                       # hand size relative to the pose, tilt (fingers lean out)
    ax, ay = 1068.0, 1131.0                             # the hand's cuff, bottom centre (hand-set sheet px)
    tx, ty = 309.0, 1351.0                              # ... placed on the pose's wrist (pose sheet px)
    c, sn = np.cos(ang), np.sin(ang)
    R = np.float64([[c, sn], [-sn, c]]) * s_            # counter-clockwise on screen: the fingertips lean left
    # hand part px -> hand sheet -> pose sheet -> pose crop px
    A = np.zeros((2, 3))
    A[:, :2] = 4 * R / K
    A[:, 2] = 4 * (R @ (np.float64([hox, hoy]) - [ax, ay]) + [tx, ty] - [x0, y0])
    w = cv2.warpAffine(hp, A, (W, H), flags=cv2.INTER_AREA, borderValue=0)
    ha = w[..., 3] / 255.0
    im[:] = np.clip(im * (1 - ha[..., None]) + w[..., :3] * ha[..., None], 0, 255).astype(np.uint8)
    a[:] = np.maximum(a, ha)


def extend_down(im, a, frac):
    """continue the body below the cell edge: the torso's lowest wide row (arms and stray bits excluded) is held at
    its full width and repeated downwards, so the figure reaches behind the table as a solid body"""
    H, W = a.shape
    f = im.astype(np.int16)
    skin = (f[..., 2] > f[..., 1] + 15) & (f[..., 1] > f[..., 0] + 10) & (f[..., 2] > 170) & \
           ((f[..., 1] - f[..., 0]) > 25)                       # arms / hands are not torso
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
    # nothing outside the body run continues below the cell edge (drops stray columns)
    return im2, a2


def cut(name, spec):
    sh, x0, y0, x1, y1 = spec[:5]
    big = SHEETS[sh]
    X0, Y0, X1, Y1 = x0 * 4, y0 * 4, x1 * 4, y1 * 4
    im = big[Y0:Y1, X0:X1].copy()
    h, w = im.shape[:2]
    ff = cv2.GaussianBlur(im, (3, 3), 0)
    mask = np.zeros((h + 2, w + 2), np.uint8)
    flags = 4 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE * 0 | (255 << 8)
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
    if name == "js_hand3":
        three_fingers(im, a, x0, y0)
    if name in JASON:
        restyle_jason(name, im, a, x0, y0)
    if name == "js_g_three":
        three_finger_arm(im, a, x0, y0)
    if name in EXTEND:
        im, a = extend_down(im, a, EXTEND[name])
        h, w = a.shape
    ys, xs = np.where(a > 0.02)
    bx0, by0, bx1, by1 = max(0, xs.min() - 8), max(0, ys.min() - 8), min(w, xs.max() + 9), min(h, ys.max() + 9)
    rgba = np.dstack([im, (a * 255).astype(np.uint8)])[by0:by1, bx0:bx1]
    cv2.imwrite(f"build/parts/{name}.png", rgba)
    return dict(sheet=sh, box=[x0, y0, x1, y1], off=[x0 + int(bx0) / 4, y0 + int(by0) / 4], size=[int(bx1 - bx0), int(by1 - by0)])


# drawings seen large on screen get a second 4x AI upscale (then halved): 8 part px per sheet px
# waist-up gesture drawings stop at the sheet's cell edge: the torso is continued downwards (last rows repeated)
# so the body always reaches behind the table instead of ending in mid-air
EXTEND = {"br_g_shrug": 0.5, "br_g_talk": 0.5, "om_g_explain": 0.35, "js_g_point": 0.4, "js_g_three": 0.4,
          "js_g_explain": 0.4, "ck_g_explain": 0.4, "ck_g_talk": 0.4, "ck_g_crossed": 0.4}
X8 = ["js_g_three", "ck_front", "ck_g_explain", "js_g_point", "om_g_explain", "br_g_shrug", "br_g_talk", "js_hand3"]


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
    for name, spec in P.items():
        if only and not any(name.startswith(o) for o in only): continue
        if spec[0] not in SHEETS:
            if not os.path.exists(S[spec[0]]): print("no 4x sheet yet:", S[spec[0]]); continue
            SHEETS[spec[0]] = cv2.imread(S[spec[0]])
        meta[name] = cut(name, spec)
        if name in X8:
            second_pass(name)
            meta[name]["scale"] = 8
            meta[name]["size"] = [meta[name]["size"][0] * 2, meta[name]["size"][1] * 2]
        print(name, meta[name]["size"])
    json.dump(meta, open("build/parts/meta.json", "w"), indent=1)
    for c in S:
        ns = [n for n in P if n.startswith(c + "_") and n in meta and os.path.exists(f"build/parts/{n}.png")]
        if ns and (not only or any(n.startswith(o) for o in only for n in ns)): check(ns, f"build/parts/check_{c}.jpg")
