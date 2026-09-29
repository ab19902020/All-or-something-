"""The shot list for Episode 1, "Three Midfielders": every cut, camera move, set-up and on-screen text, keyed to the
dialogue edit (timeline.py).

Two kinds of shot:
  * single - one character in close-up / medium close-up. Layers: the set behind him (a boardroom plate, blurred:
    shallow depth of field), the character (placed on screen by his eyes and eye distance), and a table edge in the
    foreground cut from a plate's own table (so everyone reads as seated at the same table).
  * world  - several characters placed in a plate (1x plate px) with the plate's own furniture in front of them.
Eyelines follow the seating in the wide shot (see EYES): Carrick at the head of the table under the tactics screen,
Bruno beside him, Jim further down the same side, Jason and Omar at the far end opposite Carrick."""
import math
import json
from timeline import TL
LN = json.load(open("build/lines.json"))

T_END = TL["total"]


def m(k): return TL["marks"][k]
def ls(k): return TL["lines"][k]["start"]
def le(k): return TL["lines"][k]["end"]


PLATES = {"EXT": "carrington-entrance", "W": "boardroom-wide", "T": "tactics-room-screen",
          "V": "boardroom-window-view", "S": "boardroom-side-view", "M": "monaco-office"}

# things in front of the actors (1x plate px polygons)
OCCL = {
    "T": {"table": [[(0, 1214), (100, 1180), (200, 1147), (300, 1137.5), (470, 1135), (600, 1136), (700, 1141),
                     (800, 1154), (900, 1174), (941, 1186), (941, 1672), (0, 1672)]]},
    "V": {"table": [[(0, 851), (200, 761), (604, 755), (941, 969), (941, 1260), (0, 1260)]]},
    "W": {"table": [[(474, 758), (941, 734), (941, 1672), (0, 1672), (0, 977)]],
          "fgchair": [[(62, 1225), (80, 1188), (130, 1170), (360, 1164), (600, 1166), (640, 1180), (656, 1214),
                       (660, 1672), (58, 1672)],
                      [(878, 1335), (896, 1302), (941, 1298), (941, 1672), (868, 1672)]]},
    "M": {"coffee": [[(0, 1168), (120, 1172), (205, 1190), (252, 1232), (252, 1310), (205, 1356), (0, 1398)],
                     [(0, 1330), (392, 1330), (396, 1672), (0, 1672)]]},
}

# ---------------------------------------------------------------- singles: the set-up behind / in front of each one
# bg = (plate, cx, cy, zoom, blur px); fg = (plate, mask, cx, table-edge y in the plate, zoom, blur px)
SET = {
    "ck": dict(bg=("T", 470, 690, 1.85, 5.0), fg=("T", "table", 470, 1136, 2.6, 2.0)),
    "js": dict(bg=("V", 505, 430, 1.9, 6.0), fg=("V", "table", 420, 758, 3.1, 2.5)),
    "om": dict(bg=("V", 150, 400, 1.95, 6.0), fg=("V", "table", 380, 758, 3.1, 2.5)),
    "br": dict(bg=("S", 175, 470, 1.9, 6.0), fg=("T", "table", 330, 1140, 2.6, 2.0)),
    "jr": dict(bg=("W", 255, 470, 2.0, 6.0), fg=("V", "table", 300, 760, 3.1, 2.5)),
}
# the main drawing for each character's single
MAIN = {"ck": "ck_front", "js": "js_hero", "om": "om_hero", "br": "br_hero", "jr": "jr_hero"}

# gaze in each character's single: screen direction (x: -1 left .. 1 right, y: + down) and head turn towards
# each other character, from the seating (see the module docstring)
EYES = {
    "ck": dict(br=(-1.0, 0.05, -0.45), jr=(0.2, -0.95, 0.1), js=(-0.3, 0.1, -0.08), om=(0.45, 0.1, 0.15)),
    "br": dict(ck=(0.95, 0.0, 0.45), js=(-0.7, 0.08, -0.2), om=(-0.35, 0.08, -0.1), jr=(0.85, -0.6, 0.35)),
    "js": dict(ck=(0.05, -0.05, 0.0), om=(-1.0, 0.05, -0.45), br=(0.4, 0.0, 0.12), jr=(0.2, -0.7, 0.05)),
    "om": dict(ck=(0.15, -0.05, 0.05), js=(1.0, 0.05, 0.45), br=(0.45, 0.0, 0.15), jr=(0.1, -0.7, 0.05)),
    "jr": dict(ck=(0.8, 0.0, 0.3), br=(1.0, 0.05, 0.4), js=(-0.5, 0.05, -0.15), om=(-0.3, 0.05, -0.1)),
}


