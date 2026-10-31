"""The dialogue edit for Clear the Air: the conversation plays at its own pace (no voice is sped up), cuts land on
the line that answers, and the comedy's beats are held: the doorway dance, a beat after "Progress", the tablet to
camera; halfway, the door bangs and Gary inspects (each verdict gets its reaction), the two fingers, the stamp; then
the reconciliation, the handshake and Gary's last word. A mark on a gap names the moment the gap starts."""
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
    ("gap", 0.1),
    ("gap", 1.85, "cut_door"),                            # smash cut: the doorway. Bruno tries; Jason blocks
    # ---- an honest exchange
    ("gap", 0.2, "cut_a06"), ("line", "A06"),             # "Look. Maybe I could've been clearer."
    ("gap", 0.3, "cut_a07"), ("line", "A07"),             # "And maybe I shouldn't have said it on telly."
    ("gap", 0.3, "cut_a08"), ("line", "A08"),             # "So we're all right?"
    ("gap", 0.25, "cut_a09"), ("line", "A09"),            # "Yes. I still think the tactics were shit."
    ("gap", 0.4, "cut_a10"), ("line", "A10"),             # "Aye. But now you've told me indoors. Progress."
    ("gap", 0.4),
    ("gap", 0.8, "cut_smile"),                            # a tiny, reluctant smile from Bruno
    ("gap", 1.2, "cut_tick"),                             # behind them: RESOLVED, ticked
    ("gap", 1.3, "cut_card2"),                            # Wilcox, to camera: UNITED BEHIND THE MANAGER
    # ---- halfway: the inspection
    ("gap", 0.9, "cut_gary"),                             # the door bangs open: Gary, lanyard, clipboard
    ("gap", 0.15, "cut_a17"), ("line", "A17"),            # "Surprise standards inspection."
    ("gap", 0.25, "cut_a18"), ("line", "A18"),            # "Gary, you're not Ofsted."
    ("gap", 0.3, "cut_g01"), ("line", "G01"),             # "No. I'm worse."
    ("gap", 0.5),
    ("gap", 0.15, "cut_g02"), ("line", "G02"),            # "Manager. Where's the hairdryer?"
    ("gap", 0.2, "cut_g03"), ("line", "G03"),             # "The what?"
    ("gap", 0.25, "cut_g04"), ("line", "G04"),            # "When I played here... You've got a laptop."
    ("gap", 0.35),
    ("gap", 0.15, "cut_g05"), ("line", "G05"),            # "Captain."
    ("gap", 0.1),
    ("gap", 1.0, "cut_arms"),                             # Bruno's arms go up
    ("gap", 0.1, "cut_g06"), ("line", "G06"),             # "There it is."
    ("gap", 0.35),
    ("gap", 0.2, "cut_g07"), ("line", "G07"),             # the board: "One, talk. Two, listen. Three... photo."
    ("gap", 0.4),
    ("gap", 0.15, "cut_a19"), ("line", "A19"),            # "Who's in charge here?"
    ("gap", 0.35, "cut_point"),                           # two fingers at Jason. Together
    ("gap", 1.2),
    ("gap", 0.15, "cut_a20"), ("line", "A20"),            # "It's a collaborative structure."
    ("gap", 0.3, "cut_g08"), ("line", "G08"),             # "United behind the manager. Says the man stood..."
    ("gap", 0.3),
    ("gap", 2.0, "cut_write"),                            # the clipboard, filled in
    ("gap", 0.15, "cut_a21"), ("line", "A21"),            # "Special measures."
    ("gap", 1.0, "cut_stamp"),                            # SPECIAL MEASURES, stamped
    # ---- on the same side
    ("gap", 1.0, "cut_look"),                             # Carrick and Bruno look at each other
    ("gap", 0.2, "cut_a15"), ("line", "A15"),             # "Next time, just come straight to me."
    ("gap", 0.3, "cut_a16"), ("line", "A16"),             # "Move Jason first."
    ("gap", 0.3),
    ("gap", 1.3, "cut_shake"),                            # the handshake
    ("gap", 0.1, "cut_g09"), ("line", "G09"),             # Gary, writing: "Handshake... limp."
    ("gap", 0.9),
    ("gap", 2.2, "cut_black"),                            # black; ALL OR SOMETHING
]

TL = build(SEQ, L)
