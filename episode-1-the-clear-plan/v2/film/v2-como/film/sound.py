"""Leeds, Como and the plan: the soundtrack: the grounds, the office (a telly's commentary murmur, the final whistle, one small clap), the
away dressing room's colder air, the tunnel's swelling noise, the match crowd under the touchline shots (it rises for
the first two goals only; on the fourth the crowd drops away and the camera's own handling noise is what is left),
the paraphrase cards with the mixed zone's hallway and the press room's hush, the corridor's footsteps overlapping
and stopping, the rolling board, the laptop's keys, the lid, the ceramic tap. Low travel music under Leeds-to-Como;
no music over the goals. The sound is cut at the very end.
python3 -m studio.film v2-como sound -> build/episode_audio.wav"""
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
    return s.get("plate") or s.get("draw")


def ambience(bus):
    for a, b in spans(lambda s: plate_of(s) == "AW"):
        A.bed(bus, "ambience/wind", a, b, -47)
        A.bed(bus, "crowd/crowd-large", a, b, -48, lowpass=1500)
    for a, b in spans(lambda s: plate_of(s) in ("OF", "clap", "brush", "bluemug", "whitemug")):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -52)
    for a, b in spans(lambda s: plate_of(s) in ("W", "CW", "CW2", "CD", "board_compact", "pen_click", "board_ht",
                                                "cap")):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -49, lowpass=2600)
    for a, b in spans(lambda s: plate_of(s) in ("TN",)):
        A.bed(bus, "crowd/crowd-large", a, b, -34, lowpass=2500, fin=1.2)
    for a, b in spans(lambda s: plate_of(s) in ("CS", "pen_click2", "tactic")):
        A.bed(bus, "crowd/crowd-large", a, b, -36)
    for a, b in spans(lambda s: plate_of(s) == "MZ"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -48, highpass=150)
        A.bed(bus, "ambience/street-distant", a, b, -60, lowpass=900)
    for a, b in spans(lambda s: plate_of(s) == "PR"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -54)
    for a, b in spans(lambda s: plate_of(s) == "CO"):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -50, highpass=120)
    for a, b in spans(lambda s: plate_of(s) in ("BN", "laptop", "mug_dark")):
        A.bed(bus, "ambience/city-through-window", a, b, -58, lowpass=2000)
        A.bed(bus, "ambience/room-tone-hvac", a, b, -58)


