"""The cast: every drawing used, with its face landmarks (build/facemarks.json + hand overrides, sheet px) and
how it is sized and aimed on screen.

ed     = the eye distance used for sizing (sheet px): a shot asks for an eye distance in screen px, so every drawing
         of a character comes out the same size (3/4 views count their foreshortened eyes as 85 %)
anchor = the point placed on screen (between the eyes)
look0  = gaze offset that makes the drawing look straight into the lens (the sheets' pupils wander)
faces  = which way the drawing faces ("F" front, "L" / "R" towards the viewer's left / right)"""
import json, numpy as np
from engine import Drawing

FM = json.load(open("build/facemarks.json"))

# hand-measured landmarks where the detector can't see (beards) or the chin is hidden
OVR = {
    "br_hero": dict(chin=352.0, neck=(175.0, 374.0)),
    "br_q34l": dict(mouth=(542.5, 233.5, 558.0, 233.0, 550.0, 232.5), chin=249.0, neck=(550.0, 258.0)),
    "br_g_shrug": dict(mouth=(1036.0, 1155.8, 1050.0, 1155.4, 1043.0, 1155.3), chin=1167.0, neck=(1043.0, 1175.0)),
    "br_g_talk": dict(mouth=(906.0, 1153.0, 921.0, 1151.0, 913.5, 1151.5), chin=1166.0, neck=(913.0, 1174.0)),
    "js_q34l": dict(mouth=None), "js_q34r": dict(mouth=None), "br_q34r": dict(mouth=None),
}
FACES = {"ck_front": "R", "ck_q34l": "R", "ck_q34r": "R", "ck_g_explain": "F", "ck_g_crossed": "F",
         "js_hero": "F", "js_q34l": "L", "js_q34r": "R", "js_g_explain": "F", "js_g_three": "F", "js_g_point": "R",
         "om_hero": "F", "om_q34l": "R", "om_q34r": "L", "om_g_explain": "F",
         "br_hero": "F", "br_q34l": "R", "br_q34r": "R", "br_g_shrug": "F", "br_g_talk": "F",
         "jr_hero": "F", "jr_q34l": "R", "jr_q34r": "R"}
LOOK0 = {}
# back views: no face; sized by the head (box in sheet px), placed by the head's centre
BACKS = {"js_back": (968, 140, 1064, 262), "om_back": (972, 145, 1070, 262)}


class Cast:
    def __init__(self):
        self.d, self.info = {}, {}

    def get(self, name):
        if name not in self.d and name in BACKS:
            x0, y0, x1, y1 = BACKS[name]
            self.d[name] = Drawing(name, name)
            self.info[name] = dict(anchor=((x0 + x1) / 2, (y0 + y1) / 2), ed=(x1 - x0) / 4.24, faces="B", look0=(0.0, 0.0))
        if name not in self.d:
            fm = dict(FM[name]); fm.update(OVR.get(name, {}))
            eyes = [tuple(e) for e in fm.get("eyes", [])]
            mouth = fm.get("mouth")
            spec = dict(mouth=tuple(mouth) if mouth else None, chin=fm.get("chin"), eyes=eyes,
                        neck=tuple(fm["neck"]) if fm.get("neck") else None, head=tuple(fm["head"]))
            self.d[name] = Drawing(name, name, **spec)
            em = np.mean([e[:2] for e in eyes], 0) if eyes else np.float32([(fm["head"][0] + fm["head"][2]) / 2,
                                                                               (fm["head"][1] + fm["head"][3]) / 2])
            ed = abs(eyes[1][0] - eyes[0][0]) if len(eyes) == 2 else 20.0
            if FACES.get(name, "F") != "F": ed /= 0.85
            self.info[name] = dict(anchor=(float(em[0]), float(em[1])), ed=float(ed), faces=FACES.get(name, "F"),
                                   look0=LOOK0.get(name, (0.0, 0.0)))
        return self.d[name], self.info[name]


CAST = Cast()
