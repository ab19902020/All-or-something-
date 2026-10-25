"""The acting for Upstairs (see studio/film/perf.py for every table).

  Martínez  in the mixed zone, serious and unhurried: he looks at the reporter, points up on "Upstairs.", says the rest
            straight; at the second interview arms crossed, chin up; in the corridor his eyes narrow.
  Ratcliffe clipped and getting there; "It's you, Jason." with a stare.
  Berrada   helpful, precise, slightly pained.
  Wilcox    breezy, then caught: "In a sense." with a look away."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["licho", "jim", "omar", "wilcox"]
SPK = {w: w for w in WHO}

META = {
    "X04": ("serious", "reporter", ["upstairs"]),
    "X06": ("serious", "reporter", ["technical", "director", "honest", "defender", "danger", "say"]),
    "X08": ("indignant", "reporter", ["not", "close", "mouth"]),
    "X10": ("irritated", "wilcox", ["upstairs", "who's"]),
    "X11": ("diplomatic", "jim", ["technically", "we"]),
    "X12": ("firm", "wilcox", ["technical", "director"]),
    "X13": ("casual", "jim", ["anyone", "jim"]),
    "X14": ("firm", "wilcox", ["you", "jason"]),
    "X15": ("awkward", "jim", ["sense"]),
    "X16": ("firm", "omar", ["fine", "statement"]),
    "X17": ("diplomatic", "jim", ["apology"]),
    "X18": ("firm", "omar", ["statement", "sorry", "somewhere"]),
}
BASE = dict(licho=(-0.1, 0.0), jim=(0.0, 0.1), omar=(0.1, 0.15), wilcox=(0.2, 0.25))

GAZE = {
    "licho": [(m("cut_x04"), le("X04") + 0.2, ("dir", 0.0, -0.9, 0.0)),                   # up: upstairs
              (m("cut_x20"), TL["total"], ("dir", 0.45, 0.05, 0.15))],                    # the new theory
    "wilcox": [(le("X14") + 0.1, le("X15") + 0.4, ("dir", 0.7, 0.3, 0.2))],                # looks away
}
EXPR = {
    "licho": [(m("cut_x08"), le("X08") + 0.4, -0.5, -0.2, 0.2), (m("cut_x20"), TL["total"], -0.75, -0.35, 0.2)],
    "jim": [(m("cut_x14"), le("X14") + 0.4, -0.6, -0.2, 0.15)],
    "wilcox": [(le("X14") + 0.1, le("X15") + 0.4, 0.6, -0.1, 0.1)],
    "omar": [(m("cut_x17"), le("X17") + 0.3, 0.3, -0.1, 0.25)],
}
LIDS = {"licho": [(m("cut_x20") + 0.6, TL["total"], 0.4, 0.25)]}
NODS = {"licho": [(wt("X06", "honest"), 1, 1.4)], "jim": [(wt("X16", "fine"), 1, 1.6)]}
TURN = {}
FORCED = {"wilcox": [le("X15") + 0.3], "jim": [le("X18") + 0.3]}
NOBLINK = {"jim": [(ls("X14"), le("X14") + 0.4)], "licho": [(m("cut_x20") + 0.4, TL["total"])]}
SHAKES = {"licho": [(ls("X08") + 0.2, 1, 0.08)]}
REST = dict(licho="reporter", jim="wilcox", omar="jim", wilcox="jim")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, shakes=SHAKES)
