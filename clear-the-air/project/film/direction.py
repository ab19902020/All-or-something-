"""The shot list for Clear the Air, framed for a portrait film (EP_RES=1080x1920), keyed to the dialogue edit.

The office (documentary/ceo-office, plate OF) from the desk's side: Carrick behind the desk on screen LEFT, Bruno on
screen RIGHT, the desk's top crossing them at the chest (seated); Wilcox stands behind, between them, with the
whiteboard on wheels at his left shoulder (CLEAR THE AIR / no leaks; after the tick, RESOLVED). The same room's wide
angle (aos/office, OW) has the door beside the same board: Wilcox in the doorway, and Gary in it. Carrick looks screen
right to Bruno, Bruno screen left to Carrick; both look up and back to Wilcox. Every character is the drawing the
rest of All or Something films him in: Carrick in the black club tracksuit, Bruno in the full kit, Wilcox in his
black tracksuit poses (always behind the desk); Gary is Overcrap Daily's house-style Gary (the Pass Mic model sheet),
with a lanyard. Framed for a phone: tight three-shots, close-ups from the head to below the chest, the doorway filled
by the standing figure; the point is a reverse on Wilcox with their two fingers jabbing in from the camera's side."""
import json

from studio.film import ep
from studio.film.shots import Marks, finish, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"OF": "documentary/ceo-office", "OF2": "documentary/ceo-office", "OW": "aos/office",
          "OW2": "aos/office", "OWD": "aos/office", "OWD2": "aos/office", "OWW": "aos/office", "OWW2": "aos/office"}

# the desk and what stands on it (1x plate px, from Como's office)
DESK = [(268, 486), (1416, 498), (1416, 592), (1292, 600), (1292, 795), (348, 795), (348, 600), (268, 566)]
ON_DESK = [[(1070, 432), (1173, 432), (1160, 490), (1056, 490)],                    # the laptop's screen
           [(970, 475), (1022, 475), (1022, 492), (970, 492)],                       # the pen pot
           [(1211, 457), (1306, 457), (1306, 484), (1188, 484), (1188, 476), (1211, 476)],   # the books' top
           [(396, 466), (472, 466), (472, 498), (396, 498)], [(476, 424), (676, 424), (676, 498), (476, 498)]]
# (each the object's own outline, so nothing of the chair or the wall behind it is laid over a body)
FRONT = [(0, 481), (268, 486), (1416, 498), (1672, 501), (1672, 941), (0, 941)]     # the desk and all before it
OCCL = {"OF": {"desk": [FRONT] + ON_DESK}, "OF2": {"desk": [FRONT] + ON_DESK}}
DESK_Y = 494

DRAW = {"carrick": "michael-carrick:arms", "bruno": "bruno-fernandes:full", "wilcox": "jason-wilcox:pockets",
        "gary": "gary-neville:arms"}
C_EXPLAIN, C_POINT, C_TRACK = "michael-carrick:track_explain", "michael-carrick:point", "michael-carrick:track"
B_TALK, B_POINT, B_SHRUG = "bruno-fernandes:talk", "bruno-fernandes:point", "bruno-fernandes:shrug"
J_CLIP, J_SHRUG, J_POINT, J_CROSS, J_PHONE = ("jason-wilcox:clipboard", "jason-wilcox:shrug", "jason-wilcox:point",
                                              "jason-wilcox:crossarms", "jason-wilcox:phone")
G_CROSS = "gary-neville:crossed"
ALSO = []

EYES = {
    "carrick": dict(bruno=(0.55, 0.04, 0.18), wilcox=(0.62, -0.18, 0.2), gary=(0.85, -0.04, 0.3),
                    can=(0.7, -0.2, 0.22)),
    "bruno": dict(carrick=(-0.55, 0.04, -0.18), wilcox=(-0.35, -0.2, -0.12), gary=(0.6, -0.04, 0.22),
                  table=(-0.1, 0.6, -0.03)),
    "wilcox": dict(carrick=(-0.55, 0.12, -0.18), bruno=(0.45, 0.12, 0.15), gary=(0.85, 0.0, 0.3)),
    "gary": dict(wilcox=(-0.55, 0.05, -0.18), room=(-0.35, 0.08, -0.1), clip=(0.05, 0.7, 0.0)),
}
EYES_FIRST = True