def foley(bus):
    for s in SHOTS:
        if s["kind"] == "insert" and str(s["draw"]).startswith("card_"):
            A.ev(bus, "impacts/tom-hit", s["t"] + 0.02, -31, semis=-5, lowpass=900)
    A.ev(bus, "impacts/tom-hit", m("flip_leeds"), -33, semis=-2, lowpass=1200)
    # the office: the telly's commentary (a crowd far off, band-limited), the whistle, one small clap
    A.bed(bus, "crowd/crowd-large", m("cut_office"), m("cut_lake"), -46, lowpass=1600, highpass=300)
    A.ev(bus, "sport/whistle-ref", m("whistle"), -36, lowpass=3500, highpass=500)
    A.ev(bus, "foley/clap-single", m("cut_clap") + 0.38, -38, semis=2)
    A.ev(bus, "cloth/cloth-a", m("cut_brush") + 0.15, -40)
    A.ev(bus, "cloth/cloth-b", m("cut_brush") + 0.55, -41)
    A.ev(bus, "foley/cup-down", m("cut_bluemug") + 0.35, -42, semis=-2)
    # Como: the board, the pen, everybody up, everybody back
    A.ev(bus, "creaks/creak-small", m("cut_compact") + 0.4, -48, semis=10, highpass=1500)
    A.ev(bus, "foley/pen-click-a", m("cut_click") + 0.32, -30)
    for k, (dt, p) in enumerate([(0.05, -0.4), (0.1, 0.3), (0.15, 0.0), (0.2, -0.2), (0.24, 0.45)]):
        A.ev(bus, "cloth/cloth-" + "abcde"[k], m("cut_go") + dt, -42, pan=p)
    A.steps(bus, m("cut_go") + 0.1, m("cut_go") + 0.75, -42, pace=0.13, pan=-0.2)
    A.steps(bus, m("cut_hold") + 0.75, m("cut_hold") + 1.95, -45, pace=0.2, pan=0.1)
    # half-time: the marker, the cap
    for k in range(4):
        A.ev(bus, "creaks/creak-small", m("w_press") + 0.05 + 0.24 * k, -46, semis=12, highpass=2000, dur=0.18)
    for k in range(6):
        A.ev(bus, "creaks/creak-small", m("w_together") + 0.05 + 0.22 * k, -46, semis=11, highpass=2000, dur=0.18)
    A.ev(bus, "foley/pen-click-c", m("cut_cap") + 0.72, -36, semis=-3)
    # the goals: the crowd goes up for the first two only
    for k, lvl in (("cut_g1", -30), ("cut_g2", -31), ("cut_g3", -33)):
        A.ev(bus, "crowd/applause-big", m(k) - 0.6, lvl, lowpass=5000, dur=3.0)
    A.ev(bus, "sport/whistle-ref", m("cut_board_ht") - 0.3, -36)
    A.ev(bus, "sport/whistle-ref", m("cut_ft") + 0.05, -34)
    # the camera's own handling noise in the silence after the fourth
    A.ev(bus, "creaks/creak-small", m("cut_push") + 1.4, -50, semis=-6, lowpass=1200)
    A.ev(bus, "cloth/cloth-f", m("cut_push") + 2.1, -50)
    A.ev(bus, "cloth/cloth-c", m("cut_sees") + 0.95, -44)                              # the lens comes down
    # the corridor: footsteps overlapping, then stopping; the board's wheels
    A.steps(bus, m("cut_corr") + 0.2, m("cut_corr") + 3.0, -40, pace=0.42, pan=-0.6, pan_to=-0.9)
    A.steps(bus, m("cut_corr") + 0.35, m("cut_corr") + 3.2, -46, pace=0.47, pan=0.4, pan_to=0.6)
    A.bed(bus, "ambience/rain-concrete", m("board_roll"), m("board_roll") + 3.4, -50, lowpass=600, fin=0.3, fout=0.4)
    A.ev(bus, "creaks/creak-long", m("board_roll") + 0.4, -46, semis=5, highpass=500)
    # the laptop: keys, backspaces, the lid; the mug
    rng = np.random.default_rng(3)
    for t0, t1 in ((m("type1"), m("type1") + 1.4), (m("type2"), m("type2") + 0.9)):
        t = t0
        while t < t1:
            A.ev(bus, "foley/pen-click-b", t, -46 + rng.uniform(-3, 2), semis=rng.uniform(3, 8), highpass=900)
            t += rng.uniform(0.09, 0.17)
    A.ev(bus, "foley/cup-down", m("lid") + 0.55, -38, semis=-6, lowpass=2500)
    A.ev(bus, "foley/cup-down", m("cut_mugdark") + 1.1, -42, semis=6, highpass=800)


def music(bus):
    # Leeds to Como: low travel music, no assertion
    a, b = m("cut_bluemug"), m("cut_compact") + 1.0
    n = b - a
    ch = A.strings([A.note("A2"), A.note("E3"), A.note("A3"), A.note("C4")], n + 1.0, 1.2, 1.2, 1400)[:int(n * A.SR)]
    y = np.stack([ch, ch], 1) * A.fade(int(n * A.SR), 1.0, 1.2)[:, None]
    bus.add(A.at_level(y, -33), a)
    # the credits: the opening's chord, quietly, cut dead at the end
    a, b = m("cut_credits"), TL["total"]
    y = A.title_sting(b - a + 0.2)[:int((b - a) * A.SR)]
    y *= A.fade(len(y), 0.4, 0.05)[:, None]
    bus.add(A.at_level(y, -30), a)


def main():
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.3, room_db=-23)
    ambience(amb)
    foley(fx)
    music(mus)
    A.master(dlg, [amb, fx], [mus])
