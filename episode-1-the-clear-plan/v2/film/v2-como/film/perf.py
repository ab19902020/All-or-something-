"""The acting for Leeds, Como and the plan (see studio/film/perf.py for every table).

  The office  the three of them watch the screen; at the whistle Wilcox looks to Martínez (caught), Martínez narrows
              his eyes at him, Berrada looks at nobody.
  Carrick     deliberately calm at the briefing; at the click he looks at the pen, then at the players; small and
              embarrassed for "That wasn't it."; firmer at half-time, then mildly irritated; on the touchline still;
              after the match he sees the documentary camera; in the press room, controlled frustration, then a
              breath, and he hears himself.
  Bruno       genuinely asking; probing; suspicious; on the pitch he looks to the bench; he reads the board twice;
              looks round the room; drained after the match; in the mixed zone tired, not gleeful, and he looks back
              towards the dressing-room door.
  Maguire     completely sincere: "Is there a signal?"
  Zirkzee     an arm up for the goal; he sees the scoreboard."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["carrick", "bruno", "maguire", "licho", "mainoo", "zirkzee", "wilcox", "omar", "cunha"]   # cunha last: the
# others' blinks are seeded by their place in this list and stay as they were
SPK = {w: w for w in WHO}

META = {
    "C05": ("calm", "bruno", ["compact", "play", "front"]),
    "C06": ("honest", "carrick", ["when", "go"]),
    "C07": ("calm", "bruno", ["moment", "right"]),
    "C08": ("innocent", "carrick", ["signal"]),
    "C09": ("awkward", "licho", ["wasn't"]),
    "C12": ("firm", "bruno", ["need", "braver"]),
    "C13": ("concerned", "carrick", ["go", "them"]),
    "C14": ("firm", "bruno", ["together"]),
    "C15": ("disbelieving", "carrick", ["everyone"]),
    "C16": ("irritated", "bruno", ["usually", "together"]),
    "C22": ("exhausted", "bruno", ["ideal"]),
    "C23": ("exhausted", "carrick", ["michael", "used"]),
    "C25": ("dry", "reporter", ["told", "not", "press", "honestly", "executed"]),
    "C26": ("defensive", "reporter", ["tactics", "staff", "not", "me"]),
    "C41": ("indignant", "carrick", ["forty", "michael", "five"]),
    "C42": ("flat", "cunha", ["tactical", "decision"]),
    "C43": ("angry", "carrick", ["one", "came", "off", "lost"]),
    "C44": ("honest", "carrick", ["fair", "point"]),
    "C45": ("dry", "maguire", ["thanks", "harry"]),
    "C46": ("sarcastic", "carrick", ["warm", "everybody", "time"]),
    "C28": ("frustrated", "reporter", ["draw", "arrows", "carry", "eleven"]),
    "C29": ("quiet", "reporter", ["review"]),
    "C31": ("salesman", "cam", ["very", "clear", "plan"]),
}
BASE = dict(carrick=(-0.05, -0.05), bruno=(-0.15, -0.1), maguire=(0.15, 0.05), licho=(-0.1, 0.0), mainoo=(0.0, 0.0),
            zirkzee=(0.0, 0.0), wilcox=(0.2, 0.25), omar=(0.1, 0.15), cunha=(0.0, 0.0))

SCREEN = ("dir", 0.0, -0.08, 0.0)                # the telly: where the camera is, a little up
office = (m("cut_office"), m("cut_lake"))
GAZE = {
    "licho": [(office[0], m("whistle") + 0.3, SCREEN), (m("whistle") + 0.3, office[1], "wilcox"),
              (m("cut_go"), m("cut_g1"), ("dir", -0.6, 0.0, -0.2))],
    "wilcox": [(office[0], m("whistle") + 0.15, SCREEN), (m("cut_wi_sees") + 0.25, m("cut_brush"), "licho"),
               (m("cut_brush"), office[1], ("dir", 0.1, 0.8, 0.0)), (m("cut_bd"), ls("C31"), ("dir", 0.2, 0.55, 0.05))],
    "omar": [(office[0], office[1], SCREEN)],
    "carrick": [(m("cut_c09") + 0.05, m("cut_c09") + 0.55, ("dir", -0.2, 0.85, -0.05)),     # the pen...
                (m("cut_c09") + 0.55, ls("C09"), "licho"),                                  # ...the players
                (m("cut_touch"), m("cut_board_ht"), ("dir", 0.35, -0.05, 0.12)),             # the pitch
                (m("cut_ck_board"), m("cut_br_ck"), "board"),
                (m("cut_push"), m("cut_g5"), ("dir", 0.3, -0.05, 0.1)),
                (m("cut_sees") + 0.35, m("cut_par1"), "cam")],                              # the documentary camera
    "bruno": [(m("cut_br_ck"), m("cut_g4"), ("dir", -0.7, 0.05, -0.25)),                     # at Carrick
              (m("cut_par1"), ls("C25"), ("dir", -0.25, 0.3, -0.08)),
              (m("look_back"), ls("C26") + 0.3, ("dir", 0.85, 0.0, 0.32))],                 # back to the door
    "zirkzee": [(m("cut_zz"), m("cut_zz") + 0.9, "cam"), (m("cut_zz") + 0.9, m("cut_ft"), ("dir", 0.5, -0.45, 0.15))],
}
EXPR = {
    "wilcox": [(m("whistle"), m("cut_wi_sees") + 0.2, 0.4, 0.5, 0.15),                    # the tiny clap
               (m("cut_wi_sees") + 0.25, m("cut_brush"), 0.8, -0.15, 0.08),              # caught
               (m("cut_bd"), m("cut_laptop"), 0.3, 0.4, 0.4)],
    "licho": [(m("whistle") + 0.3, office[1], -0.7, -0.3, 0.2)],
    "omar": [(m("whistle") + 0.4, office[1], 0.3, -0.05, 0.3)],
    "carrick": [(m("cut_c09"), ls("C09"), 0.5, -0.2, 0.15),
                (m("cut_touch"), m("cut_board_ht"), -0.1, -0.2, 0.4),
                (m("cut_ck_board"), m("cut_br_ck"), -0.3, -0.3, 0.3),
                (m("cut_push"), m("cut_g5"), -0.2, -0.3, 0.3),
                (m("cut_sees") + 0.35, m("cut_par1"), 0.45, -0.25, 0.15),
                (le("C29") + 0.3, m("cut_corr"), 0.55, -0.15, 0.4)],                     # he hears himself
    "bruno": [(m("cut_br_ck"), m("cut_g4"), -0.4, -0.3, 0.2),
              (m("cut_par1"), ls("C25"), 0.15, -0.35, 0.4)],
    "maguire": [(m("cut_c08m") - 0.1, le("C08") + 0.4, 0.55, 0.05, 0.2)],
    "zirkzee": [(m("cut_zz"), m("cut_zz") + 0.9, 0.4, 0.45, 0.15), (m("cut_zz") + 1.0, m("cut_ft"), 0.4, -0.3, 0.2)],
}
LIDS = {"licho": [(m("whistle") + 0.3, office[1], 0.35, 0.2)],
        "bruno": [(le("C22"), le("C23") + 0.3, 0.28, 0.3), (m("cut_par1"), ls("C25"), 0.25, 0.4)],
        "carrick": [(m("cut_touch"), m("cut_board_ht"), 0.15, 0.3), (le("C28"), le("C29") + 0.3, 0.2, 0.3)]}
NODS = {"carrick": [(wt("C05", "compact") + 0.05, 1, 1.5), (wt("C14", "together"), 1, 2.0)],
        "bruno": [(wt("C25", "executed"), 1, 1.4)],
        "wilcox": [(le("C31") - 0.3, 1, 1.6)]}
TURN = {"carrick": [(m("cut_c09") + 0.05, m("cut_c09") + 0.55, 0.0, -2.0)],
        "maguire": [(ls("C08") - 0.1, le("C08") + 0.3, 0.0, 4.0)],
        "bruno": [(ls("C15") - 0.05, le("C15") + 0.3, 0.0, -3.5)]}
FORCED = {"carrick": [le("C09") + 0.35, le("C29") + 0.9], "bruno": [le("C23") + 0.4],
          "wilcox": [m("cut_wi_sees") + 0.5]}
NOBLINK = {"carrick": [(m("cut_sees") + 0.3, m("cut_par1"))], "licho": [(m("cut_li_eyes"), m("cut_omar"))]}
SHAKES = {"bruno": [(le("C23") - 0.4, 1, 0.08)]}
REST = dict(carrick="bruno", bruno="carrick", maguire="carrick", licho="carrick", mainoo="carrick",
            zirkzee="carrick", wilcox=SCREEN, omar=SCREEN, cunha="carrick")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, shakes=SHAKES)