def wt(lid, word, k=1):
    """timeline time of the k-th occurrence of a word in a line"""
    n = 0
    for w in LN[lid]["words"]:
        if w["w"] == word:
            n += 1
            if n == k: return ls(lid) + w["s"]
    raise KeyError(word)


def single(t, who, draw=None, ed=140.0, eye=(540, 660), table=4.6, push=(1.0, 1.04), drift=1.0, grade="board",
           bg=None, fg=None, quiet=0.0, lean=None, punch=None):
    """one character on screen: eye = where the point between his eyes goes, ed = his eye distance (screen px),
    table = the table edge's distance below the eyes in eye distances, push = scale at the shot's start / end"""
    s = SET[who]
    return dict(t=t, kind="single", who=who, draw=draw or MAIN[who], ed=ed, eye=eye, table=table, push=push,
                drift=drift, grade=grade, bg=bg or s["bg"], fg=fg if fg is not None else s["fg"], quiet=quiet,
                punch=punch)


# ---------------------------------------------------------------- world shots
# actors: (who, drawing, (x, y) 1x plate px of the eyes / head centre, eye distance in plate px, mirror)
# sized to sit in the plate's own chairs: shoulders fill the chair, the head rises above the backrest, and
# nearer chairs get bigger people (Carrick in the chair at the head of the table, 153 px wide; Bruno in the next
# chair along the left side; Jim in the near-left chair; Jason and Omar with their backs to camera at the near end)
WIDE_FAR = [("ck", "ck_front", (712, 664), 25.0, False),
            ("br", "br_q34l", (420, 700), 26.0, False)]          # Jim's chair is empty: he is on the TV
WIDE_NEAR = [("js", "js_back", (330, 1030), 72.0, False),
             ("om", "om_back", (842, 1046), 72.0, False)]
# the three-shot is a portrait lineup (stage px at zoom 1): Omar, Jason, Jim side by side behind the table
EXECS = [("om", "om_hero", (196, 912), 71.0, False),
         ("js", "js_hero", (542, 900), 74.0, False)]
EXEC_MONITOR = ((880, 905), 372)            # Jim on a monitor on the table: screen centre and width (stage px)
MONACO = [("jr", "jr_hero", (312, 688), 49.0, False)]


def world(t, plate, cam0, cam1=None, layers=(), grade="board", drift=0.6, blur=0.0, ease="inout", cams=None):
    """layers: ("actors", [...]) or ("occl", name), composited in order (far actors, the table, near actors, ...).
    cams: optional [(t, (cx, cy, z)), ...] keyframes instead of cam0 -> cam1"""
    return dict(t=t, kind="world", plate=plate, cam0=cam0, cam1=cam1 or cam0, layers=list(layers), grade=grade,
                drift=drift, blur=blur, ease=ease, cams=cams)


def group(t, actors, cams, table_y, bg=("V", 505, 430, 1.55, 5.0), fg=("V", "table", 420, 758, 2.4, 2.0),
          grade="board", drift=0.5):
    """several characters composited like a single (blurred set behind, table edge in front); cams: [(t, (stage x,
    stage y, zoom))] - the stage point at the centre of the frame; table_y: the table edge in stage px"""
    return dict(t=t, kind="group", actors=actors, cams=cams, table_y=table_y, bg=bg, fg=fg, grade=grade, drift=drift,
                monitor=None)


def card(t, kind):
    return dict(t=t, kind=kind)


W_LAYERS = [("screen", "tv"), ("actors", WIDE_FAR), ("occl", "table"), ("actors", WIDE_NEAR), ("occl", "fgchair")]
TV_SHOT = [("screen", "tv")]                # a close shot of the boardroom TV (Jim on the call)

