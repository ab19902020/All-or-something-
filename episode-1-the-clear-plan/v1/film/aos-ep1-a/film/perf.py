"""The acting for part A, beat by beat (see studio/film/perf.py for every table).

  Carrick   never raises his voice: "Not ideal" flat; "It's one game" calm and reasonable; pleased for one line at
            Ipswich; dry with Martínez; the smallest genuine smile of the episode after Sabah; "Not..." stopped dead,
            the mouth closed, held; to the documentary camera, diplomatic, and then nothing else to offer.
  Bruno     indignant at Hull; proud at Ipswich (to the lens); firm after City and Brighton; a list of numbers at Fulham.
  Maguire   dead sincere: "Two set pieces", "Execution?", helpful to Šeško, proud of expected goals.
  Cunha     proud of the captain; trying not to smile about his own finish.
  Šeško     delighted, then put in his place: he looks anywhere but at Harry.
  Martínez  proud of his goal (to the lens); defensive after City; at Fulham he looks straight ahead.
  Wilcox    the salesman, every time.
  The room  at Hull nobody looks at anybody; the silence before "Execution?" and the turn after "expected goals":
            every head to Maguire."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["carrick", "bruno", "maguire", "cunha", "sesko", "licho", "mount", "mainoo", "wilcox"]
SPK = {w: w for w in WHO}

META = {
    "H01": ("flat", "bruno", ["ideal"]),
    "H02": ("angry", "carrick", ["ideal", "literally", "set", "five", "kickoff"]),
    "H03": ("matter", "bruno", ["two", "set"]),
    "H04": ("indignant", "maguire", ["how", "conceded", "two"]),
    "H05": ("innocent", "bruno", ["execution"]),
    "H06": ("calm", "bruno", ["one", "judge", "season"]),
    "R01": ("proud", "bruno", ["hat", "captain"]),
    "R02": ("pleased", "cunha", ["more", "like"]),
    "R03": ("salesman", "carrick", ["gentlemen", "fantastic", "plan"]),
    "R04": ("energised", "carrick", ["yes", "thought", "winner"]),
    "R05": ("positive", "sesko", ["positive", "away", "home"]),
    "R06": ("helpful", "sesko", ["did", "eight"]),
    "R07": ("flat", "maguire", ["thanks"]),
    "R08": ("proud", "cam", ["scored"]),
    "R09": ("dry", "licho", ["encourage"]),
    "R10": ("salesman", "carrick", ["european", "dna"]),
    "R11": ("defensive", "bruno", ["nearly"]),
    "R12": ("firm", "licho", ["nearly", "not"]),
    "R13": ("helpful", "bruno", ["counts", "expected"]),
    "R14": ("innocent", "bruno", ["what", "listening", "jason"]),
    "R15": ("confused", "carrick", ["two", "lost"]),
    "R16": ("dry", "lacey", ["learnt", "quickly"]),
    "R17": ("firm", "carrick", ["michael", "not", "ideal"]),
    "R18": ("restrained", "bruno", ["not"]),
    "R19": ("awkward", "licho", ["good", "mine", "sorry"]),
    "R20": ("frustrated", "carrick", ["five", "out", "cup"]),
    "R21": ("motivational", "bruno", ["right", "international", "away", "reset", "fresh"]),
    "R22": ("calm", "carrick", ["describe", "month"]),
    "R23": ("diplomatic", "producer", ["positives"]),
    "R24": ("calm", "carrick", ["such"]),
    "R25": ("deadpan", "producer", ["sabah"]),
    "N01": ("calm", "cam", []),
    "N02": ("calm", "cam", []),
}
BASE = dict(carrick=(-0.1, -0.05), bruno=(-0.2, -0.1), maguire=(0.1, 0.05), cunha=(0.1, 0.2), sesko=(0.0, 0.05),
            licho=(-0.1, 0.0), mount=(-0.1, 0.0), mainoo=(0.0, 0.0), wilcox=(0.2, 0.35))

DOWN = "down"
AWAY_SE = ("dir", -0.65, 0.35, -0.22)             # Šeško, anywhere but at Harry
AHEAD = ("dir", 0.08, 0.04, 0.0)                  # Martínez at Fulham: straight ahead

hull_end = m("cut_ck1")
silence = (le("H04") + 0.3, ls("H05") + 0.1)
turn = (m("cut_turn") + 0.15, m("cut_mg4") + 0.4)

GAZE = {
    # Hull: nobody looks at anybody; then the silence: every head to Maguire
    "carrick": [(0.0, hull_end, DOWN), (silence[0] + 0.2, silence[1], "maguire"), (turn[0] + 0.25, turn[1], "maguire"),
                (m("cut_int"), m("cut_cal"), "producer")],
    "bruno": [(0.0, hull_end, ("dir", 0.3, 0.6, 0.1)), (silence[0], silence[1], "maguire"),
              (turn[0], turn[1], "maguire"), (m("cut_ips_wide"), m("cut_cu1"), "cam")],
    "maguire": [(0.0, hull_end, ("dir", -0.2, 0.7, -0.05)), (silence[0] + 0.4, ls("H05"), ("dir", 0.4, -0.35, 0.1)),
                (turn[0] + 0.5, turn[1], "carrick")],
    "cunha": [(0.0, hull_end, DOWN), (silence[0] + 0.1, silence[1], "maguire"), (turn[0] + 0.1, turn[1], "maguire"),
              (m("cut_ips_wide"), le("R01"), "bruno")],
    "mainoo": [(0.0, hull_end, DOWN), (silence[0] + 0.3, silence[1], "maguire"), (turn[0] + 0.3, turn[1], "maguire")],
    "licho": [(m("cut_ful_li"), m("cut_ck_ful"), AHEAD), (turn[0] + 0.05, turn[1], "maguire"),
              (m("cut_sab_wide"), m("cut_li1"), "cam")],
    "sesko": [(le("R06") - 0.3, m("est_sab"), AWAY_SE)],
    "mount": [],
    "wilcox": [(m("cut_door"), m("cut_wi1"), "carrick")],
}
EXPR = {
    "carrick": [(0.0, hull_end, -0.3, -0.25, 0.4),                                   # Hull: grim
                (le("R02"), m("cut_door") + 0.5, 0.15, 0.3, 0.3),                    # that's more like it
                (m("cut_ck_smile") + 0.35, m("est_city"), 0.2, 0.45, 0.6),           # the smallest smile
                (m("cut_city_wide"), le("R14"), -0.2, -0.2, 0.3),                    # City: no smiles
                (le("R16"), ls("R18"), 0.45, -0.25, 0.2),                            # what to say to the boy
                (le("R18") + 0.05, m("est_ful"), -0.15, -0.3, 0.2),                  # he closes his mouth
                (le("R25") + 0.1, m("cut_cal"), 0.3, -0.05, 0.5)],                   # nothing else
    "bruno": [(m("cut_ips_wide"), m("cut_door"), 0.35, 0.6, 0.2),                     # the hat-trick
              (silence[0], silence[1], 0.6, -0.3, 0.2),
              (m("cut_city_wide"), ls("R12"), -0.3, -0.25, 0.3)],
    "maguire": [(silence[0] + 0.4, ls("H05"), 0.55, -0.05, 0.3),                      # thinking
                (le("R06"), m("est_sab"), 0.35, 0.5, 0.2),                            # genuinely helping
                (le("R13"), m("cut_mg4"), 0.25, 0.45, 0.2)],                          # proud of it
    "cunha": [(m("cut_ips_wide"), le("R01") + 0.5, 0.3, 0.55, 0.2),
              (ls("R19") - 0.2, le("R19") + 0.4, 0.15, 0.4, 0.2)],                     # trying not to smile
    "sesko": [(le("R06"), m("est_sab"), 0.1, -0.35, 0.2)],
    "licho": [(m("cut_sab_wide"), le("R08") + 0.4, 0.3, 0.55, 0.2),
              (m("cut_ful_li"), m("cut_ck_ful"), -0.2, -0.25, 0.3)],
    "wilcox": [(m("cut_door"), le("R03") + 1.0, 0.4, 0.55, 0.3)],
}
NODS = {"carrick": [(wt("H06", "season") + 0.05, 1, 1.4), (le("R21") - 0.25, 1, 1.6)],
        "bruno": [(m("cut_ips_wide") + 0.5, 2, 2.0)],
        "maguire": [(le("H03") - 0.2, 1, 2.0), (le("R06") - 0.15, 2, 1.6)],
        "wilcox": [(le("R03") - 0.3, 2, 1.8), (le("R10") - 0.2, 1, 2.0)]}
TURN = {"maguire": [(silence[0] + 0.4, ls("H05"), 0.0, 4.0)],
        "sesko": [(le("R06") - 0.2, m("est_sab"), 0.0, -3.0)],
        "carrick": [(le("R25") + 0.3, m("cut_cal"), 0.0, 1.5)]}
LIDS = {"carrick": [(0.0, hull_end, 0.25, 0.4), (ls("R09") - 0.1, le("R09") + 0.2, 0.22, 0.2),
                    (le("R18") + 0.2, m("est_ful"), 0.2, 0.4)],
        "licho": [(m("cut_ful_li"), m("cut_ck_ful"), 0.18, 0.3)],
        "wilcox": [(le("R10") + 0.05, m("cut_ck_smile"), 0.25, 0.3)]}
FORCED = {"carrick": [le("H01") + 0.2, le("R18") + 0.45, le("R25") + 0.9],
          "maguire": [le("H04") + 0.5, le("R13") + 0.4],
          "bruno": [le("H02") + 0.1],
          "sesko": [le("R07") + 0.3]}
NOBLINK = {"carrick": [(ls("R18"), le("R18") + 0.4), (ls("R25"), le("R25") + 0.8)],
           "maguire": [(ls("H05") - 0.6, le("H05") + 0.2)],
           "licho": [(m("cut_ful_li"), m("cut_cu2"))]}
SHAKES = {"bruno": [(wt("H02", "ideal") + 0.05, 1, 0.12)]}
MOUTH = {"carrick": [(le("R18") + 0.02, le("R18") + 0.28, "AI", 0.35, 0.03)]}     # "Not..." then it closes
REST = dict(carrick="bruno", bruno="carrick", maguire="carrick", cunha="carrick", sesko="carrick", licho="carrick",
            mount="carrick", mainoo="carrick", wilcox="carrick")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, mouth=MOUTH, shakes=SHAKES)
