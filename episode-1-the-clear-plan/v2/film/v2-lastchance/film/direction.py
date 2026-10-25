"""The shot list: The Handover's, cut for cut (episodes/the-handover/film/direction.py), keyed to this edit.

Where everyone is (the boardroom, club/boardroom): the three executives sit along the far side of the long table
(from screen left: Omar by the trophy cabinet, Jason by the window, Jim under the screen); Carrick sits opposite
them, alone, with the coffee counter and the door behind him. The executives look a little screen LEFT to him in
every shot of them; he looks screen RIGHT to them.

The door's end of the room: Carrick stands to the left of the door (his feet at plate x 1050), Ole stops on the
threshold (x 1205), both at true scale; the closer shots by the door use plate "D", that end of the room upscaled 8x
(props.door_end). Every character is the same cut-out as in the rest of the episode (Wilcox in his black tracksuit
pose, the one The Mole and the meeting use)."""
import json

from studio.film import ep
from studio.film.shots import Marks, card, finish, group, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"B": "club/boardroom", "D": "club/boardroom", "DO": "club/boardroom"}

DX0, DY0 = 860, 110


def d(x, y):
    return (2.0 * (x - DX0), 2.0 * (y - DY0))


def dpoly(poly):
    return [d(x, y) for x, y in poly]


TABLE = [(598, 440), (1068, 440), (1500, 735), (1500, 780), (85, 780), (85, 712)]
GLASSES = [[(701, 446), (702, 435), (706, 433), (721, 433), (725, 435), (726, 446), (726, 463), (701, 463)],
           [(939, 442), (940, 432), (944, 429), (976, 429), (980, 432), (981, 442), (981, 457), (939, 457)]]
CHAIR_A = [(1100, 520), (1102, 480), (1106, 463), (1111, 441), (1118, 414), (1121, 399), (1126, 397), (1150, 400),
           (1157, 402), (1162, 403), (1164, 408), (1159, 418), (1156, 428), (1150, 446), (1144, 470), (1141, 480),
           (1138, 520)]
ARM_A = [(1072, 457), (1102, 457), (1102, 464), (1072, 464)]
CHAIR_B = [(1166, 520), (1171, 480), (1177, 457), (1184, 434), (1190, 411), (1194, 406), (1232, 410), (1238, 412),
           (1243, 415), (1243, 421), (1236, 430), (1229, 454), (1222, 480), (1216, 520)]
CHAIR_C = [(1238, 600), (1245, 550), (1250, 530), (1260, 495), (1272, 455), (1283, 427), (1287, 422), (1345, 431),
           (1360, 434), (1367, 440), (1362, 450), (1357, 452), (1345, 495), (1330, 540), (1322, 600)]
CORNER = [(990, 440), (1066, 440), (1088, 460), (1104, 478), (1110, 540), (990, 540)]
FRONT = [CHAIR_A, ARM_A, CHAIR_B, CHAIR_C, CORNER]
OCCL = {"B": {"table": [TABLE] + GLASSES, "front": FRONT}, "O": {"front": FRONT},
        "D": {"front": [dpoly(p) for p in FRONT]}, "DO": {"front": [dpoly(p) for p in FRONT]}}
RIM_Y = 440

EYES = {
    "jim": dict(carrick=(-0.32, 0.03, -0.10), jason=(-0.85, 0.03, -0.25), omar=(-0.95, 0.03, -0.3)),
    "jason": dict(carrick=(-0.38, 0.04, -0.12), jim=(0.85, 0.03, 0.25), omar=(-0.85, 0.03, -0.25)),
    "omar": dict(carrick=(-0.45, 0.05, -0.14), jason=(0.8, 0.03, 0.25), jim=(0.92, 0.03, 0.3)),
    "carrick": dict(jim=(0.32, 0.03, 0.10), jason=(0.45, 0.03, 0.14), omar=(0.62, 0.04, 0.2),
                    ole=(0.85, -0.02, 0.10)),
    "ole": dict(carrick=(-0.35, 0.03, 0.0), jim=(-0.15, 0.04, 0.0)),
}
EYES_FIRST = True

DRAW = {"jim": "jim-ratcliffe:suit", "jason": "jason-wilcox:pockets", "omar": "omar-berrada:front",
        "carrick": "michael-carrick:track", "ole": "ole-gunnar-solskjaer:arms"}
