"""The acting for Clear the Air (see studio/film/perf.py for every table).

  Carrick  understated: short pauses, tired patience, never a shout; at the start he notices Wilcox waving the camera
           in; sincere on "Maybe I could've been clearer"; a hint of warmth on "Progress"; he looks at the can, then at
           Jason; low and sincere on "come straight to me"; at the end, resigned.
  Bruno    direct and proud, not shouting: he hasn't looked up at the start; a glance back towards Jason on "standing
           in it"; softens; completely sincere on "the tactics were shit"; a tiny reluctant smile after "Progress";
           baffled at the can; a small smile on "Move Jason first".
  Wilcox   procedural confidence, a manager of appearances: he waves the camera closer, sprays with quiet pride, holds
           a fixed smile at Gary, and only "collaborative structure" betrays panic.
  Gary     a self-appointed inspector: brisk, then almost bored."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["carrick", "bruno", "wilcox", "gary"]
SPK = {w: w for w in WHO}

META = {
    "A02": ("firm", "bruno", ["problem", "tactics", "tell", "television"]),
    "A03": ("defensive", "carrick", ["tried", "door", "open"]),
    "A04": ("flat", "bruno", ["is"]),
    "A05": ("dry", "carrick", ["jason", "standing"]),
    "A06": ("honest", "bruno", ["maybe", "clearer"]),
    "A07": ("regretful", "carrick", ["shouldn't", "telly"]),
    "A08": ("hopeful", "bruno", ["right"]),
    "A09": ("honest", "carrick", ["yes", "still", "shit"]),
    "A10": ("dry", "bruno", ["aye", "indoors", "progress"]),
    "A11": ("confused", "wilcox", ["jason", "doing"]),
    "A12": ("proud", "carrick", ["clearing", "air", "agenda"]),
    "A13": ("deadpan", "wilcox", ["air", "freshener"]),
    "A14": ("proud", "cam", ["fresh", "start"]),
    "A15": ("calm", "bruno", ["next", "straight", "me"]),
    "A16": ("deadpan_happy", "carrick", ["move", "jason"]),
    "A17": ("firm", "room", ["surprise", "standards", "inspection"]),
    "A18": ("annoyed", "gary", ["gary", "ofsted"]),
    "A19": ("firm", "room", ["who's", "charge"]),
    "A20": ("awkward", "gary", ["collaborative", "structure"]),
    "A21": ("flat", "clip", ["special", "measures"]),
}
BASE = dict(carrick=(-0.05, -0.05), bruno=(-0.12, -0.08), wilcox=(0.2, 0.3), gary=(0.0, -0.1))

GAZE = {
    "carrick": [(wt("A01", "jason"), wt("A01", "crew") + 0.6, "wilcox"),                    # he notices
                (m("cut_a13"), wt("A13", "freshener"), "can"), (wt("A13", "freshener"), le("A13") + 0.3, "wilcox"),
                (m("cut_look"), m("cut_a15"), "bruno"),
                (m("cut_end"), TL["total"], ("dir", 0.15, 0.25, 0.05))],                     # resigned
    "bruno": [(0.0, wt("A01", "crew") + 0.6, "table"),                                     # hasn't looked up
              (wt("A05", "jason") - 0.1, le("A05") + 0.2, "wilcox"),
              (m("cut_a11"), le("A11") + 0.3, "wilcox"),
              (m("cut_look"), m("cut_a15"), "carrick"),
              (m("cut_end"), TL["total"], ("dir", -0.1, 0.25, -0.03))],
    "wilcox": [(wt("A01", "jason") - 0.1, m("cut_a02"), "cam"),                              # beckoning the camera
               (m("cut_door"), m("cut_a06"), ("dir", -0.15, 0.05, -0.05)),
               (m("cut_spray"), m("cut_a11"), ("dir", 0.5, -0.4, 0.15)),                     # up into the air
               (m("cut_card"), m("cut_gary"), "cam")],
    "gary": [(m("cut_write"), m("cut_a21") + 0.2, "clip")],
}
EXPR = {
    "bruno": [(m("cut_smile"), m("cut_tick"), 0.2, 0.55, 0.15), (m("cut_a16"), le("A16") + 0.4, 0.15, 0.5, 0.2),
              (m("cut_look"), m("cut_a15"), 0.55, -0.35, 0.15)],
    "carrick": [(le("A10") - 0.6, m("cut_smile"), 0.1, 0.3, 0.2), (m("cut_look"), m("cut_a15"), 0.5, -0.35, 0.15),
                (m("cut_end"), TL["total"], 0.2, -0.3, 0.3)],
    "wilcox": [(m("cut_spray"), m("cut_a11"), 0.3, 0.45, 0.3), (m("cut_a14"), le("A14") + 0.6, 0.35, 0.6, 0.15),
               (m("cut_a18"), le("A18") + 0.3, -0.5, 0.45, 0.15), (m("cut_a20"), le("A20") + 0.3, 0.75, -0.3, 0.1)],
    "gary": [(m("cut_a21"), le("A21") + 0.4, -0.2, -0.1, 0.3)],
}
LIDS = {"carrick": [(m("cut_end"), TL["total"], 0.3, 0.3)], "bruno": [(m("cut_end"), TL["total"], 0.25, 0.3)],
        "gary": [(m("cut_write"), m("cut_a21"), 0.55, 0.2)]}
NODS = {"carrick": [(wt("A10", "progress"), 1, 1.3), (wt("A15", "straight"), 1, 1.5)],
        "bruno": [(wt("A07", "telly"), 1, 1.2)], "wilcox": [(wt("A14", "start"), 1, 1.6)],
        "gary": [(wt("A21", "measures"), 1, 1.4)]}
TURN = {"bruno": [(ls("A11") - 0.25, le("A11"), 0.0, 4.0)]}
FORCED = {"carrick": [le("A04") + 0.3, le("A13") + 0.5], "bruno": [le("A09") + 0.3], "wilcox": [le("A20") + 0.3]}
NOBLINK = {"carrick": [(m("cut_point"), m("cut_a20"))], "bruno": [(m("cut_point"), m("cut_a20"))],
           "wilcox": [(m("cut_a14"), le("A14") + 0.6)]}
SHAKES = {"bruno": [(ls("A09") + 0.4, 1, 0.06)], "gary": [(ls("A19"), 1, 0.05)]}
REST = dict(carrick="bruno", bruno="carrick", wilcox="cam", gary="room")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, shakes=SHAKES)
