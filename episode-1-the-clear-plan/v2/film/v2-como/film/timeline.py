"""The dialogue edit for Leeds, Como and the plan: the narrator carries every result and every silent gag (the clap
in the office, the lake, the goals, the corridor, the laptop), cuts land on his words, and the only held beats are
the comedy's (everyone for the door on the pen's click, the shuffle back, the lens lowered). A mark on a gap names
the moment the gap starts; the props' marks keep their names from the first cut (flip_leeds, cut_go, cut_hold,
w_press, w_together, cut_par1, cut_b05, cut_par2, cut_c08, cut_corr, board_roll, type1, type2, aplan, lid)."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    # ---- Leeds, 18 October; the office
    ("gap", 0.3, "open"), ("line", "C01"),                # LEEDS 0-1 UNITED... 1-1
    ("gap", 0.25, "cut_office"), ("line", "C02"),         # the three of them watch the screen
    ("gap", 0.5, "whistle"),                  # the final whistle on the telly
    ("gap", 0.9, "cut_clap"),                 # Wilcox: one tiny clap
    ("gap", 0.9, "cut_wi_sees"),              # he sees Martínez
    ("gap", 1.1, "cut_brush"),                # ...and turns it into brushing dust off his trousers
    ("gap", 1.2, "cut_li_eyes"),              # Martínez points: I'm watching you
    ("gap", 0.9, "cut_omar"),                 # Berrada
    ("gap", 0.4, "cut_bluemug"),              # quietly removes a blue mug from the desk
    ("line", "C03"),            # "Nobody said anything. Everybody noticed."
    # ---- Como, 21 October: the lake, the ground, the board
    ("gap", 0.3, "cut_lake"), ("line", "C04"),            # "Three days later: Como. A lake. A stadium. A plan."
    ("gap", 0.5),
    ("gap", 0.15, "cut_c05"), ("line", "C05"),            # "Stay compact. Make them play in front of us."
    ("gap", 0.2, "cut_c06"), ("line", "C06"),             # "And when do we go?"
    ("gap", 0.2, "cut_c07"), ("line", "C07"),             # "When the moment is right."
    ("gap", 0.25, "cut_c08m"), ("line", "C08"),           # "Is there a signal?"
    ("gap", 0.3),
    ("gap", 0.8, "cut_click"),                # Carrick clicks his pen
    ("gap", 1.3, "cut_go"),                   # everyone goes for the door
    ("gap", 0.5, "cut_c09"), ("line", "C09"),             # "That wasn't it."
    ("gap", 0.1),
    ("gap", 2.1, "cut_hold"),                 # they shuffle back
    # ---- the early goal
    ("gap", 0.1, "cut_g1"), ("line", "C10"),              # 2' NICO PAZ: "Nico Paz scored after two minutes."
    ("gap", 0.25, "cut_touch"), ("line", "C11"),          # Carrick on the touchline: "The plan had survived..."
    # ---- half-time
    ("gap", 0.3, "cut_board_ht"),             # COMPACT crossed out...
    ("gap", 0.25, "w_press"), ("line", "C12"),            # ...PRESS, as he says "We need to be braver."
    ("gap", 1.3, "w_together"),               # ...TOGETHER underneath
    ("gap", 0.15, "cut_c13"), ("line", "C13"),            # "So we go to them?"
    ("gap", 0.2, "cut_c14"), ("line", "C14"),             # "Together."
    ("gap", 0.25, "cut_c15"), ("line", "C15"),            # "Everyone?"
    ("gap", 0.25, "cut_c16"), ("line", "C16"),            # "That's usually what together means."
    ("gap", 0.3, "cut_cap"),                  # Maguire, still on the dry pen: the cap comes off in his hand
    ("gap", 1.6),
    # ---- the collapse
    ("gap", 0.1, "cut_g2"), ("line", "C17"),              # 49' DOUVIKAS 2-0; "On the board, the arrows were perfect."
    ("gap", 0.3, "cut_g3"), ("line", "C18"),              # 57' PAZ 3-0
    ("gap", 0.9, "cut_ck_board"),             # Carrick looks at the board
    ("gap", 0.9, "cut_br_ck"),                # Bruno looks at Carrick. Cut before either speaks
    ("gap", 0.15, "cut_g4"), ("line", "C19"),              # 76' RAMÓN 4-0; the heroic push
    ("gap", 0.25), ("line", "C20"),           # "It's still looking."
    ("gap", 0.3, "cut_g5"), ("line", "C21"),              # 90+1' ZIRKZEE 4-1; full time
    # ---- the dressing-room button
    ("gap", 0.3, "cut_btn"),                  # Bruno standing right; Carrick at the door
    ("gap", 0.5, "cut_c22"), ("line", "C22"),             # "Not ideal."
    ("gap", 0.3, "cut_c23"), ("line", "C23"),             # "Michael. We've used that one."
    ("gap", 0.3),
    ("gap", 1.3, "cut_sees"),                 # Carrick sees the documentary camera; the lens is lowered
    # ---- the interviews: the real positions, paraphrased by the narrator; then the parody
    ("gap", 0.2, "cut_par1"), ("line", "C24"),            # Bruno's position (the card, the narrator)
    ("gap", 0.5),
    ("gap", 0.3, "cut_b05"), ("line", "C25"),             # PARODY: "We gave them space..."
    ("gap", 0.3), ("mark", "look_back"),      # he looks back towards the dressing-room door
    ("gap", 0.6), ("line", "C26"),            # "I just wanted us to make them uncomfortable..."
    ("gap", 0.4),
    ("gap", 0.2, "cut_par2"), ("line", "C27"),            # Carrick's response (the card, the narrator)
    ("gap", 0.5),
    ("gap", 0.3, "cut_c08"), ("line", "C28"),             # PARODY: "I can draw the arrows..."
    ("gap", 1.6, "cut_magnets"),              # his board: only two magnets followed the arrows
    ("gap", 0.15, "cut_c09r"), ("line", "C29"),            # "We'll review it."
    ("gap", 0.6),
    # ---- the distance; the clear plan
    ("gap", 0.2, "cut_corr"),                 # Bruno leaves one end, Carrick the other
    ("gap", 0.6), ("line", "C30"),            # "The board was cleaned overnight..."
    ("mark", "board_roll"),                   # the board rolls through: CLARITY / ALIGNMENT / SUSTAINABILITY / AGILITY
    ("gap", 2.8),
    ("gap", 0.4, "cut_bd"), ("line", "C31"),              # Wilcox, alone, late: "We've got a very clear plan."
    ("gap", 0.4),
    ("gap", 0.3, "cut_laptop"),               # CLEAR PLAN.pptx...
    ("gap", 0.6, "type1"), ("line", "C32"),               # ...FINAL - FINAL 2: "The plan was saved. As final. Final two."
    ("gap", 1.0, "type2"),                    # CLEAR deleted from the title
    ("gap", 1.3, "aplan"),                    # A PLAN
    ("gap", 0.9, "lid"),                      # he closes the laptop
    ("gap", 2.2, "cut_mugdark"),              # the dark; the white mug lit (the last-chance meeting follows, then
]                                             # the credits: episodes/v2-lastchance)

TL = build(SEQ, L)


def _wt(lid, word, k=1):
    """when the k-th `word` of a line starts"""
    n = 0
    for w in L[lid]["words"]:
        if w["w"] == word:
            n += 1
            if n == k:
                return TL["lines"][lid]["start"] + w["s"]
    raise KeyError((lid, word, k))


# cuts that land on the narrator's words
TL["marks"].update(flip_leeds=_wt("C01", "equalised") - 0.05, est_como=_wt("C04", "stadium") - 0.08,
                   cut_compact=_wt("C04", "plan") - 0.08, cut_tac=_wt("C17", "on") - 0.08,
                   cut_push=_wt("C19", "the") - 0.08, cut_zz=_wt("C21", "joshua") - 0.08,
                   cut_ft=_wt("C21", "the", 1) - 0.08)