C_ARMS, C_POINT, C_OUT = "michael-carrick:arms", "michael-carrick:point", "michael-carrick:track_explain"
C_Q34, C_BACK = "michael-carrick:track_q34", "michael-carrick:track_back"
J_POINT = "jim-ratcliffe:point"
O_WAVE, O_ARMS, O_SHRUG, O_NEUTRAL = ("ole-gunnar-solskjaer:wave", "ole-gunnar-solskjaer:arms",
                                      "ole-gunnar-solskjaer:shrug", "ole-gunnar-solskjaer:neutral")
ALSO = [O_WAVE]

EYE = {"jim": (1075, 445), "jason": (1060, 440), "omar": (1050, 440), "carrick": (845, 448)}
FZ = 3.4
BGZ = 3.2


def under(x_plate, x_screen):
    return x_plate - (x_screen - 960) / (1920 / 1672 * FZ)


SET = {
    "jim": dict(bg=("B", 905, 262, BGZ, 0.0), fg=("B", "table", under(833, 1075), RIM_Y, FZ, 0.0)),
    "jason": dict(bg=("B", 470, 282, BGZ, 0.0), fg=("B", "table", under(833, 1060), RIM_Y, FZ, 0.0)),
    "omar": dict(bg=("B", 200, 272, BGZ, 0.0), fg=("B", "table", under(833, 1050), RIM_Y, FZ, 0.0)),
    "carrick": dict(bg=("B", 1330, 300, BGZ, 0.0), fg=("B", "table", under(833, 845), RIM_Y, FZ, 0.0)),
}


def close(t, who, ed=108.0, eye=None, push=(1.0, 1.03), drift=0.7, table=3.9, draw=None, **kw):
    st = SET[who]
    return single(t, who, draw or DRAW[who], st["bg"], st["fg"], ed=ed, eye=eye or EYE[who], table=table,
                  push=push, drift=drift, **kw)


def execs(t, ed=70.0, push=(1.0, 1.03), **kw):
    acts = [("omar", DRAW["omar"], (520, 440), ed, False), ("jason", DRAW["jason"], (930, 440), ed, False),
            ("jim", DRAW["jim"], (1330, 440), ed, False)]
    return group(t, acts, cams=[(t, (960, 540, push[0])), (t + 3.0, (960, 540, push[1]))],
                 bg=("B", 470, 285, 1.6, 0.0), fg=("B", "table", 833, RIM_Y, 2.9, 0.0), table_y=440 + 3.6 * ed, **kw)


C_FEET, C_H = (1050, 476), 216.0
O_FEET, O_H = (1205, 466), 203.0


def carrick_at_door(draw=None, plate="B", mirror=False):
    f, h = (C_FEET, C_H) if plate in ("B", "O") else (d(*C_FEET), 2 * C_H)
    return ("carrick", draw or DRAW["carrick"], f, 0.0, mirror, {"stand": h})


def ole_at_door(draw, mirror=False):
    return ("ole", draw, d(*O_FEET), 0.0, mirror, {"stand": 2 * O_H})


def zcam(cx, cy, s):
    return (cx, cy, s / 1.6)


DOOR_CAM = (1150, 330, 3.8)


def door_wide(t, layers, cams=None, drift=0.35, plate="B"):
    return world(t, plate, DOOR_CAM, layers=[("props", "doorway")] + layers + [("occl", "front")], cams=cams,
                 drift=drift, blur=0.0)


def by_door(t, plate, actors, cams, drift=0.4):
    return world(t, plate, cams[0][1], layers=[("actors", actors), ("occl", "front")], cams=cams, drift=drift,
                 blur=0.0)


