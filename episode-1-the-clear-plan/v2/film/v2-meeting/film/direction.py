"""The shot list for the meeting, keyed to the dialogue edit (timeline.py).

The boardroom is The Handover's (club/boardroom), with the same people in the same seats and the same coverage:
the three executives along the far side of the table (from screen left: Berrada by the trophy cabinet, Wilcox by
the window, Ratcliffe under the big screen); Carrick alone opposite them. The executives look a little screen LEFT
to him; he looks screen RIGHT to them. Close singles at the table (the wall behind sharp, the table's far end in
front), the three executives held wide for the awkward beats.

The big screen carries the running gag (props.screen_plate): black until Wilcox's tablet tries to connect, then
CONNECTING TO BOARDROOM DISPLAY... 3% behind Ratcliffe for the whole list of positions; the objectives once it
connects; the owners' call (two tiles, CAMERA OFF); CALL ENDED 0:41. Plates "B", "BC", "BO", "BE" are the room with
the screen in each state; the screen's own shots ("SC") animate it (props.screen)."""
import json

from studio.film import ep
from studio.film.shots import Marks, card, finish, group, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"B": "club/boardroom", "BC": "club/boardroom", "BO": "club/boardroom", "BE": "club/boardroom",
          "SC": "club/boardroom", "CQ": "training-ground/carrington-quiet"}

# the table's far end (from The Handover) and the two glasses that stand up over it
TABLE = [(598, 440), (1068, 440), (1500, 735), (1500, 780), (85, 780), (85, 712)]
GLASSES = [[(701, 446), (702, 435), (706, 433), (721, 433), (725, 435), (726, 446), (726, 463), (701, 463)],
           [(939, 442), (940, 432), (944, 429), (976, 429), (980, 432), (981, 442), (981, 457), (939, 457)]]
OCCL = {k: {"table": [TABLE] + GLASSES} for k in ("B", "BC", "BO", "BE")}
RIM_Y = 440

EYES = {
    "jim": dict(carrick=(-0.32, 0.03, -0.10), wilcox=(-0.85, 0.03, -0.25), omar=(-0.95, 0.03, -0.3)),
    "wilcox": dict(carrick=(-0.38, 0.04, -0.12), jim=(0.85, 0.03, 0.25), omar=(-0.85, 0.03, -0.25)),
    "omar": dict(carrick=(-0.45, 0.05, -0.14), wilcox=(0.8, 0.03, 0.25), jim=(0.92, 0.03, 0.3)),
    "carrick": dict(jim=(0.32, 0.03, 0.10), wilcox=(0.45, 0.03, 0.14), omar=(0.62, 0.04, 0.2),
                    screen=(0.28, -0.32, 0.08)),
}
EYES_FIRST = False

DRAW = {"jim": "jim-ratcliffe:suit", "wilcox": "jason-wilcox:clipboard", "omar": "omar-berrada:front",
        "carrick": "michael-carrick:track"}
C_ARMS, C_POINT, C_OUT = "michael-carrick:arms", "michael-carrick:point", "michael-carrick:track_explain"
J_POINT = "jim-ratcliffe:point"
W_CROSS, W_POCKETS = "jason-wilcox:crossarms", "jason-wilcox:pockets"
ALSO = []

EYE = {"jim": (1075, 445), "wilcox": (1060, 440), "omar": (1050, 440), "carrick": (845, 448)}
FZ = 3.4                            # the table's zoom in a single
BGZ = 3.2                           # the wall's zoom


def under(x_plate, x_screen):
    return x_plate - (x_screen - 960) / (1920 / 1672 * FZ)


BGXY = {"jim": (905, 262), "wilcox": (470, 282), "omar": (200, 272), "carrick": (1330, 300)}


def screen_state(t):
    """which plate the room is in at t: the big screen's state"""
    if t < m("cut_tab"):
        return "B"
    if t < m("cut_obj"):
        return "BC"
    if t < m("chime"):
        return "BO"
    return "BE"


