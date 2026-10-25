"""The acting, beat by beat: The Handover's (episodes/the-handover/film/perf.py) on the new lines.

  Carrick  arms crossed, waiting; ONE eyebrow up at "we backed you" and two slow blinks at Wilcox; controlled, then
           the rant (a head shake on every "No"), arms out; "Balanced?!" with his jaw left hanging; "It is what it
           is" with heavy lids and dropped shoulders; at the door, irritated, then indignant; the click: his eyes go
           to the door; Ole: his jaw drops; frozen through Ole's line; then he turns to us, lids heavy, and mutters
           the last line down the lens, no blink.
  Jim      cool and disappointed; "one more thing" pointing, polite smile, brows up; the standby mentioned like
           borrowing a stapler: cheery.
  Jason    leans in, smug, sure of it; blank during the rant.
  Omar     calm, polished, pleased with "balanced", a slow smug blink while the others look at the table.
  Ole      beaming; a wave and a nod; brows up on "standby"; a wink on "before"."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["jim", "jason", "omar", "carrick", "ole"]
SPK = {w: w for w in WHO}

META = {
    "K01": ("cool", "carrick", ["disappointed", "results", "expected", "decided", "last", "chance"]),
    "K02": ("smug", "carrick", ["frankly", "backed", "everything"]),
    "K03": ("restrained", "jason", ["know", "last", "something"]),
    "K04": ("angry", "jason", ["backed", "three", "bloody", "midfielders", "striker", "left", "defensive", "fuck",
                               "supposed"]),
    "K05": ("corporate", "carrick", ["felt", "balanced", "squad"]),
    "K06": ("disbelieving", "omar", ["balanced"]),
    "K07": ("resigned", "jim", ["know", "is"]),
    "K08": ("casual", "carrick", ["michael", "before", "more", "thing"]),
    "K09": ("irritated", "jim", ["what"]),
    "K10": ("cheery", "carrick", ["asked", "someone", "standby", "case"]),
    "K11": ("indignant", "jim", ["already", "someone"]),
    "K12": ("beaming", "carrick", ["hello", "michael"]),
    "K13": ("beaming", "carrick", ["worry", "only", "standby", "done", "before"]),
    "K14": ("bitter", "cam", ["got", "fucking", "joking"]),
}
TAGS = dict(cool=(0.1, -0.15), corporate=(0.25, 0.3), cheery=(0.45, 0.5), beaming=(0.4, 0.45),
            bitter=(0.12, -0.32))
BASE = dict(jim=(-0.1, -0.05), jason=(-0.15, 0.15), omar=(0.05, 0.2), carrick=(-0.1, -0.05), ole=(0.2, 0.05))

DOOR = ("dir", 0.9, -0.04, 0.12)
TO_JIM = ("dir", -0.25, 0.0, -0.04)

GAZE = {
    "carrick": [(ls("K02") + 0.2, ls("K03"), "jason"),
                (m("cut_omar") + 0.15, m("cut_balanced"), "omar"),
                (m("cut_balanced"), m("cut_resign"), "omar"),
                (m("cut_door1") - 0.3, m("cut_door3") + 0.05, TO_JIM),
                (m("cut_door3") + 0.05, m("click") + 0.08, TO_JIM),
                (m("click") + 0.08, m("stop"), DOOR),
                (m("stop"), m("look"), "ole"),
                (m("look"), TL["total"], "cam")],
    "jim": [(m("cut_omar") + 0.45, m("cut_balanced") + 0.4, "down")],
    "jason": [(m("cut_omar") + 0.7, m("cut_balanced") + 0.4, ("dir", -0.35, 0.8, -0.05))],
    "omar": [],
    "ole": [(m("stop"), TL["total"], "carrick")],
}
EXPR = {
    "carrick": [(m("open") + 0.2, ls("K02"), -0.15, -0.1, 0.4),
                (wt("K02", "we") + 0.05, ls("K03") - 0.05, 0.75, -0.2, 0.15),
                (wt("K03", "i'm"), le("K03"), -0.45, -0.15, 0.25),
                (wt("K04", "what") - 0.1, le("K04"), 0.55, -0.45, 0.15),
                (le("K06"), m("cut_resign"), 1.0, -0.3, 0.06),
                (le("K07"), m("cut_door1"), 0.1, -0.3, 0.2),
                (ls("K09") - 0.05, le("K09") + 0.2, -0.75, -0.3, 0.08),
                (le("K11"), m("click"), 0.55, -0.35, 0.2),
                (m("click") + 0.05, m("stop"), 0.65, -0.15, 0.12),
                (m("stop") + 0.08, m("look"), 0.95, -0.35, 0.1),
                (m("look"), ls("K14"), 0.05, -0.3, 0.35)],
    "jim": [(le("K01"), m("cut_jason1") + 0.6, -0.1, -0.1, 0.3),
            (wt("K08", "before") - 0.1, le("K08"), 0.5, 0.35, 0.2),
            (le("K10"), m("cut_door3") + 0.5, 0.4, 0.45, 0.2)],
    "jason": [(wt("K04", "defensive") - 0.3, ls("K05"), 0.3, -0.05, 0.2),
              (ls("K05"), m("cut_balanced") + 0.3, 0.05, 0.1, 0.3)],
    "omar": [(wt("K04", "defensive") - 0.3, ls("K05"), 0.15, 0.2, 0.2),
             (le("K05"), m("cut_balanced") + 0.3, 0.2, 0.45, 0.2)],
    "ole": [(m("stop"), ls("K12"), 0.5, 0.5, 0.12),
            (wt("K13", "only") - 0.05, we("K13", "standby") + 0.2, 0.7, 0.45, 0.1),
            (wt("K13", "i've") - 0.05, le("K13") + 0.4, 0.55, 0.6, 0.15)],
}
BROWX = {"carrick": [(wt("K02", "we") + 0.05, ls("K03") - 0.05, 0.45, 0.12)],
         "ole": [(wt("K13", "i've") - 0.05, le("K13") + 0.4, -0.25, 0.15)]}
NODS = {"omar": [(wt("K05", "balanced") + 0.05, 1, 2.6)],
        "jim": [(le("K01") - 0.35, 1, 1.8), (wt("K10", "case"), 1, 1.6)],
        "jason": [(le("K02") - 0.2, 2, 1.8)],
        "ole": [(m("stop") + 0.05, 1, 2.4), (le("K13") + 0.05, 1, 2.0)],
        "carrick": [(ls("K06") - 0.02, 1, -3.0),
                    (wt("K14", "joking"), 1, 1.4)]}
SHAKES = {"carrick": [(wt("K04", "no", 1) + 0.02, 2, 0.16), (wt("K04", "no", 2) + 0.02, 2, 0.16),
                      (wt("K04", "no", 3) + 0.02, 2, 0.14), (wt("K07", "it", 1), 2, 0.10)]}
TURN = {"carrick": [(m("click") + 0.08, m("stop"), 0.18, 0.0),
                    (wt("K02", "we") + 0.1, ls("K03") - 0.1, 0.0, 3.0),
                    (wt("K04", "what") - 0.1, le("K04"), 0.0, -2.5)],
        "ole": [(m("stop"), ls("K12") + 0.6, 0.0, 4.0), (wt("K13", "i've"), le("K13") + 0.4, 0.0, -3.5)],
        "jim": [(wt("K10", "someone"), le("K10"), 0.0, 3.0)]}
BODY = {"jason": [(ls("K02") - 0.25, le("K02") + 0.2, 0.7, 0.0, 0.35)],
        "carrick": [(wt("K03", "seeing"), le("K03"), 0.35, 0.0, 0.5),
                    (ls("K07") - 0.05, m("rise"), 0.0, 0.3, 0.45),
                    (ls("K11"), le("K11") + 0.3, 0.3, 0.0, 0.15)]}
LIDS = {"carrick": [(wt("K01", "disappointed"), wt("K01", "the"), 0.18, 0.3),
                    (wt("K03", "i'm"), le("K03") + 0.1, 0.18, 0.2),
                    (ls("K07") + 0.2, m("cut_door1"), 0.38, 0.35),
                    (m("look") + 0.1, TL["total"], 0.36, 0.45)],
        "omar": [(le("K05") + 0.05, m("cut_balanced"), 0.3, 0.25)],
        "jim": [(wt("K01", "decided"), le("K01"), 0.12, 0.3)]}
MOUTH = {"carrick": [(le("K06") + 0.03, m("cut_resign"), "O", 0.95, 0.07),
                     (m("stop") + 0.12, m("cut_ole1"), "O", 0.9, 0.1),
                     (m("cut_last"), m("look") - 0.05, "O", 0.3, 0.05)]}
WINK = {"ole": [(wt("K13", "before") + 0.06, "L", 0.22)]}
FORCED = {"carrick": [le("K02") + 0.12, le("K02") + 0.48, le("K07") + 0.05, m("cut_what") + 0.32],
          "jim": [le("K01") + 0.15], "jason": [wt("K04", "defensive") + 0.25], "omar": [le("K05") + 0.35],
          "ole": [m("cut_ole1") + 0.5]}
NOBLINK = {"carrick": [(m("cut_balanced"), m("cut_resign")), (m("cut_rant"), wt("K04", "three")),
                       (m("stop"), m("cut_ole1")), (m("cut_last"), TL["total"])],
           "ole": [(wt("K13", "before") - 0.3, le("K13") + 0.5)]}
REST = dict(jim="carrick", jason="carrick", omar="carrick", carrick="jim", ole="carrick")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, body=BODY, forced=FORCED, noblink=NOBLINK, tags=TAGS,
                   rest_target=REST, cuts=[s["t"] for s in SHOTS], lids=LIDS, wink=WINK, browx=BROWX, mouth=MOUTH,
                   shakes=SHAKES)
