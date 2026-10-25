"""The shot list for Leeds, Como and the plan, keyed to the dialogue edit (timeline.py). Every character is the same
drawing as in the rest of the episode (Martínez in the kit The Mole films him in, Wilcox in his black tracksuit).

Leeds: the result, then a silent office cutaway (documentary/ceo-office). Martínez, Wilcox and Berrada stand behind the
desk watching the screen where the camera is (from screen left: Martínez, Wilcox, Berrada); the desk's top and front
hide where the drawings end. Inserts carry the hands (the tiny clap, the dust, the blue mug).

Como: the away dressing room is the opening's room with its reds taken out (plate "CW": neutral, cold), a standing
whiteboard painted in by the board (COMPACT; after half-time PRESS / TOGETHER: plate "CW2"). Where everyone stands:
Carrick by the board on the left; Martínez front left; Maguire front right; Bruno right; Mainoo and Zirkzee at the
back. Carrick's singles have the board corner behind him (documentary/locker-room, neutralised: "CD"); the players'
the neutral shirts. The touchline singles have Como's stand behind (stadiums/red-seated turned blue: "CS").

The interview: the paraphrase cards sit over a still mixed zone (Bruno) and an empty press room (Carrick's reply); the
parody lines carry the PARODY DIALOGUE label. The corridor: they leave from opposite ends; the board rolls through.
The clear plan: the boardroom at night (club/boardroom, darkened: "BN"), Wilcox alone behind the table."""
import json

from studio.film import ep
from studio.film.cast import CAST
from studio.film.shots import Marks, finish, group, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"AW": "aos/stadium-exterior", "OF": "documentary/ceo-office", "W": "aos/locker-room-wide",
          "CW": "aos/locker-room-wide", "CW2": "aos/locker-room-wide", "CD": "documentary/locker-room",
          "TN": "aos/tunnel", "CS": "stadiums/red-seated", "MZ": "aos/mixed-zone",
          "PR": "tv-and-media/press-conference-room", "CO": "documentary/corridor", "BN": "club/boardroom"}

# the office desk (1x plate px): its top and front, and what stands on it
DESK = [(268, 486), (1416, 498), (1416, 592), (1292, 600), (1292, 795), (348, 795), (348, 600), (268, 566)]
ON_DESK = [[(476, 424), (676, 424), (676, 498), (476, 498)], [(1028, 428), (1178, 428), (1178, 518), (1028, 518)],
           [(962, 452), (1024, 452), (1024, 528), (962, 528)], [(1178, 452), (1318, 452), (1318, 528), (1178, 528)],
           [(396, 466), (472, 466), (472, 498), (396, 498)]]
# the boardroom table (from The Handover)
TABLE = [(598, 440), (1068, 440), (1500, 735), (1500, 780), (85, 780), (85, 712)]
OCCL = {"OF": {"desk": [DESK] + ON_DESK}, "BN": {"table": [TABLE]}}

HOR, EYE_H = 402.0, 0.84                         # the dressing room (as in part A)


def px_per_m(y):
    return (y - HOR) / EYE_H


HEIGHT = dict(carrick=1.76, bruno=1.79, maguire=1.94, licho=1.75, mainoo=1.80, zirkzee=1.93, wilcox=1.78,
              omar=1.80, cunha=1.84)
SEAT = dict(carrick=(600, 590), bruno=(1150, 612), maguire=(1000, 668), licho=(760, 668), mainoo=(880, 548),
            zirkzee=(1060, 548), board=(420, 560))
DRAW = {"carrick": "michael-carrick:track", "bruno": "bruno-fernandes:front", "maguire": "harry-maguire:front",
        "licho": "lisandro-martinez:stand", "mainoo": "kobbie-mainoo:front", "zirkzee": "joshua-zirkzee:squad",
        "wilcox": "jason-wilcox:pockets", "omar": "omar-berrada:front", "cunha": "matheus-cunha:front"}
C_EXPLAIN, C_ARMS, C_BACK = "michael-carrick:track_explain", "michael-carrick:arms", "michael-carrick:track_back"
LI_POINT, LI_CROSS, WI_CROSS = "lisandro-martinez:point", "lisandro-martinez:crossarms", "jason-wilcox:crossarms"
ALSO = [C_BACK]


