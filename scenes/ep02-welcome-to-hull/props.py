"""Derived art for Episode 2, built from the upscaled sheets and sets (run after upscale_all.sh and parts.py):

  build/x4/door-store-cupboard.png  the wrong door. The door is the one in the dressing-room panel of the stadium
                                    strip (images/backgrounds/hull-stadium-strip.png); its "TO THE PITCH" lettering
                                    is painted out and it becomes the store cupboard Carrick marches up to; plain wall is added on its right.
  build/parts/mg_arm.png            Harry Maguire's open palm (his sheet's hand drawing) turned fingers-up, its forearm
                                    continued straight down, so it can rise into his close-up from below the frame.
                                    meta.json "mg_arm": wrist = the wristband centre (part px), scale = part px per
                                    sheet px."""
import json, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

INK = (22, 28, 45)


def door():
    strip = cv2.imread("build/x4/hull-stadium-strip.png")
    x0, y0, x1, y1 = 0, 370, 130, 700                       # 1x strip px: the door, its frame and a strip of wall
    im = strip[y0 * 4:y1 * 4, x0 * 4:x1 * 4].copy()
    P = lambda x, y: (int(round((x - x0) * 4)), int(round((y - y0) * 4)))
    # paint out "TO / THE / PITCH ->": the light lettering on the dark door, inpainted from the door around it
    (ax, ay), (bx, by) = P(30, 420), P(82, 532)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = np.zeros(im.shape[:2], np.uint8)
    m[ay:by, ax:bx] = (hsv[ay:by, ax:bx, 2] > 70).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((13, 13), np.uint8))
    # the door is a smooth painted panel: each row of the lettering is bridged by a straight blend between the
    # clean door on either side (inpainting leaves dark smudges on a surface this even)
    f = im.astype(np.float32)
    for y in range(ay, by):
        row = m[y] > 0
        if not row.any(): continue
        xs = np.nonzero(row)[0]
        l_, r_ = max(0, xs.min() - 3), min(im.shape[1] - 1, xs.max() + 3)
        cl = f[max(0, y - 2):y + 3, max(0, l_ - 6):l_].reshape(-1, 3).mean(0)
        cr = f[max(0, y - 2):y + 3, r_:r_ + 6].reshape(-1, 3).mean(0)
        u = np.linspace(0, 1, r_ - l_ + 1)[:, None]
        f[y, l_:r_ + 1] = cl * (1 - u) + cr * u
    im = cv2.GaussianBlur(f, (0, 0), 1.0) * (m[..., None] > 0) + f * (m[..., None] == 0)
    im = np.clip(im, 0, 255).astype(np.uint8)
    # the door's own grain back over the patch (inpainting leaves it too smooth)
    rng = np.random.default_rng(5)
    g = cv2.GaussianBlur(rng.standard_normal(im.shape[:2]).astype(np.float32), (0, 0), 1.2)
    sm = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 6)[..., None]
    im = np.clip(im.astype(np.float32) + g[..., None] * 3.0 * sm, 0, 255).astype(np.uint8)
    # new lettering in the same style: pale condensed capitals, straight on the door
    pil = Image.fromarray(im[..., ::-1])
    dr = ImageDraw.Draw(pil)
    col = (224, 214, 196)
    for text, y, size in (("STORE", 440, 66), ("CUPBOARD", 464, 66)):
        f = ImageFont.truetype("fonts/BebasNeue-Regular.ttf", size)
        track = 6
        widths = [dr.textlength(ch, font=f) for ch in text]
        tw = sum(widths) + track * (len(text) - 1)
        x = P(46, 0)[0] - tw / 2                            # left of centre: Carrick stops at its right edge
        for ch, w in zip(text, widths):
            dr.text((x, P(0, y)[1]), ch, font=f, fill=col)
            x += w + track
    out = np.asarray(pil)[..., ::-1].copy()
    # soften the new letters to the door's painted look
    lay = cv2.GaussianBlur(out.astype(np.float32), (0, 0), 0.8)
    box = (slice(P(0, 432)[1], P(0, 492)[1]), slice(P(6, 0)[0], P(80, 0)[0]))
    out = out.astype(np.float32); out[box] = lay[box]
    # the panel's lockers start just right of the door: a stretch of plain wall (and floor) replaces them, so the
    # door can be framed with Carrick beside it; the wall is the dark paint above the door, the floor its own rows
    pad = 80 * 4
    wall = np.median(out[P(0, 371)[1]:P(0, 378)[1], P(12, 0)[0]:P(100, 0)[0]].reshape(-1, 3), 0)
    fy = P(0, 657)[1]                                       # the floor line under the door
    left = np.zeros((out.shape[0], pad, 3), np.float32)
    yy = np.arange(out.shape[0], dtype=np.float32)[:, None]
    left[:] = wall * (1.0 + 0.10 * (yy / out.shape[0] - 0.5))[..., None]
    floor = out[fy:, P(20, 0)[0]:P(100, 0)[0]].mean(1)       # each floor row's own colour
    left[fy:] = floor[:, None, :]
    left[fy - 18:fy + 2] = wall * 0.55                      # the skirting
    left += cv2.GaussianBlur(rng.standard_normal(left.shape[:2]).astype(np.float32), (0, 0), 1.5)[..., None] * 2.5
    xx = np.linspace(1.0, 0.9, pad)[None, :, None]          # a touch darker away from the door
    left *= xx
    out = np.concatenate([out, left], 1)
    cv2.imwrite("build/x4/door-store-cupboard.png", np.clip(out, 0, 255).astype(np.uint8))


