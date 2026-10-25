"""The dialogue edit for Bournemouth: the narrator opens on the ground and lands "team sheet" on the sheet; the team
talk is four quick lines and a held look; the match is four cards under the narrator and Cunha on the touchline; the
row is the fastest cutting in the episode (no gap over a fifth of a second until Carrick tries to speak), and it ends
on one word from the whole room. A mark on a gap names the moment the gap starts."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    # ---- Old Trafford; the team sheet
    ("gap", 0.25, "open"), ("line", "B01"),               # "Four days later. Old Trafford... missing from the team sheet."
    ("gap", 0.3, "cut_b02"), ("line", "B02"),             # "Michael. My name is not on here."
    ("gap", 0.25, "cut_b03"), ("line", "B03"),            # "It's a pure football decision."
    ("gap", 0.3, "cut_b04"), ("line", "B04"),             # "Is this because of what I said?"
    ("gap", 0.5, "cut_b05"), ("line", "B05"),             # "Tactics are for the staff, Bruno. That one's not on me."
    ("gap", 0.3, "cut_look"),                             # Bruno's face
    ("gap", 1.2),
    # ---- the match
    ("gap", 0.1, "cut_g1"), ("line", "B06"),              # 38' RAYAN 0-1
    ("gap", 0.25, "cut_g2"), ("line", "B07"),             # 43' TAVERNIER 0-2
    ("gap", 0.3, "cut_ht"), ("line", "B08"),              # half-time: Cunha on the touchline
    ("gap", 0.6, "cut_g3"), ("line", "B09"),              # 71' EVANILSON 0-3
    ("gap", 0.3, "cut_ft"), ("line", "B10"),              # full time: Carrick on the touchline; the boos
    ("gap", 0.6),
    # ---- the row
    ("gap", 0.15, "cut_room"), ("line", "B11"),           # "Who was marking Rayan?" (the room)
    ("gap", 0.05, "cut_b12"), ("line", "B12"),            # "I was on the bench!"
    ("gap", 0.05, "cut_b13"), ("line", "B13"),            # "I asked for minutes. Not these minutes!"
    ("gap", 0.1, "cut_b14"), ("line", "B14"),             # "Can everyone just calm down?"
    ("gap", 0.05, "cut_b15"), ("line", "B15"),            # "Nobody's calm, Ben!"
    ("gap", 0.05, "cut_b16"), ("line", "B16"),            # "I'm calm!"
    ("gap", 0.2, "cut_b17"), ("line", "B17"),             # "If I was playing..."
    ("gap", 0.05, "cut_b18"), ("line", "B18"),            # "Don't start! It's upstairs! I said it! Upstairs!"
    ("gap", 0.05, "cut_b19"), ("line", "B19"),            # "You said it on television!"
    ("gap", 0.05, "cut_b20"), ("line", "B20"),            # "So did I!"
    ("gap", 0.05, "cut_b21"), ("line", "B21"),            # "We know, Bruno!"
    ("gap", 0.15, "cut_b22"), ("line", "B22"),            # "Enough! Enough!"
    ("gap", 0.6, "cut_quiet"),                            # quiet. Everyone looks at him
    ("gap", 0.3, "cut_b23"), ("line", "B23"),             # "Look. It's..."
    ("gap", 0.5, "cut_b24"), ("line", "B24"),             # "Not..."
    ("gap", 0.08, "cut_b25"), ("line", "B25"),            # the whole room: "Don't!"
    ("gap", 1.3, "cut_end"),                              # Carrick, mouth still open; the end title follows
]

TL = build(SEQ, L)
