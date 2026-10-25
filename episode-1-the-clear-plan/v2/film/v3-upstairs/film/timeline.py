"""The dialogue edit for Upstairs: the narrator takes us from Madrid to the mixed zone, the paraphrase card holds
Martínez's real words, the parody follows at interview pace (the producer's two off-camera questions), the second
interview is one line, and the board meeting plays as quick singles with a beat before "In a sense." A mark on a gap
names the moment the gap starts."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    # ---- Madrid, the mixed zone
    ("gap", 0.25, "open"), ("line", "X01"),               # "Madrid. Two-nil. Afterwards, Lisandro Martinez stopped..."
    ("gap", 0.25, "cut_par"), ("line", "X02"),            # the paraphrase card: upstairs, the technical director
    ("gap", 0.5),
    ("gap", 0.2, "cut_x03"), ("line", "X03"),             # PARODY: "Upstairs?"
    ("gap", 0.3, "cut_x04"), ("line", "X04"),             # "Upstairs." (he points up)
    ("gap", 0.6, "cut_x05"), ("line", "X05"),             # "Who's upstairs?"
    ("gap", 0.2, "cut_x06"), ("line", "X06"),             # "The technical director. I have to be honest..."
    ("gap", 0.4),
    # ---- the second interview
    ("gap", 0.2, "cut_x07"), ("line", "X07"),             # "The next day, he gave a second interview. Just to be sure."
    ("gap", 0.2, "cut_x08"), ("line", "X08"),             # "I am not going to close my mouth."
    ("gap", 0.6),
    # ---- upstairs: the boardroom
    ("gap", 0.2, "cut_board"), ("line", "X09"),           # "Upstairs, both interviews were watched. Several times."
    ("gap", 0.2, "cut_x10"), ("line", "X10"),             # "Upstairs. Who's upstairs?"
    ("gap", 0.35, "cut_x11"), ("line", "X11"),            # "Technically... we are."
    ("gap", 0.35, "cut_x12"), ("line", "X12"),            # "And the technical director?"
    ("gap", 0.2, "cut_x13"), ("line", "X13"),             # "Could be anyone, Jim."
    ("gap", 0.25, "cut_x14"), ("line", "X14"),            # "It's you, Jason."
    ("gap", 0.7, "cut_x15"), ("line", "X15"),             # "In a sense."
    ("gap", 0.35, "cut_x16"), ("line", "X16"),            # "Fine him. And I want a statement."
    ("gap", 0.2, "cut_x17"), ("line", "X17"),             # "An apology?"
    ("gap", 0.2, "cut_x18"), ("line", "X18"),             # "A statement. With sorry in it. Somewhere."
    ("gap", 0.5),
    # ---- the statement; Martínez's new theory (The Mole follows)
    ("gap", 0.2, "cut_x19"), ("line", "X19"),             # the statement card
    ("gap", 0.3, "cut_x20"), ("line", "X20"),             # "Lisandro now had a new theory about upstairs."
    ("gap", 1.1, "end"),                                  # his eyes narrow; cut to the hedge
]

TL = build(SEQ, L)
