"""The acting for Hull and the month, beat by beat (see studio/film/perf.py for every table).

  Carrick   calm at the board before Hull; "Not ideal" flat; "It's one game" reasonable; pleased for one line at
            Ipswich; dry with Martínez; the smallest genuine smile of the episode after Sabah; "Not..." stopped dead,
            the mouth closed, held; to the documentary camera, diplomatic, and then nothing else to offer.
  Bruno     shouting from the touchline at Hull; indignant in the dressing room; proud at Ipswich; firm after City
            and Brighton; a list of numbers at Fulham.
  Maguire   dead sincere: "Set pieces. Got it.", "Execution?", helpful to Šeško, proud of expected goals.
  Cunha     proud of the captain; trying not to smile about his own finish.
  Šeško     delighted, then put in his place: he looks anywhere but at Harry.
  Martínez  proud of his goal (to the lens); defensive after City.
  Wilcox    the salesman, every time.
  The room  after Hull nobody looks at anybody; the silence before "Execution?" and the turn after "expected goals":
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
    "H02": ("explaining", "maguire", ["newly", "crowd", "basics", "importantly", "set", "pieces"]),
    "H03": ("matter", "carrick", ["set", "got"]),
    "H06": ("angry", "pitch", ["come", "wake", "concentrate"]),
    "H08": ("angry", "pitch", ["easy", "too"]),
    "H10": ("flat", "bruno", ["ideal"]),
    "H11": ("angry", "carrick", ["ideal", "literally", "set", "five", "kick"]),
    "H12": ("matter", "bruno", ["two", "set"]),
    "H13": ("indignant", "maguire", ["how", "conceded", "two"]),
    "H14": ("innocent", "bruno", ["execution"]),
    "H15": ("calm", "bruno", ["one", "judge", "season"]),
    "R02": ("proud", "bruno", ["hat", "captain"]),
    "R03": ("pleased", "cunha", ["more", "like"]),
    "R04": ("salesman", "carrick", ["gentlemen", "fantastic", "plan"]),
    "R07": ("energised", "carrick", ["yes", "thought", "winner"]),
    "R08": ("helpful", "sesko", ["did", "eight"]),
    "R09": ("flat", "maguire", ["thanks"]),
    "R10": ("positive", "sesko", ["positive", "away", "home"]),
    "R13": ("proud", "cam", ["scored"]),
    "R14": ("dry", "licho", ["encourage"]),
    "R15": ("salesman", "carrick", ["european", "dna"]),
    "R18": ("defensive", "bruno", ["nearly"]),
    "R19": ("firm", "licho", ["nearly", "not"]),
    "R20": ("helpful", "bruno", ["counts", "expected"]),
    "R21": ("innocent", "bruno", ["what", "listening", "jason"]),
    "R26": ("dry", "lacey", ["learnt", "quickly"]),
    "R27": ("firm", "carrick", ["michael", "not", "ideal"]),
    "R28": ("restrained", "bruno", ["not"]),
    "R31": ("awkward", "licho", ["good", "mine", "sorry"]),
    "R32": ("frustrated", "carrick", ["five", "five", "out", "cup"]),
    "R33": ("motivational", "bruno", ["right", "international", "away", "reset", "fresh"]),
    "R35": ("diplomatic", "producer", ["positives"]),
    "R37": ("deadpan", "producer", ["sabah"]),
}
BASE = dict(carrick=(-0.1, -0.05), bruno=(-0.2, -0.1), maguire=(0.1, 0.05), cunha=(0.1, 0.2), sesko=(0.0, 0.05),
            licho=(-0.1, 0.0), mount=(-0.1, 0.0), mainoo=(0.0, 0.0), wilcox=(0.2, 0.35))

DOWN = "down"
AWAY_SE = ("dir", -0.65, 0.35, -0.22)             # Šeško, anywhere but at Harry

dr0, dr1 = m("cut_dr"), m("cut_ck1") + 0.4        # after Hull: nobody looks at anybody
silence = (le("H13") + 0.2, ls("H14") + 0.1)
turn = (m("cut_turn") + 0.15, m("cut_mg4") + 0.4)

GAZE = {
    "carrick": [(m("cut_talk"), ls("H02"), "board"), (dr0, dr1, DOWN), (silence[0] + 0.2, silence[1], "maguire"),
                (turn[0] + 0.25, turn[1], "maguire"), (m("cut_int"), m("cut_cal"), "producer")],
    "bruno": [(dr0, dr1, ("dir", 0.3, 0.6, 0.1)), (silence[0], silence[1], "maguire"),
              (turn[0], turn[1], "maguire"), (m("cut_ips_wide"), m("cut_cu1"), "cam"),
              (m("cut_br1"), ls("H06"), "pitch"), (m("cut_br2"), ls("H08"), "pitch")],
    "maguire": [(dr0, dr1, ("dir", -0.2, 0.7, -0.05)), (silence[0] + 0.4, ls("H14"), ("dir", 0.4, -0.35, 0.1)),
                (turn[0] + 0.5, turn[1], "carrick"), (le("H03"), m("cut_m1"), "carrick")],
    "cunha": [(dr0, dr1, DOWN), (silence[0] + 0.1, silence[1], "maguire"), (turn[0] + 0.1, turn[1], "maguire"),
              (m("cut_ips_wide"), m("cut_cu1"), "bruno")],
    "mainoo": [(dr0, dr1, DOWN), (silence[0] + 0.3, silence[1], "maguire"), (turn[0] + 0.3, turn[1], "maguire")],
    "licho": [(turn[0] + 0.05, turn[1], "maguire"), (m("cut_talk"), ls("H02") + 2.0, "carrick")],
    "sesko": [(le("R08") - 0.3, m("cut_sab"), AWAY_SE)],
    "mount": [],
    "wilcox": [],
}
EXPR = {
    "carrick": [(dr0, dr1 + 0.3, -0.3, -0.25, 0.4),                                  # Hull: grim
                (le("R03") - 0.2, m("cut_wi1") + 0.5, 0.15, 0.3, 0.3),               # that's more like it
                (m("cut_ck_smile") + 0.35, m("cut_city"), 0.2, 0.45, 0.6),           # the smallest smile
                (le("R26"), ls("R28"), 0.45, -0.25, 0.2),                            # what to say to the boy
                (le("R28") + 0.05, m("cut_ful"), -0.15, -0.3, 0.2),                  # he closes his mouth
                (le("R37") + 0.1, m("cut_cal"), 0.3, -0.05, 0.5)],                   # nothing else
    "bruno": [(m("cut_ips_wide"), m("cut_cu1") + 2, 0.35, 0.6, 0.2),                  # the hat-trick
              (silence[0], silence[1], 0.6, -0.3, 0.2),
              (m("cut_br1"), le("H06") + 0.3, -0.5, -0.45, 0.1),
              (m("cut_br2"), le("H08") + 0.3, -0.6, -0.5, 0.1),
              (m("cut_li2"), ls("R19"), -0.3, -0.25, 0.3)],
    "maguire": [(le("H03"), m("cut_m1"), 0.25, 0.4, 0.2),                             # he has got it
                (silence[0] + 0.4, ls("H14"), 0.55, -0.05, 0.3),                     # thinking
                (le("R08"), m("cut_sab"), 0.35, 0.5, 0.2),                           # genuinely helping
                (le("R20"), m("cut_mg4"), 0.25, 0.45, 0.2)],                         # proud of it
    "cunha": [(m("cut_ips_wide"), le("R02") + 0.5, 0.3, 0.55, 0.2),
              (ls("R31") - 0.2, le("R31") + 0.4, 0.15, 0.4, 0.2)],                    # trying not to smile
    "sesko": [(le("R08"), m("cut_sab"), 0.1, -0.35, 0.2)],
    "licho": [(m("cut_li1"), le("R13") + 0.4, 0.3, 0.55, 0.2)],
    "wilcox": [(m("cut_wi1"), le("R04") + 1.0, 0.4, 0.55, 0.3)],
}
NODS = {"carrick": [(wt("H15", "season") + 0.05, 1, 1.4), (le("R33") - 0.25, 1, 1.6),
                    (wt("H02", "basics"), 1, 1.4)],
        "bruno": [(m("cut_ips_wide") + 0.5, 2, 2.0)],
        "maguire": [(le("H03") - 0.2, 2, 2.0), (le("R08") - 0.15, 2, 1.6), (ls("H04") + 0.3, 1, 1.4)],
        "wilcox": [(le("R04") - 0.3, 2, 1.8), (le("R15") - 0.2, 1, 2.0)]}
TURN = {"maguire": [(silence[0] + 0.4, ls("H14"), 0.0, 4.0)],
        "sesko": [(le("R08") - 0.2, m("cut_sab"), 0.0, -3.0)],
        "carrick": [(le("R37") + 0.3, m("cut_cal"), 0.0, 1.5)]}
LIDS = {"carrick": [(dr0, dr1, 0.25, 0.4), (ls("R14") - 0.1, le("R14") + 0.2, 0.22, 0.2),
                    (le("R28") + 0.2, m("cut_ful"), 0.2, 0.4)],
        "wilcox": [(le("R15") + 0.05, m("cut_tab2"), 0.25, 0.3)]}
FORCED = {"carrick": [le("H10") + 0.2, le("R28") + 0.45, le("R37") + 0.9],
          "maguire": [le("H12") + 0.5, le("R20") + 0.4],
          "bruno": [le("H11") + 0.1],
          "sesko": [le("R09") + 0.3]}
NOBLINK = {"carrick": [(ls("R28"), le("R29") + 0.2), (ls("R37"), le("R37") + 0.6)],
           "maguire": [(ls("H14") - 0.6, le("H14") + 0.2)]}
SHAKES = {"bruno": [(wt("H11", "ideal") + 0.05, 1, 0.12), (wt("H06", "concentrate"), 1, 0.12)]}
MOUTH = {"carrick": [(le("R28") + 0.02, le("R28") + 0.28, "AI", 0.35, 0.03)]}     # "Not..." then it closes
REST = dict(carrick="bruno", bruno="carrick", maguire="carrick", cunha="carrick", sesko="carrick", licho="carrick",
            mount="carrick", mainoo="carrick", wilcox="carrick")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, mouth=MOUTH, shakes=SHAKES)
