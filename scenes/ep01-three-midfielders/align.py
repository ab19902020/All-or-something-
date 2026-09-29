"""Word + phone forced alignment (pocketsphinx, en-us model from the PyPI wheel) of every voice clip the episode
uses, against its corrected transcript. Output: phones.json {clip: {dur, words:[{w,s,e,ph}], phones:[{p,w,s,e}]}}."""
import json, re, numpy as np, librosa
from pocketsphinx import Decoder

A = "../../audio/"
# transcripts from ../../audio/transcripts.json, corrected by ear
TEXT = {
 "narrator/narrator_01_deadline-day-intro.mp3": "Manchester United. Transfer deadline day. The manager asked for two players. He got three midfielders. Nobody appears entirely sure why. This is All or Something.",
 "michael-carrick/carrick_01_two-things-left-back-striker.mp3": "Right. Just two things. Left back. Striker. Brilliant. Sorry. I said left back and striker. That's not the same thing. Look, I'm not complaining.",
 "michael-carrick/carrick_02_not-complaining-whos-scoring.mp3": "Look, I'm not complaining. Obviously, love the lads, great window. But who's actually scoring the goals? And the left back? Luke? For the whole season?",
 "michael-carrick/carrick_03_no-striker-brilliant_take1.mp3": "Right, so no striker? No left back? But three midfielders? Yeah, brilliant, brilliant.",
 "jason-wilcox/jason_01_sorted-three-midfielders.mp3": "Sorted. We bought three midfielders. Yeah, but three midfielders. It's three things instead of two. Technically, you've won. Who's scoring? Bruno.",
 "jason-wilcox/jason_02_perfect-loads-of-midfielders.mp3": "Perfect. We've got loads of midfielders. Left back. We've got Luke. For the whole season, next question. No striker. No left back. Three midfielders.",
 "omar-berrada/omar_01_market-presented-opportunities.mp3": "Yeah, but three midfielders. We felt the market presented opportunities and we took those opportunities. Were they the positions we needed? No.",
 "omar-berrada/omar_02_efficient-recruitment.mp3": "But they were available. Who's scoring the goals? Bruno. He's already here, so technically that's efficient recruitment. Left back, we have internal solutions.",
 "omar-berrada/omar_03_no-striker-three-midfielders.mp3": "No striker. No left back. Three midfielders.",
 "bruno-fernandes/bruno_01_sorry-what-three-midfielders.mp3": "Sorry, what? You bought three midfielders? So who am I crossing the ball to? Me? I'm taking the corner. I'm a midfielder. Brilliant. Absolutely brilliant.",
 "bruno-fernandes/bruno_02_should-have-gone-to-saudi.mp3": "What am I even doing here? Saudi Arabia offered me sunshine and probably a striker. No left back, no striker. I should have gone to Saudi.",
 "jim-ratcliffe/jim_01_bigger-issues-facing-britain.mp3": "We need to focus on the bigger issues facing Britain. Standards, discipline, efficiency. Everyone always wants more players. Sometimes you have to make do with what you've got.",
 "jim-ratcliffe/jim_02_i-live-in-monaco.mp3": "That's how you build character and save money. Yes. I live in Monaco. That's completely different. It gives me an outside perspective.",
}
EXTRA = {"midfielders": "M IH D F IY L D ER Z", "midfielder": "M IH D F IY L D ER", "saudi": "S AW D IY",
         "monaco": "M AA N AH K OW", "carrick": "K AE R IH K"}


def words_of(text):
    return re.sub(r"[^a-z' ]", " ", text.lower().replace("-", " ")).split()


def align(f, text):
    y, _ = librosa.load(f, sr=16000, mono=True)
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
    d = Decoder(samprate=16000, bestpath=False, loglevel="FATAL")
    for w, ph in EXTRA.items():
        if d.lookup_word(w) is None: d.add_word(w, ph, True)
    ws = words_of(text)
    d.set_align_text(" ".join(ws))
    d.start_utt(); d.process_raw(pcm, full_utt=True); d.end_utt()
    d.set_alignment()
    d.start_utt(); d.process_raw(pcm, full_utt=True); d.end_utt()
    words, phones = [], []
    for wseg in d.get_alignment():
        name = re.sub(r"\(\d+\)$", "", wseg.name)
        if name in ("<sil>", "<s>", "</s>", "[NOISE]"): continue
        i = len(words)
        ps = [(p.name, p.start / 100, (p.start + p.duration) / 100) for p in wseg]
        words.append({"w": name, "s": wseg.start / 100, "e": (wseg.start + wseg.duration) / 100, "ph": [p[0] for p in ps]})
        phones += [{"p": n, "w": i, "s": s, "e": e} for n, s, e in ps]
    assert [w["w"] for w in words] == ws, ([w["w"] for w in words], ws)
    return {"dur": len(y) / 16000, "words": words, "phones": phones}


if __name__ == "__main__":
    out = {}
    for k, t in TEXT.items():
        out[k] = align(A + k, t)
        print("==", k); print("  ".join(f"{w['w']}@{w['s']:.2f}-{w['e']:.2f}" for w in out[k]["words"]))
    json.dump(out, open("phones.json", "w"), indent=1)
