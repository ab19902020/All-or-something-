"""The dialogue edit: every line in script order with the beats between them, and the named marks the shots
and the acting hang off. Shorts pacing: gaps of a few frames, holds only where the script asks for one.

Output (import): TL = {"total": s, "lines": {id: {start, end, speaker}}, "marks": {name: t}}"""
import json

L = json.load(open("build/lines.json"))

# (kind, value[, mark name]): "gap" seconds of room tone before the next item; "line" id; "mark" a named point
BR_MISSING = L["br_monaco"].get("missing", False)     # Bruno's Monaco line not recorded yet: a silent stare

SEQ = [
    ("gap", 0.25, "open"),                   # exterior: music, slow push, big white text
    ("line", "nar_deadline"),
    ("gap", 0.22, "cut_wide"),               # boom, hard cut: the room plays on its own sound
    ("line", "ck_two_things"),
    ("gap", 0.12, "cut_js1"), ("line", "js_sorted"),
    ("gap", 0.08, "cut_ck1"), ("line", "ck_brilliant"),
    ("gap", 0.12, "cut_js2"), ("line", "js_bought"),
    ("gap", 0.05, "music_stop"),
    ("gap", 0.35, "cut_ck2"),                 # close-up Carrick: one blink, tiny head move
    ("line", "ck_i_said"),
    ("gap", 0.12, "cut_om1"), ("line", "om_yeah_but"),
    ("gap", 0.10, "cut_js3"), ("line", "js_three_things"),
    ("gap", 0.85, "cut_ck3"),                 # no dialogue: Carrick slowly looks into the lens and holds
    ("gap", 0.10, "cut_om5"), ("line", "om_positions"),       # Omar, calmly honest: "...No."
    ("gap", 1.05, "cut_br1"),                 # Bruno looks from Carrick to Jason, then at the lens
    ("line", "br_you_bought"),
    ("gap", 0.45, "cut_js_nod"),              # Jason nods proudly
    ("gap", 0.10, "cut_ck4"),                 # Carrick tries to stay diplomatic
    ("line", "ck_not_complaining"),
    ("gap", 0.28, "ck_lean"),                 # a short pause, he leans forward
    ("line", "ck_whos_scoring"),
    ("gap", 0.07, "cut_om2"), ("line", "om_bruno"),
    ("gap", 0.08, "cut_br2"), ("line", "br_sorry_what"),      # whip cut
    ("gap", 0.10, "cut_om3"), ("line", "om_efficient"),
    ("gap", 0.08, "cut_br3"), ("line", "br_crossing"),
    ("gap", 0.07, "cut_js4"), ("line", "js_bruno"),
    ("gap", 0.05, "cut_br4"), ("line", "br_me"),
    ("gap", 0.45, "cut_ck5"),                 # Carrick trying not to react
    ("gap", 0.05, "cut_br5"), ("line", "br_midfielder"),
    ("gap", 0.08, "cut_js5"), ("line", "js_perfect"),
    ("gap", 0.10, "cut_br9"), ("line", "br_brilliant"),       # Bruno, dead-eyed: "Brilliant. Absolutely brilliant."
    ("gap", 0.35, "cut_ck6"), ("line", "ck_left_back"),       # a small breath first
    ("gap", 0.07, "cut_js6"), ("line", "js_luke"),
    ("gap", 0.35, "cut_ck7"), ("line", "ck_luke"),            # a pause, the camera pushes closer
    ("gap", 0.07, "cut_js7"),
    ("gap", 0.70, "js_next"),                 # Jason freezes, glances at Omar, then at the lens
    ("line", "js_next_question"),
    ("gap", 0.60, "cut_br6"),                 # Bruno slowly sinks back into his chair
    ("gap", 0.28, "cut_jr1"), ("line", "jr_bigger_issues"),  # Jim lowers his paperwork
    ("gap", 0.55, "cut_wide2"),               # everyone looks at Jim
    ("gap", 0.25, "cut_br7"), ("line", "br_monaco"),         # Bruno turns to him (a silent stare until recorded)
    ("gap", 0.40 if BR_MISSING else 0.55, "cut_jr2"),        # silence, hold on Jim
    ("gap", 0.25, "cut_monaco"), ("line", "jr_yes_monaco"),  # hard cut to Monaco
    ("gap", 0.40, "jr_beat"), ("line", "jr_perspective"),
    ("gap", 0.07, "cut_ck8"),                 # smash cut back to Manchester
    ("gap", 0.10), ("line", "ck_no_striker"),
    ("gap", 0.07, "cut_om4"), ("line", "om_no_striker"),
    ("gap", 0.07, "cut_ck9"), ("line", "ck_no_left_back"),
    ("gap", 0.07, "cut_js8"), ("line", "js_no_left_back"),
    ("gap", 0.50, "cut_ck10"), ("line", "ck_but_three"),     # looks between all three first
    ("gap", 0.30, "cut_execs"), ("line", "js_three_mids"),   # all three nod
    ("gap", 0.08, "om_line"), ("line", "om_three_mids"),
    ("gap", 0.28, "jr_nod"), ("line", "jr_good_meeting"),    # Jim, satisfied: "Good meeting."
    ("gap", 0.45, "cut_br8"), ("line", "br_sunshine"),       # Bruno button: everything behind him quieter
    ("gap", 0.40, "br_pause"), ("line", "br_saudi"),
    ("gap", 0.40, "cut_black"),               # cut to black
    ("gap", 0.25, "cut_title"),               # title: boom
    ("gap", 0.25), ("line", "nar_title"),
    ("gap", 0.35, "title_end"),               # hard ending (loops back to the exterior)
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
