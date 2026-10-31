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
    "A15": ("calm", "bruno", ["next", "straight", "me"]),
    "A16": ("deadpan_happy", "carrick", ["move", "jason"]),
    "A17": ("firm", "room", ["surprise", "standards", "inspection"]),
    "A18": ("annoyed", "gary", ["gary", "ofsted"]),
    "G01": ("deadpan", "wilcox", ["no", "worse"]),
    "G02": ("firm", "carrick", ["manager", "hairdryer"]),
    "G03": ("confused", "gary", ["what"]),
    "G04": ("dry", "carrick", ["played", "hairdryer", "laptop"]),
    "G05": ("firm", "bruno", ["captain"]),
    "G06": ("deadpan", "bruno", ["there", "is"]),
    "G07": ("flat", "board", ["one", "two", "three", "photo", "course"]),
    "A19": ("firm", "room", ["who's", "charge"]),
    "A20": ("awkward", "gary", ["collaborative", "structure"]),
    "G08": ("dry", "wilcox", ["united", "manager", "doorway"]),
    "A21": ("flat", "clip", ["special", "measures"]),
    "G09": ("deadpan", "clip", ["handshake", "limp"]),
}
BASE = dict(carrick=(-0.05, -0.05), bruno=(-0.12, -0.08), wilcox=(0.2, 0.3), gary=(0.0, -0.1))

GAZE = {
    "carrick": [(wt("A01", "jason"), wt("A01", "crew") + 0.6, "wilcox"),                    # he notices
                (m("cut_gary"), m("cut_look"), "gary"),
                (m("cut_look"), m("cut_a15"), "bruno")],
    "bruno": [(0.0, wt("A01", "crew") + 0.6, "table"),                                     # hasn't looked up
              (wt("A05", "jason") - 0.1, le("A05") + 0.2, "wilcox"),
              (m("cut_door"), m("cut_a06"), ("dir", 0.0, -0.1, 0.0)),                    # past him, into the room
              (m("cut_gary"), m("cut_look"), "gary"),
              (m("cut_arms"), m("cut_g06"), "gary"),
              (m("cut_look"), m("cut_a15"), "carrick")],
    "wilcox": [(wt("A01", "jason") - 0.1, m("cut_a02"), "cam"),                              # beckoning the camera
               (m("cut_door"), m("cut_a06"), "cam"),                                       # smiling, blocking
               (m("cut_card2"), m("cut_gary"), "cam"),
               (m("cut_point") + 0.35, m("cut_point") + 0.75, ("dir", -0.55, 0.45, -0.12)),   # one finger...
               (m("cut_point") + 0.75, m("cut_point") + 1.15, ("dir", 0.55, 0.45, 0.12)),    # ...the other
               (m("cut_point") + 1.15, m("cut_a20"), "cam")],
    "gary": [(m("cut_g01"), le("G01") + 0.3, "cam"),                                       # to the lens
             (m("cut_g05"), m("cut_g07"), "bruno"),
             (m("cut_g07"), wt("G07", "photo"), "board"),
             (wt("G07", "photo") + 0.1, le("G07") + 0.3, "cam"),                           # the look to the crew
             (m("cut_write"), m("cut_a21") + 0.2, "clip"),
             (m("cut_g09"), TL["total"], "clip")],
}
EXPR = {
    "bruno": [(m("cut_door"), m("cut_a06"), 0.7, -0.45, 0.08),                      # getting past him
              (m("cut_smile"), m("cut_tick"), 0.2, 0.55, 0.15),
              (m("cut_arms"), m("cut_g06"), 0.75, -0.4, 0.05),                       # arms up: outraged
              (m("cut_look"), m("cut_a15"), 0.3, 0.2, 0.15), (m("cut_a16"), le("A16") + 0.4, 0.15, 0.5, 0.2)],
    "carrick": [(le("A10") - 0.6, m("cut_smile"), 0.1, 0.3, 0.2), (m("cut_g03"), le("G03") + 0.3, 0.6, -0.1, 0.1),
                (m("cut_look"), m("cut_a15"), 0.3, 0.2, 0.15)],
    "wilcox": [(m("cut_door"), m("cut_a06"), 0.05, 0.75, 0.08),                     # the fixed smile
               (m("cut_card2"), m("cut_gary"), 0.1, 0.7, 0.1),
               (m("cut_a18"), le("A18") + 0.3, -0.5, 0.45, 0.15),
               (m("cut_point") + 0.3, m("cut_a20"), 0.6, -0.25, 0.12),
               (m("cut_a20"), le("A20") + 0.3, 0.75, -0.3, 0.1)],
    "gary": [(m("cut_g01"), le("G01") + 0.4, -0.15, 0.15, 0.1),                      # a little pleased with that
             (m("cut_g06"), le("G06") + 0.3, -0.2, 0.25, 0.1),
             (m("cut_a21"), le("A21") + 0.4, -0.2, -0.1, 0.3),
             (m("cut_g09"), TL["total"], -0.25, -0.15, 0.2)],
}
LIDS = {"gary": [(m("cut_write"), m("cut_a21"), 0.55, 0.2), (m("cut_g09"), TL["total"], 0.5, 0.2)]}
NODS = {"carrick": [(wt("A10", "progress"), 1, 0.9)],
        "bruno": [(wt("A07", "telly"), 1, 1.2)],
        "gary": [(wt("A21", "measures"), 1, 1.4), (wt("G06", "is"), 1, 1.0)]}
TURN = {}
FORCED = {"carrick": [le("A04") + 0.3], "bruno": [le("A09") + 0.3], "wilcox": [le("A20") + 0.3]}
NOBLINK = {"wilcox": [(m("cut_card2"), m("cut_gary"))], "bruno": [(m("cut_arms"), m("cut_g06"))]}
SHAKES = {"bruno": [(ls("A09") + 0.4, 1, 0.06)], "gary": [(ls("A19"), 1, 0.05)]}
REST = dict(carrick="bruno", bruno="carrick", wilcox="cam", gary="room")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, shakes=SHAKES)


# Carrick is understated: in the portrait close-ups his head barely moves (a third of the idle sway, half the nods
# and turns), the stillness the rest of All or Something plays him with
_head = PERF.head


def _calm_head(w, t):
    tilt, nod, turn = _head(w, t)
    if w == "carrick":
        return 0.33 * tilt, 0.5 * nod, 0.5 * turn
    return tilt, nod, turn


PERF.head = _calm_head
