"""The shot list for Hull and the month, keyed to the dialogue edit (timeline.py).

The dressing room is the one every match in this episode uses (aos/locker-room-wide, the symmetrical room with the
door at the back left). Where everyone stands (feet in plate px): Carrick in the middle by the carpet's far edge;
Bruno front right; Maguire front left; Cunha and Mainoo back right / back left; Šeško far left; Martínez left of
Carrick, a step forward; Mount far right. Carrick's singles have the tactics board behind him (documentary/
locker-room, the board's corner); the players' singles have the shirts on the wall behind them, out of focus.
Bruno's touchline singles at Hull have the stand behind him (stadiums/red-seated).

Every character is the same drawing as in the rest of the episode: Carrick in his black tracksuit, Martínez in his
kit (the drawings The Mole uses), Wilcox with his tablet. The match itself is the broadcast (the episode's own
animated wide shots, the clock and the score graphics corrected to the real minutes), played under the narrator.
Every result lands as a score card under the narrator's line, then the room answers it."""
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


SHOTS = finish([
    # ---- Hull: the ground, the team talk
    world(0.0, "AW", (836, 440, 1.08), (836, 430, 1.22), layers=[], drift=0.25, grade="studio"),
    wide(m("cut_talk"), ["mainoo", "cunha", "maguire", "carrick", "bruno"], push=1.04),
    close(wt("H02", "crowd") - 0.05, "carrick", draw=C_EXPLAIN, ed=106, push=(1.0, 1.04)),
    close(m("cut_mg0"), "maguire", ed=110, push=(1.0, 1.05), drift=0.4),
    # ---- the match
    insert(m("cut_m1"), "hull1"),
    close(m("cut_br1"), "bruno", key="br_pitch", ed=108, grade="studio", punch=(ls("H06") + 0.05, 1.06)),
    insert(m("cut_m2"), "hull2"),
    close(m("cut_br2"), "bruno", key="br_pitch", draw=B_CLAP, ed=104, grade="studio",
          punch=(wt("H08", "that's") - 0.03, 1.07)),
    insert(m("cut_ft"), "card_hull"),
    # ---- the dressing room
    wide(m("cut_dr"), ROOM, push=1.03),
    close(m("cut_ck1"), "carrick", ed=108),
    close(m("cut_br3"), "bruno", ed=112, punch=(wt("H11", "literally") - 0.03, 1.06)),
    close(m("cut_mg1"), "maguire", ed=108),
    close(m("cut_br4"), "bruno", ed=124, push=(1.0, 1.02)),
    wide(m("cut_silence"), ROOM, cam=(760, 450, 1.75), push=1.03),
    close(m("cut_mg2"), "maguire", ed=128, push=(1.0, 1.0), drift=0.3),
    close(m("cut_ck2"), "carrick", draw=C_EXPLAIN, ed=108, push=(1.0, 1.03)),
    insert(m("cut_board1"), "board_hull", grade="insert"),
    # ---- Ipswich
    insert(m("cut_ips"), "card_ips"),
    wide(m("cut_ips_wide"), ["mainoo", "maguire", "carrick", "cunha"],
         extra=[actor("bruno", B_CLAP, at=(980, 615))], push=1.0),
    close(m("cut_cu1"), "cunha", draw=CU_POINT, ed=110),
    close(m("cut_ck_ips"), "carrick", ed=110),
    close(m("cut_wi1"), "wilcox", ed=110),
    wide(m("cut_tab1"), ["maguire", "carrick", "cunha"], extra=[actor("bruno", B_CLAP, at=(980, 615))],
         push=1.02, tablet=(m("cut_tab1"), "THE PLAN", "IT'S WORKING")),
    # ---- Everton
    insert(m("cut_eve"), "card_eve"),
    close(m("cut_se1"), "sesko", ed=108),
    close(m("cut_mg_eve"), "maguire", ed=110),
    close(m("cut_se2"), "sesko", draw=SE_ARMS, ed=116),
    close(m("cut_ck_eve"), "carrick", ed=110),
    wide(m("cut_eve_wide"), ["mainoo", "cunha", "maguire", "carrick", "bruno"], extra=[actor("sesko")],
         push=1.03),
    # ---- Sabah
    insert(m("cut_sab"), "card_sab"),
    close(m("cut_li1"), "licho", draw=LI_POINT, ed=108),
    close(m("cut_ck_sab"), "carrick", draw=C_ARMS, ed=106),
    close(m("cut_wi2"), "wilcox", ed=110, eye=(1040, 432)),
    insert(m("cut_tab2"), "tab_dna"),
    close(m("cut_ck_smile"), "carrick", ed=120, push=(1.0, 1.06), drift=0.3),
    # ---- City
    insert(m("cut_city"), "card_city"),
    close(m("cut_li2"), "licho", draw=LI_CROSS, ed=110),
    close(m("cut_br5"), "bruno", ed=112),
    close(m("cut_mg3"), "maguire", ed=112),
    wide(m("cut_turn"), ["mainoo", "cunha", "maguire", "carrick", "bruno", "licho"], cam=(700, 440, 1.7), push=1.0),
    close(m("cut_mg4"), "maguire", ed=120),
    insert(m("cut_charge"), "tab_charge"),
    # ---- Brighton
    insert(m("cut_bri"), "card_bri"),
    insert(m("cut_bri_shirt"), "lacey_shirt"),
    close(m("cut_mo1"), "mount", ed=110),
    close(m("cut_br6"), "bruno", ed=114),
    close(m("cut_ck_not"), "carrick", ed=124, push=(1.0, 1.04), drift=0.2),
    # ---- Fulham
    insert(m("cut_ful"), "card_ful"),
    close(m("cut_cu2"), "cunha", ed=112),
    close(m("cut_br7"), "bruno", ed=112),
    close(m("cut_ck_ful"), "carrick", draw=C_EXPLAIN, ed=106),
    close(m("cut_int"), "carrick", ed=132, eye=(880, 440), push=(1.0, 1.10), drift=0.25),
    insert(m("cut_cal"), "calendar"),
    # ---- Tottenham, the reset, Atlético, Leeds week
    insert(m("cut_tot"), "card_tot"),
    insert(m("cut_reset"), "board_reset", grade="insert"),
    insert(m("cut_atl"), "card_atl"),
    insert(m("cut_mug"), "mug"),
], TL["total"])

CAPTIONS = [
    (0.35, m("cut_talk") - 0.1, "place", "HULL AWAY", "Premier League  |  Matchday 1  |  22 August 2026"),
    (m("cut_mg0") + 0.15, m("cut_m1") - 0.1, "name", "HARRY MAGUIRE", "Defender. Has got it."),
    (m("cut_br1") + 0.1, m("cut_m2") - 0.1, "name_r", "BRUNO FERNANDES", "Captain."),
    (m("cut_cu1") + 0.1, m("cut_ck_ips") - 0.1, "name_r", "MATHEUS CUNHA", "Forward."),
    (m("cut_se1") + 0.1, m("cut_mg_eve") - 0.1, "name", "BENJAMIN ŠEŠKO", "Striker."),
    (m("cut_li1") + 0.05, m("cut_ck_sab") - 0.05, "name", "LISANDRO MARTÍNEZ", "Defender. Scored."),
    (m("cut_bri_shirt") + 0.3, m("cut_mo1") - 0.1, "name", "SHEA LACEY", "Academy graduate. Off camera."),
    (m("cut_mo1") + 0.1, m("cut_br6") - 0.1, "name_r", "MASON MOUNT", "Midfielder. Has been here a while."),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
