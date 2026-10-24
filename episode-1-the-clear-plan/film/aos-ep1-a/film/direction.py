"""The shot list for part A: every cut, camera move and caption, keyed to the dialogue edit (timeline.py).

The dressing room is the one the Hull opening used (aos/locker-room-wide, the symmetrical room with the door at the
back left). After every result the documentary camera goes back to the same wide (W_CAM), so the room's mood is what
changes. Where everyone stands in it (feet in plate px, from the camera): Carrick in the middle by the carpet's far
edge; Bruno front right; Maguire front left; Cunha and Mainoo back right / back left; Šeško far left; Martínez left of
Carrick, a step forward; Mount far right; Wilcox in the doorway at the back left. Everyone looks the way that seating
says, in every shot (EYES comes from SEAT). Carrick's singles have the tactics board behind him (documentary/locker-room,
the same club's room from the board's corner); the players' singles have the shirts on the wall behind them, out of
focus.

Every result: the ground (a documentary lower third, as the opening's HULL AWAY), the score card (cards.py, the
opening's own card design), then the room."""
import json

from studio.film import ep
from studio.film.cast import CAST, feet
from studio.film.shots import Marks, card, finish, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"W": "aos/locker-room-wide", "D": "documentary/locker-room", "ST": "street/manchester-matchday",
          "OT": "stadiums/old-trafford", "AW": "aos/stadium-exterior", "MZ": "aos/mixed-zone",
          "OF": "documentary/ceo-office", "CQ": "training-ground/carrington-quiet"}
OCCL = {}

# ---------------------------------------------------------------- the room
HOR = 402.0                      # the room's horizon (the carpet's sides meet there), plate px
EYE_H = 0.84                     # the camera's height (m): the door is 2.1 m


def px_per_m(y):
    return (y - HOR) / EYE_H


HEIGHT = dict(carrick=1.76, bruno=1.79, maguire=1.94, cunha=1.84, sesko=1.95, licho=1.75, mount=1.81,
              mainoo=1.80, wilcox=1.78, zirkzee=1.93)
SEAT = dict(carrick=(820, 592), bruno=(1165, 612), maguire=(540, 612), cunha=(1035, 548), mainoo=(640, 548),
            sesko=(420, 598), licho=(960, 645), mount=(1245, 600), wilcox=(478, 515), lacey=(1300, 560))
DRAW = {"carrick": "michael-carrick:track", "bruno": "bruno-fernandes:front", "maguire": "harry-maguire:front",
        "cunha": "matheus-cunha:front", "sesko": "benjamin-sesko:front", "licho": "lisandro-martinez:squad",
        "mount": "mason-mount:squad", "mainoo": "kobbie-mainoo:front", "wilcox": "jason-wilcox:clipboard"}
C_EXPLAIN, C_ARMS = "michael-carrick:track_explain", "michael-carrick:arms"
B_CLAP, CU_POINT, LI_POINT, SE_ARMS = ("bruno-fernandes:clap", "matheus-cunha:points", "lisandro-martinez:point",
                                      "benjamin-sesko:arms-folded")
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
    """a character standing in the room at true scale: by their feet and their height"""
    draw = draw or DRAW[who]
    x, y = at or SEAT[who]
    ensure_stand(draw)
    return (who, draw, (x, y), 0.0, mirror, {"stand": HEIGHT.get(who, 1.8) * px_per_m(y)})


def _eyes():
    """off-screen eyelines from the seating: towards where the other one stands, a little down to the shorter or
    nearer, the head turned a third of the way"""
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
    return out


EYES = _eyes()

W_CAM = (836, 438, 1.45)                    # the dressing room's documentary wide: always the same


def wide(t, who, extra=None, cam=None, push=1.025, drift=0.45, **kw):
    """the room's wide: the people in it this time"""
    acts = [actor(w) for w in who] + list(extra or [])
    acts.sort(key=lambda a: a[2][1])                      # the back of the room first
    c0 = cam or W_CAM
    return world(t, "W", c0, (c0[0], c0[1], c0[2] * push), layers=[("actors", acts)], drift=drift, grade="room",
                 **kw)


SET = {   # each one's single: the wall behind (plate, cx, cy, zoom, blur) and where the eyes go (look room)
    "carrick": dict(bg=("D", 360, 300, 2.3, 2.6), eye=(830, 432)),
    "bruno": dict(bg=("W", 1210, 330, 2.7, 2.6), eye=(1060, 432)),
    "maguire": dict(bg=("W", 470, 330, 2.7, 2.6), eye=(860, 432)),
    "cunha": dict(bg=("W", 1330, 300, 2.7, 2.6), eye=(1040, 432)),
    "sesko": dict(bg=("W", 300, 300, 2.7, 2.6), eye=(880, 432)),
    "licho": dict(bg=("W", 700, 300, 2.7, 2.6), eye=(880, 432)),
    "mount": dict(bg=("W", 1260, 320, 2.7, 2.6), eye=(1040, 432)),
    "wilcox": dict(bg=("W", 480, 330, 2.5, 2.8), eye=(900, 432)),
}


