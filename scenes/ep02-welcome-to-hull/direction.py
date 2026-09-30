"""The shot list for Episode 2, "Welcome to Hull": every cut, camera move, set-up and on-screen text, keyed to the
dialogue edit (timeline.py).

Kinds of shot:
  * single - one character close: the set behind (a dressing-room plate, blurred: shallow depth of field), the
    character (placed on screen by his eyes and eye distance), and in front of the seated players the edge of the
    dressing-room table cut from the plate's own table. Props and moves per shot: Steve's clipboard, Harry's
    raised hand, Bruno standing up, Carrick's clap and his exit.
  * world  - characters placed in a plate (1x plate px) with the plate's own furniture in front of them; an actor
    can move and change drawing on keyframes (Carrick's walk to the wrong door and back).
  * group  - a portrait lineup of the seated players (blurred set behind, the table edge in front).
  * cards  - the full-time score, the match flashes, black, the title, the Tigers ending.
Where everyone is: before the game Carrick stands at the tactics board (screen right), Steve beside him (on his
right, screen left of him); the players sit on the bench behind the table (screen left of Steve), Kobbie at the
far end, apart from them. After the game Carrick is back in exactly the same spot, behind the counter, Steve beside
him; the players sit round the room, Kobbie across it. So in the singles the players look screen right to Carrick
and Steve, Carrick and Steve look screen left to the players, and Carrick and Steve look at each other."""
import json
from timeline import TL
LN = json.load(open("build/lines.json"))

T_END = TL["total"]


def m(k): return TL["marks"][k]
def ls(k): return TL["lines"][k]["start"]
def le(k): return TL["lines"][k]["end"]


def wt(lid, word, k=1):
    """timeline time of the k-th occurrence of a word in a line"""
    n = 0
    for w in LN[lid]["words"]:
        if w["w"] == word:
            n += 1
            if n == k: return ls(lid) + w["s"]
    raise KeyError(word)


def we(lid, word, k=1):
    """timeline time the k-th occurrence of a word ends"""
    n = 0
    for w in LN[lid]["words"]:
        if w["w"] == word:
            n += 1
            if n == k: return ls(lid) + w["e"]
    raise KeyError(word)


PLATES = {"EXT": "hull-stadium-exterior", "PRE": "hull-away-dressing-room-pre-match",
          "POST": "hull-away-dressing-room-post-match", "PITCH": "hull-pitch-corner", "DOOR": "door-store-cupboard"}

# things in front of the actors (1x plate px polygons)
OCCL = {
    "PRE": {"table": [[(300, 764), (706, 764), (852, 978), (852, 1004), (836, 1252), (190, 1252), (170, 1004),
                       (170, 978)],
                      [(558, 752), (702, 752), (702, 772), (558, 772)]]},       # the table, the bottle crate on it
    "POST": {"counter": [[(0, 668), (330, 672), (590, 742), (592, 1075), (0, 1075)],
                         [(12, 625), (72, 625), (72, 672), (12, 672)], [(212, 622), (242, 622), (242, 674), (212, 674)],
                         [(248, 650), (268, 650), (268, 674), (248, 674)], [(276, 650), (300, 650), (300, 674), (276, 674)],
                         [(368, 668), (408, 668), (408, 702), (368, 702)], [(410, 690), (447, 690), (447, 745), (410, 745)]]},
}

