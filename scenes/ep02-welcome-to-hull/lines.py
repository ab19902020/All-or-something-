"""Every line of Episode 2, cut word-exact from the voice clips in ../../audio.

Each scripted line is taken from its clip at the aligned word boundaries (phones.json); nothing is re-ordered
inside a line. Cuts snap to the quietest point in the gap next to the first / last word, so no breath or
neighbouring word leaks in. A line whose voice has not been recorded yet (see MISSING) gets a silent slot sized
from its syllables (mouth closed) until its clip is filed in ../../audio/ and added to align.py's TEXT; then it is
cut like every other line.

Output: build/lines/<id>.wav (48 kHz mono) and build/lines.json {id: {speaker, clip, dur, text, words, phones}}
with word / phone times relative to the start of the cut."""
import json, os, re, glob, numpy as np, librosa, soundfile as sf

A = "../../audio/"
CLIP = dict(
    nar3="narrator/narrator_03_new-season-hull-same-corners.mp3",
    ck10="michael-carrick/carrick_10_fresh-season-same-corner-impact.mp3",
    br3="bruno-fernandes/bruno_03_nine-of-us-seventy-percent-saudi.mp3",
    mn1="kobbie-mainoo/mainoo_01_again-came-on-after-67-ipswich.mp3",
    mg1="harry-maguire/maguire_01_play-striker-set-pieces-shooting.mp3",
    sh1="steve-holland/steve_01_practise-defending-wrong-door-ipswich.mp3",
)
SPK = dict(nar="narrator", ck="carrick", sh="steve", mn="mainoo", br="bruno", mg="maguire")

# (id, clip, words, occurrence) in script order
LINES = [
    # ---- opening: MKM Stadium
    ("nar_new_season", "nar3", "new season new manchester united", 1),
    ("nar_probably", "nar3", "probably", 1),
    # ---- pre-match dressing room
    ("ck_right_lads", "ck10", "right lads fresh season clean slate", 1),
    ("ck_hull_come_up", "ck10", "hull have just come up so they'll be aggressive physical dangerous from set pieces", 1),
    ("sh_practise", "sh1", "should we practise defending those then", 1),
    ("ck_already", "ck10", "already did thursday", 1),
    ("sh_attacking", "sh1", "that was attacking corners", 1),
    ("ck_same_corner", "ck10", "same corner though isn't it", 1),
    ("ck_kobbie", "ck10", "kobbie you're on the bench", 1),
    ("mn_again", "mn1", "again", 1),
    ("ck_bought", "ck10", "we've bought midfielders", 1),
    ("mn_noticed", "mn1", "i noticed", 1),
    ("br_nine", "br3", "we've got about nine of us now", 1),
    ("mg_striker", "mg1", "can any of them play striker", 1),
    ("ck_come_on", "ck10", "right hull city come on", 1),
    ("sh_wrong_door", "sh1", "michael wrong door", 1),
    # ---- the match: the score, the narrator's verdict, the Hull fans' chant
    ("nar_knew", "nar3", "manchester united knew exactly what was coming", 1),
    ("nar_did_not_help", "nar3", "it did not help", 1),
    # ---- post-match dressing room
    ("ck_positives", "ck10", "right positives", 1),
    ("br_possession", "br3", "we had seventy percent possession", 1),
    ("sh_excellent", "sh1", "excellent", 1),
    ("br_lost", "br3", "we lost two zero", 1),
    ("sh_less_excellent", "sh1", "less excellent", 1),
    ("mg_both_goals", "mg1", "both goals were set pieces", 1),
    ("ck_yep1", "ck10", "yep", 1),
    ("mg_warned", "mg1", "the thing you warned us about before the game", 1),
    ("ck_yep2", "ck10", "yep", 2),
    ("mg_twice", "mg1", "twice", 1),
    ("ck_aware", "ck10", "harry i'm aware", 1),
    ("mn_came_on", "mn1", "i came on after sixty seven minutes two nil down", 1),
    ("mn_plan", "mn1", "what exactly was the plan", 1),
    ("ck_impact", "ck10", "impact", 1),
    ("mn_didnt_score", "mn1", "we didn't score", 1),
    ("ck_nearly", "ck10", "nearly impact", 1),
    ("br_newly", "br3", "so newly promoted hull two set pieces no goals", 1),
    ("mg_shooting", "mg1", "i had to start shooting", 1),
    ("br_centre_back", "br3", "harry you're a centre back", 1),
    ("mg_nobody", "mg1", "nobody else was doing it", 1),
    ("sh_good_news", "sh1", "good news", 1),
    ("sh_ipswich", "sh1", "we've got ipswich next", 1),
    ("mn_ipswich", "mn1", "didn't ipswich just get promoted as well", 1),
    ("ck_good_meeting", "ck10", "good meeting", 1),
    ("br_saudi", "br3", "can somebody check if saudi are still calling", 1),
    # ---- title
    ("nar_title", "nar3", "new season same corners this is all or something", 1),
]
SR = 48000
# pauses inside a line longer than this are shortened to it (Shorts pacing: no dead air); per-line overrides
MAXGAP, GAP = 0.20, {"nar_new_season": 0.42, "ck_right_lads": 0.28, "ck_hull_come_up": 0.21, "ck_come_on": 0.22,
                     "nar_title": 0.30, "mn_came_on": 0.24, "sh_wrong_door": 0.30}
# every line is played a little faster (ffmpeg atempo: pitch unchanged) to keep the Short's pace
TEMPO = 1.08
# voices not recorded yet: {clip key: glob under ../../audio}. Once the file exists, add its transcript to
# align.py's TEXT and run align.py; until then each of its lines is a silent slot sized from its syllables.
MISSING = {}