def ensure_stand(key):
    cid, name = key.split(":")
    sp = CAST.spec(cid)["drawings"][name]
    if not sp.get("stand_h"):
        import numpy as np
        d, info = CAST.get(key)
        a = d.u8[1.0][..., 3] > 128
        ys = np.nonzero(a.any(1))[0]
        sp["stand_h"] = float((ys.max() - ys.min()) / d.S)
    return sp["stand_h"]


def actor(who, draw=None, at=None, mirror=False, h=None):
    draw = draw or DRAW[who]
    x, y = at or SEAT[who]
    ensure_stand(draw)
    return (who, draw, (x, y), 0.0, mirror, {"stand": h or HEIGHT.get(who, 1.8) * px_per_m(y)})


def _eyes():
    out = {}
    for a, (xa, ya) in SEAT.items():
        out[a] = {}
        for b, (xb, yb) in SEAT.items():
            if a == b:
                continue
            lx = max(-0.9, min(0.9, (xb - xa) / 330.0))
            out[a][b] = (lx, 0.05 + (0.06 if yb < ya - 20 else 0.0), lx * 0.32)
    out["carrick"]["board"] = (-0.85, 0.0, -0.3)
    out["bruno"]["board"] = (-0.9, -0.05, -0.3)
    # the office: the three of them, side by side behind the desk (Martínez, Wilcox, Berrada)
    out.setdefault("licho", {}).update(wilcox=(0.8, 0.02, 0.28), omar=(0.9, 0.02, 0.3))
    out.setdefault("wilcox", {}).update(licho=(-0.85, 0.02, -0.3), omar=(0.85, 0.02, 0.3))
    out.setdefault("omar", {}).update(licho=(-0.9, 0.02, -0.3), wilcox=(-0.8, 0.02, -0.28))
    for w in ("bruno", "carrick", "zirkzee"):
        out.setdefault(w, {})["bench"] = (-0.75, 0.12, -0.25) if w != "carrick" else (0.6, 0.1, 0.2)
        out[w]["producer"] = (0.15, 0.02, 0.05)
        out[w]["reporter"] = (-0.32, 0.03, -0.1)
    return out


EYES = _eyes()
EYES_FIRST = False

C_CAM = (820, 440, 1.5)                          # the Como dressing room's wide


def room(t, who, plate="CW", extra=None, cam=None, push=1.025, drift=0.4, **kw):
    acts = [actor(w) for w in who] + list(extra or [])
    acts.sort(key=lambda a: a[2][1])
    c0 = cam or C_CAM
    return world(t, plate, c0, (c0[0], c0[1], c0[2] * push), layers=[("actors", acts)], drift=drift, grade="room", **kw)


SET = {
    "carrick": dict(bg=("CD", 360, 300, 2.3, 2.6), eye=(830, 432)),
    "bruno": dict(bg=("CW", 1210, 330, 2.7, 2.6), eye=(1060, 432)),
    "maguire": dict(bg=("CW", 1100, 330, 2.7, 2.6), eye=(1000, 432)),
    "licho": dict(bg=("CW", 600, 300, 2.7, 2.6), eye=(880, 432)),
    "zirkzee": dict(bg=("CS", 900, 300, 2.2, 3.0), eye=(900, 440)),
    "ck_touch": dict(bg=("CS", 700, 330, 2.0, 3.2), eye=(980, 440)),
    "br_pitch": dict(bg=("CS", 1100, 300, 2.2, 3.0), eye=(880, 440)),
    "wilcox": dict(bg=("OF", 900, 280, 2.6, 3.0), eye=(960, 432)),
    "licho_of": dict(bg=("OF", 600, 300, 2.6, 3.0), eye=(900, 432)),
    "omar": dict(bg=("OF", 1250, 260, 2.6, 3.0), eye=(1000, 432)),
    "br_mz": dict(bg=("MZ", 1000, 330, 2.0, 3.4), eye=(1060, 438)),
    "ck_pr": dict(bg=("PR", 836, 300, 1.9, 3.2), eye=(900, 438)),
}