def arm():
    meta = json.load(open("build/parts/meta.json"))
    m = meta["mg_hand"]
    K = m.get("scale", 4)
    p = cv2.imread("build/parts/mg_hand.png", cv2.IMREAD_UNCHANGED)
    H, W = p.shape[:2]
    # the forearm runs down-left from the wristband: wrist centre -> stub centre (part px, measured on the 8x part)
    wx, wy = 205.0, 645.0
    sx, sy = 112.0, 780.0
    ang = math.degrees(math.atan2(sx - wx, sy - wy))       # the forearm's lean from straight down
    # turn the hand about the wrist so the forearm points straight down (fingers up), on a canvas with room below
    pad = 3 * max(H, W)
    big = np.zeros((H + pad, W + pad, 4), np.uint8)
    ox, oy = pad // 2, pad // 4
    big[oy:oy + H, ox:ox + W] = p
    R = cv2.getRotationMatrix2D((wx + ox, wy + oy), -ang, 1.0)
    rot = cv2.warpAffine(big, R, (big.shape[1], big.shape[0]), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
    wxr, wyr = wx + ox, wy + oy
    a = rot[..., 3].astype(np.float32) / 255
    # the forearm's full cross-section: the lowest row below the wristband that still spans the arm's width
    rows = [y for y in range(int(wyr + 60), rot.shape[0]) if (a[y] > 0.5).sum() > 0]
    best, by = 0, None
    for y in rows:
        xs = np.nonzero(a[y] > 0.5)[0]
        run = xs.max() - xs.min() if len(xs) else 0
        if run >= best * 0.97 and abs((xs.min() + xs.max()) / 2 - wxr) < 60:
            best, by = max(best, run), y
        elif by is not None and run < best * 0.8:
            break
    xs = np.nonzero(a[by] > 0.5)[0]
    l, r = xs.min(), xs.max()
    # continue the forearm straight down from that row: its skin tone between two ink edges, 2.5 hand heights long
    n = int(2.5 * H)
    band = rot[by - 3:by, l:r + 1].astype(np.float32).mean(0)
    skin = np.median(band[(band[:, 2] > 120)], 0)
    body = np.zeros((n, r - l + 1, 4), np.float32)
    body[:] = skin
    ew = max(8, int(0.07 * (r - l)))
    body[:, :ew] = INK + (255,); body[:, -ew:] = INK + (255,)
    # a soft shadow side, like the sheet's shading
    sh = np.linspace(0, 1, r - l + 1)[None, :, None]
    body[..., :3] = body[..., :3] * (1 - 0.12 * np.clip((sh - 0.6) / 0.4, 0, 1))
    body[..., 3] = 255
    out = rot.copy()
    out[by:, :] = 0
    out = np.concatenate([out[:by], np.zeros((n, out.shape[1], 4), np.uint8)], 0)
    out[by:by + n, l:r + 1] = body.astype(np.uint8)
    # crop to the drawing
    ys, xs2 = np.nonzero(out[..., 3] > 5)
    cx0, cy0, cx1, cy1 = xs2.min() - 6, ys.min() - 6, xs2.max() + 7, ys.max() + 7
    out = out[cy0:cy1, cx0:cx1]
    cv2.imwrite("build/parts/mg_arm.png", out)
    meta["mg_arm"] = dict(sheet="mg", wrist=[float(wxr - cx0), float(wyr - cy0)], scale=K, size=[out.shape[1], out.shape[0]],
                          palm=float(0.62 * W))
    json.dump(meta, open("build/parts/meta.json", "w"), indent=1)
    c = out.astype(np.float32) / 255
    c = c[..., :3] * c[..., 3:4] + np.float32([1, 0, 1]) * (1 - c[..., 3:4])
    cv2.imwrite("build/parts/check_arm.jpg", cv2.resize((c * 255).astype(np.uint8), None, fx=0.35, fy=0.35))


if __name__ == "__main__":
    door()
    arm()
    print("props done")
