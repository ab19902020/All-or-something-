"""The cast: every drawing used, with its face landmarks (build/facemarks.json + hand overrides, sheet px) and
how it is sized and aimed on screen.

ed     = the eye distance used for sizing (sheet px): a shot asks for an eye distance in screen px, so every drawing
         of a character comes out the same size (3/4 views count their foreshortened eyes as 85 %)
anchor = the point placed on screen (between the eyes)
look0  = gaze offset that makes the drawing look straight into the lens (the sheets' pupils wander)
faces  = which way the drawing faces ("F" front, "L" / "R" towards the viewer's left / right, "B" back)"""
import json, numpy as np
from engine import Drawing

FM = json.load(open("build/facemarks.json"))

# hand-measured landmarks where the detector can't see (beards, a smile line on dark skin) or where a drawn
# mouth must stay as drawn (Bruno's touchline shout)
OVR = {
    "br_hero": dict(chin=352.0, neck=(175.0, 374.0)),
    "br_q34l": dict(mouth=(542.5, 233.5, 558.0, 233.0, 550.0, 232.5), chin=249.0, neck=(550.0, 258.0)),
    "br_g_shrug": dict(mouth=(1036.0, 1155.8, 1050.0, 1155.4, 1043.0, 1155.3), chin=1167.0, neck=(1043.0, 1175.0)),
    "br_g_talk": dict(mouth=(906.0, 1153.0, 921.0, 1151.0, 913.5, 1151.5), chin=1166.0, neck=(913.0, 1174.0)),
    "br_q34r": dict(mouth=None), "br_g_celebrate": dict(mouth=None),
    "mn_hero": dict(mouth=(116.4, 277.3, 174.3, 277.3, 145.3, 283.0), chin=312.5, neck=(145.3, 336.0)),
    "mn_q34r": dict(mouth=None), "ck_side": dict(mouth=None),
}
FACES = {"ck_front": "R", "ck_q34l": "R", "ck_q34r": "R", "ck_g_explain": "F", "ck_g_crossed": "F", "ck_g_point": "R",
         "ck_side": "R",
         "br_hero": "F", "br_q34l": "R", "br_q34r": "R", "br_g_shrug": "F", "br_g_talk": "F", "br_g_celebrate": "F",
         "mn_hero": "F", "mn_q34l": "R", "mn_q34r": "L", "mn_g_crossed": "R",
         "mg_hero": "F", "mg_q34l": "R", "mg_q34r": "R", "mg_confused": "F", "mg_g_talk": "F",
         "sh_hero": "F", "sh_q34l": "R", "sh_q34r": "R",
         "bs_hero": "F", "yt_hero": "F", "ls_hero": "F", "sl_hero": "F"}
LOOK0 = {}
# back views: no face; sized by the head (box in sheet px), placed by the head's centre
BACKS = {"ck_back": (935, 118, 1055, 250), "br_back": (958, 150, 1048, 245), "mg_back": (962, 146, 1052, 250),
         "mn_back": (955, 148, 1050, 262)}
# drawings without a face to animate (seen small or moving): (anchor between the eyes, eye distance), sheet px,
# measured against the same character's front view (the walk pose is drawn at 40 % of the turnaround's size)
PLAIN = {"ck_walk": ((882.0, 1230.0), 12.4)}
# eye distances set by hand where a drawing has only one eye showing (the profile), matched to the front view
ED = {"ck_side": 31.1}


class Cast:
    def __init__(self):
        self.d, self.info = {}, {}

    def get(self, name):
        if name not in self.d and name in BACKS:
            x0, y0, x1, y1 = BACKS[name]
            self.d[name] = Drawing(name, name)
            self.info[name] = dict(anchor=((x0 + x1) / 2, (y0 + y1) / 2), ed=(x1 - x0) / 4.24, faces="B",
                                   look0=(0.0, 0.0))
        if name not in self.d and name in PLAIN:
            (ax, ay), ed = PLAIN[name]
            self.d[name] = Drawing(name, name)
            self.info[name] = dict(anchor=(ax, ay), ed=ed, faces="R", look0=(0.0, 0.0))
        if name not in self.d:
            fm = dict(FM[name]); fm.update(OVR.get(name, {}))
            eyes = [tuple(e) for e in fm.get("eyes", [])]
            mouth = fm.get("mouth")
            spec = dict(mouth=tuple(mouth) if mouth else None, chin=fm.get("chin"), eyes=eyes,
                        neck=tuple(fm["neck"]) if fm.get("neck") else None, head=tuple(fm["head"]))
            self.d[name] = Drawing(name, name, **spec)
            em = np.mean([e[:2] for e in eyes], 0) if eyes else np.float32([(fm["head"][0] + fm["head"][2]) / 2,
                                                                               (fm["head"][1] + fm["head"][3]) / 2])
            ed = abs(eyes[1][0] - eyes[0][0]) if len(eyes) == 2 else (fm["head"][2] - fm["head"][0]) / 4.24
            if FACES.get(name, "F") != "F": ed /= 0.85
            ed = ED.get(name, ed)
            self.info[name] = dict(anchor=(float(em[0]), float(em[1])), ed=float(ed), faces=FACES.get(name, "F"),
                                   look0=LOOK0.get(name, (0.0, 0.0)))
        return self.d[name], self.info[name]


CAST = Cast()
