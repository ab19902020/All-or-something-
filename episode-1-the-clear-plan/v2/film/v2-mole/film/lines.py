"""One take per line: every line of The Mole is its own Fish Audio take, spoken by the character's cloned voice
(voiceovers/<id>-<voice>.wav; All-or-something-/episode-1-the-clear-plan/v2 made them and chose the takes), so the
narrator, Lisandro and Wilcox sound the same here as in the rest of the episode. Each take is force-aligned word by
word and cut at its quiet edges (studio.film.voices.build) -> build/lines/<id>.wav and build/lines.json.
The next-episode teaser (L061 to L063) is not in this cut."""
import re

from studio.film import ep

SPEAKER = {"NARRATOR": "narrator", "LISANDRO": "licho", "WILCOX": "wilcox"}
SCRIPT = ep.DIR / "script.md"
VO = ep.DIR / "voiceovers"
MAXGAP = 0.3           # pauses inside a line are trimmed to this
GAPS = {"L001": 0.45, "L009": 0.3, "L010": 0.4, "L017": 0.45, "L023": 0.8, "L028": 0.5, "L040": 0.35,
        "L041": 0.5, "L054": 0.45}   # the pauses the lines are built on
TEMPO = 1.0
EXTRA = {"lisandro": "L IH S AE N D R OW", "berrada": "B EH R AA D AH", "bielsa": "B IY EH L S AH",
         "hermano": "ER M AA N OW", "immersing": "IH M ER S IH NG", "shhh": "SH", "carrington": "K AE R IH NG T AH N",
         "wilcox": "W IH L K AA K S", "mia": "M IY AH", "madre": "M AA D R EY", "vamos": "V AA M OW S"}


def script():
    """every scripted line in this cut, in order: [(id, speaker, text)]"""
    return [(lid, SPEAKER[spk], text) for lid, spk, text in
            re.findall(r"^\[(L\d+)\]\s+([A-Z]+):\s*(.+)$", SCRIPT.read_text(), re.M) if int(lid[1:]) <= 60]


def lines():
    """[(id, speaker, text, take, None, 1)]: the whole take is the line"""
    takes = {p.name.split("-")[0]: p for p in VO.glob("*.wav")}
    return [(lid, spk, text, str(takes[lid]), None, 1) for lid, spk, text in script()]