# ---------------------------------------------------------------- singles: the set behind / in front of each one
# bg = (plate, cx, cy, zoom, blur px); fg = (plate, mask, cx, table-edge y in the plate, zoom, blur px) or None
SET = {
    # before the game
    "ck": dict(bg=("PRE", 790, 585, 2.5, 4.5), fg=None),                 # the tactics board behind him
    "sh": dict(bg=("PRE", 640, 575, 2.6, 5.0), fg=None),                 # the lockers, the board's edge
    "br": dict(bg=("PRE", 420, 565, 2.8, 5.5), fg=("PRE", "table", 470, 764, 3.0, 3.0)),
    "mg": dict(bg=("PRE", 530, 565, 2.8, 5.5), fg=("PRE", "table", 560, 764, 3.0, 3.0)),
    "mn": dict(bg=("PRE", 118, 585, 2.6, 5.5), fg=("PRE", "table", 380, 764, 3.0, 3.0)),   # off on his own
    # after the game
    "ck_post": dict(bg=("POST", 352, 445, 2.4, 5.0), fg=("POST", "counter", 300, 672, 2.6, 3.0)),
    "sh_post": dict(bg=("POST", 470, 450, 2.4, 5.0), fg=("POST", "counter", 380, 690, 2.6, 3.0)),
    "br_post": dict(bg=("POST", 690, 470, 2.6, 5.5), fg=("POST", "counter", 240, 672, 2.8, 3.5)),
    "mg_post": dict(bg=("POST", 860, 470, 2.6, 5.5), fg=("POST", "counter", 120, 672, 2.8, 3.5)),
    "mn_post": dict(bg=("POST", 130, 470, 2.5, 5.5), fg=("POST", "counter", 420, 700, 2.8, 3.5)),   # across the room
    # the match
    "pitch": dict(bg=("PITCH", 470, 300, 2.2, 6.0), fg=None),
}
MAIN = {"ck": "ck_front", "sh": "sh_hero", "br": "br_hero", "mg": "mg_hero", "mn": "mn_hero"}

# gaze in each character's single: screen direction (x: -1 left .. 1 right, y: + down) and head turn towards
# each other character, from where they are (see the module docstring)
EYES = {
    "ck": dict(sh=(-0.85, 0.0, -0.35), br=(-0.8, 0.1, -0.3), mg=(-0.7, 0.1, -0.25), mn=(-1.0, 0.05, -0.45),
               board=(0.9, -0.1, 0.4)),
    "sh": dict(ck=(0.85, 0.0, 0.35), br=(-0.7, 0.1, -0.25), mg=(-0.6, 0.1, -0.2), mn=(-0.9, 0.05, -0.35)),
    "br": dict(ck=(0.85, -0.12, 0.35), sh=(0.7, -0.12, 0.25), mg=(0.45, 0.05, 0.15), mn=(0.95, 0.0, 0.4)),
    "mg": dict(ck=(0.8, -0.12, 0.3), sh=(0.65, -0.12, 0.22), br=(-0.5, 0.05, -0.18), mn=(0.9, 0.0, 0.35)),
    "mn": dict(ck=(0.9, -0.1, 0.35), sh=(0.8, -0.1, 0.3), br=(-0.3, 0.05, -0.1), mg=(-0.2, 0.05, -0.08)),
}


def single(t, who, draw=None, ed=180.0, eye=(540, 700), table=4.5, push=(1.0, 1.04), drift=1.0, grade="room",
           set_=None, bg=None, fg=None, punch=None, **extra):
    """one character on screen: eye = where the point between his eyes goes, ed = his eye distance (screen px),
    table = the table edge's distance below the eyes in eye distances, push = scale at the shot's start / end"""
    s = SET[set_ or who]
    d = dict(t=t, kind="single", who=who, draw=draw or MAIN[who], ed=ed, eye=eye, table=table, push=push,
             drift=drift, grade=grade, bg=bg or s["bg"], fg=fg if fg is not None else s["fg"], punch=punch)
    d.update(extra)
    return d


# ---------------------------------------------------------------- world shots
# actors: (who, drawing, (x, y) 1x plate px of the eyes / head centre, eye distance in plate px, mirror)
# Before the game, sized by the room: a hanging shirt is ~110 px wide at the back wall, so a seated player's
# shoulders fill a locker; Carrick and Steve stand at the board (their heads at two thirds of its height).
PRE_SQUAD = [("sl", "sl_hero", (330, 652), 22.0, False), ("bs", "bs_hero", (410, 650), 22.0, False),
             ("br", "br_hero", (490, 652), 22.0, False), ("mg", "mg_hero", (570, 650), 22.5, False)]
