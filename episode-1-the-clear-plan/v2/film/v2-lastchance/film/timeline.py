"""The dialogue edit: The Handover's own edit, beat for beat (the eyebrow after "we backed you", the silence after
"balanced squad", the jaw after "Balanced?!", the pause before the door, Carrick's stare before the last line), with
the narrator's line over the opening shot and the episode's end title and credits after the smash to black."""
import json

from studio.film import ep
from studio.film.timeline import build

L = json.loads(ep.path("lines.json").read_text())

SEQ = [
    ("gap", 0.45, "open"),                    # on Carrick, arms crossed; room tone; the narrator
    ("line", "K00"),                          # "The morning after Como, the board asked to see Michael Carrick..."
    ("gap", 0.35, "jim_in"),
    ("line", "K01"),                          # Jim: the last chance (the three of them, then the punch-in on Jim)
    ("gap", 0.14, "cut_jason1"),
    ("line", "K02"),                          # Jason leans in: "...we backed you": cut to Carrick's eyebrow
    ("gap", 0.60),                            # Carrick blinks at Wilcox
    ("line", "K03"),                          # "Seeing as it's my last chance..."
    ("gap", 0.18, "cut_rant"),
    ("line", "K04"),                          # the rant: pointing, then a step in on every missing position
    ("gap", 0.40, "cut_omar"),                # the three of them: the others avoid his eye
    ("line", "K05"),                          # "...a very balanced squad."
    ("gap", 0.50),                            # hold the wide, uncomfortable: Omar pleased with himself
    ("gap", 0.08, "cut_balanced"),            # smash to Carrick
    ("line", "K06"),                          # "Balanced?!"
    ("gap", 0.80),                            # his jaw hangs
    ("gap", 0.10, "cut_resign"),
    ("line", "K07"),                          # "It is what it is."
    ("gap", 0.22),
    ("gap", 0.28, "rise"),                    # he gets up: cut on the action
    ("gap", 1.05, "cut_door1"),               # the door: the camera follows him to it
    ("line", "K08"),                          # "Oh, Michael." over the door, "Before you go..." on Jim
    ("gap", 0.12, "cut_what"),
    ("line", "K09"),                          # "What?"
    ("gap", 0.14, "cut_jim3"),
    ("line", "K10"),                          # "...someone to be on standby. Just in case."
    ("gap", 0.14, "cut_door3"),
    ("line", "K11"),                          # "You've already got someone?!"
    ("gap", 0.60),                            # silence: nobody answers him
    ("gap", 0.30, "click"),                   # the latch
    ("gap", 0.30, "swing"),                   # the door swings in
    ("gap", 0.95, "walk"),                    # Ole walks into the doorway
    ("gap", 0.50, "stop"),                    # stops on the threshold, turns to them, waves
    ("line", "K12"),                          # "Hello, Michael!"
    ("gap", 0.22, "cut_ole1"),
    ("line", "K13"),                          # "Don't worry, Michael. I'm only on standby..." / Carrick / "...done this before!"
    ("gap", 0.45, "cut_last"),                # Carrick, frozen on Ole...
    ("gap", 0.75, "look"),                    # ...then he looks down the lens
    ("line", "K14"),                          # "Oh, you've got to be fucking joking!"
    ("gap", 0.45, "cut_black"),               # smash to black
    ("gap", 2.6, "cut_title"),                # ALL OR SOMETHING / LAST CHANCE
    ("gap", 8.0, "cut_credits"),              # the credits
]

TL = build(SEQ, L)
