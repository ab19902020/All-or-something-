"""Face landmarks for every talking drawing, found on the 4x part and stored in sheet (1x) coordinates.

eyes  = (cx, cy, rx, ry) of each eye opening (the white of the eye, pupil included)
mouth = (left corner x, y, right corner x, y, centre x, y) of the closed mouth line
chin  = y of the chin outline under the mouth; neck = the head's pivot (collar centre); head = head box
Found automatically from the drawing (white eye blobs; the dark mouth line under them; the chin outline), with
per-drawing overrides in OVR where the detector can't see it (a beard hides the mouth line).
Output: build/facemarks.json; check build/parts/marks_<char>.jpg (landmarks drawn over each head)."""
import json, sys, numpy as np, cv2

META = json.load(open("build/parts/meta.json"))
# approximate head box (1x sheet px) of each drawing that talks / blinks
HEAD = {
    "mg_front": (45, 110, 130, 218),
    "ck_front": (68, 118, 196, 245), "ck_q34l": (290, 118, 420, 245), "ck_q34r": (712, 118, 842, 245),
    "ck_g_explain": (160, 1198, 238, 1272), "ck_g_crossed": (38, 1198, 110, 1272),
    "js_hero": (50, 100, 262, 350), "js_q34l": (492, 138, 590, 250), "js_q34r": (792, 138, 900, 250),
    "js_g_explain": (318, 1212, 402, 1296), "js_g_point": (186, 1212, 270, 1296),
    "om_hero": (40, 115, 295, 370), "om_q34l": (515, 145, 615, 255), "om_q34r": (808, 145, 912, 255),
    "om_g_explain": (170, 1206, 262, 1290),
    "br_hero": (55, 112, 255, 365), "br_q34l": (478, 148, 575, 260), "br_q34r": (792, 148, 898, 260),
    "br_g_shrug": (996, 1090, 1066, 1160), "br_g_talk": (866, 1090, 940, 1160),
    "jr_hero": (35, 110, 275, 365), "jr_q34l": (500, 155, 612, 272), "jr_q34r": (800, 155, 912, 272),
}
OVR = {}