PRE_MAINOO = [("mn", "mn_hero", (682, 655), 21.5, False)]                 # at the far end, on his own
PRE_STAFF = [("sh", "sh_hero", (790, 612), 22.0, False), ("ck", "ck_front", (872, 606), 22.0, False)]
PRE_LAYERS = [("actors", PRE_SQUAD + PRE_MAINOO), ("occl", "table"), ("actors", PRE_STAFF)]
# after the game: Carrick and Steve behind the counter at the board, Harry and Bruno from behind in the foreground
POST_STAFF = [("ck", "ck_front", (352, 416), 21.0, False), ("sh", "sh_hero", (470, 410), 21.0, False)]
POST_BACKS = [("mg", "mg_back", (170, 1330), 62.0, False), ("br", "br_back", (760, 1310), 60.0, False)]
POST_LAYERS = [("actors", POST_STAFF), ("occl", "counter"), ("actors", POST_BACKS)]

# the lineups (stage px at zoom 1): the seated players side by side behind the table
LINE_PRE = [("mn", "mn_hero", (150, 905), 84.0, False), ("br", "br_hero", (530, 900), 88.0, False),
            ("mg", "mg_hero", (900, 895), 88.0, False)]
LINE_POST = [("mg", "mg_hero", (175, 900), 88.0, False), ("br", "br_hero", (545, 905), 88.0, False),
             ("mn", "mn_hero", (910, 900), 84.0, False)]


def world(t, plate, cam0, cam1=None, layers=(), grade="room", drift=0.6, blur=0.0, ease="inout", cams=None, **extra):
    """layers: ("actors", [...]) or ("occl", name), composited in order (far actors, the table, near actors, ...).
    cams: optional [(t, (cx, cy, z)), ...] keyframes instead of cam0 -> cam1"""
    d = dict(t=t, kind="world", plate=plate, cam0=cam0, cam1=cam1 or cam0, layers=list(layers), grade=grade,
             drift=drift, blur=blur, ease=ease, cams=cams)
    d.update(extra)
    return d


def group(t, actors, cams, table_y=None, bg=("PRE", 470, 575, 1.7, 5.0), fg=("PRE", "table", 470, 764, 2.4, 2.5),
          grade="room", drift=0.5, **extra):
    """several characters composited like a single (blurred set behind, table edge in front); cams: [(t, (stage x,
    stage y, zoom))] - the stage point at the centre of the frame; table_y: the table edge in stage px"""
    d = dict(t=t, kind="group", actors=actors, cams=cams, table_y=table_y, bg=bg, fg=fg, grade=grade, drift=drift,
             monitor=None)
    d.update(extra)
    return d


def card(t, kind, **extra):
    d = dict(t=t, kind=kind); d.update(extra); return d


# ---------------------------------------------------------------- moving actors
# Carrick strides off to the wrong door: left, across the back of the room behind the table, past the players;
# nobody follows. (t, drawing, (x, y), ed, mirror) keys, a walk bob while he moves, his shadow on the floor
def walk_off():
    t0 = m("cut_walk")
    return {"who": "ck", "bob": 1.0, "shadow": 1.0,
            "keys": [(t0, "ck_walk", (872, 610), 22.0, True), (t0 + 1.25, "ck_walk", (500, 624), 22.0, True)]}


# at the store cupboard (the door plate: 1x px, the door at x 12-108 with its sign on the left half, plain wall to
# x 210, the floor at y 287; Carrick sized by the door, 1.8 m to its 2 m): he marches in from the right and stops,
# faces it and reads it, turns and looks at everyone (back the way he came), then walks off that way
def at_the_door():
    t0 = m("cut_ck7")
    return {"who": "ck", "shadow": 1.0, "bob": 1.0,
            "keys": [(t0, "ck_walk", (196, 98), 18.7, True), (t0 + 0.34, "ck_walk", (112, 98), 18.7, True),
                     (t0 + 0.36, "ck_back", (104, 87), 17.0, False), (t0 + 0.68, "ck_front", (104, 97), 18.7, False),
                     (t0 + 1.14, "ck_walk", (104, 98), 18.7, False), (t0 + 1.80, "ck_walk", (250, 98), 18.7, False)],
            "still": [(t0 + 0.34, t0 + 1.14)]}         # no bob while he stands


