"""Part A's soundtrack: the dressing room's air-conditioning under every room shot (cut dead on the cards), the
grounds (a street on matchday, a crowd behind the walls, wind at the away grounds at dusk), a soft low hit as each
result lands, the foley the pictures ask for (the eraser, the marker, the tape letting go, the page turning, the
camera flashes), and the corporate theme the opening set up: it comes back for Ipswich and Sabah and winds down
after City; Brighton's "Not..." and the hold after it have no music at all.
python3 -m studio.film aos-ep1-a sound -> build/episode_audio.wav"""
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


def spans(kinds):
    """(start, end) of every shot whose draw / plate is in kinds"""
    out = []
    for s in SHOTS:
        key = s.get("draw") if s["kind"] in ("insert", "single") else s.get("plate")
        if s["kind"] == "single" and s.get("bg", (None,))[0] in ("W", "D"):
            key = "room"
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
    for a, b in spans({"room", "board_hull", "board_reset", "lacey_shirt", "calendar", "tab_dna"}):
        if a >= m("cut_empty") - 1e-3 and b <= m("est_tot") + 1e-3:
            continue
        A.bed(bus, "ambience/room-tone-hvac", a, b, -50, lowpass=3200)
    for a, b in spans({"ST"}):
        A.bed(bus, "ambience/street-distant", a, b, -40)
        A.bed(bus, "crowd/crowd-large", a, b, -52, lowpass=1800)
    for a, b in spans({"OT"}):
        A.bed(bus, "crowd/crowd-large", a, b, -38, lowpass=4000)
    for a, b in spans({"AW"}):
        A.bed(bus, "ambience/wind", a, b, -47)
        A.bed(bus, "crowd/crowd-large", a, b, -50, lowpass=1500)
    for a, b in spans({"MZ"}):
        A.bed(bus, "ambience/room-tone-hvac", a, b, -47, highpass=200)
    for a, b in spans({"tab_charge"}):
        A.bed(bus, "ambience/city-through-window", a, b, -55, lowpass=2500)
    for a, b in spans({"mug"}):
        A.bed(bus, "ambience/city-through-window", a, b, -52, lowpass=2600)
        A.bed(bus, "ambience/wind", a, b, -60)


def foley(bus):
    # the cards: a soft low hit as each result lands; a second, smaller one when the score changes
    for s in SHOTS:
        if s["kind"] == "insert" and str(s["draw"]).startswith("card_"):
            A.ev(bus, "impacts/tom-hit", s["t"] + 0.02, -30, semis=-5, lowpass=900)
    for k in ("flip_eve", "flip_bri", "flip_tot", "flip_atl"):
        A.ev(bus, "impacts/tom-hit", m(k), -33, semis=-2, lowpass=1200)
    # Hull: they drift back in; a bag dropped on a bench, cloth
    A.ev(bus, "cloth/cloth-d", 0.3, -46, pan=0.3)
    A.ev(bus, "foley/cup-down", 0.9, -44, pan=-0.4, semis=-7, lowpass=1500)
    A.ev(bus, "creaks/creak-small", 1.6, -50, pan=0.2, semis=-3)
    # the board: the eraser squeaking across, the marker writing BASICS
    for k in range(4):
        A.ev(bus, "creaks/creak-short", m("wipe") + 0.05 + 0.24 * k, -44, semis=9 + k, highpass=1200, dur=0.22)
    for k in range(6):
        A.ev(bus, "creaks/creak-small", m("write_basics") + 0.05 + 0.24 * k, -45, semis=12, highpass=2000, dur=0.18)
    A.ev(bus, "foley/pen-click-c", m("write_basics") + 1.7, -40)
    # Wilcox at the door
    A.ev(bus, "doors/door-shut", m("cut_door") + 0.05, -40, pan=-0.4, semis=2, lowpass=3500)
    A.steps(bus, m("cut_door") + 0.4, m("cut_wi1") + 0.2, -46, pace=0.3, pan=-0.3)
    A.ev(bus, "cloth/cloth-c", m("cut_tab1") + 0.15, -45, pan=0.4)
    A.ev(bus, "foley/pen-click-b", m("cut_tab2") + 1.5, -44, semis=6)
    # the tablet charging: a tiny chime
    bus.add(A.at_level(A.beep(1320.0, 0.12) * 0.8, -42), m("cut_charge") + 0.6)
    # the calendar: the page
    A.ev(bus, "paper/page-turn", m("cut_cal") + 0.85, -38)
    # the RESET sheet: paper handled, then the tape letting go and the corner falling
    A.ev(bus, "paper/paper-short", m("cut_reset") + 0.2, -46)
    A.ev(bus, "paper/paper-lower", m("tape") + 0.02, -38)
    # the mixed zone: camera shutters
    rng = np.random.default_rng(13)
    t = m("cut_mz") + 0.1
    while t < m("cut_leeds") - 0.2:
        A.ev(bus, "foley/pen-click-a", t, -42 + rng.uniform(-4, 2), pan=rng.uniform(-0.6, 0.6), semis=rng.uniform(6, 11))
        t += rng.uniform(0.18, 0.7)
    # the lights going off, bank by bank, in the empty room
    for tk in (0.9, 1.6, 2.3):
        A.ev(bus, "foley/pen-click-c", m("cut_empty") + tk, -38, semis=-14, lowpass=1800)
    A.ev(bus, "doors/door-shut", m("cut_empty") + 2.8, -44, pan=-0.4, lowpass=2500)
    # back in the room after the break: bags down
    A.ev(bus, "foley/cup-down", m("cut_return") + 0.3, -44, pan=-0.3, semis=-7, lowpass=1500)
    A.ev(bus, "cloth/cloth-e", m("cut_return") + 0.7, -46, pan=0.3)
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
    # Ipswich: it's the plan
    a, b = m("cut_ips_wide"), m("est_eve")
    bus.add(theme(b - a, up, level=-31), a)
    # Sabah: warmer light, the corporate music briefly returns
    a, b = m("cut_sab_wide"), m("est_city")
    bus.add(theme(b - a, up[1:] + up[:1], level=-32), a)
    # City: it winds down (slower, falling away)
    a, b = m("cut_city_wide"), m("cut_li2") + 1.6
    y = theme(b - a, [("A2", "E3", "A3", "C4"), ("F2", "C3", "F3", "A3")], bpm=70, level=-34)
    y *= np.linspace(1, 0, len(y), dtype=np.float32)[:, None] ** 1.5
    bus.add(y, a)
    # Leeds week: a low held note under the card and the mug, the documentary turning sinister
    a, b = m("cut_leeds"), TL["total"]
    st = A.strings([A.note("D2"), A.note("A2"), A.note("D3")], b - a + 0.5, 1.0, 1.0, 900)[:int((b - a) * A.SR)]
    bus.add(A.at_level(np.stack([st, st], 1), -34), a)


def main():
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.3, room_db=-23)
    ambience(amb)
    foley(fx)
    music(mus)
    A.master(dlg, [amb, fx], [mus])
