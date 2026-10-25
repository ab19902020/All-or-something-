"""The shot list for Upstairs, keyed to the dialogue edit (timeline.py). Every character is the same drawing as in the
rest of the episode (Martínez in the home kit The Mole films him in, Wilcox in his black tracksuit).

Madrid: the mixed zone (aos/mixed-zone, as Bruno's Como interview), Martínez in a single with the reporter's
microphone in from the left; the paraphrase card over him, then the PARODY DIALOGUE label for the parody lines. The
second interview: the press room (tv-and-media/press-conference-room) with the desk's microphones. Upstairs: The
Handover's boardroom (club/boardroom) by day, the three executives along the far side of the table as in the meeting
and in Last Chance (from screen left: Berrada, Wilcox, Ratcliffe), singles of each with the table's edge in front.
The statement: a card. The new theory: Martínez in the Carrington corridor, arms crossed (The Mole follows)."""
import json

from studio.film import ep
from studio.film.cast import CAST
from studio.film.shots import Marks, finish, group, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"MZ": "aos/mixed-zone", "PR": "tv-and-media/press-conference-room", "CO": "documentary/corridor",
          "B": "club/boardroom"}

# the boardroom table (from The Handover) and the glasses on it
TABLE = [(598, 440), (1068, 440), (1500, 735), (1500, 780), (85, 780), (85, 712)]
GLASSES = [[(701, 446), (702, 435), (706, 433), (721, 433), (725, 435), (726, 446), (726, 463), (701, 463)],
           [(939, 442), (940, 432), (944, 429), (976, 429), (980, 432), (981, 442), (981, 457), (939, 457)]]
OCCL = {"B": {"table": [TABLE] + GLASSES}}
RIM_Y = 440

DRAW = {"licho": "lisandro-martinez:stand", "jim": "jim-ratcliffe:suit", "wilcox": "jason-wilcox:pockets",
        "omar": "omar-berrada:front"}
LI_POINT, LI_CROSS = "lisandro-martinez:point", "lisandro-martinez:crossarms"
J_POINT, WI_CROSS = "jim-ratcliffe:point", "jason-wilcox:crossarms"
ALSO = []

EYES = {
    "licho": dict(reporter=(-0.32, 0.03, -0.1), producer=(-0.3, 0.03, -0.1)),
    "jim": dict(wilcox=(-0.85, 0.03, -0.25), omar=(-0.95, 0.03, -0.3)),
    "wilcox": dict(jim=(0.85, 0.03, 0.25), omar=(-0.85, 0.03, -0.25)),
    "omar": dict(wilcox=(0.8, 0.03, 0.25), jim=(0.92, 0.03, 0.3)),
}
EYES_FIRST = True

FZ, BGZ = 3.4, 3.2


def under(x_plate, x_screen):
    return x_plate - (x_screen - 960) / (1920 / 1672 * FZ)


SET = {
    "li_mz": dict(bg=("MZ", 1000, 330, 2.0, 3.4), fg=None, eye=(1060, 438)),
    "li_pr": dict(bg=("PR", 836, 300, 1.9, 3.2), fg=None, eye=(900, 438)),
    "li_co": dict(bg=("CO", 900, 300, 2.4, 3.0), fg=None, eye=(940, 432)),
    "jim": dict(bg=("B", 905, 262, BGZ, 0.0), fg=("B", "table", under(833, 1075), RIM_Y, FZ, 0.0), eye=(1075, 445)),
    "wilcox": dict(bg=("B", 470, 282, BGZ, 0.0), fg=("B", "table", under(833, 1060), RIM_Y, FZ, 0.0),
                   eye=(1060, 440)),
    "omar": dict(bg=("B", 200, 272, BGZ, 0.0), fg=("B", "table", under(833, 1050), RIM_Y, FZ, 0.0), eye=(1050, 440)),
}


def li(t, key, draw=None, ed=112.0, push=(1.0, 1.035), drift=0.5, **kw):
    st = SET[key]
    return single(t, "licho", draw or DRAW["licho"], st["bg"], None, ed=ed, eye=st["eye"], push=push, drift=drift,
                  grade="studio", **kw)