def close(t, who, key=None, ed=112.0, draw=None, push=(1.0, 1.035), drift=0.6, eye=None, grade="room", **kw):
    st = SET[key or who]
    return single(t, who, draw or DRAW[who], st["bg"], None, ed=ed, eye=eye or st["eye"], push=push, drift=drift,
                  grade=grade, **kw)


def ground(t, plate, cam0, cam1, grade="studio"):
    return world(t, plate, cam0, cam1, layers=[], drift=0.25, grade=grade)


# the office: three behind the desk, watching the screen at the camera
OFFICE = [("licho", LI_CROSS, (600, 640), 0.0, False, {"stand": 395}),
          ("wilcox", DRAW["wilcox"], (905, 640), 0.0, False, {"stand": 400}),
          ("omar", DRAW["omar"], (1215, 640), 0.0, False, {"stand": 405})]
for a in OFFICE:
    ensure_stand(a[1])

# everyone for the door (the pen's click), then back: (who, drawing, from, to, t0, t1)
GO = [("licho", DRAW["licho"], SEAT["licho"], (690, 640)), ("maguire", DRAW["maguire"], SEAT["maguire"], (900, 642)),
      ("bruno", DRAW["bruno"], SEAT["bruno"], (1040, 598)), ("mainoo", DRAW["mainoo"], SEAT["mainoo"], (800, 540)),
      ("zirkzee", DRAW["zirkzee"], SEAT["zirkzee"], (975, 540))]
for a in GO:
    ensure_stand(a[1])
ensure_stand(C_BACK)