# ---- the master: eyes and eye distances in plate px (OF)
CK, BR, JW = (1088, 362), (1282, 366), (1186, 316)     # close enough to fill a portrait frame
ED_CB, ED_J = 30.0, 22.5
M_CAM = (1186, 388, 5.4)
WIDE_JASON = ("wilcox", J_CLIP, JW, ED_J)                 # the card reveal: he raises the tablet
END_JASON = ("wilcox", "jason-wilcox:pockets", (1186, 314), 21.5)


def master(t, cam=None, push=1.03, carrick=None, bruno=None, jason=True, plate="OF", props=(), drift=0.35, ck=CK,
           br=BR, ed=ED_CB, **kw):
    acts = [("carrick", carrick or DRAW["carrick"], ck, ed, False), ("bruno", bruno or DRAW["bruno"], br, ed, False)]
    if jason:
        acts = [("wilcox", jason if isinstance(jason, str) else DRAW["wilcox"], JW, ED_J, False)] + acts
    c0 = cam or M_CAM
    layers = [("actors", acts)] + [("props", p) for p in props] + [("occl", "desk")]
    return world(t, plate, c0, (c0[0], c0[1], c0[2] * push), layers=layers, drift=drift, grade="studio", **kw)


def back_master(t, props, cam=None, push=1.03, carrick=None, bruno=None, plate="OF", drift=0.35):
    """the master with Wilcox drawn by a props layer (he holds something, or moves)"""
    acts = [("carrick", carrick or DRAW["carrick"], CK, ED_CB, False), ("bruno", bruno or DRAW["bruno"], BR, ED_CB, False)]
    c0 = cam or M_CAM
    layers = [("props", p) for p in props] + [("actors", acts), ("occl", "desk")]
    return world(t, plate, c0, (c0[0], c0[1], c0[2] * push), layers=layers, drift=drift, grade="studio")


# ---- singles (layout px: the 1920-wide layout scaled to the 1080-wide frame)
SET = {
    "carrick": dict(bg=("OF", 1010, 330, 3.9, 2.2), fg=("OF", "desk", 1066, DESK_Y, 4.3, 0.0), eye=(860, 1300)),
    "bruno": dict(bg=("OF", 1290, 330, 3.9, 1.6), fg=("OF", "desk", 1300, DESK_Y, 4.3, 0.0), eye=(1060, 1300)),
    "wilcox": dict(bg=("OF", 1215, 280, 4.4, 2.4), fg=("OF", "desk", 1200, DESK_Y, 4.6, 1.2), eye=(940, 1100),
                   table=5.6),                                    # he stands behind the desk: its edge at his hip
    "gary": dict(bg=("OWW2", 1330, 330, 5.4, 2.6), fg=("OF", "desk", 1240, DESK_Y, 4.6, 1.6), eye=(960, 1030)),
}


G_DESK = 5.6            # Gary stands at the desk's end: its edge at his waist, below his drawing's lanyard


def close(t, who, draw=None, ed=250.0, push=(1.0, 1.03), drift=0.5, table=None, key=None, eye=None, **kw):
    st = SET[key or who]
    table = st.get("table", 3.4) if table is None else table
    return single(t, who, draw or DRAW[who], st["bg"], st["fg"], ed=ed, eye=eye or st["eye"], table=table,
                  push=push, drift=drift, grade="studio", **kw)


DOOR_CAM = (1330, 352, 7.6)                    # close on the doorway
DOOR_JASON = ("wilcox", "jason-wilcox:pockets", (1330, 288), 30.0)       # filling the doorway
DOOR_BRUNO = ("bruno", "bruno-fernandes:full", (1330, 296), 25.0)        # behind him, in the corridor
DOOR_GARY = ("gary", "gary-neville:standing", (1330, 268), 30.0)      # plain: placed by the head's centre