MCU, CU = 180.0, 222.0          # eye distance of a medium close-up / close-up (screen px)
ST = 150.0                      # the standing medium shots (Carrick at the board, Steve with the clipboard)
SHOTS = [
    # 00:00 MKM Stadium: slow documentary push, HULL / OPENING DAY
    dict(world(0.0, "EXT", (470, 836, 1.0), (470, 760, 1.14), grade="sunny", drift=0.3), text="ext"),
    # 00:04 the away dressing room before the game: slow push towards Carrick at the board
    world(m("cut_room_wide"), "PRE", (470, 820, 1.0), (700, 700, 1.6), PRE_LAYERS),
    # Carrick points at the board: "Hull have just come up..."
    single(m("cut_ck_board"), "ck", draw="ck_g_point", ed=80, eye=(330, 760), table=0, push=(1.0, 1.07)),
    single(m("cut_sh1"), "sh", ed=ST, eye=(540, 640), push=(1.0, 1.03), clipboard=True),      # looks up from it
    single(m("cut_ck2"), "ck", ed=ST, eye=(560, 640), push=(1.0, 1.02)),                       # Already did. Thursday.
    single(m("cut_sh2"), "sh", ed=ST, eye=(540, 640), push=(1.0, 1.03), clipboard=True),      # That was attacking corners.
    single(m("cut_ck3"), "ck", ed=162, eye=(560, 650), push=(1.0, 1.06)),                      # the board... Steve... same corner?
    single(m("cut_br1"), "br", ed=CU, eye=(540, 720), table=4.3, push=(1.0, 1.06), drift=0.4),   # Bruno: into the lens
    single(m("cut_ck4"), "ck", ed=ST, eye=(600, 640)),                                         # Kobbie... you're on the bench
    single(m("cut_mn1"), "mn", ed=MCU, eye=(540, 700), push=(1.0, 1.03)),                      # Again?
    single(m("cut_ck5"), "ck", ed=ST, eye=(600, 640), push=(1.0, 1.02)),                       # We've bought midfielders.
    single(m("cut_mn2"), "mn", ed=196, eye=(540, 700), push=(1.0, 1.04)),                      # I noticed.
    single(m("cut_br2"), "br", draw="br_g_shrug", ed=132, eye=(540, 640), table=4.9, push=(1.0, 1.03)),   # nine of us
    single(m("cut_mg1"), "mg", ed=MCU, eye=(540, 700), push=(1.0, 1.03)),                      # play striker?
    # silence: the players slowly turn to Carrick; he pretends not to notice... then claps
    group(m("cut_wide2"), LINE_PRE, cams=[(m("cut_wide2"), (530, 1010, 1.0)), (m("cut_wide2") + 1.1, (540, 1000, 1.04))],
          table_y=1330),
    single(m("cut_ck6"), "ck", ed=ST, eye=(560, 640), push=(1.0, 1.02), clap=m("clap")),       # ...COME ON!
    world(m("cut_walk"), "PRE", (640, 720, 1.3), (600, 715, 1.32),
          [("actors", PRE_SQUAD + PRE_MAINOO + [walk_off()]), ("occl", "table"), ("actors", PRE_STAFF[:1])]),
    single(m("cut_sh3"), "sh", ed=ST, eye=(540, 640), push=(1.0, 1.03), clipboard=True),      # Michael... wrong door.
    world(m("cut_ck7"), "DOOR", (90, 150, 1.30), (92, 146, 1.34), [("actors", [at_the_door()])], drift=0.5),
    # 00:37 SMASH CUT: full time. The score, then the narrator over the two corners and the two goals, then the
    # Hull fans' chant over the reactions
    card(m("cut_score"), "score"),
    card(ls("nar_knew") - 0.05, "corner", n=1),
    card(we("nar_knew", "coming") - 0.35, "goal", n=1),
    card(m("flash2") - 0.02, "corner", n=2),
    card(m("chant"), "goal", n=2),
    single(m("chant") + 1.15, "ck", ed=150, eye=(560, 660), set_="pitch", push=(1.0, 1.05), grade="pitch",
           drift=0.3),                                                                            # Carrick on the touchline
    single(m("chant") + 2.55, "mg", ed=190, eye=(540, 760), set_="pitch", push=(1.0, 1.04), grade="pitch",
           table=0),                                                                              # Harry: lost
    single(m("chant") + 3.85, "br", draw="br_g_celebrate", ed=180, eye=(540, 1010), set_="pitch", push=(1.0, 1.06),
           grade="pitch", table=0, shake=True),                                                   # Bruno shouting
    # 00:48 hard cut back inside: total silence, the room wrecked, nobody moves
    world(m("cut_post_wide"), "POST", (470, 700, 1.02), (420, 560, 1.35), POST_LAYERS, drift=0.25),
    group(m("cut_silence"), LINE_POST, cams=[(m("cut_silence"), (540, 1000, 1.0)), (m("cut_silence") + 0.5, (540, 995, 1.02))],
          table_y=1330, bg=("POST", 760, 470, 1.8, 5.5), fg=("POST", "counter", 300, 672, 2.4, 3.0)),  # nobody speaks
    single(m("cut_br3"), "br", ed=MCU, eye=(540, 700), set_="br_post"),                          # Bruno looks up
    single(m("cut_sh4"), "sh", ed=ST, eye=(540, 640), set_="sh_post", clipboard=True, table=5.7),           # Excellent.
    single(m("cut_br4"), "br", ed=196, eye=(540, 700), set_="br_post", push=(1.0, 1.03)),        # We lost two zero.
    single(m("cut_sh5"), "sh", ed=ST, eye=(540, 640), set_="sh_post", clipboard=True, table=5.7),           # Less excellent.
    # Harry's set-piece gag: a slightly raised hand
    single(m("cut_mg2"), "mg", ed=196, eye=(600, 700), set_="mg_post", hand=True),               # Both goals were set pieces.
    single(m("cut_ck8"), "ck", ed=ST, eye=(560, 640), set_="ck_post", table=4.9),                # Yep.
    single(m("cut_mg3"), "mg", ed=196, eye=(600, 700), set_="mg_post", hand=True),               # ...before the game.
    single(m("cut_ck9"), "ck", ed=162, eye=(560, 650), set_="ck_post", table=4.9, push=(1.0, 1.03)),   # Yep.
    single(m("cut_mg4"), "mg", ed=196, eye=(600, 700), set_="mg_post", hand=True),               # Twice.
    single(m("cut_ck10"), "ck", ed=170, eye=(560, 650), set_="ck_post", table=4.9),              # Harry... I'm aware.
    single(m("cut_mg5"), "mg", ed=196, eye=(600, 700), set_="mg_post", hand=True, push=(1.0, 1.1)),    # lowers it
    # Kobbie, arms folded, across the room
    single(m("cut_mn3"), "mn", draw="mn_g_crossed", ed=132, eye=(560, 640), set_="mn_post", table=4.5,
           push=(1.0, 1.03), whip=True),                                                          # came on after 67
    single(m("cut_ck11"), "ck", ed=ST, eye=(560, 640), set_="ck_post", table=4.9, push=(1.0, 1.03)),   # ...Impact.
    single(m("cut_mn4"), "mn", draw="mn_g_crossed", ed=132, eye=(560, 640), set_="mn_post", table=4.5),  # didn't score
    single(m("cut_ck12"), "ck", ed=ST, eye=(560, 640), set_="ck_post", table=4.9),              # Nearly impact.
    single(m("cut_mn5"), "mn", draw="mn_g_crossed", ed=150, eye=(560, 660), set_="mn_post", table=4.5,
           push=(1.0, 1.08), drift=0.3),                                                          # into the lens
    # Harry becomes the striker
    single(m("cut_br5"), "br", ed=MCU, eye=(540, 760), set_="br_post", rise=(m("cut_br5") + 0.08, 0.5)),   # stands
    single(m("cut_mg6"), "mg", ed=MCU, eye=(540, 700), set_="mg_post"),                          # I had to start shooting.
    single(m("cut_br6"), "br", ed=MCU, eye=(540, 700), set_="br_post", push=(1.0, 1.03)),        # You're a centre-back.
    single(m("cut_mg7"), "mg", ed=MCU, eye=(540, 700), set_="mg_post"),                          # Nobody else was doing it.
    single(m("cut_ck13"), "ck", ed=162, eye=(560, 650), set_="ck_post", table=4.9, push=(1.0, 1.05)),  # starts... stops
    # the final gag
    single(m("cut_sh6"), "sh", ed=ST, eye=(540, 640), set_="sh_post", clipboard=True, table=5.7),           # Good news.
    group(m("cut_hope"), LINE_POST, cams=[(m("cut_hope"), (540, 1000, 1.0)), (m("cut_hope") + 0.6, (540, 990, 1.04))],
          table_y=1330, bg=("POST", 760, 470, 1.8, 5.5), fg=("POST", "counter", 300, 672, 2.4, 3.0)),  # they all look up
    single(m("cut_sh7"), "sh", ed=ST, eye=(540, 640), set_="sh_post", clipboard=True, table=5.7, push=(1.0, 1.04)),   # Ipswich next.
    single(m("cut_mn6"), "mn", draw="mn_g_crossed", ed=132, eye=(560, 640), set_="mn_post", table=4.5),  # promoted as well?
    group(m("cut_turn"), LINE_POST, cams=[(m("cut_turn"), (540, 1000, 1.0)), (m("cut_turn") + 0.6, (540, 995, 1.02))],
          table_y=1330, bg=("POST", 760, 470, 1.8, 5.5), fg=("POST", "counter", 300, 672, 2.4, 3.0)),  # they turn to Carrick
    single(m("cut_ck14"), "ck", ed=175, eye=(540, 650), set_="ck_post", table=4.9, push=(1.0, 1.08), drift=0.4,
           exit=m("ck_exit") + 0.02),                                                             # Good meeting. Out.
    single(m("cut_br7"), "br", ed=CU, eye=(540, 720), set_="br_post", push=(1.0, 1.06), drift=0.4, quiet=1.0),
    card(m("cut_black"), "black"),
    card(m("cut_title"), "title"),                                                                # ALL OR SOMETHING
    card(m("cut_tigers"), "tigers"),                                                              # the Tigers song
]
for i, s in enumerate(SHOTS):
    s["end"] = SHOTS[i + 1]["t"] if i + 1 < len(SHOTS) else T_END
    s["i"] = i

