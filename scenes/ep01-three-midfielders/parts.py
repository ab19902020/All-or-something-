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
CLOSE = {"js_g_explain": (364.5, 1290.5, 10.5, 6.2), "js_g_point": (223.0, 1291.0, 11.5, 6.6),
         "om_g_explain": (224.0, 1278.5, 8.6, 3.2)}
# paper enclosed by the drawing (e.g. between arm and body) to clear: seed points (1x sheet px)
HOLES = {}
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
        hole = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(ff, hole, (int((hx - x0) * 4), int((hy - y0) * 4)), 0, (4, 4, 4), (4, 4, 4), flags)
        hm = cv2.dilate(hole[1:-1, 1:-1], np.ones((3, 3), np.uint8)) > 0
        a[hm] = 0
    if name in CLOSE:
        close_mouth(im, a, x0, y0, *CLOSE[name])
    if name == "js_hand3":
        three_fingers(im, a, x0, y0)
    ys, xs = np.where(a > 0.02)
    bx0, by0, bx1, by1 = max(0, xs.min() - 8), max(0, ys.min() - 8), min(w, xs.max() + 9), min(h, ys.max() + 9)
    rgba = np.dstack([im, (a * 255).astype(np.uint8)])[by0:by1, bx0:bx1]
    cv2.imwrite(f"build/parts/{name}.png", rgba)
    return dict(sheet=sh, box=[x0, y0, x1, y1], off=[x0 + int(bx0) / 4, y0 + int(by0) / 4], size=[int(bx1 - bx0), int(by1 - by0)])


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
        print(name, meta[name]["size"])
    json.dump(meta, open("build/parts/meta.json", "w"), indent=1)
    for c in S:
        ns = [n for n in P if n.startswith(c + "_") and n in meta and os.path.exists(f"build/parts/{n}.png")]
        if ns and (not only or any(n.startswith(o) for o in only for n in ns)): check(ns, f"build/parts/check_{c}.jpg")
