"""The dialogue edit for part B: Leeds and the silent office cutaway, Como (the briefing, the early goal, half-time,
the collapse, the consolation, the dressing-room button), the interviews (the real positions as paraphrase cards,
the comic ones labelled PARODY DIALOGUE), the corridor, and the clear plan. A mark on a gap names the moment the gap
starts."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

CARD = 2.9                                    # a goal card in the collapse
PARA = 13.0                                   # a paraphrase card: long enough to read twice
CREDITS = 45.2065                                 # set so the whole episode lands on 15:00 (assembly)

SEQ = [
    # ---- 6. Leeds, 18 October
    ("gap", 2.6, "open"),                     # an away ground at dusk: LEEDS AWAY
    ("gap", 2.1, "cut_leeds"),                # 0-1 (Mbeumo 35')...
    ("gap", 2.3, "flip_leeds"),               # ...1-1 (Calvert-Lewin 51')
    ("gap", 2.3, "cut_office"),               # the office: the three of them watch the screen
    ("gap", 1.3, "whistle"),                  # the final whistle on the telly
    ("gap", 1.1, "cut_clap"),                 # Wilcox: one tiny clap
    ("gap", 1.25, "cut_wi_sees"),             # he sees Martínez
    ("gap", 1.3, "cut_brush"),                # ...and turns the clap into brushing dust off his trousers
    ("gap", 1.7, "cut_li_eyes"),              # Martínez: I'm watching you
    ("gap", 1.1, "cut_omar"),                 # Berrada
    ("gap", 1.6, "cut_bluemug"),              # quietly removes a blue mug from the desk
    ("gap", 2.7, "cut_gather"),               # the dressing room: Carrick, last out, towards the exit
    ("gap", 2.0, "cut_whitemug"),             # the white mug on an otherwise empty table
    ("gap", 3.6, "cut_lake"),                 # dissolve: a hotel breakfast cup by a lake-view window
    ("gap", 3.3, "cut_como"),                 # COMO / 21 OCTOBER
    # ---- 7. Como, 21 October: the briefing
    ("gap", 3.0, "est_como"),                 # the ground: COMO AWAY
    ("gap", 3.0, "cut_wide"),                 # the away dressing room: neutral, cold; Carrick by the board
    ("gap", 2.6, "cut_compact"),              # the board: COMPACT; blue magnets face red; the pen almost dry
    ("gap", 0.15, "cut_c01"), ("line", "C01"),            # "Stay compact. Make them play in front of us."
    ("gap", 0.2, "cut_b01"), ("line", "B01"),             # "And when do we go?"
    ("gap", 0.2, "cut_c02"), ("line", "C02"),             # "When the moment is right."
    ("gap", 0.25, "cut_m01"), ("line", "M01"),            # "Is there a signal?"
    ("gap", 0.35),
    ("gap", 0.9, "cut_click"),                # Carrick clicks the pen
    ("gap", 1.7, "cut_go"),                   # everyone goes for the door
    ("gap", 1.0, "cut_c03"), ("line", "C03"),             # he looks at the pen, then the players: "That wasn't it."
    ("gap", 0.2),
    ("gap", 3.0, "cut_hold"),                 # three seconds: they shuffle back
    ("gap", 2.2, "cut_tunnel"),               # the tunnel: the noise
    # ---- the early goal
    ("gap", 3.2, "cut_g1"),                   # 2' NICO PAZ: COMO 1-0 UNITED
    ("gap", 1.6, "cut_br_look"),              # Bruno looks to the bench
    ("gap", 1.1, "cut_pen2"),                 # the pen clicks again, unheard; nobody moves
    ("gap", 0.5, "cut_touch"), ("line", "N03"),           # Carrick on the touchline: "The plan had survived..."
    ("gap", 0.9),
    # ---- half-time
    ("gap", 2.4, "cut_ht"),                   # HALF-TIME: COMO 1-0 UNITED
    ("gap", 1.0, "cut_board_ht"),             # COMPACT crossed out...
    ("gap", 2.0, "w_press"),                  # ...PRESS; a hesitation...
    ("gap", 1.9, "w_together"),               # ...TOGETHER underneath
    ("gap", 1.7, "cut_br_read"),              # Bruno reads both words twice
    ("gap", 0.15, "cut_c04"), ("line", "C04"),            # "We need to be braver."
    ("gap", 0.2, "cut_b02"), ("line", "B02"),             # "So we go to them?"
    ("gap", 0.2, "cut_c05"), ("line", "C05"),             # "Together."
    ("gap", 0.3, "cut_b03"), ("line", "B03"),             # "Everyone?"
    ("gap", 0.3, "cut_c06"), ("line", "C06"),             # "That's usually what together means."
    ("gap", 0.4),
    ("gap", 1.8, "cut_room"),                 # Bruno looks around the room
    ("gap", 2.1, "cut_cap"),                  # Maguire, still on the dry pen: the cap comes off in his hand
    # ---- the collapse
    ("gap", CARD, "cut_g2"),                  # 49' DOUVIKAS: 2-0
    ("gap", 3.4, "cut_tac"),                  # two step forward; the others stay behind
    ("gap", CARD, "cut_g3"),                  # 57' PAZ: 3-0
    ("gap", 1.3, "cut_ck_board"),             # Carrick looks at the board
    ("gap", 1.4, "cut_br_ck"),                # Bruno looks at Carrick. Cut before either speaks
    ("gap", CARD, "cut_g4"),                  # 76' RAMÓN: 4-0
    ("gap", 3.4, "cut_push"),                 # a heroic push towards the bench that stops: nothing heroic to find
    # ---- the consolation
    ("gap", CARD, "cut_g5"),                  # 90+1' ZIRKZEE: 4-1
    ("gap", 2.0, "cut_zz"),                   # an arm up; the scoreboard; the arm comes down
    ("gap", 2.2, "cut_ft"), ("line", "N04"),              # FULL TIME, held: "Four-one. The consolation..."
    ("gap", 0.9),
    # ---- the dressing-room button
    ("gap", 2.0, "cut_btn"),                  # Bruno standing right; Carrick at the door; the bench empty between them
    ("gap", 0.15, "cut_c07"), ("line", "C07"),            # "Not ideal."
    ("gap", 0.3, "cut_b04"), ("line", "B04"),             # "Michael. We've used that one."
    ("gap", 0.5),
    ("gap", 1.4, "cut_sees"),                 # Carrick sees the documentary camera; the operator lowers the lens
    # ---- 8. the interview: Bruno's real position, paraphrased; then the parody
    ("gap", PARA, "cut_par1"),
    ("gap", 0.35, "cut_b05"), ("line", "B05"),            # "We gave them space..."
    ("gap", 0.4), ("mark", "look_back"),      # he looks back towards the dressing-room door
    ("gap", 1.1), ("line", "B06"),            # "I just wanted us to make them uncomfortable..."
    ("gap", 0.8),
    # ---- Carrick's real response, paraphrased; then the parody
    ("gap", PARA, "cut_par2"),
    ("gap", 0.35, "cut_c08"), ("line", "C08"),            # "I can draw the arrows..."
    ("gap", 0.35),
    ("gap", 2.8, "cut_magnets"),              # his board: only two magnets followed the arrows
    ("gap", 0.1, "cut_c09"), ("line", "C09"),             # "We'll review it."
    ("gap", 2.3),                             # he realises how often he has said that
    # ---- the distance
    ("gap", 3.4, "cut_corr"),                 # Bruno leaves one end, Carrick the other; footsteps
    ("gap", 5.0, "board_roll"),               # the board rolls through: CLARITY / ALIGNMENT / SUSTAINABILITY / AGILITY
    # ---- 9. the clear plan
    ("gap", 1.0, "cut_bd"), ("line", "W01"),              # Wilcox, alone, late: "We've got a very clear plan."
    ("gap", 0.6),
    ("gap", 1.4, "cut_laptop"),               # CLEAR PLAN.pptx...
    ("gap", 2.0, "type1"),                    # ...CLEAR PLAN - FINAL - FINAL 2
    ("gap", 1.8, "type2"),                    # CLEAR deleted from the title
    ("gap", 1.6, "aplan"),                    # A PLAN
    ("gap", 1.1, "lid"),                      # he closes the laptop
    ("gap", 2.6, "cut_mugdark"),              # the dark; the white mug lit; a ceramic tap
    ("gap", CREDITS, "cut_credits"),          # credits, no next-week tease; sound cut at the end
]

TL = build(SEQ, L)
