"""Word + phone forced alignment (pocketsphinx, en-us model from the PyPI wheel) of every voice clip the episode
uses, against its corrected transcript. Output: phones.json {clip: {dur, words:[{w,s,e,ph}], phones:[{p,w,s,e}]}}."""
import json, re, sys, numpy as np, librosa
from pocketsphinx import Decoder

A = "../../audio/"
# transcripts from ../../audio/transcripts.json, corrected by ear
TEXT = {
 "narrator/narrator_03_new-season-hull-same-corners.mp3": "New season. New Manchester United. Probably. Hull City. Newly promoted. Physical. Aggressive. Dangerous from set pieces. Manchester United knew exactly what was coming. It did not help. Hull City two. Manchester United nil. Seventy percent possession, zero points. New season, same corners. This is All or Something.",
 "michael-carrick/carrick_10_fresh-season-same-corner-impact.mp3": "Right lads, fresh season, clean slate. Hull have just come up, so they'll be aggressive, physical, dangerous from set pieces. Already did. Thursday. Same corner though, isn't it? Kobbie, you're on the bench. We've bought midfielders. Right, Hull City, come on. Right, positives. Yep. Yep. Harry, I'm aware. Impact. Nearly impact. Good meeting.",
 "bruno-fernandes/bruno_03_nine-of-us-seventy-percent-saudi.mp3": "We've got about nine of us now. Can any of them actually play striker though? So we know they're dangerous from set pieces and the plan is hope they don't get one. Brilliant, absolutely brilliant. We had seventy percent possession, we lost two zero. Two set pieces, two goals. The exact thing we talked about before the game. So, newly promoted Hull, two set pieces, no goals. Harry, you're a centre back. And somehow you were the one having shots. What are we actually doing here? Saudi Arabia offered me sunshine, they probably had a striker as well. Can somebody check if Saudi are still calling? I should have went to Saudi.",
 "kobbie-mainoo/mainoo_01_again-came-on-after-67-ipswich.mp3": "Again? I noticed. I came on after sixty seven minutes, two nil down. What exactly was the plan? We didn't score. Didn't Ipswich just get promoted as well? So that's two newly promoted teams in a row then. Lovely. Good start to the season. This",
 "harry-maguire/maguire_01_play-striker-set-pieces-shooting.mp3": "Can any of them play striker? Both goals were set pieces. The thing you warned us about before the game. Twice. I had to start shooting. Nobody else was doing it. I'm a centre back and somehow I'm the goal threat. That's probably not ideal. Still, could have been three.",
}
# clips aligned from a start time (seconds): the phone pass fails on the whole of Jim's third clip, so only its
# first "Good meeting." is aligned (times are still clip times)
CROP = {}
EXTRA = {"midfielders": "M IH D F IY L D ER Z", "midfielder": "M IH D F IY L D ER", "saudi": "S AW D IY",
         "monaco": "M AA N AH K OW", "carrick": "K AE R IH K", "kobbie": "K AA B IY", "ipswich": "IH P S W IH CH",
         "maguire": "M AH G W AY ER"}


def words_of(text):
    return re.sub(r"[^a-z' ]", " ", text.lower().replace("-", " ")).split()


def align(f, text, crop=None):
    y, _ = librosa.load(f, sr=16000, mono=True)
    if crop:
        t0, t1 = crop
        r = align_samples(y[int(t0 * 16000):int(t1 * 16000)], text)
        for w in r["words"]: w["s"] += t0; w["e"] += t0
        for p in r["phones"]: p["s"] += t0; p["e"] += t0
        r["dur"] = len(y) / 16000
        return r
    return align_samples(y, text)


def align_samples(y, text):
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
    import os
    out = json.load(open("phones.json")) if os.path.exists("phones.json") and "--all" not in sys.argv else {}
    for k, t in TEXT.items():
        if k in out: continue
        out[k] = align(A + k, t, CROP.get(k))
        print("==", k); print("  ".join(f"{w['w']}@{w['s']:.2f}-{w['e']:.2f}" for w in out[k]["words"]))
    json.dump(out, open("phones.json", "w"), indent=1)
