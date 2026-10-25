"""The shot list for Bournemouth, keyed to the dialogue edit (timeline.py). The home dressing room is the one every
match in this episode uses (aos/locker-room-wide), everyone where they stand after every result (see the month's
direction); the team sheet is an insert; the match is four cards, Cunha on the touchline at half-time and Carrick on
it at full time (stadiums/red-seated behind them). The row: the room's wide, then a single for every line, pushing in
a little harder each time; "Don't!" is the room's wide again; the last shot is Carrick, mouth still open.

Every character is the same drawing as in the rest of the episode: Carrick in his black tracksuit, Bruno in the full
kit, Martínez in his home kit (the drawings The Mole uses)."""
import json

from studio.film import ep
from studio.film.cast import CAST
from studio.film.shots import Marks, finish, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"W": "aos/locker-room-wide", "D": "documentary/locker-room", "AW": "aos/stadium-exterior",
          "OF": "documentary/ceo-office", "CQ": "training-ground/carrington-quiet", "HS": "stadiums/red-seated"}
OCCL = {}

HOR = 402.0                      # the room's horizon, plate px
EYE_H = 0.84                     # the camera's height (m)


def px_per_m(y):
    return (y - HOR) / EYE_H


HEIGHT = dict(carrick=1.76, bruno=1.79, maguire=1.94, cunha=1.84, sesko=1.95, licho=1.75, mount=1.81,
              mainoo=1.80, wilcox=1.78)
SEAT = dict(carrick=(820, 592), bruno=(1165, 612), maguire=(540, 612), cunha=(1035, 548), mainoo=(640, 548),
            sesko=(420, 598), licho=(960, 645), mount=(1245, 600), wilcox=(478, 515), lacey=(1300, 560))
DRAW = {"carrick": "michael-carrick:track", "bruno": "bruno-fernandes:full", "maguire": "harry-maguire:front",
        "cunha": "matheus-cunha:front", "sesko": "benjamin-sesko:front", "licho": "lisandro-martinez:stand",
        "mount": "mason-mount:squad", "mainoo": "kobbie-mainoo:front", "wilcox": "jason-wilcox:clipboard"}
C_EXPLAIN, C_ARMS = "michael-carrick:track_explain", "michael-carrick:arms"
B_CLAP, CU_POINT, LI_POINT, SE_ARMS = ("bruno-fernandes:full", "matheus-cunha:points", "lisandro-martinez:point",
                                      "benjamin-sesko:arms-folded")
LI_CROSS, LI_SHRUG = "lisandro-martinez:crossarms", "lisandro-martinez:shrug"
ALSO = []


def ensure_stand(key):
    """film.yaml's stand_h (head top to soles, sheet px) for a drawing that has none: read off the drawing"""
    cid, name = key.split(":")
    sp = CAST.spec(cid)["drawings"][name]
    if not sp.get("stand_h"):
        d, info = CAST.get(key)
        a = d.u8[1.0][..., 3] > 128
        import numpy as np
        ys = np.nonzero(a.any(1))[0]
        sp["stand_h"] = float((ys.max() - ys.min()) / d.S)
    return sp["stand_h"]


def actor(who, draw=None, at=None, mirror=False):
    draw = draw or DRAW[who]
    x, y = at or SEAT[who]
    ensure_stand(draw)
    return (who, draw, (x, y), 0.0, mirror, {"stand": HEIGHT.get(who, 1.8) * px_per_m(y)})


def _eyes():
    out = {}
    for a, (xa, ya) in SEAT.items():
        out[a] = {}
        for b, (xb, yb) in SEAT.items():
            if a == b:
                continue
            lx = max(-0.9, min(0.9, (xb - xa) / 330.0))
            ly = 0.05 + (0.06 if yb < ya - 20 else 0.0)
            out[a][b] = (lx, ly, lx * 0.32)
        out[a]["producer"] = (0.18 if xa < 900 else -0.18, 0.02, 0.06 if xa < 900 else -0.06)
        out[a]["board"] = (-0.75, -0.05, -0.25)
        out[a]["pitch"] = (-0.55, -0.02, -0.2)
    return out


EYES = _eyes()

W_CAM = (836, 438, 1.45)                    # the dressing room's documentary wide: always the same
ROOM = ["mainoo", "cunha", "maguire", "carrick", "bruno"]


def wide(t, who, extra=None, cam=None, push=1.025, drift=0.45, **kw):
    acts = [actor(w) for w in who] + list(extra or [])
    acts.sort(key=lambda a: a[2][1])
    c0 = cam or W_CAM
    return world(t, "W", c0, (c0[0], c0[1], c0[2] * push), layers=[("actors", acts)], drift=drift, grade="room",
                 **kw)


