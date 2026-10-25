"""Upstairs: the soundtrack: the mixed zone's hallway and a far-off crowd emptying out, the press room's hush, the
boardroom's air-conditioning and the city through the window, the statement card's low hit, the corridor. No music:
the board meeting plays dry. python3 -m studio.film v3-upstairs sound -> build/episode_audio.wav"""
import json

from studio.film import audio as A
from studio.film import ep
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt


def spans(pred):
    out = []
    for s in SHOTS:
        if pred(s):
            if out and abs(out[-1][1] - s["t"]) < 1e-3:
                out[-1] = (out[-1][0], s["end"])
            else:
                out.append((s["t"], s["end"]))
    return out


def plate_of(s):
    if s["kind"] == "single":
        return s["bg"][0]
    if s["kind"] == "group":
        return s["bg"][0]
    return s.get("plate") or s.get("draw")


def ambience(bus):
    for a, b in spans(lambda s: plate_of(s) == "MZ"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -48, highpass=150)
        A.bed(bus, "crowd/crowd-large", a, b, -56, lowpass=900)
    for a, b in spans(lambda s: plate_of(s) == "PR"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -54)
    for a, b in spans(lambda s: plate_of(s) == "B"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -53, lowpass=3600)
        A.bed(bus, "ambience/city-through-window", a, b, -62, lowpass=2200)
    for a, b in spans(lambda s: plate_of(s) == "CO"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -50, highpass=120)


def foley(bus):
    A.ev(bus, "impacts/tom-hit", m("cut_x19") + 0.02, -33, semis=-5, lowpass=900)
    A.ev(bus, "cloth/cloth-b", m("cut_x04") + 0.05, -46)                     # the point up
    A.ev(bus, "cloth/cloth-c", m("cut_x08") + 0.1, -46)
    A.ev(bus, "cloth/cloth-a", m("cut_x14") + 0.05, -48)
    A.ev(bus, "creaks/creak-small", m("cut_x15") + 0.2, -52, semis=-3)     # Wilcox shifts in his chair
    A.steps(bus, m("cut_x20") + 0.1, m("cut_x20") + 1.2, -50, pace=0.45, pan=0.3)


def main():
    dlg, amb, fx = A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.3, room_db=-24)
    ambience(amb)
    foley(fx)
    A.master(dlg, [amb, fx], [])
