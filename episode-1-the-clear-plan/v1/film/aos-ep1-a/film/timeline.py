"""The dialogue edit for part A: the Hull dressing room, the month of results in the same room (the same camera after
every result), and the reset that leads into Leeds week. Every result card holds long enough to read twice; the
script's silences are kept (before "Execution?", after "Not...", after "Sabah"). A mark on a gap names the moment the
gap starts (a cut on the end of a line, then the new shot's lead-in)."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

CARD = 3.4                                    # a result card on screen
EST = 2.6                                     # the ground before it, with its lower third

SEQ = [
    # ---- 1. Hull: the dressing room after the final whistle (the opening's match cut in hard to here)
    ("gap", 3.0, "open"),                     # the wide: they drift back in; nobody looks at anybody; room tone
    ("gap", 0.75, "cut_ck1"), ("line", "H01"),            # Carrick at the board: "Not ideal."
    ("gap", 0.18, "cut_br1"), ("line", "H02"),            # Bruno: "Not ideal?! He literally said set pieces..."
    ("gap", 0.22, "cut_mg1"), ("line", "H03"),            # Maguire: "Two set pieces."
    ("gap", 0.14, "cut_br2"), ("line", "H04"),            # Bruno: "Then how have we conceded two?!"
    ("gap", 0.18),
    ("gap", 1.3, "cut_silence"),              # the wide: the silence; every head to Maguire
    ("gap", 0.1, "cut_mg2"), ("line", "H05"),             # "Execution?"
    ("gap", 0.45, "cut_ck2"), ("line", "H06"),            # Carrick: "It's one game..."
    ("gap", 0.45),
    ("gap", 0.5, "cut_board1"),               # the board: SET PIECES...
    ("gap", 1.6, "wipe"),                     # ...wiped; it stays faintly there
    ("gap", 1.8, "write_basics"),             # BASICS over it
    ("gap", 3.4, "board_push"),               # the camera pushes in on both words
    # ---- 2. the response: Ipswich, 30 August
    ("gap", EST, "est_ips"),                  # the street to Old Trafford: OLD TRAFFORD / 30 August
    ("gap", CARD, "cut_ips"),                 # UNITED 5-2 IPSWICH
    ("gap", 2.6, "cut_ips_wide"),             # Bruno, captain, celebrating; the room pleased with itself
    ("gap", 0.15, "cut_cu1"), ("line", "R01"),            # Cunha: "Hat-trick. Captain."
    ("gap", 0.2, "cut_ck_ips"), ("line", "R02"),          # Carrick: "That's more like it."
    ("gap", 0.3),
    ("gap", 1.3, "cut_door"),                 # the door: Wilcox, with his tablet
    ("gap", 0.15, "cut_wi1"), ("line", "R03"),            # "Gentlemen, fantastic! This is the plan."
    ("gap", 0.25),
    ("gap", 2.6, "cut_tab1"),                 # he moves the tablet into the camera's shot: the claim of credit
    # ---- Everton, 6 September
    ("gap", EST, "est_eve"),                  # an away ground at dusk: EVERTON AWAY
    ("gap", 2.2, "cut_eve"),                  # 88' ŠEŠKO: 1-2...
    ("gap", 2.1, "flip_eve"),                 # ...90+6': 2-2
    ("gap", 1.4, "cut_eve_wide"),
    ("gap", 0.15, "cut_se1"), ("line", "R04"),            # Šeško: "Yes! I thought I scored the winner."
    ("gap", 0.2, "cut_ck_eve"), ("line", "R05"),          # Carrick: "Positive point away from home."
    ("gap", 0.2, "cut_mg_eve"), ("line", "R06"),          # Maguire, helpful: "You did. For about eight minutes."
    ("gap", 0.3, "cut_se2"), ("line", "R07"),             # "Thanks, Harry."
    ("gap", 1.2),                             # he looks anywhere but at Harry
    # ---- Sabah, 10 September
    ("gap", EST, "est_sab"),                  # Old Trafford, a European night
    ("gap", CARD, "cut_sab"),                 # UNITED 4-0 SABAH
    ("gap", 1.3, "cut_sab_wide"),             # warmer; the corporate music returns
    ("gap", 0.15, "cut_li1"), ("line", "R08"),            # Martínez: "I scored!"
    ("gap", 0.2, "cut_ck_sab"), ("line", "R09"),          # Carrick: "Don't encourage him."
    ("gap", 0.2, "cut_wi2"), ("line", "R10"),             # Wilcox: "European DNA."
    ("gap", 0.15),
    ("gap", 2.6, "cut_tab2"),                 # THE PLAN: NOW WITH EUROPEAN DNA; moved out of Martínez's way
    ("gap", 1.7, "cut_ck_smile"),             # Carrick's smallest genuine smile of the episode
    # ---- Manchester City, 13 September
    ("gap", EST, "est_city"),                 # Old Trafford, derby day
    ("gap", CARD, "cut_city"),                # UNITED 0-1 MAN CITY
    ("gap", 1.9, "cut_city_wide"),            # the same room, the same shot, no smiles; the music winds down
    ("gap", 0.15, "cut_li2"), ("line", "R11"),            # Martínez: "We nearly scored."
    ("gap", 0.18, "cut_br3"), ("line", "R12"),            # Bruno: "Nearly does not count."
    ("gap", 0.2, "cut_mg3"), ("line", "R13"),             # Maguire: "It counts in expected goals."
    ("gap", 0.25),
    ("gap", 1.5, "cut_turn"),                 # the wide: every head turns to him
    ("gap", 0.1, "cut_mg4"), ("line", "R14"),             # "What? I've been listening to Jason."
    ("gap", 0.3),
    ("gap", 2.4, "cut_charge"),               # the tablet, charging, alone on a desk
    # ---- Brighton, League Cup, 16 September
    ("gap", EST, "est_bri"),                  # Old Trafford, the League Cup
    ("gap", 2.0, "cut_bri"),                  # 2-0 (Lacey 8', Mount 10')...
    ("gap", 2.2, "flip_bri"),                 # ...2-3
    ("gap", 0.4, "cut_bri_shirt"), ("line", "R15"),       # Lacey (his shirt still on its hook): "We were two-nil up..."
    ("gap", 0.2, "cut_mo1"), ("line", "R16"),             # Mount: "You've learnt Manchester United very quickly."
    ("gap", 0.25),
    ("gap", 0.9, "cut_ck_bri"),               # Lacey looks to Carrick for a different explanation
    ("gap", 0.15, "cut_br4"), ("line", "R17"),            # Bruno: "Michael, do not say not ideal."
    ("gap", 0.25, "cut_ck_not"), ("line", "R18"),         # Carrick: "Not..."
    ("gap", 2.2),                             # he closes his mouth. Hold. No music
    # ---- Fulham, 20 September
    ("gap", EST, "est_ful"),                  # an away ground: FULHAM AWAY
    ("gap", CARD, "cut_ful"),                 # FULHAM 1-1 UNITED
    ("gap", 1.1, "cut_ful_li"),               # Martínez looks straight ahead
    ("gap", 0.15, "cut_cu2"), ("line", "R19"),            # Cunha: "Good finish. Mine. Sorry."
    ("gap", 0.25, "cut_br5"), ("line", "R20"),            # Bruno: "Five points. From five games..."
    ("gap", 0.3, "cut_ck_ful"), ("line", "R21"),          # Carrick: "Right. International break..."
    ("gap", 0.3),
    ("gap", 0.25, "cut_int"),                 # to the documentary camera
    ("line", "R22"),                          # (off) "How would you describe the opening month?"
    ("gap", 0.35), ("line", "R23"),           # "There have been positives."
    ("gap", 0.3), ("line", "R24"),            # (off) "Such as?"
    ("gap", 0.55), ("line", "R25"),           # "Sabah."
    ("gap", 2.2),                             # the camera searches his face for a second example
    ("gap", 3.0, "cut_cal"),                  # calendar pages turning: September, October
    ("gap", 3.0, "cut_intl"),                 # INTERNATIONAL BREAK
    ("gap", 3.2, "cut_empty"),                # the dressing room, empty, the lights going off row by row
    # ---- 3. Reset: Tottenham, 10 October; Atlético, 13 October; Leeds week
    ("gap", EST, "est_tot"),                  # Old Trafford again
    ("gap", 1.9, "cut_tot"),                  # 1-0 (Mbeumo 73')...
    ("gap", 1.9, "flip_tot"),                 # ...1-1 (Solanke 90+2')
    ("gap", 2.8, "cut_return"),               # back in the identical room
    ("gap", 0.5, "cut_reset"), ("line", "N01"),           # RESET over BASICS: "After the break, United returned..."
    ("gap", 0.15), ("mark", "tape"),          # the tape lets go; one corner falls
    ("gap", 1.6),
    ("gap", EST, "est_atl"),                  # an away ground: MADRID
    ("gap", 1.8, "cut_atl"),                  # 1' BARRIOS: 1-0...
    ("gap", 2.0, "flip_atl"),                 # ...2-0
    ("gap", 2.0, "cut_mz"), ("line", "N02"),              # press flashes over an empty mixed zone: "Madrid brought..."
    ("gap", 1.2),
    ("gap", 3.3, "cut_leeds"),                # LEEDS WEEK / A FICTIONALISED CARRINGTON DETOUR
    ("gap", 3.0, "cut_mug"),                  # the white mug on the sill; Carrington beyond, the hedge
]

TL = build(SEQ, L)
