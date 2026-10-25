"""The acting for the meeting, beat by beat (see studio/film/perf.py for every table).

  Carrick   level and polite; arms crossed waiting for the plan; "who are we signing?" with one eyebrow; the list
            of positions quicker and flatter every time; "Fair enough" with heavy lids; "sell to buy?" dry; to the
            call, listening to a speaker; "Good input" deadpan.
  Wilcox    the salesman: pleased with every word, a nod on each buzzword; "a lot" with a shrug of the brows.
  Berrada   polished, calm; pleased with "responsive squad optimisation" (a slow smug blink).
  Ratcliffe flat "No."s, a little firmer each time; "You already asked that" pointing; "Debt." with no expression at
            all; "Funny you should mention them" pleased with himself; "Don't lose" pointing."""
import json

from studio.film import ep
from studio.film.perf import Performance
from studio.film.shots import Marks
from film.direction import SHOTS
from film.timeline import TL

L = json.loads(ep.path("lines.json").read_text())
T = Marks(TL, L)
m, ls, le, wt, we = T.m, T.ls, T.le, T.wt, T.we

WHO = ["carrick", "jim", "wilcox", "omar"]
SPK = {w: w for w in WHO}

META = {
    "M01": ("calm", "cam", []), "M02": ("calm", "cam", []),
    "M03": ("salesman", "carrick", ["right", "new", "chapter", "clear"]),
    "M04": ("calm", "wilcox", ["plan"]),
    "M05": ("casual", "carrick", ["second"]),
    "M06": ("calm", "cam", []),
    "M07": ("salesman", "carrick", ["clarity", "alignment", "sustainability", "agility", "yeah"]),
    "M08": ("restrained", "wilcox", ["right", "okay", "jason", "who", "signing"]),
    "M09": ("diplomatic", "carrick", ["invested", "significantly"]),
    "M10": ("calm", "omar", ["know", "thinking", "striker"]),
    "M11": ("confident", "carrick", ["options"]),
    "M12": ("flat", "jim", ["left"]), "M13": ("flat", "carrick", ["no"]),
    "M14": ("flat", "jim", ["centre"]), "M15": ("flat", "carrick", ["no"]),
    "M16": ("flat", "jim", ["forward"]), "M17": ("firm", "carrick", ["already", "asked"]),
    "M18": ("flat", "jim", ["goalkeeper"]), "M19": ("matter", "carrick", ["got", "one"]),
    "M20": ("resigned", "jim", ["fair"]),
    "M21": ("calm", "cam", []),
    "M22": ("calm", "wilcox", ["how", "much"]),
    "M23": ("salesman", "carrick", ["moment", "lot"]),
    "M24": ("dry", "wilcox", ["how", "lot"]),
    "M25": ("confident", "carrick", ["enough", "not", "striker"]),
    "M26": ("dry", "wilcox", ["sell", "buy"]),
    "M27": ("smug", "carrick", ["describe", "responsive", "optimisation"]),
    "M28": ("calm", "jim", ["objectives"]),
    "M29": ("firm", "carrick", ["don't", "complain", "squad"]),
    "M30": ("sarcastic", "jim", ["brilliant", "good", "positive", "where", "money", "actually"]),
    "M31": ("diplomatic", "carrick", ["cash", "infrastructure"]),
    "M32": ("deadpan", "carrick", ["debt"]),
    "M33": ("dry", "jim", ["glazer", "dividends"]),
    "M34": ("diplomatic", "carrick", ["technically", "weren't", "dividends", "year"]),
    "M35": ("smug", "carrick", ["funny", "mention"]),
    "M36": ("calm", "cam", []), "M42": ("calm", "cam", []),
    "M43": ("deadpan", "carrick", ["unfortunately"]),
    "M44": ("deadpan", "screen", ["cheers", "brilliant", "yep", "good", "input"]),
    "M45": ("firm", "carrick", ["hull", "don't", "lose"]),
}
TAGS = dict(salesman=(0.45, 0.45), smug=(0.2, 0.4), sarcastic=(0.35, 0.1), deadpan=(0.0, -0.1))
BASE = dict(carrick=(-0.1, -0.05), jim=(-0.1, -0.05), wilcox=(0.05, 0.25), omar=(0.05, 0.2))

