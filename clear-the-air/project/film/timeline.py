"""The dialogue edit for Clear the Air: the conversation plays at its own pace (no voice is sped up), cuts land on
the line that answers, and the comedy's beats are held as the pack asks: 0.4-0.8 s after the doorway sidestep, 0.5 s
after "Progress", 0.6 s after "Fresh start", a full second on the two of them pointing. A mark on a gap names the
moment the gap starts."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    # ---- a private conversation
    ("gap", 0.6, "open"), ("line", "A01"),                # "Carrington. A private meeting... a camera crew."
    ("gap", 0.5, "beckon"),                               # Wilcox waves the camera in; Carrick notices
    ("gap", 0.3, "cut_a02"), ("line", "A02"),             # "Bruno, if you've got a problem with the tactics..."
    ("gap", 0.2, "cut_a03"), ("line", "A03"),             # "I tried. You said your door was always open."
    ("gap", 0.2, "cut_a04"), ("line", "A04"),             # "It is."
    ("gap", 0.4, "cut_a05"), ("line", "A05"),             # "Jason was standing in it."
    # ---- the door
    ("gap", 0.25, "cut_door"),                            # Wilcox in the doorway, the camera eases in
    ("gap", 0.8, "shuffle"),                              # six inches sideways
    ("gap", 0.6),
    ("gap", 0.7, "still_there"),                          # still mostly in the doorway
    # ---- an honest exchange
    ("gap", 0.2, "cut_a06"), ("line", "A06"),             # "Look. Maybe I could've been clearer."
    ("gap", 0.3, "cut_a07"), ("line", "A07"),             # "And maybe I shouldn't have said it on telly."
    ("gap", 0.3, "cut_a08"), ("line", "A08"),             # "So we're all right?"
    ("gap", 0.25, "cut_a09"), ("line", "A09"),            # "Yes. I still think the tactics were shit."
    ("gap", 0.4, "cut_a10"), ("line", "A10"),             # "Aye. But now you've told me indoors. Progress."
    ("gap", 0.5),
    ("gap", 0.9, "cut_smile"),                            # a tiny, reluctant smile from Bruno
    # ---- clearing the air
    ("gap", 1.3, "cut_tick"),                             # behind them: RESOLVED, ticked
    ("gap", 0.4, "cut_spray"),                            # the blue can
    ("gap", 0.45, "psst1"),
    ("gap", 0.75, "psst2"),
    ("gap", 0.6),
    ("gap", 0.15, "cut_a11"), ("line", "A11"),            # "Jason. What are you doing?"
    ("gap", 0.2, "cut_a12"), ("line", "A12"),             # "Clearing the air. It's on the agenda."
    ("gap", 0.3, "cut_a13"), ("line", "A13"),             # "That's air freshener."
    ("gap", 0.25, "cut_a14"), ("line", "A14"),            # "Fresh start."
    ("gap", 0.6),
    ("gap", 1.3, "cut_look"),                             # the first shared look: the same exhausted disbelief
    # ---- the reconciliation
    ("gap", 0.2, "cut_a15"), ("line", "A15"),             # "Next time, just come straight to me."
    ("gap", 0.3, "cut_a16"), ("line", "A16"),             # "Move Jason first."
    ("gap", 0.3),
    ("gap", 1.4, "cut_shake"),                            # the handshake
    ("gap", 1.1, "cut_card"),                             # widen: behind them, Wilcox raises the tablet...
    ("gap", 1.6, "cut_card2"),                            # ...UNITED BEHIND THE MANAGER, for the camera
    # ---- standards inspection
    ("gap", 1.0, "cut_gary"),                             # the door bangs open: Gary, lanyard, clipboard
    ("gap", 0.15, "cut_a17"), ("line", "A17"),            # "Surprise standards inspection."
    ("gap", 0.25, "cut_a18"), ("line", "A18"),            # "Gary, you're not Ofsted."
    ("gap", 0.15, "cut_a19"), ("line", "A19"),            # "Who's in charge here?"
    ("gap", 0.35, "cut_point"),                           # both of them point at Jason. Together
    ("gap", 1.2),
    ("gap", 0.15, "cut_a20"), ("line", "A20"),            # "It's a collaborative structure."
    ("gap", 1.6, "cut_write"),                            # Gary writes, without looking up
    ("gap", 0.15, "cut_a21"), ("line", "A21"),            # "Special measures."
    ("gap", 1.0, "cut_stamp"),                            # SPECIAL MEASURES, stamped
    ("gap", 1.3, "cut_end"),                              # side by side, resigned; Wilcox lowers the can
    ("gap", 0.6, "psst3"),                                # one tiny accidental PSSHT
    ("gap", 2.2, "cut_black"),                            # black; ALL OR SOMETHING
]

TL = build(SEQ, L)