def close(t, who, ed=112.0, draw=None, push=(1.0, 1.035), drift=0.6, eye=None, **kw):
    st = SET[who]
    return single(t, who, draw or DRAW[who], st["bg"], None, ed=ed, eye=eye or st["eye"], push=push, drift=drift,
                  grade="room", **kw)


def ground(t, plate, cam0, cam1):
    """the ground before the result: an empty plate, a slow move"""
    return world(t, plate, cam0, cam1, layers=[], drift=0.25, grade="studio")


HOME_ST = ((836, 470, 1.15), (900, 455, 1.32))       # the street towards Old Trafford: a slow push up it
HOME_OT = ((836, 420, 1.05), (836, 400, 1.2))        # inside the ground
AWAY = ((836, 440, 1.08), (836, 430, 1.22))          # an away ground at dusk (the opening's Hull exterior)

SHOTS = finish([
    # ---- Hull: the dressing room
    wide(0.0, ["mainoo", "cunha", "maguire", "carrick", "bruno"], push=1.03),
    close(m("cut_ck1"), "carrick", ed=108),
    close(m("cut_br1"), "bruno", ed=112, punch=(wt("H02", "literally") - 0.03, 1.06)),
    close(m("cut_mg1"), "maguire", ed=108),
    close(m("cut_br2"), "bruno", ed=124, push=(1.0, 1.02)),
    wide(m("cut_silence"), ["mainoo", "cunha", "maguire", "carrick", "bruno"], cam=(760, 450, 1.75), push=1.03),
    close(m("cut_mg2"), "maguire", ed=128, push=(1.0, 1.0), drift=0.3),
    close(m("cut_ck2"), "carrick", draw=C_EXPLAIN, ed=108, push=(1.0, 1.03)),
    insert(m("cut_board1"), "board_hull", grade="insert"),
    # ---- Ipswich
    ground(m("est_ips"), "ST", *HOME_ST),
    insert(m("cut_ips"), "card_ips"),
    wide(m("cut_ips_wide"), ["mainoo", "maguire", "carrick", "cunha"],
         extra=[actor("bruno", B_CLAP, at=(980, 615))], push=1.0),
    close(m("cut_cu1"), "cunha", draw=CU_POINT, ed=110),
    close(m("cut_ck_ips"), "carrick", ed=110),
    world(m("cut_door"), "W", (560, 400, 2.4), (545, 398, 2.55),
          layers=[("actors", [actor("wilcox"), actor("mainoo")])], drift=0.4, grade="room"),
    close(m("cut_wi1"), "wilcox", ed=110),
    wide(m("cut_tab1"), ["maguire", "carrick", "cunha"], extra=[actor("bruno", B_CLAP, at=(980, 615))],
         push=1.02, tablet=(m("cut_tab1"), "THE PLAN", "IT'S WORKING")),
    # ---- Everton
    ground(m("est_eve"), "AW", *AWAY),
    insert(m("cut_eve"), "card_eve"),
    wide(m("cut_eve_wide"), ["mainoo", "cunha", "maguire", "carrick", "bruno"],
         extra=[actor("sesko", at=(420, 598))]),
    close(m("cut_se1"), "sesko", ed=108),
    close(m("cut_ck_eve"), "carrick", ed=110),
    close(m("cut_mg_eve"), "maguire", ed=110),
    close(m("cut_se2"), "sesko", draw=SE_ARMS, ed=116),
    # ---- Sabah
    ground(m("est_sab"), "OT", *HOME_OT),
    insert(m("cut_sab"), "card_sab"),
    wide(m("cut_sab_wide"), ["cunha", "maguire", "carrick", "bruno", "licho"],
         extra=[actor("wilcox", at=(1330, 585))]),
    close(m("cut_li1"), "licho", draw=LI_POINT, ed=108),
    close(m("cut_ck_sab"), "carrick", draw=C_ARMS, ed=106),
    close(m("cut_wi2"), "wilcox", ed=110, eye=(1040, 432)),
    insert(m("cut_tab2"), "tab_dna"),
    close(m("cut_ck_smile"), "carrick", ed=120, push=(1.0, 1.05), drift=0.3),
    # ---- Manchester City
    ground(m("est_city"), "ST", (760, 470, 1.2), (700, 460, 1.34)),
    insert(m("cut_city"), "card_city"),
    wide(m("cut_city_wide"), ["mainoo", "cunha", "maguire", "carrick", "bruno", "licho"], push=1.015, drift=0.3),
    close(m("cut_li2"), "licho", ed=110),
    close(m("cut_br3"), "bruno", ed=112),
    close(m("cut_mg3"), "maguire", ed=112),
    wide(m("cut_turn"), ["mainoo", "cunha", "maguire", "carrick", "bruno", "licho"], cam=(700, 440, 1.7), push=1.0),
    close(m("cut_mg4"), "maguire", ed=120),
    insert(m("cut_charge"), "tab_charge"),
    # ---- Brighton
    ground(m("est_bri"), "OT", (700, 420, 1.12), (760, 405, 1.25)),
    insert(m("cut_bri"), "card_bri"),
    insert(m("cut_bri_shirt"), "lacey_shirt"),
    close(m("cut_mo1"), "mount", ed=110),
    close(m("cut_ck_bri"), "carrick", ed=114, push=(1.0, 1.0)),
    close(m("cut_br4"), "bruno", ed=114),
    close(m("cut_ck_not"), "carrick", ed=124, push=(1.0, 1.03), drift=0.2),
    # ---- Fulham
    ground(m("est_ful"), "AW", (760, 450, 1.1), (700, 440, 1.24)),
    insert(m("cut_ful"), "card_ful"),
    close(m("cut_ful_li"), "licho", ed=104, push=(1.0, 1.0), drift=0.2),
    close(m("cut_cu2"), "cunha", ed=112),
    close(m("cut_br5"), "bruno", ed=112),
    close(m("cut_ck_ful"), "carrick", draw=C_EXPLAIN, ed=106),
    close(m("cut_int"), "carrick", ed=132, eye=(880, 440), push=(1.0, 1.10), drift=0.25),
    insert(m("cut_cal"), "calendar"),
    insert(m("cut_intl"), "card_intl"),
    world(m("cut_empty"), "W", (836, 440, 1.3), (836, 438, 1.36), layers=[("props", "lights_off")], drift=0.2,
          grade="room"),
    # ---- Tottenham, the reset
    ground(m("est_tot"), "ST", (900, 465, 1.18), (940, 455, 1.3)),
    insert(m("cut_tot"), "card_tot"),
    wide(m("cut_return"), ["mainoo", "cunha", "maguire", "carrick", "bruno", "licho"], push=1.02, drift=0.3),
    insert(m("cut_reset"), "board_reset", grade="insert"),
    # ---- Atlético
    ground(m("est_atl"), "AW", (900, 440, 1.1), (900, 430, 1.22)),
    insert(m("cut_atl"), "card_atl"),
    world(m("cut_mz"), "MZ", (836, 470, 1.12), (836, 462, 1.24), layers=[("props", "flashes")], drift=0.3),
    # ---- Leeds week
    insert(m("cut_leeds"), "card_leeds"),
    insert(m("cut_mug"), "mug"),
], TL["total"])

