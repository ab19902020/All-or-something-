"""Hull and the month: the soundtrack. The dressing room's air-conditioning under every room shot, Hull's ground at
dusk, the match (a crowd behind the broadcast, the whistle, the kick, the home end going up for each goal),
Bruno's touchline under the noise, a soft low hit as each result lands, the foley the pictures ask for (the eraser,
the marker, the tape letting go, the page turning), and the corporate theme: it comes back for Ipswich and Sabah and
winds down after City; Brighton's "Not..." has no music at all; low strings under the mug into The Mole.
python3 -m studio.film v2-month sound -> build/episode_audio.wav"""
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

ROOM = {"room", "board_hull", "board_reset", "lacey_shirt", "calendar", "tab_dna"}


def spans(kinds):
    """(start, end) of every shot whose draw / plate is in kinds (room singles and wides count as "room")"""
    out = []
    for s in SHOTS:
        key = s.get("draw") if s["kind"] in ("insert", "single") else s.get("plate")
        if s["kind"] == "single":
            key = "room" if s.get("bg", (None,))[0] in ("W", "D") else s["bg"][0]
        if s["kind"] == "world" and s.get("plate") == "W":
            key = "room"
        if key in kinds:
            out.append((s["t"], s["end"]))
    merged = []
    for a, b in out:
        if merged and abs(a - merged[-1][1]) < 1e-3:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def ambience(bus):
    for a, b in spans(ROOM):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -50, lowpass=3200)
    # Hull at dusk: wind, the crowd inside the walls
    A.bed(bus, "ambience/wind", 0.0, m("cut_talk"), -47)
    A.bed(bus, "crowd/crowd-large", 0.0, m("cut_talk"), -46, lowpass=1500)
    # before kick-off, the crowd through the dressing-room walls
    A.bed(bus, "crowd/crowd-large", m("cut_talk"), m("cut_m1"), -55, lowpass=700)
    # the match: the broadcast's crowd, the touchline right in it
    A.bed(bus, "crowd/crowd-large", m("cut_m1"), m("cut_ft"), -43, lowpass=4000)
    for a, b in spans({"HS"}):
        A.bed(bus, "crowd/crowd-large", a, b, -33, lowpass=6000)
    A.bed(bus, "ambience/city-through-window", m("cut_charge"), m("cut_bri"), -55, lowpass=2500)
    A.bed(bus, "ambience/city-through-window", m("cut_mug"), TL["total"], -52, lowpass=2600)
    A.bed(bus, "ambience/wind", m("cut_mug"), TL["total"], -60)


def match(bus):
    # the corner is swung in, the header, the net, the home end goes up; then again
    for c, goal in ((m("cut_m1"), 2.25), (m("cut_m2"), 2.6)):
        A.ev(bus, "sport/whistle-ref", c + 0.15, -36, semis=2, highpass=600)
        A.ev(bus, "sport/ball-kick", c + 0.55, -32)
        A.ev(bus, "sport/ball-kick", c + goal - 0.25, -30, semis=-2)
        bus.add(A.at_level(A.looped("crowd/applause-big", 2.6) * A.fade(int(2.6 * A.SR), 0.08, 1.2)[:, None], -35),
                c + goal)
        A.ev(bus, "impacts/tom-hit", c + goal + 0.02, -34, semis=-9, lowpass=500)
    # full time
    A.ev(bus, "sport/whistle-ref", m("cut_ft") + 0.05, -30)
    A.ev(bus, "sport/whistle-ref", m("cut_ft") + 0.45, -30)
    A.ev(bus, "sport/whistle-ref", m("cut_ft") + 0.85, -28, dur=0.9)