def est_dur(text):
    """a deadpan delivery's length for a line nobody has recorded yet"""
    syl = sum(max(1, len(re.findall(r"[aeiouy]+", w))) for w in words_of(text))
    return round((0.18 + 0.19 * syl) / TEMPO, 2)


def words_of(t):
    return re.sub(r"[^a-z' ]", " ", t.lower()).split()


def find(words, seq, occ):
    n, k = len(seq), 0
    for i in range(len(words) - n + 1):
        if [w["w"] for w in words[i:i + n]] == seq:
            k += 1
            if k == occ: return i, i + n - 1
    raise KeyError(" ".join(seq))


def quiet_point(y, sr, a, b):
    """time of the lowest-energy 20 ms window between a and b (seconds)"""
    if b - a < 0.03: return (a + b) / 2
    i0, i1 = int(a * sr), int(b * sr)
    seg = y[i0:i1] ** 2
    w = int(0.02 * sr)
    if len(seg) <= w: return (a + b) / 2
    e = np.convolve(seg, np.ones(w) / w, mode="valid")
    return (i0 + int(np.argmin(e)) + w // 2) / sr


def tempo(seg):
    """speed a cut up by TEMPO without changing its pitch (ffmpeg atempo)"""
    import subprocess, tempfile
    if abs(TEMPO - 1) < 1e-3: return seg
    with tempfile.TemporaryDirectory() as d:
        sf.write(f"{d}/a.wav", seg.astype(np.float32), SR)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{d}/a.wav", "-filter:a", f"atempo={TEMPO}",
                        "-ar", str(SR), f"{d}/b.wav"], check=True)
        return sf.read(f"{d}/b.wav", dtype="float32")[0]


def main():
    ph = json.load(open("phones.json"))
    os.makedirs("build/lines", exist_ok=True)
    out, cache = {}, {}
    for lid, clip, text, occ in LINES:
        spk = SPK[lid.split("_")[0]]
        if clip in MISSING:
            found = sorted(glob.glob(A + MISSING[clip]))
            key = found[0][len(A):] if found else None
            if key is None or key not in ph:
                dur = est_dur(text)
                sf.write(f"build/lines/{lid}.wav", np.zeros(int(dur * SR), np.float32), SR)
                out[lid] = dict(speaker=spk, clip=None, dur=dur, text=text, words=[], phones=[], missing=True)
                why = "not aligned yet (add it to align.py TEXT)" if key else "NO RECORDING"
                print(f"{lid:20s} {why} -> {dur:.2f}s silent slot: {text}")
                continue
            path = A + key
        else:
            key = CLIP[clip]; path = A + key
        if key not in cache: cache[key] = librosa.load(path, sr=SR, mono=True)[0]
        y = cache[key]
        W, P = ph[key]["words"], ph[key]["phones"]
        i, j = find(W, words_of(text), occ)
        s, e = W[i]["s"], W[j]["e"]
        prev_e = W[i - 1]["e"] if i > 0 else 0.0
        next_s = W[j + 1]["s"] if j + 1 < len(W) else len(y) / SR
        cs = quiet_point(y, SR, max(prev_e, s - 0.10), s) if s - prev_e > 0.04 else s
        ce = quiet_point(y, SR, e, min(next_s, e + 0.14)) if next_s - e > 0.04 else e
        # keep-intervals of the clip: the whole cut, minus the middle of any long pause between words
        keep, a = [], cs
        for k in range(i, j):
            g0, g1 = W[k]["e"], W[k + 1]["s"]
            mg = GAP.get(lid, MAXGAP)
            L = g1 - g0
            if L > mg + 0.05:
                q = quiet_point(y, SR, g0 + 0.04, g1 - 0.04)
                cut = L - mg
                r0 = min(max(g0 + 0.02, q - cut / 2), g1 - 0.02 - cut)
                keep.append((a, r0)); a = r0 + cut
        keep.append((a, ce))
        f = int(0.008 * SR)
        parts, tmap = [], []
        t = 0.0
        for k0, k1 in keep:
            p = y[int(k0 * SR):int(k1 * SR)].copy()
            p[:f] *= np.linspace(0, 1, f); p[-f:] *= np.linspace(1, 0, f)
            parts.append(p); tmap.append((k0, k1, t)); t += len(p) / SR
        seg = np.concatenate(parts)
        def T(x):
            for k0, k1, o in tmap:
                if x <= k1: return round(o + max(0.0, x - k0), 3)
            return round(tmap[-1][2] + x - tmap[-1][0], 3)
        seg = tempo(seg)
        sf.write(f"build/lines/{lid}.wav", seg.astype(np.float32), SR)
        phones = [dict(p=p["p"], s=round(T(p["s"]) / TEMPO, 3), e=round(T(p["e"]) / TEMPO, 3)) for p in P if i <= p["w"] <= j]
        words = [dict(w=w["w"], s=round(T(w["s"]) / TEMPO, 3), e=round(T(w["e"]) / TEMPO, 3)) for w in W[i:j + 1]]
        out[lid] = dict(speaker=spk, clip=key, dur=round(len(seg) / SR, 3), text=text, words=words, phones=phones)
        ce = cs + len(seg) / SR
        print(f"{lid:20s} {cs:6.2f}-{ce:6.2f} ({ce - cs:4.2f}s) {text}")
    json.dump(out, open("build/lines.json", "w"), indent=1)


if __name__ == "__main__":
    main()
