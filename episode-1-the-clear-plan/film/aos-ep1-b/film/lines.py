"""One take per line: every line is its own Fish Audio take, spoken by the character's cloned voice
(voiceovers/<id>-<voice>.wav; All-or-something-/episode-1-the-clear-plan/voices/ made them and chose the takes).
Each take is force-aligned word by word and cut at its quiet edges (studio.film.voices.build)
-> build/lines/<id>.wav and build/lines.json"""
import re

from studio.film import ep

SPEAKER = {"CARRICK": "carrick", "BRUNO": "bruno", "MAGUIRE": "maguire", "CUNHA": "cunha", "WILCOX": "wilcox",
           "SESKO": "sesko", "MARTINEZ": "licho", "LACEY": "lacey", "MOUNT": "mount", "PRODUCER": "producer",
           "NARRATOR": "narrator"}
SCRIPT = ep.DIR / "script.md"
VO = ep.DIR / "voiceovers"
MAXGAP = 0.3           # pauses inside a line are trimmed to this
GAPS = {"B05": 0.38, "B06": 0.35}    # the interview lines keep their beats
TEMPO = 1.0
EXTRA = {"douvikas": "D UW V IY K AH S"}


def script():
    """every scripted line in order: [(id, speaker, text)]"""
    return [(lid, SPEAKER[spk], text) for lid, spk, text in
            re.findall(r"^\[([A-Z]\d+)\]\s+([A-Z]+):\s*(.+)$", SCRIPT.read_text(), re.M)]


def lines():
    """[(id, speaker, text, take, None, 1)]: the whole take is the line"""
    takes = {p.name.split("-")[0]: p for p in VO.glob("*.wav")}
    return [(lid, spk, text, str(takes[lid]), None, 1) for lid, spk, text in script()]
