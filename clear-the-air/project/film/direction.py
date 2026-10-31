"""The shot list for Clear the Air, framed for a portrait film (EP_RES=1080x1920), keyed to the dialogue edit.

The office (documentary/ceo-office, plate OF) from the desk's side: Carrick behind the desk on screen LEFT, Bruno on
screen RIGHT, the desk's top crossing them at the chest (seated); Wilcox stands behind, between them, with the
whiteboard on wheels at his left shoulder (CLEAR THE AIR / no leaks; after the tick, RESOLVED). The same room's wide
angle (aos/office, OW) has the door beside the same board: Wilcox in the doorway, and Gary in it. Carrick looks screen
right to Bruno, Bruno screen left to Carrick; both look up and back to Wilcox. Every character is the drawing the
rest of All or Something films him in: Carrick in the black club tracksuit, Bruno in the full kit (the model sheet's
upper-body gestures for the point), Wilcox in his black tracksuit poses; Gary is Overcrap Daily's house-style Gary
(the Pass Mic model sheet), with a lanyard."""
import json

from studio.film import ep
from studio.film.shots import Marks, finish, insert, shot_at as _shot_at, single, world
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt

PLATES = {"OF": "documentary/ceo-office", "OF2": "documentary/ceo-office", "OW": "aos/office",
          "OW2": "aos/office", "OWD": "aos/office", "OWD2": "aos/office"}

# the desk and what stands on it (1x plate px, from Como's office)
DESK = [(268, 486), (1416, 498), (1416, 592), (1292, 600), (1292, 795), (348, 795), (348, 600), (268, 566)]
ON_DESK = [[(476, 424), (676, 424), (676, 498), (476, 498)], [(1028, 428), (1178, 428), (1178, 518), (1028, 518)],
           [(962, 452), (1024, 452), (1024, 528), (962, 528)], [(1178, 452), (1318, 452), (1318, 528), (1178, 528)],
           [(396, 466), (472, 466), (472, 498), (396, 498)]]
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
CK, BR, JW = (1062, 362), (1302, 366), (1186, 316)
ED_CB, ED_J = 28.0, 21.0
M_CAM = (1183, 421, 4.0)
WIDE_JASON = ("wilcox", J_CLIP, JW, ED_J)                 # the card reveal: he raises the tablet
END_JASON = ("wilcox", "jason-wilcox:pockets", (1186, 314), 20.0)


def master(t, cam=None, push=1.03, carrick=None, bruno=None, jason=True, plate="OF", props=(), drift=0.35, ck=CK,
           br=BR, ed=ED_CB):
    acts = [("carrick", carrick or DRAW["carrick"], ck, ed, False), ("bruno", bruno or DRAW["bruno"], br, ed, False)]
    if jason:
        acts = [("wilcox", jason if isinstance(jason, str) else DRAW["wilcox"], JW, ED_J, False)] + acts
    c0 = cam or M_CAM
    layers = [("actors", acts)] + [("props", p) for p in props] + [("occl", "desk")]
    return world(t, plate, c0, (c0[0], c0[1], c0[2] * push), layers=layers, drift=drift, grade="studio")


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
    "wilcox": dict(bg=("OF", 1215, 280, 4.4, 2.4), fg=None, eye=(940, 1150)),
    "gary": dict(bg=("OWD2", 1372, 330, 5.4, 2.6), fg=("OF", "desk", 1240, DESK_Y, 4.6, 1.6), eye=(960, 1030)),
}


G_DESK = 5.6            # Gary stands at the desk's end: its edge at his waist, below his drawing's lanyard


def close(t, who, draw=None, ed=250.0, push=(1.0, 1.03), drift=0.5, table=3.0, key=None, eye=None, **kw):
    st = SET[key or who]
    return single(t, who, draw or DRAW[who], st["bg"], st["fg"], ed=ed, eye=eye or st["eye"], table=table,
                  push=push, drift=drift, grade="studio", **kw)


DOOR_CAM = (1352, 380, 5.0)
DOOR_JASON = ("wilcox", "jason-wilcox:pockets", (1371, 296), 28.0)
DOOR_GARY = ("gary", "gary-neville:standing", (1372, 302), 29.5)