def foley(bus):
    # the cards: a soft low hit as each result lands; a second, smaller one when the score changes
    for s in SHOTS:
        if s["kind"] == "insert" and str(s["draw"]).startswith("card_"):
            A.ev(bus, "impacts/tom-hit", s["t"] + 0.02, -30, semis=-5, lowpass=900)
    for t in (m("flip_eve"), m("flip_bri"), wt("R39", "ninety") + 0.1, wt("R41", "lasted")):
        A.ev(bus, "impacts/tom-hit", t, -33, semis=-2, lowpass=1200)
    # the team talk: a marker tapped on the board
    A.ev(bus, "foley/pen-click-c", wt("H02", "set", 1) - 0.1, -42, semis=-3)
    A.ev(bus, "foley/pen-click-c", wt("H02", "pieces", 1) + 0.05, -44, semis=-3)
    # after the match: bags dropped, cloth
    A.ev(bus, "cloth/cloth-d", m("cut_dr") + 0.05, -46, pan=0.3)
    A.ev(bus, "foley/cup-down", m("cut_dr") + 0.3, -44, pan=-0.4, semis=-7, lowpass=1500)
    # the board: the eraser squeaking across, the marker writing BASICS
    for k in range(4):
        A.ev(bus, "creaks/creak-short", m("wipe") + 0.05 + 0.24 * k, -44, semis=9 + k, highpass=1200, dur=0.22)
    for k in range(6):
        A.ev(bus, "creaks/creak-small", m("write_basics") + 0.05 + 0.24 * k, -45, semis=12, highpass=2000, dur=0.18)
    A.ev(bus, "foley/pen-click-c", m("write_basics") + 1.5, -40)
    # Ipswich: Bruno's clap
    for k in range(4):
        A.ev(bus, "foley/clap-single", m("cut_ips_wide") + 0.3 + 0.32 * k, -40, pan=0.25)
    A.ev(bus, "cloth/cloth-c", m("cut_tab1") + 0.15, -45, pan=0.4)
    A.ev(bus, "foley/pen-click-b", m("cut_tab2") + 1.5, -44, semis=6)
    # the tablet charging: a tiny chime
    bus.add(A.at_level(A.beep(1320.0, 0.12) * 0.8, -42), m("cut_charge") + 0.6)
    # the calendar: the page
    A.ev(bus, "paper/page-turn", m("cut_cal") + 0.85, -38)
    # the RESET sheet: the tape letting go and the corner falling
    A.ev(bus, "paper/paper-short", m("cut_reset") + 0.2, -46)
    A.ev(bus, "paper/paper-lower", m("tape") + 0.02, -38)
    # the mug: a ceramic tap as the focus pulls
    A.ev(bus, "foley/cup-down", m("cut_mug") + 0.4, -44, semis=4, highpass=600)


def theme(dur, chords, bpm=96, level=-30):
    """the corporate theme: soft piano on the beat over long strings"""
    beat = 60.0 / bpm
    n = int(dur * A.SR)
    y = np.zeros((n, 2), np.float32)
    per = dur / len(chords)
    for i, ch in enumerate(chords):
        fs = [A.note(c) for c in ch]
        st = A.strings(fs, per + 0.8, 0.4, 0.8, 1700)
        a = int(i * per * A.SR)
        seg = st[:max(0, min(len(st), n - a))]
        y[a:a + len(seg)] += np.stack([seg, seg], 1) * 0.6
        k = 0
        while k * beat < per:
            f = fs[(k % (len(fs) - 1)) + 1] * 2
            pn = A.piano_note(f, beat * 1.6, 0.7 if k % 2 == 0 else 0.45)
            b = a + int(k * beat * A.SR)
            seg = pn[:max(0, min(len(pn), n - b))]
            y[b:b + len(seg), 0] += seg * 0.5
            y[b:b + len(seg), 1] += seg * 0.45
            k += 1
    y *= A.fade(n, 0.6, 1.2)[:, None]
    return A.at_level(y, level)


def music(bus):
    up = [("C3", "E3", "G3", "C4"), ("A2", "E3", "A3", "C4"), ("F2", "C3", "F3", "A3"), ("G2", "D3", "G3", "B3")]
    # Hull: a low, uneasy pulse under the team talk, out at the first goal
    a, b = m("cut_talk"), m("cut_m1") + 2.2
    st = A.strings([A.note("A1"), A.note("E2"), A.note("A2")], b - a + 0.5, 0.8, 1.0, 900)[:int((b - a) * A.SR)]
    bus.add(A.at_level(np.stack([st, st], 1), -36), a)
    # Ipswich: it's the plan
    a, b = m("cut_ips"), m("cut_eve")
    bus.add(theme(b - a, up, level=-31), a)
    # Sabah: the corporate music briefly returns
    a, b = m("cut_sab"), m("cut_city")
    bus.add(theme(b - a, up[1:] + up[:1], level=-32), a)
    # City: it winds down (slower, falling away)
    a, b = m("cut_city"), m("cut_li2") + 1.6
    y = theme(b - a, [("A2", "E3", "A3", "C4"), ("F2", "C3", "F3", "A3")], bpm=70, level=-34)
    y *= np.linspace(1, 0, len(y), dtype=np.float32)[:, None] ** 1.5
    bus.add(y, a)
    # Leeds week: a low held note under the mug, the documentary turning sinister
    a, b = m("cut_mug"), TL["total"]
    st = A.strings([A.note("D2"), A.note("A2"), A.note("D3")], b - a + 0.5, 1.0, 1.0, 900)[:int((b - a) * A.SR)]
    bus.add(A.at_level(np.stack([st, st], 1), -33), a)


def main():
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.3, room_db=-23)
    ambience(amb)
    match(fx)
    foley(fx)
    music(mus)
    A.master(dlg, [amb, fx], [mus])
