"""The dialogue edit for the meeting: tight (a few frames between lines), the narrator over the open, the tablet and
the call; the only held beats are the ones the comedy needs (the silence after "who are we signing?", the slide
scrolling, the chime, CALL ENDED). A mark on a gap names the moment the gap starts."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    ("gap", 0.45, "open"),                    # Carrington from the air; the parody notice
    ("line", "M01"),                          # NARRATOR: "Manchester United. Twenty league titles..."
    ("gap", 0.2, "cut_room"), ("line", "M02"),            # the three of them waiting: "This is the story of the plan."
    ("gap", 0.2, "cut_wi1"), ("line", "M03"),             # Wilcox: "Right, Michael. New season..."
    ("gap", 0.15, "cut_ck1"), ("line", "M04"),            # Carrick: "What's the plan?"
    ("gap", 0.15, "cut_wi2"), ("line", "M05"),            # "One second."
    ("gap", 0.25, "cut_tab"), ("line", "M06"),            # the tablet: CONNECTING... 3%
    ("gap", 0.25, "cut_wi3"), ("line", "M07"),            # the buzzwords, stamped on the picture
    ("gap", 0.2, "cut_ck2"), ("line", "M08"),             # "...who are we signing?" the music stops dead
    ("gap", 0.6, "cut_om1"), ("line", "M09"),             # the silence; Berrada
    ("gap", 0.15, "cut_ck3"), ("line", "M10"),
    ("gap", 0.15, "cut_wi4"), ("line", "M11"),
    ("gap", 0.12, "cut_q1"), ("line", "M12"),             # the list: Carrick / Jim, quicker every time
    ("gap", 0.1, "cut_n1"), ("line", "M13"),
    ("gap", 0.1, "cut_q2"), ("line", "M14"),
    ("gap", 0.1, "cut_n2"), ("line", "M15"),
    ("gap", 0.1, "cut_q3"), ("line", "M16"),
    ("gap", 0.12, "cut_n3"), ("line", "M17"),
    ("gap", 0.3, "cut_q4"), ("line", "M18"),
    ("gap", 0.12, "cut_n4"), ("line", "M19"),
    ("gap", 0.35, "cut_q5"), ("line", "M20"),
    ("gap", 0.2, "cut_fair"), ("line", "M21"),            # the three of them: "In fairness, they did have one."
    ("gap", 0.2, "cut_ck4"), ("line", "M22"),
    ("gap", 0.15, "cut_wi5"), ("line", "M23"),
    ("gap", 0.15, "cut_ck5"), ("line", "M24"),
    ("gap", 0.15, "cut_wi6"), ("line", "M25"),
    ("gap", 0.25, "cut_ck6"), ("line", "M26"),
    ("gap", 0.15, "cut_om2"), ("line", "M27"),
    ("gap", 0.3, "cut_ck7"), ("line", "M28"),             # "And the objectives?"
    ("gap", 0.15, "cut_obj"),                 # the display connects at last: OBJECTIVES, scrolling
    ("gap", 3.0),
    ("line", "M29"),                          # (Jim, off) "And don't complain about the squad." as the last bullet
    ("gap", 0.45, "cut_ck8"), ("line", "M30"),
    ("gap", 0.15, "cut_om3"), ("line", "M31"),
    ("gap", 0.1, "cut_jim1"), ("line", "M32"),            # "Debt."
    ("gap", 0.3, "cut_ck9"), ("line", "M33"),
    ("gap", 0.2, "cut_om4"), ("line", "M34"),
    ("gap", 0.2, "cut_jim2"), ("line", "M35"),
    ("gap", 0.15),
    ("gap", 1.1, "chime"),                    # the video-call chime: INCOMING VIDEO CALL
    ("gap", 0.3, "cut_call"), ("line", "M36"),            # two tiles, CAMERA OFF: the narrator
    ("gap", 0.3), ("line", "M37"),            # Joel
    ("gap", 0.2, "cut_ck_call"), ("line", "M38"),         # Carrick, listening to the speakers; Avram
    ("gap", 0.15, "cut_call2"), ("line", "M39"),          # Joel
    ("gap", 0.1), ("line", "M40"),            # Avram: "Need to run."
    ("gap", 0.1), ("line", "M41"),            # Joel: "Go United!"
    ("gap", 0.2, "ended"),                    # CALL ENDED  0:41
    ("gap", 0.5), ("line", "M42"),
    ("gap", 0.25, "cut_jim3"), ("line", "M43"),           # "Unfortunately."
    ("gap", 0.3, "cut_ck10"), ("line", "M44"),            # "Cheers. Brilliant. Yep. Good input."
    ("gap", 0.25, "cut_jim4"), ("line", "M45"),           # "Right. Hull. Don't lose."
    ("gap", 0.3, "cut_title"),                # ALL OR SOMETHING / THE CLEAR PLAN
    ("gap", 2.5),
]

TL = build(SEQ, L)