SHOTS = finish([
    # ---- a private conversation
    master(0.0, cam=(1183, 421, 3.6), push=1.08, drift=0.25),
    master(wt("A01", "jason") - 0.08, cam=(1190, 380, 5.2), push=1.04, jason=J_POINT),       # he waves the camera in
    close(m("cut_a02"), "carrick", ed=240),
    close(m("cut_a03"), "bruno", ed=240),
    close(m("cut_a04"), "carrick", ed=256, push=(1.0, 1.0)),
    close(m("cut_a05"), "bruno", ed=256, push=(1.0, 1.0)),
    # ---- the door
    world(m("cut_door"), "OWD", DOOR_CAM, (DOOR_CAM[0], DOOR_CAM[1], DOOR_CAM[2] * 1.07), layers=[("props", "door_jason")],
          drift=0.2, grade="studio"),
    # ---- an honest exchange
    close(m("cut_a06"), "carrick", draw=C_EXPLAIN, ed=246),
    close(m("cut_a07"), "bruno", draw=B_TALK, ed=272, push=(1.0, 1.03)),
    master(m("cut_a08"), cam=(1183, 410, 4.6), push=1.02, drift=0.3),
    close(m("cut_a09"), "bruno", ed=262, push=(1.0, 1.04)),
    close(m("cut_a10"), "carrick", ed=268, push=(1.0, 1.05)),
    close(m("cut_smile"), "bruno", ed=280, push=(1.0, 1.0), drift=0.2),
    # ---- clearing the air
    insert(m("cut_tick"), "tick"),
    close(m("cut_spray"), "wilcox", draw=J_PHONE, ed=280, push=(1.0, 1.02), props=["can"],
          pssts=[m("psst1"), m("psst2")]),
    master(m("cut_a11"), plate="OF2", cam=(1186, 400, 4.2), push=1.02, bruno=B_TALK, jason=J_PHONE,
           props=["can_jason"]),
    close(m("cut_a12"), "wilcox", draw=J_PHONE, ed=286, props=["can"]),
    close(m("cut_a13"), "carrick", ed=256, push=(1.0, 1.0)),
    close(m("cut_a14"), "wilcox", draw=J_PHONE, ed=300, props=["can"], push=(1.0, 1.0)),
    master(m("cut_look"), plate="OF2", cam=(1183, 405, 4.8), push=1.06, jason=J_PHONE, drift=0.15,
           props=["can_jason"]),
    # ---- the reconciliation
    close(m("cut_a15"), "carrick", ed=262, push=(1.0, 1.03)),
    close(m("cut_a16"), "bruno", ed=262, push=(1.0, 1.03)),
    insert(m("cut_shake"), "shake"),
    back_master(m("cut_card"), ["card_world"], plate="OF2", cam=(1183, 405, 4.0), push=0.97),
    close(m("cut_card2"), "wilcox", draw=J_CLIP, ed=270, props=["card"], card_up=m("cut_card2") + 0.1,
          push=(1.0, 1.04)),
    # ---- standards inspection
    world(m("cut_gary"), "OWD2", DOOR_CAM, (DOOR_CAM[0], DOOR_CAM[1], DOOR_CAM[2] * 1.03), layers=[("props", "door_gary")],
          drift=0.1, grade="studio"),
    close(m("cut_a17"), "gary", ed=250, props=["lanyard"], table=G_DESK),
    close(m("cut_a18"), "wilcox", ed=280, draw=J_CROSS, push=(1.0, 1.02)),
    close(m("cut_a19"), "gary", draw=G_CROSS, ed=256, props=["lanyard"], push=(1.0, 1.0), table=G_DESK),
    master(m("cut_point"), plate="OF2", cam=(1183, 410, 4.3), push=1.0, carrick=C_POINT, bruno=B_POINT, jason=J_CLIP,
           drift=0.0, props=["card_jason"]),
    close(m("cut_a20"), "wilcox", draw=J_SHRUG, ed=262, push=(1.0, 0.98)),
    insert(m("cut_write"), "clip"),
    close(m("cut_a21"), "gary", ed=270, props=["lanyard"], push=(1.0, 1.0), drift=0.1, table=G_DESK),
    insert(m("cut_stamp"), "stamp"),
    back_master(m("cut_end"), ["puff_world"], plate="OF2", cam=(1183, 405, 4.6), push=1.01, carrick=C_TRACK),
    insert(m("cut_black"), "end"),
], TL["total"])
WHIPS = []


def shot_at(t):
    return _shot_at(SHOTS, t)
