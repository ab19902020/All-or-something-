"""Bournemouth: the soundtrack: Old Trafford's crowd outside, the home dressing room's air before the game (quiet:
the sheet), the cards' low hits, the crowd going up for the visitors' goals only (thin, far away, an away end), the
half-time whistle and the boos, the chant of Carrick's name turning into boos at full time; the row is dry and close
(every line its own, the room under them); "Don't!" and then nothing but the room tone. No music.
python3 -m studio.film v3-bournemouth sound -> build/episode_audio.wav"""
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
    return s.get("plate") or s.get("draw")


def ambience(bus):
    for a, b in spans(lambda s: plate_of(s) == "AW"):
        A.bed(bus, "ambience/wind", a, b, -48)
        A.bed(bus, "crowd/crowd-large", a, b, -44, lowpass=1600)
    for a, b in spans(lambda s: plate_of(s) in ("W", "D", "team_sheet")):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -50, lowpass=2600)
    for a, b in spans(lambda s: plate_of(s) == "HS" or str(plate_of(s)).startswith("card_")):
        A.bed(bus, "crowd/crowd-large", a, b, -40, lowpass=3000)


def foley(bus):
    for s in SHOTS:
        if s["kind"] == "insert" and str(s["draw"]).startswith("card_"):
            A.ev(bus, "impacts/tom-hit", s["t"] + 0.02, -33, semis=-5, lowpass=900)
    # the visitors' goals: a thin cheer from one corner
    for k in ("cut_g1", "cut_g2", "cut_g3"):
        A.ev(bus, "crowd/applause-big", m(k) - 0.3, -40, lowpass=2500, highpass=400, dur=2.2, pan=0.6)
    A.ev(bus, "sport/whistle-ref", m("cut_ht") - 0.25, -36)
    A.ev(bus, "sport/whistle-ref", m("cut_ft") - 0.25, -35)
    # Carrick's name, then the boos (the crowd bed pitched down, swelling on "booed")
    A.bed(bus, "crowd/crowd-large", m("cut_ft") + 0.2, wt("B10", "then"), -38, lowpass=2200, fin=0.4, fout=0.3)
    A.bed(bus, "crowd/crowd-large", wt("B10", "then"), m("cut_room"), -34, lowpass=900, fin=0.3, fout=0.15)
    # the sheet: a finger on paper; Bruno sits
    A.ev(bus, "paper/paper-short", wt("B01", "one") + 0.4, -46)
    A.ev(bus, "cloth/cloth-b", m("cut_look") + 0.3, -46)
    # the row: shuffles and a slammed locker; the quiet
    for k, key in enumerate(("cut_b12", "cut_b13", "cut_b15", "cut_b18", "cut_b19", "cut_b21")):
        A.ev(bus, "cloth/cloth-" + "abcdef"[k], m(key) + 0.03, -44, pan=(-0.3 + 0.12 * k))
    A.ev(bus, "impacts/tom-hit", m("cut_b18") + 0.05, -40, semis=4, lowpass=2500)
    A.ev(bus, "cloth/cloth-c", m("cut_b22") + 0.05, -44)


def main():
    dlg, amb, fx = A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.35, room_db=-22)
    ambience(amb)
    foley(fx)
    A.master(dlg, [amb, fx], [])