MCU, CU = 180.0, 222.0          # eye distance of a medium close-up / close-up (screen px)
SHOTS = [
    # 00:00 Carrington exterior: slow cinematic push, grey Manchester, big white text
    dict(world(0.0, "EXT", (470, 836, 1.0), (470, 800, 1.13), grade="grey", drift=0.3), text="ext"),
    # 00:03 boardroom wide: all at the table, slow push towards Carrick
    world(m("cut_wide"), "W", (470, 800, 1.0), (706, 734, 2.0), W_LAYERS),
    single(m("cut_js1"), "js", ed=MCU),                                           # Sorted.
    single(m("cut_ck1"), "ck", ed=MCU),                                           # Brilliant. (relieved)
    single(m("cut_js2"), "js", ed=MCU, push=(1.0, 1.03)),                         # We bought three midfielders.
    single(m("cut_ck2"), "ck", ed=CU, eye=(520, 700), table=4.4, push=(1.0, 1.05)),   # close-up: blink, head move
    single(m("cut_om1"), "om", draw="om_g_explain", ed=128, eye=(560, 620), table=5.0, push=(1.0, 1.03)),
    single(m("cut_js3"), "js", draw="js_g_three", ed=130, eye=(600, 620), table=5.0, push=(1.0, 1.02),
           punch=(wt("js_three_things", "technically"), 1.14)),                   # three fingers; snap on "technically"
    single(m("cut_ck3"), "ck", ed=190, push=(1.0, 1.09), drift=0.5),              # slowly looks into the lens, holds
    single(m("cut_om5"), "om", ed=MCU, push=(1.0, 1.03),
           punch=(wt("om_positions", "no"), 1.18)),                               # "...No." (snap in on it)
    single(m("cut_br1"), "br", ed=CU, eye=(540, 700), table=4.3, push=(1.0, 1.05)),   # Bruno realises
    single(m("cut_js_nod"), "js", ed=MCU),                                        # Jason nods proudly
    single(m("cut_ck4"), "ck", ed=MCU, push=(1.0, 1.0)),                          # Look, I'm not complaining...
    single(m("ck_lean"), "ck", ed=192, eye=(520, 670), push=(1.0, 1.08)),         # leans forward: who's scoring the GOALS?
    single(m("cut_om2"), "om", ed=MCU),                                           # Bruno.
    dict(single(m("cut_br2"), "br", ed=CU, eye=(540, 700), table=4.3), whip=True),    # whip: Sorry... what?
    single(m("cut_om3"), "om", draw="om_g_explain", ed=128, eye=(560, 620), table=5.0, push=(1.0, 1.04)),
    single(m("cut_br3"), "br", draw="br_g_shrug", ed=132, eye=(540, 620), table=4.9, push=(1.0, 1.03)),
    single(m("cut_js4"), "js", draw="js_g_point", ed=134, eye=(660, 620), table=4.22),     # Bruno. (points)
    single(m("cut_br4"), "br", ed=205, eye=(540, 700), table=4.2, push=(1.0, 1.04),
           punch=(ls("br_me") + 0.02, 1.16)),                                     # ME? (snap) I'm taking the corner!
    single(m("cut_ck5"), "ck", ed=190),                                           # trying not to react
    single(m("cut_br5"), "br", draw="br_g_talk", ed=132, eye=(540, 620), table=4.9),      # I'm a MIDFIELDER
    single(m("cut_js5"), "js", ed=MCU),                                           # Perfect... loads of midfielders
    single(m("cut_br9"), "br", ed=CU, eye=(540, 700), table=4.3, push=(1.0, 1.02), drift=0.4,
           punch=(wt("br_brilliant", "absolutely"), 1.1)),                        # "Brilliant. Absolutely brilliant."
    single(m("cut_ck6"), "ck", ed=MCU),                                           # And the left-back?
    single(m("cut_js6"), "js", ed=MCU, punch=(wt("js_luke", "luke"), 1.12)),       # We've got... LUKE.
    single(m("cut_ck7"), "ck", ed=185, push=(1.0, 1.16)),                         # Luke? For the WHOLE season?
    single(m("cut_js7"), "js", ed=192, push=(1.0, 1.05)),                         # freezes... Next question.
    single(m("cut_br6"), "br", ed=192, eye=(540, 670)),                           # sinks back into his chair
    world(m("cut_jr1"), "W", (724, 425, 3.75), (724, 425, 3.95), TV_SHOT, drift=0.5),   # on the TV: bigger issues
    world(m("cut_wide2"), "W", (560, 640, 1.35), (560, 636, 1.42), W_LAYERS),     # everyone turns to the TV
    single(m("cut_br7"), "br", ed=205, eye=(540, 690), push=(1.0, 1.08), drift=0.4),   # Jim... you live in Monaco.
    world(m("cut_jr2"), "W", (724, 425, 3.8), (724, 425, 4.3), TV_SHOT, drift=0.3),    # silence... the glitch
    world(m("cut_monaco"), "M", (320, 830, 1.35), (300, 752, 2.0), [("actors", MONACO), ("occl", "coffee")],
          grade="monaco", drift=0.4),                                             # HARD CUT TO MONACO
    single(m("cut_ck8"), "ck", ed=MCU),                                           # smash cut: Right, so no striker?
    single(m("cut_om4"), "om", ed=MCU),                                           # No striker.
    single(m("cut_ck9"), "ck", ed=186),                                           # No left-back?
    single(m("cut_js8"), "js", ed=MCU),                                           # No left-back.
    single(m("cut_ck10"), "ck", ed=186, push=(1.0, 1.06)),                        # looks between them: But THREE?
    dict(group(m("cut_execs"), EXECS, table_y=1232,                               # the three of them nod
          cams=[(m("cut_execs"), (540, 1010, 1.0)), (ls("js_three_mids") + 0.02, (542, 905, 1.85)),
                (m("om_line") + 0.08, (206, 915, 1.85)), (m("jr_nod") - 0.02, (880, 905, 1.95))]),
         monitor=EXEC_MONITOR),
    single(m("cut_br8"), "br", ed=CU, eye=(540, 700), table=4.3, push=(1.0, 1.08), quiet=1.0),   # the button
    card(m("cut_black"), "black"),
    card(m("cut_title"), "title"),                                                # ALL OR SOMETHING
]
for i, s in enumerate(SHOTS):
    s["end"] = SHOTS[i + 1]["t"] if i + 1 < len(SHOTS) else T_END
    s["i"] = i