SET = {
    "cu_pitch": dict(bg=("HS", 860, 300, 2.2, 3.0), eye=(900, 440)),
    "ck_touch": dict(bg=("HS", 700, 330, 2.0, 3.2), eye=(980, 440)),
    "carrick": dict(bg=("D", 360, 300, 2.3, 2.6), eye=(830, 432)),
    "bruno": dict(bg=("W", 1210, 330, 2.7, 2.6), eye=(1060, 432)),
    "maguire": dict(bg=("W", 470, 330, 2.7, 2.6), eye=(860, 432)),
    "cunha": dict(bg=("W", 1330, 300, 2.7, 2.6), eye=(1040, 432)),
    "sesko": dict(bg=("W", 300, 300, 2.7, 2.6), eye=(880, 432)),
    "licho": dict(bg=("W", 700, 300, 2.7, 2.6), eye=(880, 432)),
    "mount": dict(bg=("W", 1260, 320, 2.7, 2.6), eye=(1040, 432)),
    "wilcox": dict(bg=("W", 480, 330, 2.5, 2.8), eye=(900, 432)),
    "br_pitch": dict(bg=("HS", 1100, 300, 2.2, 3.0), eye=(880, 440)),
}


def close(t, who, key=None, ed=112.0, draw=None, push=(1.0, 1.035), drift=0.6, eye=None, grade="room", **kw):
    st = SET[key or who]
    return single(t, who, draw or DRAW[who], st["bg"], None, ed=ed, eye=eye or st["eye"], push=push, drift=drift,
                  grade=grade, **kw)


ROW = ["mainoo", "cunha", "maguire", "carrick", "bruno", "sesko", "licho", "mount"]
LI_SCREAM = "lisandro-martinez:scream"

SHOTS = finish([
    # ---- Old Trafford; the team sheet
    world(0.0, "AW", (836, 420, 1.0), (836, 400, 1.12), layers=[], drift=0.3, grade="studio"),
    insert(wt("B01", "one") - 0.08, "team_sheet"),
    close(m("cut_b02"), "bruno", ed=112),
    close(m("cut_b03"), "carrick", ed=112, push=(1.0, 1.0)),
    close(m("cut_b04"), "bruno", ed=118, push=(1.0, 1.03)),
    close(m("cut_b05"), "carrick", draw=C_ARMS, ed=116, push=(1.0, 1.04), drift=0.3),
    close(m("cut_look"), "bruno", ed=124, push=(1.0, 1.06), drift=0.2),
    # ---- the match
    insert(m("cut_g1"), "card_bg1"),
    insert(m("cut_g2"), "card_bg2"),
    close(m("cut_ht"), "cunha", key="cu_pitch", ed=108, push=(1.0, 1.04), drift=0.4, grade="studio"),
    insert(m("cut_g3"), "card_bg3"),
    close(m("cut_ft"), "carrick", key="ck_touch", ed=104, push=(1.0, 1.06), drift=0.3, grade="studio"),
    insert(wt("B10", "then") - 0.08, "card_bft"),
    # ---- the row
    wide(m("cut_room"), ROW, push=1.02, drift=0.6),
    close(m("cut_b12"), "licho", ed=112, push=(1.0, 1.03)),
    close(m("cut_b13"), "cunha", ed=110, push=(1.0, 1.04)),
    close(m("cut_b14"), "sesko", ed=112, push=(1.0, 1.03)),
    close(m("cut_b15"), "mount", ed=114, push=(1.0, 1.04)),
    close(m("cut_b16"), "maguire", ed=116, push=(1.0, 1.05)),
    close(m("cut_b17"), "bruno", ed=114, push=(1.0, 1.03)),
    close(m("cut_b18"), "licho", draw=LI_POINT, ed=110, push=(1.0, 1.06)),
    close(m("cut_b19"), "cunha", ed=116, push=(1.0, 1.04)),
    close(m("cut_b20"), "bruno", ed=120, push=(1.0, 1.05)),
    close(m("cut_b21"), "maguire", ed=120, push=(1.0, 1.05)),
    close(m("cut_b22"), "carrick", draw=C_EXPLAIN, ed=108, push=(1.0, 1.03)),
    wide(m("cut_quiet"), ROW, push=1.01, drift=0.2),
    close(m("cut_b23"), "carrick", ed=114, push=(1.0, 1.04), drift=0.3),
    close(m("cut_b24"), "carrick", ed=126, push=(1.0, 1.06), drift=0.2),
    wide(m("cut_b25"), ROW, push=1.0, drift=0.2),
    close(m("cut_end"), "carrick", ed=126, push=(1.0, 1.0), drift=0.15),
], TL["total"])

CAPTIONS = [
    (0.3, wt("B01", "one") - 0.15, "place", "OLD TRAFFORD", "Premier League  |  25 October 2026"),
    (m("cut_b02") + 0.1, le("B02") + 0.2, "name_r", "BRUNO FERNANDES", "Captain. Substitute."),
    (m("cut_ht") + 0.2, le("B08") + 0.2, "name", "MATHEUS CUNHA", "On at half-time. As requested."),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
