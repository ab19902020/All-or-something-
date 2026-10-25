"""The dialogue edit for Hull and the month: the narrator carries every result (the score cards land under his
lines, no silent establishing shots), the dressing room answers each one in the same camera, and the only held
beats are the comedy's (the silence before "Execution?", "Not..." left hanging). A mark on a gap names the moment
the gap starts."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    # ---- Hull: the ground, the team talk
    ("gap", 0.3, "open"),                     # the ground at dusk: HULL AWAY
    ("line", "H01"),                          # "Matchday one. Hull City away..."
    ("gap", 0.2, "cut_talk"),                 # the dressing room before kick-off: Carrick at the board
    ("gap", 0.35), ("line", "H02"),           # "Newly promoted team... set pieces."
    ("gap", 0.15, "cut_mg0"), ("line", "H03"),            # Maguire: "Set pieces. Got it."
    ("gap", 0.15), ("line", "H04"),           # "He had got it."
    # ---- the match
    ("gap", 0.15, "cut_m1"),                  # the broadcast: the corner, the goal, 1-0 17'
    ("gap", 0.9), ("line", "H05"),            # "Seventeen minutes in, Hull scored."
    ("gap", 1.3),
    ("gap", 0.2, "cut_br1"), ("line", "H06"),             # Bruno on the touchline: "Come on, boys, wake up!"
    ("gap", 0.2, "cut_m2"),                   # another set piece; 2-0 38'
    ("gap", 0.9), ("line", "H07"),            # "Thirty-eight minutes in, they scored again."
    ("gap", 1.3),
    ("gap", 0.2, "cut_br2"), ("line", "H08"),             # Bruno: "Too easy! That's too easy!"
    ("gap", 0.2, "cut_ft"), ("line", "H09"),              # FULL TIME: HULL 2-0 UNITED: "...described as progress."
    # ---- the dressing room
    ("gap", 0.3, "cut_dr"),                   # nobody looks at anybody
    ("gap", 0.6, "cut_ck1"), ("line", "H10"),             # "Not ideal."
    ("gap", 0.15, "cut_br3"), ("line", "H11"),            # "Not ideal?! He literally said set pieces..."
    ("gap", 0.15, "cut_mg1"), ("line", "H12"),            # "Two set pieces."
    ("gap", 0.12, "cut_br4"), ("line", "H13"),            # "Then how have we conceded two?!"
    ("gap", 0.15),
    ("gap", 0.9, "cut_silence"),              # every head to Maguire
    ("gap", 0.05, "cut_mg2"), ("line", "H14"),            # "Execution?"
    ("gap", 0.327, "cut_ck2"), ("line", "H15"),  # (0.35 less the new "Execution?" take's extra 0.023 s)            # "It's one game..."
    ("gap", 0.2, "cut_board1"),               # the board: SET PIECES...
    ("gap", 0.25), ("mark", "wipe"),          # ...wiped as he speaks; it stays faintly there
    ("line", "H16"),                          # "They could, however, judge the first one."
    ("mark", "board_push"),
    ("gap", 1.6, "write_basics"),             # BASICS over it
    # ---- Ipswich
    ("gap", 0.1, "cut_ips"), ("line", "R01"),             # UNITED 5-2 IPSWICH: "...Bruno Fernandes scored a hat-trick."
    ("gap", 1.4, "cut_ips_wide"),             # the room pleased with itself; Bruno clapping
    ("gap", 0.15, "cut_cu1"), ("line", "R02"),             # Cunha: "Hat-trick. Captain."
    ("gap", 0.15, "cut_ck_ips"), ("line", "R03"),         # "That's more like it."
    ("gap", 0.2, "cut_wi1"), ("line", "R04"),             # Wilcox in the doorway: "Gentlemen, fantastic! This is the plan."
    ("gap", 0.15, "cut_tab1"), ("line", "R05"),           # the tablet into the lens: "The plan had been updated at full time."
    ("gap", 0.5),
    # ---- Everton
    ("gap", 0.1, "cut_eve"), ("line", "R06"),             # EVERTON 1-2 UNITED, 88' ŠEŠKO...
    ("gap", 1.2, "flip_eve"),                 # ...90+6': 2-2
    ("gap", 0.2, "cut_se1"), ("line", "R07"),             # Šeško: "Yes! I thought I scored the winner."
    ("gap", 0.15, "cut_mg_eve"), ("line", "R08"),         # Maguire: "You did. For about eight minutes."
    ("gap", 0.25, "cut_se2"), ("line", "R09"),            # "Thanks, Harry."
    ("gap", 0.25, "cut_ck_eve"), ("line", "R10"),         # "Positive point away from home."
    ("gap", 0.2, "cut_eve_wide"), ("line", "R11"),        # the room: "It was a point. It was away from home."
    # ---- Sabah
    ("gap", 0.25, "cut_sab"), ("line", "R12"),            # UNITED 4-0 SABAH
    ("gap", 0.2, "cut_li1"), ("line", "R13"),             # Martínez: "I scored!"
    ("gap", 0.15, "cut_ck_sab"), ("line", "R14"),         # "Don't encourage him."
    ("gap", 0.15, "cut_wi2"), ("line", "R15"),            # Wilcox: "European DNA."
    ("gap", 1.9, "cut_tab2"),                 # THE PLAN: NOW WITH EUROPEAN DNA, moved out of Martínez's way
    ("gap", 0.3, "cut_ck_smile"), ("line", "R16"),        # Carrick's smallest genuine smile: "...checked the footage twice."
    # ---- City
    ("gap", 0.3, "cut_city"), ("line", "R17"),            # UNITED 0-1 MAN CITY: "...a quiet afternoon."
    ("gap", 0.25, "cut_li2"), ("line", "R18"),            # Martínez: "We nearly scored."
    ("gap", 0.15, "cut_br5"), ("line", "R19"),            # Bruno: "Nearly does not count."
    ("gap", 0.15, "cut_mg3"), ("line", "R20"),            # Maguire: "It counts in expected goals."
    ("gap", 0.2),
    ("gap", 0.9, "cut_turn"),                 # every head turns to him
    ("gap", 0.05, "cut_mg4"), ("line", "R21"),            # "What? I've been listening to Jason."
    ("gap", 0.25, "cut_charge"), ("line", "R22"),         # the tablet on charge: "Nobody remembers plugging it in."
    # ---- Brighton
    ("gap", 0.3, "cut_bri"), ("line", "R23"),             # 2-0 (Lacey 8', Mount 10')
    ("gap", 0.1), ("mark", "flip_bri"), ("line", "R24"),  # ...2-3: "Brighton won three-two."
    ("gap", 0.3, "cut_bri_shirt"), ("line", "R25"),       # Lacey (off, his shirt on its hook): "We were two-nil up..."
    ("gap", 0.2, "cut_mo1"), ("line", "R26"),             # Mount: "You've learnt Manchester United very quickly."
    ("gap", 0.25, "cut_br6"), ("line", "R27"),            # Bruno: "Michael, do not say not ideal."
    ("gap", 0.2, "cut_ck_not"), ("line", "R28"),          # "Not..."
    ("gap", 0.8), ("line", "R29"),            # "He didn't."
    # ---- Fulham
    ("gap", 0.3, "cut_ful"), ("line", "R30"),             # FULHAM 1-1 UNITED: "...at the wrong end."
    ("gap", 0.25, "cut_cu2"), ("line", "R31"),            # Cunha: "Good finish. Mine. Sorry."
    ("gap", 0.2, "cut_br7"), ("line", "R32"),             # Bruno: "Five points. From five games..."
    ("gap", 0.2, "cut_ck_ful"), ("line", "R33"),          # "Right. International break..."
    ("gap", 0.3, "cut_int"), ("line", "R34"),             # to the documentary camera: (off) "How would you describe..."
    ("gap", 0.25), ("line", "R35"),           # "There have been positives."
    ("gap", 0.25), ("line", "R36"),           # (off) "Such as?"
    ("gap", 0.5), ("line", "R37"),            # "Sabah."
    ("gap", 0.6, "cut_cal"), ("line", "R38"),             # the calendar: "Sabah have not commented."
    # ---- Tottenham, the reset, Atlético
    ("gap", 0.3, "cut_tot"), ("line", "R39"),             # UNITED 1-0 TOTTENHAM ... 90+2' 1-1
    ("gap", 0.25, "cut_reset"), ("line", "R40"),          # RESET taped over BASICS: "The results returned unchanged."
    ("gap", 0.1), ("mark", "tape"),           # a corner lets go
    ("gap", 1.0),
    ("gap", 0.1, "cut_atl"), ("line", "R41"),             # ATLÉTICO 1-0 UNITED, 1'... 2-0
    ("gap", 0.4, "cut_mug"), ("line", "R42"),             # the white mug; Carrington beyond, the hedge
    ("gap", 0.6),
]

TL = build(SEQ, L)