def ex(t, who, ed=108.0, push=(1.0, 1.03), drift=0.7, draw=None, **kw):
    st = SET[who]
    return single(t, who, draw or DRAW[who], st["bg"], st["fg"], ed=ed, eye=st["eye"], table=3.9, push=push,
                  drift=drift, **kw)


def execs(t, ed=70.0, push=(1.0, 1.03), **kw):
    acts = [("omar", DRAW["omar"], (520, 440), ed, False), ("wilcox", DRAW["wilcox"], (930, 440), ed, False),
            ("jim", DRAW["jim"], (1330, 440), ed, False)]
    return group(t, acts, cams=[(t, (960, 540, push[0])), (t + 3.0, (960, 540, push[1]))],
                 bg=("B", 470, 285, 1.6, 0.0), fg=("B", "table", 833, RIM_Y, 2.9, 0.0), table_y=440 + 3.6 * ed, **kw)


SHOTS = finish([
    # ---- Madrid: the mixed zone
    world(0.0, "MZ", (980, 470, 1.05), (980, 462, 1.14), layers=[], drift=0.2),
    li(wt("X01", "lisandro") - 0.08, "li_mz", ed=100, push=(1.0, 1.04), props=["mic"]),
    li(m("cut_par"), "li_mz", ed=104, push=(1.0, 1.03), drift=0.15, props=["mic"]),
    li(m("cut_x03"), "li_mz", ed=114, push=(1.0, 1.02), props=["mic"]),
    li(m("cut_x04"), "li_mz", draw=LI_POINT, ed=104, push=(1.0, 1.0), props=["mic"]),
    li(m("cut_x05"), "li_mz", ed=120, push=(1.0, 1.05), props=["mic"]),
    # ---- the second interview
    world(m("cut_x07"), "PR", (836, 470, 1.05), (836, 466, 1.1), layers=[], drift=0.15),
    li(m("cut_x08"), "li_pr", draw=LI_CROSS, ed=112, push=(1.0, 1.06), props=["mics"]),
    # ---- upstairs
    execs(m("cut_board")),
    ex(m("cut_x10"), "jim", ed=104),
    ex(m("cut_x11"), "omar", ed=108),
    ex(m("cut_x12"), "jim", draw=J_POINT, ed=104, push=(1.0, 1.0)),
    ex(m("cut_x13"), "wilcox", ed=108),
    ex(m("cut_x14"), "jim", ed=112, punch=(wt("X14", "you") - 0.03, 1.12), push=(1.0, 1.0)),
    ex(m("cut_x15"), "wilcox", draw=WI_CROSS, ed=116, push=(1.0, 1.04), drift=0.3),
    ex(m("cut_x16"), "jim", draw=J_POINT, ed=106),
    ex(m("cut_x17"), "omar", ed=112, push=(1.0, 1.02)),
    ex(m("cut_x18"), "jim", ed=110),
    # ---- the statement; the new theory
    insert(m("cut_x19"), "card_statement"),
    li(m("cut_x20"), "li_co", draw=LI_CROSS, ed=108, push=(1.0, 1.08), drift=0.25),
], TL["total"])

CAPTIONS = [
    (0.3, wt("X01", "lisandro") - 0.15, "place", "MADRID", "After Atlético 2–0 United  |  13 October 2026"),
    (m("cut_x03") + 0.1, m("cut_x05") - 0.05, "name", "LISANDRO MARTÍNEZ", "Defender. On the record."),
    (m("cut_x08") + 0.1, le("X08") + 0.3, "place", "THE NEXT DAY", "A second interview."),
    (m("cut_board") + 0.2, m("cut_x10") - 0.1, "place", "THE BOARDROOM", "Upstairs."),
    (m("cut_x13") + 0.1, m("cut_x14") - 0.05, "name", "JASON WILCOX", "Technical Director. In a sense."),
]
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
