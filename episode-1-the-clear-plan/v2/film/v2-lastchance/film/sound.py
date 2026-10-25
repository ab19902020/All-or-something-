"""The soundtrack: The Handover's (episodes/the-handover/film/sound.py) on this edit: the voices with a little of the
boardroom round them, the room's air-conditioning and the city faintly through the glass, the foley the picture asks
for (Jason leaning in, Carrick's chair, his steps to the door, the latch, the door's squeak, Ole's steps), the title
boom with its chord, and the chord held quietly under the credits. python3 -m studio.film v2-lastchance sound"""
import json

from studio.film import audio as A
from studio.film import ep
from studio.film.shots import Marks
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt


def ambience(bus):
    A.bed(bus, "ambience/room-tone-hvac", 0.0, m("cut_black"), -53, lowpass=3600, fin=0.05)
    A.bed(bus, "ambience/city-through-window", 0.0, m("cut_black"), -64, lowpass=2200, fin=0.05)


def foley(bus):
    A.ev(bus, "cloth/cloth-c", ls("K02") - 0.22, -47, pan=0.0)
    A.ev(bus, "creaks/creak-small", ls("K02") - 0.05, -52, semis=-3)
    A.ev(bus, "cloth/cloth-b", m("cut_rant") - 0.04, -46)
    A.ev(bus, "creaks/creak-small", m("cut_rant") + 0.05, -50, semis=-2)
    A.ev(bus, "cloth/cloth-e", wt("K04", "what") - 0.15, -45)
    A.ev(bus, "cloth/cloth-a", m("rise") - 0.04, -44)
    A.ev(bus, "creaks/creak-mid", m("rise") + 0.05, -46, semis=-4, lowpass=3000)
    A.steps(bus, m("cut_door1") + 0.08, m("cut_door1") + 0.85, -41, pace=0.36, pan=-0.1, pan_to=0.3, lowpass=4500)
    A.ev(bus, "cloth/cloth-f", m("cut_what") - 0.05, -47, pan=0.2)
    A.ev(bus, "cloth/cloth-b", m("cut_door3") + 0.02, -46, pan=0.1)
    A.ev(bus, "foley/pen-click-a", m("click"), -34, pan=0.35, semis=-11, lowpass=2600)
    A.ev(bus, "foley/pen-click-b", m("click") + 0.09, -40, pan=0.35, semis=-13, lowpass=2200)
    A.ev(bus, "creaks/creak-short", m("swing") + 0.05, -37, pan=0.35, semis=4, highpass=450)
    A.steps(bus, m("walk") + 0.05, m("stop"), -40, pace=0.27, pan=0.15, pan_to=0.35, lowpass=4200)
    A.ev(bus, "cloth/cloth-d", m("stop") + 0.02, -46, pan=0.35)
    bus.add(A.at_level(A.big_boom(1.0), -16), m("cut_title"))


def music(bus):
    # the chord under the title boom, held quietly under the credits, out at the end
    n = TL["total"] - m("cut_title")
    y = A.title_sting(n + 0.2)[:int(n * A.SR)]
    y *= A.fade(len(y), 0.0, 1.2)[:, None]
    bus.add(A.at_level(y, -27), m("cut_title"))


def main():
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.35, room_db=-23)
    ambience(amb)
    foley(fx)
    music(mus)
    A.master(dlg, [amb, fx], [mus])