GAZE = {
    "carrick": [(m("chime"), le("M44"), "screen")],
    "jim": [], "wilcox": [], "omar": [],
}
EXPR = {
    "carrick": [(m("cut_ck1"), ls("M04"), -0.15, -0.1, 0.3),
                (wt("M08", "who") - 0.05, m("cut_om1"), 0.7, -0.15, 0.12),          # who are we signing?
                (le("M19"), le("M20"), 0.1, -0.3, 0.2),                             # fair enough
                (ls("M26"), le("M26"), 0.45, -0.2, 0.15),
                (le("M27"), m("cut_obj"), 0.65, -0.3, 0.12),                        # responsive squad what
                (ls("M38"), le("M38"), 0.2, -0.2, 0.2),
                (ls("M44"), le("M44"), 0.05, 0.12, 0.2)],                           # a polite, dead smile
    "jim": [(ls("M32"), le("M32"), -0.2, -0.3, 0.05),
            (ls("M35"), le("M35"), 0.35, 0.45, 0.15)],
    "wilcox": [(wt("M07", "clarity"), le("M07"), 0.5, 0.55, 0.15),
               (wt("M23", "a"), le("M23"), 0.65, 0.3, 0.1)],
    "omar": [(le("M27") - 0.3, m("cut_ck7") + 0.6, 0.2, 0.5, 0.2)],
}
NODS = {"wilcox": [(wt("M07", "clarity"), 1, 1.6), (wt("M07", "alignment"), 1, 1.6),
                   (wt("M07", "sustainability"), 1, 1.6), (wt("M07", "agility"), 1, 1.6),
                   (le("M03") - 0.3, 1, 1.8)],
        "omar": [(wt("M27", "optimisation"), 1, 2.2)],
        "jim": [(ls("M13"), 1, 1.4), (ls("M15"), 1, 1.8), (ls("M45") + 0.1, 1, 1.4)],
        "carrick": [(le("M04") - 0.1, 1, 1.2), (wt("M44", "yep"), 1, 1.2), (wt("M44", "good"), 1, 1.0)]}
SHAKES = {"jim": [(ls("M13"), 2, 0.12), (ls("M15"), 2, 0.12)]}
TURN = {"carrick": [(wt("M08", "who") - 0.1, le("M08") + 0.3, 0.0, 2.5)]}
LIDS = {"carrick": [(le("M19") - 0.1, le("M20") + 0.2, 0.32, 0.25),
                    (ls("M44"), m("cut_jim4"), 0.3, 0.3)],
        "omar": [(le("M27") - 0.1, m("cut_ck7") + 0.5, 0.3, 0.25)],
        "jim": [(ls("M32"), le("M32") + 0.2, 0.25, 0.1)]}
FORCED = {"carrick": [le("M05") + 0.3, le("M27") + 0.25, le("M27") + 0.6, le("M41") + 0.3],
          "omar": [le("M27") + 0.4], "wilcox": [le("M07") + 0.2], "jim": [le("M43") + 0.2]}
NOBLINK = {"carrick": [(wt("M08", "who"), m("cut_om1")), (le("M27"), m("cut_obj"))]}
REST = dict(carrick="jim", jim="carrick", wilcox="carrick", omar="carrick")

PERF = Performance(TL, L, WHO, SPK, META, lambda lid: ep.path("lines", f"{lid}.wav"), base=BASE, gaze=GAZE,
                   expr=EXPR, nods=NODS, turn=TURN, forced=FORCED, noblink=NOBLINK, tags=TAGS, rest_target=REST,
                   cuts=[s["t"] for s in SHOTS], lids=LIDS, shakes=SHAKES)
