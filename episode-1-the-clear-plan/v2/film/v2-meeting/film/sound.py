"""The meeting's soundtrack: Carrington's open air under the narrator, the boardroom's air-conditioning, the
corporate theme under Wilcox's pitch that stops dead on "who are we signing?", a soft stamp on each buzzword, the
tablet's spinner ticking, the objectives sliding in, the video-call chime and its hang-up tones, and the title boom.
python3 -m studio.film v2-meeting sound -> build/episode_audio.wav"""
import json

import numpy as np

from studio.film import audio as A
from studio.film import ep
from studio.film.shots import Marks
from film.direction import SHOTS
from film.props import obj_shown, OBJ
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt = T.m, T.ls, T.le, T.wt


def tone(freqs, dur, level, att=0.01, rel=0.25):
    n = int(dur * A.SR)
    tt = np.arange(n, dtype=np.float32) / A.SR
    y = sum(np.sin(2 * np.pi * f * tt) * (0.6 ** i) for i, f in enumerate(freqs)).astype(np.float32)
    y *= A.fade(n, min(att, dur * 0.3), min(rel, dur * 0.6))
    return A.at_level(np.stack([y, y], 1), level)


def ambience(bus):
    A.bed(bus, "ambience/wind", 0.0, m("cut_room"), -50, lowpass=2500, fout=0.05)
    A.bed(bus, "ambience/street-distant", 0.0, m("cut_room"), -56, lowpass=1800, fout=0.05)
    A.bed(bus, "ambience/room-tone-hvac", m("cut_room"), m("cut_title"), -53, lowpass=3600)
    A.bed(bus, "ambience/city-through-window", m("cut_room"), m("cut_title"), -64, lowpass=2200)


def foley(bus):
    # Wilcox's tablet: taps, then the spinner ticking
    A.ev(bus, "foley/pen-click-b", le("M05") - 0.2, -42, semis=8, highpass=900)
    A.ev(bus, "foley/pen-click-b", le("M05") + 0.05, -44, semis=10, highpass=900)
    t = m("cut_tab") + 0.2
    while t < m("cut_wi3") - 0.1:
        bus.add(A.at_level(A.beep(2100.0, 0.03) * 0.5, -54), t)
        t += 0.42
    # the battery warning on "three per cent"
    bus.add(A.at_level(A.beep(880.0, 0.09), -40), wt("M06", "three"))
    bus.add(A.at_level(A.beep(660.0, 0.12), -40), wt("M06", "three") + 0.13)
    # the buzzwords: a low stamp on each
    for w in ("clarity", "alignment", "sustainability", "agility"):
        A.ev(bus, "impacts/tom-hit", wt("M07", w) - 0.02, -34, semis=-7, lowpass=800)
    # Carrick's arms; Jim's points
    A.ev(bus, "cloth/cloth-b", m("cut_ck3") + 0.05, -47)
    A.ev(bus, "cloth/cloth-c", m("cut_n3") + 0.02, -46)
    A.ev(bus, "cloth/cloth-e", m("cut_jim4") + 0.02, -46)
    # the display connects: a bright two-note, then each objective slides in with a soft tick
    bus.add(tone([880, 1320], 0.18, -38), m("cut_obj") + 0.02)
    bus.add(tone([1320, 1760], 0.22, -38), m("cut_obj") + 0.16)
    last = 0
    t = m("cut_obj")
    while t < m("cut_ck8"):
        n = obj_shown(t)
        if n > last:
            if n == len(OBJ):
                A.ev(bus, "impacts/tom-hit", t, -30, semis=-3, lowpass=1200)
            else:
                A.ev(bus, "paper/paper-short", t, -46, semis=6, highpass=1500, dur=0.12)
            last = n
        t += 1 / 30
    # the video call: a ringtone while it rings, a join blip, then three falling tones as it ends
    t = m("chime")
    while t < m("cut_call"):
        bus.add(tone([987.8, 1975.5], 0.16, -34), t)
        bus.add(tone([1318.5, 2637.0], 0.22, -34), t + 0.18)
        t += 0.62
    bus.add(tone([659.3, 987.8], 0.14, -36), m("cut_call") + 0.02)
    for k, f in enumerate((880.0, 660.0, 440.0)):
        bus.add(tone([f], 0.16, -34), m("ended") + 0.04 + 0.17 * k)
    # the title: the big boom
    bus.add(A.at_level(A.big_boom(1.0), -16), m("cut_title"))


def theme(dur, chords, bpm=104, level=-30):
    """the corporate theme: soft piano on the beat over long strings (as the month uses it)"""
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
    y *= A.fade(n, 0.5, 0.004)[:, None]
    return A.at_level(y, level)


def music(bus):
    # the open: a documentary swell under the narrator, out as the boardroom starts
    a, b = 0.0, m("cut_wi1")
    st = A.strings([A.note("D2"), A.note("A2"), A.note("D3"), A.note("F#3")], b - a + 0.6, 1.2, 1.4, 1500)
    st = st[:int((b - a) * A.SR)] * A.fade(int((b - a) * A.SR), 1.0, 1.2)
    bus.add(A.at_level(np.stack([st, st], 1), -31), a)
    # Wilcox's pitch: the corporate theme, stopped dead on "signing"
    up = [("C3", "E3", "G3", "C4"), ("A2", "E3", "A3", "C4"), ("F2", "C3", "F3", "A3"), ("G2", "D3", "G3", "B3")]
    a, b = m("cut_wi1") + 0.1, we_signing()
    bus.add(theme(b - a, up + up[:2], level=-31), a)
    # the objectives: the theme again, briefly, pleased with itself
    a, b = m("cut_obj"), ls("M29")
    bus.add(theme(b - a, up[:2], level=-33), a)
    # the title: the chord under the boom
    n = TL["total"] - m("cut_title")
    y = A.title_sting(n + 0.2)[:int(n * A.SR)]
    y *= A.fade(len(y), 0.0, 0.8)[:, None]
    bus.add(A.at_level(y, -27), m("cut_title"))


def we_signing():
    return T.we("M08", "signing")


def main():
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.35, room_db=-23)
    ambience(amb)
    foley(fx)
    music(mus)
    A.master(dlg, [amb, fx], [mus])