# documentary captions: (start, end, kind, text 1, text 2). "name" = lower third on a character's first single,
# "place" = location slug, "stats" = the transfer tally
CAPTIONS = [
    (m("cut_wide") + 0.2, m("cut_js1") - 0.05, "place", "THE BOARDROOM", "Carrington, 10:47pm"),
    (m("cut_ck2") + 0.25, m("cut_om1") - 0.05, "name", "MICHAEL CARRICK", "Head Coach"),
    (m("cut_om1") + 0.15, m("cut_js3") - 0.05, "name", "OMAR BERRADA", "Chief Executive"),
    (m("cut_js3") + 0.15, m("cut_ck3") - 0.05, "name", "JASON WILCOX", "Technical Director"),
    (m("cut_br1") + 0.2, m("cut_js_nod") - 0.05, "name", "BRUNO FERNANDES", "Club Captain"),
    (m("cut_jr1") + 0.3, m("cut_wide2") - 0.05, "name", "SIR JIM RATCLIFFE", "Co-Owner. Joining remotely."),
    (m("cut_monaco") + 0.15, m("cut_ck8"), "place", "MONACO", "800 miles from Carrington"),
    (ls("js_three_mids") - 0.1, m("cut_br8"), "stats", "", ""),
    (m("cut_black") + 0.3, m("cut_title"), "epilogue", "The transfer window closed at 11pm.", ""),
    (m("cut_black") + 1.25, m("cut_title"), "epilogue2", "", "No striker was signed."),
]
# Jim's virtual background breaks up, then shows Monaco, in the last second before the cut to Monaco
GLITCH = (m("cut_jr2") + 0.35, m("cut_monaco"))

# fast cuts for the whip (Bruno "Sorry... what?") and smash (back from Monaco)
WHIPS = [m("cut_br2")]
SMASH = [m("cut_ck8"), m("cut_monaco")]


def shot_at(t):
    for s in reversed(SHOTS):
        if t >= s["t"] - 1e-9: return s
    return SHOTS[0]


def ease(u, kind="inout"):
    u = min(1.0, max(0.0, u))
    if kind == "inout": return u * u * (3 - 2 * u)
    if kind == "out": return 1 - (1 - u) ** 2
    return u
