"""The dialogue edit: every line in script order with the beats between them, and the marks the shots, the acting
and the sound hang off. A documentary pace for the narrator, sitcom pace for the rows, and room for the silent gags
(the hedge, the slurp, the unzip, the plant going off, the screams, the silence in Omar's office).

All or Something episode one (v2): the title card and the next-episode teaser are out (the episode has its own
title and goes on to Leeds), and every hold of half a second or more is a quarter shorter."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

# a mark on a gap names the moment that gap starts (a cut on the end of a line, then the new shot's lead-in)
SEQ = [
    # ---- 1. the hedge
    ("gap", 0.4, "open"),                     # Carrington at dawn, the slow drone push; strings
    ("line", "L001"), ("gap", 0.3), ("line", "L002"),
    ("gap", 0.6, "cut_hedge"),               # the hedge by the car park. It has binoculars.
    ("line", "L003"),
    ("gap", 0.75, "cut_bino"),                 # the binoculars turn to the lens
    ("line", "L004"),                         # "Shhh. I am not here."
    ("gap", 0.2), ("gap", 0.75, "slurp"),     # a long, loud slurp of mate from inside the hedge
    ("gap", 0.3), ("mark", "cut_title"),      # (no title card in this cut)
    # ---- 2. the evidence (talking head; the conspiracy board)
    ("gap", 0.35, "cut_int1"),
    ("line", "L005"), ("gap", 0.15), ("line", "L006"),
    ("gap", 0.3, "cut_board"),                # whip to the board
    ("line", "L007"), ("gap", 0.15), ("line", "L008"), ("gap", 0.15), ("line", "L009"), ("gap", 0.2),
    ("line", "L010"),                         # "Manchester City."
    ("gap", 0.12), ("gap", 0.64, "cut_compose"),   # he has to compose himself
    ("line", "L011"), ("gap", 0.2), ("line", "L012"),
    ("gap", 0.3, "cut_mug"),                  # the white mug in its evidence bag
    ("line", "L013"),
    ("gap", 0.25, "cut_clap"),
    ("line", "L014"),
    ("gap", 0.12), ("gap", 0.56, "clap"),      # one limp clap
    ("line", "L015"),
    ("gap", 0.45, "cut_spygate"),             # the 2019 back page
    ("line", "L016"),
    ("gap", 0.25, "cut_tutorial"),            # Licho, a second stripe of paint
    ("line", "L017"),
    ("gap", 0.75),
    # ---- 3. the operation
    ("gap", 0.3, "cut_corr"),                 # the corridor; the plant by the door shuffles
    ("line", "L018"),
    ("gap", 0.56), ("gap", 0.15, "cut_plantcu"),
    ("line", "L019"),
    ("gap", 0.3, "cut_office"),               # Wilcox at his desk, on the phone
    ("line", "L020"),
    ("gap", 0.75, "hangup"),                   # he hangs up; looks at the door
    ("gap", 0.2, "cut_lock"),
    ("line", "L021"),
    ("gap", 0.45, "click"),
    ("gap", 0.2, "cut_blinds"),               # the blinds come down; the plant is already in the corner
    ("line", "L022"),
    ("gap", 0.45, "cut_clock"),                # three o'clock
    ("line", "L023"),                         # "...he let it breathe": the unzip, in slow motion
    ("gap", 1.84, "reveal"),                   # a Leeds top. A sigh. Saxophone.
    ("gap", 0.86, "cut_laptop"),               # BBC Sport, Leeds live. Refresh. Refresh.
    ("gap", 0.3, "cut_pray"),
    ("line", "L024"),
    ("gap", 0.3, "cut_eyes"),                 # the plant's leaves part: two eyes
    ("line", "L025"),
    ("gap", 0.3), ("gap", 0.52, "cut_goal"), # GOAL
    ("gap", 0.1, "cut_celebrate"),
    ("line", "L026"),
    ("gap", 0.35, "boom"),                    # the plant goes off
    ("line", "L027"),                         # "I KNEW IT!"
    ("gap", 0.15), ("gap", 0.45, "scream1"), ("gap", 0.45, "scream2"), ("gap", 0.4, "scream3"),
    ("gap", 0.2, "freeze"),
    ("line", "L028"),
    ("gap", 0.52),
    # ---- 4. busted
    ("gap", 0.3, "cut_s4"),
    ("line", "L029"), ("gap", 0.15, "cut_l030"), ("line", "L030"), ("gap", 0.15, "cut_w031"), ("line", "L031"),
    ("gap", 0.15, "cut_l032"), ("line", "L032"), ("gap", 0.15, "cut_w033"), ("line", "L033"),
    ("gap", 0.3, "cut_l034"), ("line", "L034"),
    ("gap", 1.5, "cut_back"),                 # he turns round: WILCOX, signed
    ("gap", 0.15, "cut_l035"), ("line", "L035"),
    ("gap", 0.15, "cut_w036"), ("line", "L036"),
    ("gap", 0.3), ("gap", 0.52, "ping"),      # the laptop pings: a penalty
    ("gap", 0.1, "cut_w037"), ("line", "L037"),
    ("gap", 1.01, "cut_point"),                # Licho, pointing. A long hold.
    ("line", "L038"),
    ("gap", 0.15, "cut_w039"), ("line", "L039"),
    ("gap", 0.2, "cut_l040"), ("line", "L040"),
    ("gap", 0.94, "cut_strain"),               # he tries. Sweat. The eye twitches.
    ("line", "L041"),
    ("gap", 0.35, "cut_l042"), ("line", "L042"),
    ("gap", 0.4),
    # ---- 5. the right of reply
    ("gap", 0.3, "cut_pp"),                   # the tactics room: slide 1 of 214
    ("line", "L043"),
    ("gap", 0.25, "cut_w044"), ("line", "L044"),
    ("gap", 0.25, "cut_l045"), ("line", "L045"),
    ("gap", 0.15, "cut_w046"), ("line", "L046"),
    ("gap", 0.35, "cut_asleep"),              # seventy minutes later: slide 213, Licho asleep
    ("line", "L047"),
    ("gap", 0.75), ("gap", 0.15, "cut_int2"),
    ("line", "L048"),
    ("gap", 0.45, "cut_wth"),                 # Wilcox's talking head
    ("line", "L049"), ("gap", 0.25), ("line", "L050"),
    ("gap", 0.4),
    # ---- 6. going to the top
    ("gap", 0.2, "cut_int3"),
    ("line", "L051"),
    ("gap", 0.3, "cut_ceo"),                  # he bursts into the CEO's office
    ("line", "L052"),
    ("gap", 1.65, "cut_omar"),                 # Omar, in a City scarf. Frozen. One cricket.
    ("gap", 0.15, "cut_l053"), ("line", "L053"),
    ("gap", 0.3, "cut_omar2"), ("line", "L054"),
    ("gap", 0.41),
    # ---- 7. the spy who spied me
    ("gap", 0.3, "cut_night"),
    ("line", "L055"),
    ("gap", 1.05, "cut_tablet"),               # Mac Allister scores for Liverpool
    ("gap", 0.1, "cut_l056"), ("line", "L056"),
    ("gap", 1.05, "cut_plant2"),               # a pot plant in the corner that wasn't there before
    ("gap", 0.05, "cut_w057"), ("line", "L057"),   # "I KNEW IT!"
    ("gap", 0.6, "scream"),
    ("gap", 0.1, "cut_l058"), ("line", "L058"),
    ("gap", 0.15, "cut_w059"), ("line", "L059"),
    ("gap", 0.45, "cut_l060"), ("line", "L060"),
    ("gap", 1.2, "cut_spidey"),               # the two of them pointing at each other: freeze
    ("mark", "cut_hedges"), ("mark", "sip"), ("mark", "cut_end"),   # (the teaser is not in this cut)
]

TL = build(SEQ, L)