# the Tigers ending: the scoreboard, then the reactions (Harry blank, Kobbie arms folded, Steve and the clipboard,
# Bruno finished, Carrick walking away) as fast cuts to the chant; cut dead at the end (the Short loops)
TIGERS = [(0.00, "board"), (0.55, "mg"), (1.05, "mn"), (1.55, "sh"), (2.05, "br"), (2.55, "ck")]

# documentary captions: (start, end, kind, text 1, text 2). "name" = lower third on a character's first single,
# "place" = location slug, "match" = the minute and what happened, over the match flashes
CAPTIONS = [
    (m("cut_room_wide") + 0.25, m("cut_ck_board") - 0.05, "place", "AWAY DRESSING ROOM", "MKM Stadium, Hull. 2:14pm"),
    (m("cut_ck_board") + 0.3, m("cut_sh1") - 0.05, "name", "MICHAEL CARRICK", "Head Coach"),
    (m("cut_sh1") + 0.2, m("cut_ck2") - 0.05, "name", "STEVE HOLLAND", "Assistant Head Coach"),
    (m("cut_br1") + 0.2, m("cut_ck4") - 0.05, "name", "BRUNO FERNANDES", "Club Captain"),
    (m("cut_mn1") + 0.08, m("cut_ck5") - 0.05, "name", "KOBBIE MAINOO", "Midfielder. One of several."),
    (m("cut_mg1") + 0.15, m("cut_wide2") - 0.05, "name", "HARRY MAGUIRE", "Centre-back"),
    (ls("nar_knew") + 0.05, we("nar_knew", "coming") - 0.35, "match", "23'", "CORNER"),
    (m("flash2") + 0.03, m("chant"), "match", "58'", "CORNER"),
    (m("cut_post_wide") + 0.35, m("cut_silence") - 0.05, "place", "AWAY DRESSING ROOM", "Full time"),
]

WHIPS = [m("cut_mn3")]
SMASH = [m("cut_score"), m("cut_post_wide")]


def shot_at(t):
    for s in reversed(SHOTS):
        if t >= s["t"] - 1e-9: return s
    return SHOTS[0]


def ease(u, kind="inout"):
    u = min(1.0, max(0.0, u))
    if kind == "inout": return u * u * (3 - 2 * u)
    if kind == "out": return 1 - (1 - u) ** 2
    return u
