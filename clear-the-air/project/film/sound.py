"""Clear the Air: the soundtrack. A quiet office throughout (air-conditioning, the city through the window), a little
lower for the pointing; sparse dry documentary music under the narrator only, gone before the conversation; the
board's marker squeaking the tick; two short sprays and, at the end, one tiny accidental one (band-passed noise: an
aerosol is a hiss); the handshake; the door banging open on Gary with a very short official sting under it; his pen;
the stamp. No laughter. python3 -m studio.film clear-the-air sound -> build/episode_audio.wav"""
import json

import numpy as np

from studio.film import audio as A
from studio.film import ep
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt
RNG = np.random.default_rng(31)


def spray(dur, level):
    """an aerosol: a hiss with a quick start and a short tail"""
    n = int(dur * A.SR)
    y = RNG.standard_normal(n).astype(np.float32)
    y = A.bp(y, 2500, 9000).astype(np.float32)
    env = np.minimum(1.0, np.arange(n) / (0.012 * A.SR)) * np.exp(-np.maximum(0, np.arange(n) - 0.6 * n) / (0.08 * A.SR))
    y = y * env.astype(np.float32)
    return A.at_level(np.stack([y, y * 0.92], 1), level)


def ambience(bus):
    end = m("cut_black")
    A.bed(bus, "ambience/room-tone-hvac", 0.0, end, -52, lowpass=3600, fout=0.02,
          gain_fn=lambda t: np.where((t > m("cut_point")) & (t < m("cut_a20")), 0.6, 1.0))
    A.bed(bus, "ambience/city-through-window", 0.0, end, -62, lowpass=2000, fout=0.02)


def foley(bus):
    # the opening: a chair creaks; Wilcox's arm
    A.ev(bus, "creaks/creak-small", 1.2, -54, semis=-4)
    A.ev(bus, "cloth/cloth-b", wt("A01", "jason") + 0.1, -46)
    # the doorway dance: a trainer squeak and a sleeve on every dodge and every block
    from film.props import DODGE
    for dt, who, way in DODGE:
        t0 = m("cut_door") + dt
        pan = -0.3 if way == "left" else 0.3 if way == "right" else 0.0
        if way in ("left", "right"):
            A.ev(bus, "creaks/creak-small", t0 + 0.02, -42 if who == "jason" else -46, semis=14, highpass=2500,
                 dur=0.09, pan=pan)
        A.ev(bus, "cloth/cloth-c" if who == "bruno" else "cloth/cloth-b", t0, -44, pan=pan)
    A.ev(bus, "impacts/tom-hit", m("cut_door") + 1.45, -44, semis=-12, lowpass=500)          # Bruno lands
    # the tick: the marker squeaks, then RESOLVED
    for k in range(3):
        A.ev(bus, "creaks/creak-small", m("cut_tick") + 0.15 + 0.13 * k, -44, semis=12, highpass=2000, dur=0.12)
    for k in range(6):
        A.ev(bus, "creaks/creak-small", m("cut_tick") + 0.68 + 0.09 * k, -47, semis=11, highpass=2000, dur=0.08)
    # the sprays
    A.ev(bus, "cloth/cloth-a", m("cut_spray") + 0.1, -48)
    bus.add(spray(0.42, -34), m("psst1"))
    bus.add(spray(0.42, -34), m("psst2"))
    A.ev(bus, "foley/pen-click-b", m("cut_a14") - 0.1, -50, semis=-6)                  # the can set down, proudly
    # the handshake
    A.ev(bus, "cloth/cloth-d", m("cut_shake") + 0.05, -44)
    A.ev(bus, "foley/clap-single", m("cut_shake") + 0.18, -46, semis=-7, lowpass=1800)
    A.ev(bus, "cloth/cloth-e", m("cut_shake") + 0.55, -48)
    # the card: a rustle as it goes up
    A.ev(bus, "paper/paper-handle", m("cut_card") + 0.35, -46)
    # the door bangs open on Gary
    A.ev(bus, "doors/door-shut", m("cut_gary") - 0.02, -30, semis=-3)
    A.ev(bus, "impacts/tom-hit", m("cut_gary") - 0.02, -36, semis=-8, lowpass=900)
    A.steps(bus, m("cut_gary") + 0.35, m("cut_gary") + 0.9, -44, pace=0.26, pan=0.4)
    # the point: two sleeves at once
    A.ev(bus, "cloth/cloth-f", m("cut_point") + 0.1, -40, pan=-0.35)
    A.ev(bus, "cloth/cloth-b", m("cut_point") + 0.11, -40, pan=0.35)
    A.ev(bus, "paper/paper-lower", m("cut_a20") + 0.1, -48)                              # the card comes down
    # the clipboard: the pen, line by line; the stamp
    for i in range(4):
        t0 = m("cut_write") + 0.15 + 0.33 * i
        for k in range(3):
            A.ev(bus, "foley/pen-click-a", t0 + 0.06 * k, -50, semis=9 + k, highpass=1500, dur=0.05)
    A.ev(bus, "impacts/tom-hit", m("cut_stamp") + 0.08, -30, semis=-4, lowpass=1400)
    A.ev(bus, "paper/paper-short", m("cut_stamp") + 0.1, -44)
    # the last, accidental spray, small, under the table
    bus.add(spray(0.25, -44), m("psst3"))


def music(bus):
    # under the narrator only: a low, dry documentary pulse, gone before Carrick speaks
    a, b = 0.0, m("cut_a02")
    n = b - a
    ch = A.strings([A.note("D2"), A.note("A2"), A.note("D3")], n + 0.8, 1.0, 1.2, 1300)[:int(n * A.SR)]
    y = np.stack([ch, ch], 1) * A.fade(int(n * A.SR), 0.8, 0.9)[:, None]
    bus.add(A.at_level(y, -36), a)
    # Gary: a very short official sting, well under him
    st = A.strings([A.note("C3"), A.note("G3"), A.note("C4"), A.note("E4")], 0.9, 0.02, 0.5, 2200)
    bus.add(A.at_level(np.stack([st, st], 1), -34), m("cut_gary") + 0.05)


def main():
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.3, room_db=-24)
    ambience(amb)
    foley(fx)
    music(mus)
    A.master(dlg, [amb, fx], [mus], target=-14.0)