SHOTS = finish([
    # ---- a private conversation
    master(0.0, cam=(1186, 380, 4.6), push=1.08, drift=0.25),
    master(wt("A01", "jason") - 0.08, cam=(1190, 380, 5.2), push=1.04, jason=J_POINT),       # he waves the camera in
    close(m("cut_a02"), "carrick", ed=270),
    close(m("cut_a03"), "bruno", ed=270),
    close(m("cut_a04"), "carrick", ed=286, push=(1.0, 1.0)),
    close(m("cut_a05"), "bruno", ed=286, push=(1.0, 1.0)),
    # ---- the door
    world(m("cut_door"), "OWW", DOOR_CAM, (DOOR_CAM[0], DOOR_CAM[1], DOOR_CAM[2] * 1.05), layers=[("props", "door_jason")],
          drift=0.0, grade="studio", ease="out"),
    # ---- an honest exchange
    close(m("cut_a06"), "carrick", draw=C_EXPLAIN, ed=276),
    close(m("cut_a07"), "bruno", ed=300, push=(1.0, 1.03)),
    master(m("cut_a08"), cam=(1186, 388, 5.7), push=1.02, drift=0.3),
    close(m("cut_a09"), "bruno", ed=292, push=(1.0, 1.04)),
    close(m("cut_a10"), "carrick", ed=298, push=(1.0, 1.05)),
    close(m("cut_smile"), "bruno", ed=310, push=(1.0, 1.0), drift=0.2),
    # ---- clearing the air
    insert(m("cut_tick"), "tick"),
    close(m("cut_spray"), "wilcox", draw=J_POINT, ed=236, eye=(500, 1080), push=(1.0, 1.02), props=["can"],
          pssts=[m("psst1"), m("psst2")]),                                       # at arm's length: pssht, pssht
    master(m("cut_a11"), plate="OF2", cam=(1186, 386, 5.5), push=1.02, jason=J_PHONE,
           props=["can_jason"]),
    close(m("cut_a12"), "wilcox", draw=J_POINT, ed=240, eye=(500, 1080), props=["can"]),
    close(m("cut_a13"), "carrick", ed=286, push=(1.0, 1.0), mist=m("cut_a13") - 0.3),     # it reaches him
    close(m("cut_a14"), "wilcox", draw=J_PHONE, ed=300, props=["can"], push=(1.0, 1.0)),           # the advert
    master(m("cut_look"), plate="OF2", cam=(1186, 388, 5.8), push=1.06, jason=J_PHONE, drift=0.15, mist=m("cut_look") - 0.5,
           props=["can_jason"]),
    # ---- the reconciliation
    close(m("cut_a15"), "carrick", ed=292, push=(1.0, 1.03)),
    close(m("cut_a16"), "bruno", ed=292, push=(1.0, 1.03)),
    insert(m("cut_shake"), "shake"),
    back_master(m("cut_card"), ["card_world"], plate="OF2", cam=(1186, 386, 5.4), push=0.97),
    close(m("cut_card2"), "wilcox", draw=J_CLIP, ed=270, props=["card"], card_up=m("cut_card2") + 0.1,
          push=(1.0, 1.04)),
    # ---- standards inspection
    world(m("cut_gary"), "OWW2", DOOR_CAM, (DOOR_CAM[0], DOOR_CAM[1], DOOR_CAM[2] * 1.03), layers=[("props", "door_gary")],
          drift=0.1, grade="studio"),
    close(m("cut_a17"), "gary", ed=250, props=["lanyard"], table=G_DESK),
    close(m("cut_a18"), "wilcox", ed=280, draw=J_CROSS, push=(1.0, 1.02)),
    close(m("cut_a19"), "gary", ed=262, eye=(1000, 1010), props=["lanyard"], push=(1.0, 1.04), table=G_DESK),
    close(m("cut_point"), "wilcox", draw=J_CLIP, ed=270, eye=(850, 1000), props=["card"], fingers=True, push=(1.0, 1.0),
          drift=0.0, jab=m("cut_point") + 0.12),                     # the reverse: two fingers, together, at him
    close(m("cut_a20"), "wilcox", draw=J_SHRUG, ed=280, push=(1.0, 0.98)),
    insert(m("cut_write"), "clip"),
    close(m("cut_a21"), "gary", ed=270, props=["lanyard"], push=(1.0, 1.0), drift=0.1, table=G_DESK),
    insert(m("cut_stamp"), "stamp"),
    back_master(m("cut_end"), ["puff_world"], plate="OF2", cam=(1186, 390, 5.6), push=1.01, carrick=C_TRACK),
    insert(m("cut_black"), "end"),
], TL["total"])
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