SHOTS = finish([
    # ---- Leeds; the office
    insert(0.0, "card_leeds"),
    world(m("cut_office"), "OF", (880, 400, 1.55), (880, 395, 1.62), layers=[("actors", OFFICE), ("occl", "desk")],
          drift=0.35, grade="studio", blur=2.2),
    insert(m("cut_clap"), "clap"),
    close(m("cut_wi_sees"), "wilcox", ed=114, grade="studio"),
    close(m("cut_brush"), "wilcox", ed=104, push=(1.0, 1.0), drift=0.2, grade="studio"),
    close(m("cut_li_eyes"), "licho", key="licho_of", draw=LI_POINT, ed=108, grade="studio"),
    close(m("cut_omar"), "omar", ed=112, grade="studio"),
    insert(m("cut_bluemug"), "bluemug"),
    # ---- Como: the lake, the ground, the board; the briefing
    insert(m("cut_lake"), "lake"),
    ground(wt("C04", "stadium") - 0.08, "CS", (836, 430, 1.05), (836, 410, 1.2)),
    insert(wt("C04", "plan") - 0.08, "board_compact", grade="insert"),
    close(m("cut_c05"), "carrick", ed=110),
    close(m("cut_c06"), "bruno", ed=112),
    close(m("cut_c07"), "carrick", ed=114, push=(1.0, 1.0)),
    close(m("cut_c08m"), "maguire", ed=112),
    insert(m("cut_click"), "pen_click", grade="insert"),
    world(m("cut_go"), "CW", C_CAM, (C_CAM[0], C_CAM[1], C_CAM[2] * 1.01),
          layers=[("actors", [actor("carrick")]), ("props", "movers")], drift=0.4, grade="room"),
    close(m("cut_c09"), "carrick", ed=118, push=(1.0, 1.02), drift=0.3),
    world(m("cut_hold"), "CW", C_CAM, (C_CAM[0], C_CAM[1], C_CAM[2] * 1.015),
          layers=[("actors", [actor("carrick")]), ("props", "movers")], drift=0.3, grade="room"),
    # ---- the early goal
    insert(m("cut_g1"), "card_g1"),
    close(m("cut_touch"), "carrick", key="ck_touch", ed=104, push=(1.0, 1.05), drift=0.3, grade="studio"),
    # ---- half-time
    insert(m("cut_board_ht"), "board_ht", grade="insert"),
    close(m("cut_c13"), "bruno", ed=112),
    close(m("cut_c14"), "carrick", draw=C_EXPLAIN, ed=108),
    close(m("cut_c15"), "bruno", ed=120, push=(1.0, 1.0)),
    close(m("cut_c16"), "carrick", ed=116),
    insert(m("cut_cap"), "cap", grade="insert"),
    # ---- the collapse
    insert(m("cut_g2"), "card_g2"),
    insert(wt("C17", "on") - 0.08, "tactic", grade="insert"),
    insert(m("cut_g3"), "card_g3"),
    close(m("cut_ck_board"), "carrick", ed=112, push=(1.0, 1.0)),
    close(m("cut_br_ck"), "bruno", key="br_pitch", ed=114, push=(1.0, 1.0), grade="studio"),
    insert(m("cut_g4"), "card_g4"),
    single(wt("C19", "the") - 0.08, "carrick", DRAW["carrick"], SET["ck_touch"]["bg"], None, ed=58, eye=(1150, 420),
           push=(1.0, 1.55), drift=0.2, grade="studio"),
    # ---- the consolation
    insert(m("cut_g5"), "card_g5"),
    close(wt("C21", "joshua") - 0.08, "zirkzee", ed=110, push=(1.0, 1.0), drift=0.4, grade="studio"),
    insert(wt("C21", "the", 1) - 0.08, "card_ft"),
    # ---- the button
    room(m("cut_btn"), ["bruno"], plate="CW2", extra=[actor("carrick", at=(520, 560))], cam=(820, 430, 1.55),
         push=1.02),
    close(m("cut_c22"), "carrick", ed=112),
    close(m("cut_c23"), "bruno", ed=114),
    close(m("cut_sees"), "carrick", ed=122, push=(1.0, 1.0), drift=0.2, tilt_down=(m("cut_sees") + 0.7, 0.45)),
    # ---- the interviews
    close(m("cut_par1"), "bruno", key="br_mz", ed=104, push=(1.0, 1.03), drift=0.15, grade="studio",
          props=["mic"]),
    close(m("cut_b05"), "bruno", key="br_mz", ed=118, push=(1.0, 1.04), grade="studio", props=["mic"]),
    world(m("cut_par2"), "PR", (836, 470, 1.05), (836, 466, 1.1), layers=[], drift=0.15),
    close(m("cut_c08"), "carrick", key="ck_pr", ed=112, push=(1.0, 1.03), grade="studio", props=["mics"]),
    insert(m("cut_magnets"), "board_arrows", grade="insert"),
    close(m("cut_c09r"), "carrick", key="ck_pr", ed=122, push=(1.0, 1.06), drift=0.25, grade="studio",
          props=["mics"]),
    world(m("cut_corr"), "CO", (900, 470, 1.12), (900, 468, 1.16), layers=[("props", "corridor")], drift=0.25),
    # ---- the clear plan
    single(m("cut_bd"), "wilcox", "jason-wilcox:clipboard", ("BN", 470, 282, 3.2, 0.0),
           ("BN", "table", 833 - (1060 - 960) / (1920 / 1672 * 3.4), 440, 3.4, 0.0), ed=106, eye=(1060, 440),
           table=3.9, push=(1.0, 1.04), drift=0.3, grade="studio"),
    insert(m("cut_laptop"), "laptop"),
    insert(m("cut_mugdark"), "mug_dark"),
    insert(m("cut_credits"), "credits"),
], TL["total"])

CAPTIONS = [
    (m("cut_office") + 0.3, m("whistle") + 0.3, "place", "CARRINGTON", "Meanwhile. A fictionalised viewing party."),
    (m("cut_omar") + 0.1, m("cut_bluemug") - 0.1, "name_r", "OMAR BERRADA", "Chief Executive. Formerly of City."),
    (m("cut_lake") + 0.3, wt("C04", "stadium") - 0.15, "place", "COMO", "Europe  |  21 October 2026"),
    (m("cut_c05") + 0.2, m("cut_c06") - 0.1, "place", "AWAY DRESSING ROOM", "Como. Before kick-off."),
    (m("cut_touch") + 0.2, ls("C11") + 1.6, "name", "MICHAEL CARRICK", "Head Coach. Clicking."),
    (wt("C21", "joshua"), wt("C21", "the", 1) - 0.15, "name", "JOSHUA ZIRKZEE", "Scorer. 90+1'."),
    (m("cut_bd") + 0.2, m("cut_laptop") - 0.1, "place", "THE BOARDROOM", "Late."),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
