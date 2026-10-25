"""One take per line: every line is its own Fish Audio take, spoken by the character's cloned voice
(voiceovers/<id>-<voice>.wav; All-or-something-/episode-1-the-clear-plan/v2 made them and chose the takes).
Each take is force-aligned word by word and cut at its quiet edges (studio.film.voices.build)
-> build/lines/<id>.wav and build/lines.json"""
import re
import unicodedata

from studio.film import ep

SPEAKER = {"CARRICK": "carrick", "BRUNO": "bruno", "MAGUIRE": "maguire", "CUNHA": "cunha", "WILCOX": "wilcox",
           "SESKO": "sesko", "MARTINEZ": "licho", "LISANDRO": "licho", "LACEY": "lacey", "MOUNT": "mount",
           "PRODUCER": "producer", "NARRATOR": "narrator", "RATCLIFFE": "jim", "BERRADA": "omar", "JOEL": "joel",
           "AVRAM": "avram"}
SCRIPT = ep.DIR / "script.md"
VO = ep.DIR / "voiceovers"
MAXGAP = 0.3           # pauses inside a line are trimmed to this
GAPS = {}
TEMPO = 1.0
EXTRA = {"sabah": "S AA B AH", "kickoff": "K IH K AO F", "lisandro": "L IH S AE N D R OW",
         "wilcox": "W IH L K AA K S", "berrada": "B EH R AA D AH", "sesko": "SH EH SH K OW",
         "carrington": "K AE R IH NG T AH N", "glazer": "G L EY Z ER", "atletico": "AE T L EH T IH K OW",
         "zirkzee": "Z ER K Z IY", "mbeumo": "AH M B OW M OW", "elland": "EH L AH N D", "paz": "P AE Z",
         "como": "K OW M OW", "haaland": "HH AA L AH N D", "fernandes": "F ER N AE N D EH Z",
         "martinez": "M AA R T IY N EH Z", "optimisation": "AA P T AH M AH Z EY SH AH N",
         "matchday": "M AE CH D EY", "goalless": "G OW L L AH S", "ipswich": "IH P S W IH CH",
         "tottenham": "T AA T AH N AH M", "fulham": "F UH L AH M", "lacey": "L EY S IY", "everton": "EH V ER T AH N",
         "nico": "N IY K OW", "learnt": "L ER N T", "hartrick": "HH AA T R IH K",
         "equalised": "IY K W AH L AY Z D", "mbeumo": "AH M B OW M OW", "elland": "EH L AH N D"}


def fold(text):
    """the line as the aligner reads it: accents off (Šeško -> Sesko, Martínez -> Martinez)"""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def script():
    """every scripted line in order: [(id, speaker, text)]"""
    return [(lid, SPEAKER[spk], fold(text)) for lid, spk, text in
            re.findall(r"^\[([A-Z]\d+)\]\s+([A-Z]+):\s*(.+)$", SCRIPT.read_text(), re.M)]


def lines():
    """[(id, speaker, text, take, None, 1)]: the whole take is the line"""
    takes = {p.name.split("-")[0]: p for p in VO.glob("*.wav")}
    return [(lid, spk, text, str(takes[lid]), None, 1) for lid, spk, text in script()]