def detect(name):
    m = META[name]
    img = cv2.imread(f"build/parts/{name}.png", cv2.IMREAD_UNCHANGED)
    ox, oy = m["off"]
    K = m.get("scale", 4)
    def P(x, y): return (int(round((x - ox) * K)), int(round((y - oy) * K)))
    def S(px, py): return (px / K + ox, py / K + oy)
    hx0, hy0, hx1, hy1 = HEAD[name]
    (X0, Y0), (X1, Y1) = P(hx0, hy0), P(hx1, hy1)
    HB = Y1 - Y0                                   # head box height; the search area reaches below it for the chin
    Y1 = Y1 + int(0.35 * HB)
    X0, Y0 = max(0, X0), max(0, Y0); X1, Y1 = min(img.shape[1], X1), min(img.shape[0], Y1)
    sub = img[Y0:Y1, X0:X1]
    bgr, a = sub[..., :3], sub[..., 3]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    V, Sat = hsv[..., 2].astype(int), hsv[..., 1].astype(int)
    white = ((V > 200) & (Sat < 45) & (a > 200)).astype(np.uint8)
    white = cv2.morphologyEx(white, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(white, 8)
    H, W = white.shape
    cand = []
    for k in range(1, n):
        x, y, w, h, ar = st[k]
        if ar < 0.002 * HB * W or ar > 0.08 * HB * W: continue
        if y + h > 0.8 * HB or w > 0.45 * W: continue
        if not (0.4 < w / max(h, 1) < 2.6): continue
        # a real eye has a dark pupil inside its box
        box = bgr[y:y + h, x:x + w]
        if (box.max(2) < 90).mean() < 0.03: continue
        cand.append((ar, x, y, w, h))
    cand.sort(reverse=True)
    eyes = []
    for ar, x, y, w, h in cand[:4]:
        if all(abs((y + h / 2) - (e[1] + e[3] / 2)) < 0.12 * HB for e in eyes) or not eyes:
            eyes.append((x, y, w, h))
        if len(eyes) == 2: break
    eyes.sort()
    E = [((x + w / 2), (y + h / 2), w / 2, h / 2) for x, y, w, h in eyes]
    res = dict(eyes=[], head=list(HEAD[name]))
    for cx, cy, rx, ry in E:
        sx, sy = S(cx + X0, cy + Y0)
        res["eyes"].append([round(sx, 1), round(sy, 1), round(rx / K, 2), round(ry / K, 2)])
    if len(E) >= 1:
        ecy = np.mean([e[1] for e in E])
        ecx = np.mean([e[0] for e in E])
        ed = (E[1][0] - E[0][0]) if len(E) == 2 else 3 * E[0][2]
        er = np.mean([e[3] for e in E])
        # mouth: the dark, wide, thin stroke below the eyes
        ya, yb = int(ecy + er + 0.55 * ed), int(min(H, ecy + 1.5 * ed))
        xa, xb = int(max(0, ecx - 0.9 * ed)), int(min(W, ecx + 0.9 * ed))
        dark = ((V < 105) & (a > 200)).astype(np.uint8)
        reg = np.zeros_like(dark); reg[ya:yb, xa:xb] = dark[ya:yb, xa:xb]
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(reg, 8)
        best = None
        for k in range(1, n2):
            x, y, w, h, ar = st2[k]
            if w < 0.18 * ed or w > 1.3 * ed or h > 0.6 * w: continue
            touches = x <= xa or x + w >= xb
            score = w - 2 * abs((x + w / 2) - ecx) - (50 if touches else 0)
            if best is None or score > best[0]: best = (score, k, x, y, w, h)
        if best:
            _, k, x, y, w, h = best
            ys, xs = np.where(lab2 == k)
            l, r = xs.min(), xs.max()
            yl = ys[xs <= l + 2].mean(); yr = ys[xs >= r - 2].mean()
            mc = (l + r) / 2; yc = ys[np.abs(xs - mc) <= 2].mean()
            L, R, C = S(l + X0, yl + Y0), S(r + X0, yr + Y0), S(mc + X0, yc + Y0)
            res["mouth"] = [round(L[0], 1), round(L[1], 1), round(R[0], 1), round(R[1], 1), round(C[0], 1), round(C[1], 1)]
            # chin: first ink row below the mouth in the centre column (after some skin)
            col = V[:, int(mc)]
            yy = int(yc + max(4, 0.12 * ed))
            while yy < H - 1 and not (col[yy] < 90 and yy > yc + 0.25 * ed): yy += 1
            res["chin"] = round(S(0, yy + Y0)[1], 1)
            res["neck"] = [round(C[0], 1), round(res["chin"] + 0.28 * (res["chin"] - S(0, ecy + Y0)[1]), 1)]
    res.update(OVR.get(name, {}))
    return res


def draw(name, r, out):
    m = META[name]
    img = cv2.imread(f"build/parts/{name}.png", cv2.IMREAD_UNCHANGED)
    ox, oy = m["off"]
    K = m.get("scale", 4)
    def P(x, y): return (int(round((x - ox) * K)), int(round((y - oy) * K)))
    hx0, hy0, hx1, hy1 = r["head"]
    (X0, Y0), (X1, Y1) = P(hx0, hy0), P(hx1, hy1)
    Y1 += int(0.35 * (Y1 - Y0))
    X0, Y0 = max(0, X0), max(0, Y0)
    c = img[..., :3].copy()
    for cx, cy, rx, ry in r["eyes"]:
        cv2.ellipse(c, P(cx, cy), (int(rx * K), int(ry * K)), 0, 0, 360, (0, 255, 0), 2)
    if "mouth" in r:
        mo = r["mouth"]
        for i in range(3): cv2.circle(c, P(mo[2 * i], mo[2 * i + 1]), 5, (0, 0, 255), -1)
    if "chin" in r:
        x = r["mouth"][4] if "mouth" in r else (hx0 + hx1) / 2
        cv2.line(c, P(x - 10, r["chin"]), P(x + 10, r["chin"]), (255, 0, 0), 2)
    if "neck" in r: cv2.circle(c, P(*r["neck"]), 6, (255, 128, 0), -1)
    crop = c[Y0:Y1, X0:X1]
    s = 360 / crop.shape[0]
    return cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)


if __name__ == "__main__":
    only = sys.argv[1:]
    try: out = json.load(open("build/facemarks.json"))
    except FileNotFoundError: out = {}
    tiles = {}
    for n in HEAD:
        if n not in META or (only and not any(n.startswith(o) for o in only)): continue
        out[n] = detect(n)
        out[n] = json.loads(json.dumps(out[n], default=float))
        print(n, out[n])
        tiles.setdefault(n[:2], []).append(draw(n, out[n], None))
    json.dump(out, open("build/facemarks.json", "w"), indent=1)
    for c, t in tiles.items():
        cv2.imwrite(f"build/parts/marks_{c}.jpg", np.hstack(t), [cv2.IMWRITE_JPEG_QUALITY, 90])