# documentary captions: (start, end, kind, text 1, text 2)
CAPTIONS = [
    (0.35, 2.4, "place", "AWAY DRESSING ROOM", "Hull, 22 August 2026. Full time."),
    (m("cut_br1") + 0.25, m("cut_mg1") - 0.15, "name_r", "BRUNO FERNANDES", "Captain."),
    (m("cut_mg1") + 0.15, m("cut_br2") - 0.1, "name", "HARRY MAGUIRE", "Defender."),
    (m("est_ips") + 0.25, m("cut_ips") - 0.1, "place", "OLD TRAFFORD", "Premier League  |  30 August 2026"),
    (m("cut_cu1") + 0.1, m("cut_ck_ips") - 0.1, "name_r", "MATHEUS CUNHA", "Forward."),
    (m("cut_wi1") + 0.15, m("cut_tab1") - 0.1, "name", "JASON WILCOX", "Director of Football. Has a tablet."),
    (m("est_eve") + 0.25, m("cut_eve") - 0.1, "place", "EVERTON AWAY", "Premier League  |  6 September 2026"),
    (m("cut_se1") + 0.1, m("cut_ck_eve") - 0.1, "name", "BENJAMIN ŠEŠKO", "Striker."),
    (m("est_sab") + 0.25, m("cut_sab") - 0.1, "place", "OLD TRAFFORD", "European night  |  10 September 2026"),
    (m("cut_li1") + 0.1, m("cut_ck_sab") - 0.1, "name", "LISANDRO MARTÍNEZ", "Defender. Scored."),
    (m("est_city") + 0.25, m("cut_city") - 0.1, "place", "OLD TRAFFORD", "Premier League  |  13 September 2026"),
    (m("est_bri") + 0.25, m("cut_bri") - 0.1, "place", "OLD TRAFFORD", "League Cup  |  16 September 2026"),
    (m("cut_bri_shirt") + 0.3, m("cut_mo1") - 0.1, "name", "SHEA LACEY", "Academy graduate. Off camera."),
    (m("cut_mo1") + 0.1, m("cut_ck_bri") - 0.1, "name_r", "MASON MOUNT", "Midfielder. Has been here a while."),
    (m("est_ful") + 0.25, m("cut_ful") - 0.1, "place", "FULHAM AWAY", "Premier League  |  20 September 2026"),
    (m("est_tot") + 0.25, m("cut_tot") - 0.1, "place", "OLD TRAFFORD", "Premier League  |  10 October 2026"),
    (m("est_atl") + 0.25, m("cut_atl") - 0.1, "place", "ATLÉTICO MADRID AWAY", "Europe  |  13 October 2026"),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