SHOTS = finish([
    close(0.0, "carrick", draw=C_ARMS, ed=100, table=5.6, push=(1.0, 1.04)),            # arms crossed, waiting
    execs(wt("K01", "the") - 0.06),                                                     # "...what we expected."
    close(wt("K01", "we've") - 0.06, "jim", ed=104, punch=(wt("K01", "last") - 0.04, 1.14), push=(1.0, 1.0)),
    close(m("cut_jason1"), "jason", ed=108, push=(1.0, 1.06)),                          # "And frankly, Michael,"
    close(wt("K02", "we") - 0.08, "carrick", ed=112, push=(1.0, 1.05)),                 # the eyebrow; K03
    close(m("cut_rant"), "carrick", draw=C_POINT, ed=100, eye=(760, 452), push=(1.0, 1.04), drift=0.6),
    close(wt("K04", "three") - 0.05, "carrick", ed=108, eye=(880, 452), push=(1.0, 1.0), drift=0.6,
          punches=[(wt("K04", "three") + 0.05, 1.05), (wt("K04", "no", 1) - 0.03, 1.05),
                   (wt("K04", "no", 2) - 0.03, 1.05)]),
    execs(wt("K04", "defensive") - 0.05, ed=76, push=(1.0, 1.0)),
    close(wt("K04", "what") - 0.06, "carrick", draw=C_OUT, ed=104, eye=(900, 452), table=4.5, push=(1.0, 1.04),
          punch=(wt("K04", "fuck") - 0.03, 1.06)),
    execs(m("cut_omar"), ed=64, push=(1.0, 1.025), drift=0.25),
    close(m("cut_balanced"), "carrick", ed=126, eye=(900, 458), push=(1.0, 1.0), drift=0.35,
          punch=(ls("K06") + 0.02, 1.07)),
    close(m("cut_resign"), "carrick", ed=100, push=(1.0, 1.02), rise=(m("rise"), m("rise") + 0.26, 110)),
    door_wide(m("cut_door1"), [("actors", [carrick_at_door(C_BACK)])],
              cams=[(m("cut_door1"), (985, 345, 3.3)), (m("cut_door1") + 1.15, DOOR_CAM)]),
    close(wt("K08", "before") - 0.06, "jim", draw=J_POINT, ed=100, eye=(1090, 452), mirror=True,
          push=(1.0, 1.04)),
    by_door(m("cut_what"), "D", [carrick_at_door(plate="D")],
            cams=[(m("cut_what"), zcam(371, 404, 4.4)), (m("cut_jim3"), zcam(371, 404, 4.55))]),
    close(m("cut_jim3"), "jim", ed=100, push=(1.0, 1.05)),
    door_wide(m("cut_door3"), [("actors", [carrick_at_door()])],
              cams=[(m("cut_door3"), DOOR_CAM), (m("cut_ole1"), (1155, 328, 3.95))]),
    by_door(m("cut_ole1"), "DO", [ole_at_door(O_ARMS)],
            cams=[(m("cut_ole1"), zcam(722, 420, 3.84)), (wt("K13", "i'm"), zcam(722, 418, 3.95))]),
    by_door(wt("K13", "i'm") - 0.06, "DO", [carrick_at_door(C_Q34, "DO"), ole_at_door(O_ARMS)],
            cams=[(wt("K13", "i'm") - 0.06, zcam(578, 444, 3.1)), (wt("K13", "i've"), zcam(578, 444, 3.16))]),
    by_door(wt("K13", "i've") - 0.1, "DO", [ole_at_door(O_SHRUG, mirror=True)],
            cams=[(wt("K13", "i've") - 0.1, zcam(761, 402, 4.15)), (m("cut_last"), zcam(752, 396, 4.45))]),
    by_door(m("cut_last"), "DO", [carrick_at_door(plate="DO"), ole_at_door(O_NEUTRAL)],
            cams=[(m("cut_last"), zcam(398, 390, 5.2)), (m("cut_black"), zcam(398, 390, 5.45))], drift=0.3),
    card(m("cut_black"), "black"),
    card(m("cut_title"), "title"),
    insert(m("cut_credits"), "credits"),
], TL["total"])

TITLE = (("ALL OR SOMETHING", "BEBAS", 104, None, 14, 300, (255, 255, 255)),
         ("LAST CHANCE", "BEBAS", 170, None, 10, 410, (255, 255, 255)))
TAGLINE = (("EPISODE ONE: THE CLEAR PLAN", "BEBAS", 64, None, 6, 752, (236, 236, 236)),
           ("A FAN PARODY. NONE OF THIS HAPPENED.", "INTER", 30, 500, 1, 850, (170, 170, 170)))

CAPTIONS = [
    (0.3, ls("K00") + 2.4, "place", "THE BOARDROOM", "The morning after Como."),
    (ls("K00") + 2.6, wt("K01", "the") - 0.12, "name", "MICHAEL CARRICK", "Head Coach. For now."),
    (m("stop") + 0.25, m("cut_ole1") - 0.05, "name_r", "OLE GUNNAR SOLSKJÆR", "On standby. Again."),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