def close(t, who, ed=108.0, eye=None, push=(1.0, 1.03), drift=0.7, table=3.9, draw=None, **kw):
    """a close single at the table: the wall behind, the character, the table's far end in front"""
    k = screen_state(t)
    bx, by = BGXY[who]
    fg = (k, "table", under(833, (eye or EYE[who])[0]), RIM_Y, FZ, 0.0)
    return single(t, who, draw or DRAW[who], (k, bx, by, BGZ, 0.0), fg, ed=ed, eye=eye or EYE[who], table=table,
                  push=push, drift=drift, **kw)


def execs(t, ed=70.0, push=(1.0, 1.03), wdraw=None, jdraw=None, **kw):
    """the three executives behind the table"""
    k = screen_state(t)
    acts = [("omar", DRAW["omar"], (520, 440), ed, False), ("wilcox", wdraw or DRAW["wilcox"], (930, 440), ed, False),
            ("jim", jdraw or DRAW["jim"], (1330, 440), ed, False)]
    return group(t, acts, cams=[(t, (960, 540, push[0])), (t + 3.0, (960, 540, push[1]))],
                 bg=(k, 470, 285, 1.6, 0.0), fg=(k, "table", 833, RIM_Y, 2.9, 0.0), table_y=440 + 3.6 * ed, **kw)


SCR = (869, 230)                    # framing the big screen (plate px): high enough that the chair under it is out


def screen(t, z0=3.6, z1=3.75, cy=None):
    """the big screen, nearly filling the frame"""
    return world(t, "SC", (SCR[0], cy or SCR[1], z0), (SCR[0], cy or SCR[1], z1), layers=[("props", "screen")],
                 drift=0.3, grade="studio")


