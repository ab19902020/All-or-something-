"""The acting for Bournemouth (see studio/film/perf.py for every table).

  Bruno     reads the sheet twice; quietly wounded: "My name is not on here."; then hears his own words back.
  Carrick   flat for "pure football"; bone-dry for "That one's not on me."; on the touchline still while they sing,
            then they boo; in the row he tries twice, gets one word out.
  The row   everyone at everyone: Maguire at the room, Martínez at Maguire, Cunha at Carrick, Šeško at the ceiling,
            Mount at Šeško, Bruno at nobody; then all of them at Carrick."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["carrick", "bruno", "maguire", "cunha", "mainoo", "sesko", "licho", "mount"]
SPK = {w: w for w in WHO}

META = {
    "B02": ("concerned", "carrick", ["name", "not"]),
    "B03": ("flat", "bruno", ["pure", "football"]),
    "B04": ("indignant", "carrick", ["because", "said"]),
    "B05": ("dry", "bruno", ["staff", "not", "me"]),
    "B11": ("angry", "licho", ["who", "rayan"]),
    "B12": ("indignant", "maguire", ["bench"]),
    "B13": ("angry", "carrick", ["minutes", "not", "these"]),
    "B14": ("frustrated", "licho", ["everyone", "calm"]),
    "B15": ("angry", "sesko", ["nobody's", "calm", "ben"]),
    "B16": ("angry", "mount", ["calm"]),
    "B17": ("defensive", "carrick", ["playing"]),
    "B18": ("angry", "bruno", ["start", "upstairs", "said", "upstairs"]),
    "B19": ("indignant", "licho", ["television"]),
    "B20": ("indignant", "cunha", ["so", "did", "i"]),
    "B21": ("angry", "bruno", ["know", "bruno"]),
    "B22": ("firm", "maguire", ["enough", "enough"]),
    "B23": ("awkward", "bruno", ["look"]),
    "B24": ("awkward", "bruno", ["not"]),
    "B25": ("angry", "carrick", ["don't"]),
}
BASE = dict(carrick=(-0.05, -0.05), bruno=(-0.15, -0.1), maguire=(0.15, 0.05), cunha=(0.0, 0.0), mainoo=(0.0, 0.0),
            sesko=(0.05, 0.0), licho=(-0.1, 0.0), mount=(0.1, 0.05))

GAZE = {
    "bruno": [(m("cut_look"), m("cut_g1"), ("dir", -0.15, 0.25, -0.05))],
    "carrick": [(m("cut_ft"), le("B10"), ("dir", 0.35, -0.15, 0.12)),
                (m("cut_end"), TL["total"], ("dir", 0.0, 0.05, 0.0))],
    "sesko": [(m("cut_b14"), le("B14"), ("dir", 0.0, -0.5, 0.0))],
}
everyone = (m("cut_quiet"), le("B24") + 0.1)
for w in ("bruno", "maguire", "cunha", "mainoo", "sesko", "licho", "mount"):
    GAZE.setdefault(w, []).append((everyone[0], everyone[1], "carrick"))
EXPR = {
    "bruno": [(m("cut_b05") + 0.2, m("cut_g1"), -0.45, -0.3, 0.15)],
    "carrick": [(m("cut_ft"), le("B10"), -0.25, -0.3, 0.3), (m("cut_end"), TL["total"], 0.6, -0.3, 0.1)],
    "maguire": [(m("cut_room"), le("B21"), -0.6, -0.35, 0.2)],
    "licho": [(m("cut_room"), le("B19"), -0.8, -0.4, 0.2)],
    "cunha": [(m("cut_room"), le("B19"), -0.7, -0.35, 0.2)],
}
LIDS = {"carrick": [(m("cut_ft"), le("B10"), 0.2, 0.3)]}
NODS = {"carrick": [(wt("B03", "football"), 1, 1.4)]}
TURN = {"bruno": [(ls("B02") - 0.1, le("B02") + 0.2, 0.0, -3.0)]}
FORCED = {"bruno": [le("B05") + 0.4], "carrick": [le("B25") + 0.2]}
NOBLINK = {"bruno": [(m("cut_look"), m("cut_g1"))], "carrick": [(m("cut_end"), TL["total"])]}
SHAKES = {"bruno": [(ls("B04") + 0.1, 1, 0.07)], "licho": [(ls("B18") + 0.3, 2, 0.1)]}
REST = dict(carrick="bruno", bruno="carrick", maguire="carrick", cunha="carrick", mainoo="carrick", sesko="carrick",
            licho="maguire", mount="sesko")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, shakes=SHAKES)
