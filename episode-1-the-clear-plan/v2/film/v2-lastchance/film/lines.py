"""One take per line: every line is its own Fish Audio take, spoken by the character's cloned voice
(voiceovers/<id>-<voice>.wav; All-or-something-/episode-1-the-clear-plan/v2 made them and chose the takes).
Each take is force-aligned word by word and cut at its quiet edges (studio.film.voices.build)
-> build/lines/<id>.wav and build/lines.json"""
import re

from studio.film import ep

SPEAKER = {"NARRATOR": "narrator", "RATCLIFFE": "jim", "WILCOX": "jason", "CARRICK": "carrick", "BERRADA": "omar",
           "OLE": "ole"}
SCRIPT = ep.DIR / "script.md"
VO = ep.DIR / "voiceovers"
MAXGAP = 0.22          # pauses inside a line are trimmed to this (The Handover's)
GAPS = {"K03": 0.30, "K04": 0.30}   # Carrick's build-up and the rant keep a little of their rhythm
TEMPO = 1.0
EXTRA = {"wilcox": "W IH L K AA K S", "solskjaer": "S OW L SH EH R", "carrick": "K AE R IH K",
         "como": "K OW M OW", "standby": "S T AE N D B AY"}


def script():
    """every scripted line in order: [(id, speaker, text)]"""
    return [(lid, SPEAKER[spk], text) for lid, spk, text in
            re.findall(r"^\[([A-Z]\d+)\]\s+([A-Z]+):\s*(.+)$", SCRIPT.read_text(), re.M)]


def lines():
    """[(id, speaker, text, take, None, 1)]: the whole take is the line"""
    takes = {p.name.split("-")[0]: p for p in VO.glob("*.wav")}
    return [(lid, spk, text, str(takes[lid]), None, 1) for lid, spk, text in script()]