SHOTS = finish([
    # ---- Carrington; the boardroom
    world(0.0, "CQ", (836, 430, 1.0), cams=[(0.0, (836, 440, 1.0)), (m("cut_room"), (760, 400, 1.3))],
          drift=0.25, grade="sunny"),
    execs(m("cut_room"), wdraw=W_POCKETS, push=(1.0, 1.06)),
    close(m("cut_wi1"), "wilcox", ed=108, push=(1.0, 1.05)),
    close(m("cut_ck1"), "carrick", draw=C_ARMS, ed=104, table=5.6),
    close(m("cut_wi2"), "wilcox", ed=114, push=(1.0, 1.0)),
    insert(m("cut_tab"), "tablet"),
    close(m("cut_wi3"), "wilcox", draw=W_POCKETS, ed=104, push=(1.0, 1.04),
          words=[(wt("M07", "clarity") - 0.03, "CLARITY."), (wt("M07", "alignment") - 0.03, "ALIGNMENT."),
                 (wt("M07", "sustainability") - 0.03, "SUSTAINABILITY."), (wt("M07", "agility") - 0.03, "AGILITY."),
                 (wt("M07", "yeah") - 0.05, None)]),
    close(m("cut_ck2"), "carrick", ed=108, push=(1.0, 1.03),
          punch=(wt("M08", "who") - 0.04, 1.08)),
    close(m("cut_om1"), "omar", ed=108, push=(1.0, 1.04)),
    close(m("cut_ck3"), "carrick", draw=C_OUT, ed=104, table=4.5),
    close(m("cut_wi4"), "wilcox", draw=W_CROSS, ed=110, push=(1.0, 1.0)),
    # the list: the camera a little closer every time
    close(m("cut_q1"), "carrick", ed=110, push=(1.0, 1.0), drift=0.4),
    close(m("cut_n1"), "jim", ed=108, push=(1.0, 1.0), drift=0.4),
    close(m("cut_q2"), "carrick", ed=118, push=(1.0, 1.0), drift=0.4),
    close(m("cut_n2"), "jim", ed=116, push=(1.0, 1.0), drift=0.4),
    close(m("cut_q3"), "carrick", ed=126, push=(1.0, 1.0), drift=0.4),
    close(m("cut_n3"), "jim", draw=J_POINT, ed=100, eye=(1090, 452), mirror=True, push=(1.0, 1.03)),
    close(m("cut_q4"), "carrick", ed=132, push=(1.0, 1.0), drift=0.3),
    close(m("cut_n4"), "jim", ed=128, push=(1.0, 1.0), drift=0.3),
    close(m("cut_q5"), "carrick", draw=C_ARMS, ed=104, table=5.6, push=(1.0, 1.02)),
    execs(m("cut_fair"), push=(1.0, 1.04)),
    close(m("cut_ck4"), "carrick", ed=108),
    close(m("cut_wi5"), "wilcox", ed=110),
    close(m("cut_ck5"), "carrick", ed=114, push=(1.0, 1.0)),
    close(m("cut_wi6"), "wilcox", draw=W_POCKETS, ed=106),
    close(m("cut_ck6"), "carrick", draw=C_OUT, ed=104, table=4.5),
    close(m("cut_om2"), "omar", ed=112, push=(1.0, 1.05)),
    close(m("cut_ck7"), "carrick", ed=110),
    screen(m("cut_obj"), 3.5, 3.9),
    close(m("cut_ck8"), "carrick", draw=C_OUT, ed=104, table=4.5, push=(1.0, 1.04)),
    close(m("cut_om3"), "omar", ed=110, push=(1.0, 1.0)),
    close(m("cut_jim1"), "jim", ed=118, push=(1.0, 1.0), punch=(ls("M32") - 0.02, 1.06)),
    close(m("cut_ck9"), "carrick", ed=112, push=(1.0, 1.04)),
    close(m("cut_om4"), "omar", ed=106, push=(1.0, 1.04)),
    close(m("cut_jim2"), "jim", draw=J_POINT, ed=100, eye=(1090, 452), mirror=True, push=(1.0, 1.03)),
    screen(m("chime"), 3.4, 3.7),
    close(m("cut_ck_call"), "carrick", ed=110, push=(1.0, 1.03), drift=0.4),
    screen(m("cut_call2"), 3.7, 3.9),
    close(m("cut_jim3"), "jim", ed=110, push=(1.0, 1.02)),
    close(m("cut_ck10"), "carrick", draw=C_ARMS, ed=104, table=5.6, push=(1.0, 1.03)),
    close(m("cut_jim4"), "jim", draw=J_POINT, ed=100, eye=(1090, 452), mirror=True, push=(1.0, 1.04),
          punch=(wt("M45", "don't") - 0.03, 1.07)),
    card(m("cut_title"), "title"),
], TL["total"])

TITLE = (("ALL OR SOMETHING", "BEBAS", 104, None, 14, 300, (255, 255, 255)),
         ("THE CLEAR PLAN", "BEBAS", 170, None, 10, 410, (255, 255, 255)))
TAGLINE = (("EPISODE ONE", "BEBAS", 64, None, 6, 752, (236, 236, 236)),
           ("AN ANIMATED PARODY. THE PRIVATE SCENES ARE INVENTED.", "INTER", 30, 500, 1, 850, (170, 170, 170)))

CAPTIONS = [
    (0.4 + 4.4, m("cut_room") - 0.1, "place", "CARRINGTON", "August 2026. A new season."),
    (m("cut_wi1") + 0.2, m("cut_ck1") - 0.1, "name", "JASON WILCOX", "Director of Football. Has a tablet."),
    (m("cut_ck1") + 0.15, m("cut_wi2") - 0.1, "name", "MICHAEL CARRICK", "Head Coach."),
    (m("cut_om1") + 0.2, m("cut_ck3") - 0.1, "name", "OMAR BERRADA", "Chief Executive."),
    (m("cut_n1") + 0.05, m("cut_q2") - 0.05, "name", "SIR JIM RATCLIFFE", "Co-owner."),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
