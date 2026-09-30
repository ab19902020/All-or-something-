"""The dialogue edit: every line in script order with the beats between them, and the named marks the shots
and the acting hang off. Shorts pacing: gaps of a few frames, holds only where the script asks for one.

Output (import): TL = {"total": s, "lines": {id: {start, end, speaker}}, "marks": {name: t}}"""
import json

L = json.load(open("build/lines.json"))

# (kind, value[, mark name]): "gap" seconds of room tone before the next item; "line" id; "mark" a named point

SEQ = [
    ("gap", 0.25, "open"),                    # MKM Stadium: over-serious music, slow push, HULL / OPENING DAY
    ("line", "nar_new_season"),
    ("gap", 0.42, "music_stop"),              # a tiny pause... the music stops dead
    ("gap", 0.10), ("line", "nar_probably"),  # dry, in the silence
    ("gap", 0.15),
    ("gap", 0.25, "cut_room_wide"),           # hard cut inside: the away dressing room before the game
    ("line", "ck_right_lads"),
    ("gap", 0.10, "cut_ck_board"),            # Carrick points at the tactics board, slow push
    ("line", "ck_hull_come_up"),
    ("gap", 0.50, "cut_sh1"),                 # Steve looks up from his clipboard to Carrick
    ("line", "sh_practise"),
    ("gap", 0.08, "cut_ck2"), ("line", "ck_already"),        # slightly offended
    ("gap", 0.08, "cut_sh2"), ("line", "sh_attacking"),
    ("gap", 0.90, "cut_ck3"),                 # Carrick looks at the board... then back at Steve
    ("line", "ck_same_corner"),
    ("gap", 1.00, "cut_br1"),                 # Bruno slowly looks straight into the lens, holds
    ("gap", 0.20, "cut_ck4"), ("line", "ck_kobbie"),          # Carrick turns to Kobbie
    ("gap", 0.07, "cut_mn1"), ("line", "mn_again"),
    ("gap", 0.07, "cut_ck5"), ("line", "ck_bought"),          # awkward
    ("gap", 0.07, "cut_mn2"), ("line", "mn_noticed"),         # deadpan
    ("gap", 0.08, "cut_br2"), ("line", "br_nine"),
    ("gap", 0.07, "cut_mg1"), ("line", "mg_striker"),         # innocent, genuine
    ("gap", 1.15, "cut_wide2"),               # silence: everyone slowly looks at Carrick; he pretends not to notice
    ("gap", 0.25, "cut_ck6"),                 # Carrick claps his hands hard
    ("gap", 0.22, "clap"), ("line", "ck_come_on"),
    ("gap", 1.10, "cut_walk"),                # he strides off to the wrong door; nobody follows
    ("gap", 0.30, "cut_sh3"), ("line", "sh_wrong_door"),      # Steve watches
    ("gap", 1.80, "cut_ck7"),                 # stops, looks at the door, at everyone, turns round, walks the other way
    ("gap", 0.90, "cut_score"),               # SMASH CUT: black, the score slams in (a short cheer, then silence)
    ("line", "nar_knew"),                     # "Manchester United knew exactly what was coming." corner... goal
    ("gap", 0.25, "flash2"), ("line", "nar_did_not_help"),   # "It did not help." another corner... goal
    ("gap", 5.45, "chant"),                   # the Hull fans: "you're getting mauled by the tigers, mauled by the
                                              # tigers": Carrick staring from the touchline, Maguire lost, Bruno shouting
    ("gap", 1.20, "cut_post_wide"),           # hard cut back inside: total silence, the room wrecked, nobody moves
    ("line", "ck_positives"),                 # "Right... positives."
    ("gap", 0.85, "cut_silence"),             # nobody speaks: faces
    ("gap", 0.30, "cut_br3"), ("line", "br_possession"),      # Bruno looks up
    ("gap", 0.07, "cut_sh4"), ("line", "sh_excellent"),
    ("gap", 0.07, "cut_br4"), ("line", "br_lost"),
    ("gap", 0.40, "cut_sh5"), ("line", "sh_less_excellent"),  # looks down at the clipboard first
    ("gap", 0.40, "cut_mg2"), ("line", "mg_both_goals"),      # Harry raises his hand slightly
    ("gap", 0.22, "cut_ck8"), ("line", "ck_yep1"),            # a nod
    ("gap", 0.07, "cut_mg3"), ("line", "mg_warned"),
    ("gap", 0.30, "cut_ck9"), ("line", "ck_yep2"),            # his expression tightens
    ("gap", 0.07, "cut_mg4"), ("line", "mg_twice"),
    ("gap", 0.10, "cut_ck10"), ("line", "ck_aware"),
    ("gap", 0.90, "cut_mg5"),                 # tiny zoom on Harry: he slowly lowers his hand
    ("gap", 0.40, "cut_mn3"), ("line", "mn_came_on"),         # across the room to Kobbie, arms folded
    ("gap", 0.22, "mn_look"), ("line", "mn_plan"),            # he looks at Carrick
    ("gap", 0.60, "cut_ck11"), ("line", "ck_impact"),         # thinks seriously first
    ("gap", 0.07, "cut_mn4"), ("line", "mn_didnt_score"),
    ("gap", 0.22, "cut_ck12"), ("line", "ck_nearly"),         # a nod
    ("gap", 0.85, "cut_mn5"),                 # Kobbie stares straight into the lens
    ("gap", 0.50, "cut_br5"), ("line", "br_newly"),           # Bruno stands up
    ("gap", 0.07, "cut_mg6"), ("line", "mg_shooting"),
    ("gap", 0.18, "cut_br6"), ("line", "br_centre_back"),     # turns to him
    ("gap", 0.07, "cut_mg7"), ("line", "mg_nobody"),
    ("gap", 1.15, "cut_ck13"),                # Carrick starts to say something... stops... looks away
    ("gap", 0.35, "cut_sh6"), ("line", "sh_good_news"),       # Steve checks the clipboard
    ("gap", 0.80, "cut_hope"),                # everyone looks up; a little hopeful music
    ("gap", 0.10, "cut_sh7"), ("line", "sh_ipswich"),         # the music dies
    ("gap", 0.40, "cut_mn6"), ("line", "mn_ipswich"),         # Kobbie, concerned
    ("gap", 0.70, "cut_turn"),                # everyone slowly turns to Carrick
    ("gap", 0.95, "cut_ck14"),                # Carrick looks into the lens: a long uncomfortable beat
    ("line", "ck_good_meeting"),
    ("gap", 0.55, "ck_exit"),                 # ...and walks straight out
    ("gap", 0.80, "cut_br7"),                 # Bruno watches him go, then turns to us
    ("line", "br_saudi"),
    ("gap", 0.30),
    ("gap", 0.35, "cut_black"),               # hard cut to black
    ("gap", 0.20, "cut_title"),               # ALL OR SOMETHING / NEW SEASON. SAME CORNERS. (the sting)
    ("line", "nar_title"),
    ("gap", 0.25),
    ("gap", 3.20, "cut_tigers"),              # the Tigers song: the pitch, HULL 2-0 UNITED, the reactions; cut abruptly,
                                              # so it loops into "New season... new Manchester United..."
]


def build():
    t, lines, marks = 0.0, {}, {}
    for it in SEQ:
        kind = it[0]
        if kind == "gap":
            if len(it) > 2: marks[it[2]] = round(t, 3)
            t += it[1]
        elif kind == "line":
            d = L[it[1]]
            lines[it[1]] = dict(start=round(t, 3), end=round(t + d["dur"], 3), speaker=d["speaker"])
            t += d["dur"]
    marks["end"] = round(t, 3)
    return dict(total=round(t, 3), lines=lines, marks=marks)


TL = build()

if __name__ == "__main__":
    json.dump(TL, open("build/timeline.json", "w"), indent=1)
    print("total", TL["total"])
    for k, v in TL["lines"].items(): print(f"{v['start']:6.2f} {v['end']:6.2f} {k}")
