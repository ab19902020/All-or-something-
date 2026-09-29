"""Every line of Episode 1, cut word-exact from the voice clips in ../../audio.

Each scripted line is taken from its clip at the aligned word boundaries (phones.json); nothing is re-ordered
inside a line. Cuts snap to the quietest point in the gap next to the first / last word, so no breath or
neighbouring word leaks in. A line whose clip does not exist yet (Bruno's "Jim... you live in Monaco") plays as a
short silent reaction beat (mouth closed) until the recording is added; then it is aligned and used automatically.

Output: build/lines/<id>.wav (48 kHz mono) and build/lines.json {id: {speaker, clip, dur, text, words, phones}}
with word / phone times relative to the start of the cut."""
import json, os, re, glob, numpy as np, librosa, soundfile as sf

A = "../../audio/"
CLIP = dict(
    nar="narrator/narrator_01_deadline-day-intro.mp3",
    ck1="michael-carrick/carrick_01_two-things-left-back-striker.mp3",
    ck2="michael-carrick/carrick_02_not-complaining-whos-scoring.mp3",
    ck3="michael-carrick/carrick_03_no-striker-brilliant_take1.mp3",
    js1="jason-wilcox/jason_01_sorted-three-midfielders.mp3",
    js2="jason-wilcox/jason_02_perfect-loads-of-midfielders.mp3",
    om1="omar-berrada/omar_01_market-presented-opportunities.mp3",
    om2="omar-berrada/omar_02_efficient-recruitment.mp3",
    om3="omar-berrada/omar_03_no-striker-three-midfielders.mp3",
    br1="bruno-fernandes/bruno_01_sorry-what-three-midfielders.mp3",
    br2="bruno-fernandes/bruno_02_should-have-gone-to-saudi.mp3",
    jr1="jim-ratcliffe/jim_01_bigger-issues-facing-britain.mp3",
    jr2="jim-ratcliffe/jim_02_i-live-in-monaco.mp3",
    jr3="jim-ratcliffe/jim_03_excellent-business-good-meeting.mp3",
)
SPK = dict(nar="narrator", ck="carrick", js="jason", om="omar", br="bruno", jr="jim")

# (id, clip, words, occurrence) in script order
LINES = [
    ("nar_deadline", "nar", "manchester united transfer deadline day", 1),
    ("ck_two_things", "ck1", "right just two things left back striker", 1),
    ("js_sorted", "js1", "sorted", 1),
    ("ck_brilliant", "ck1", "brilliant", 1),
    ("js_bought", "js1", "we bought three midfielders", 1),
    ("ck_i_said", "ck1", "sorry i said left back and striker", 1),
    ("om_yeah_but", "om1", "yeah but three midfielders", 1),
    ("js_three_things", "js1", "it's three things instead of two technically you've won", 1),
    ("om_positions", "om1", "were they the positions we needed no", 1),
    ("br_you_bought", "br1", "you bought three midfielders", 1),
    ("ck_not_complaining", "ck2", "look i'm not complaining obviously love the lads great window", 1),
    ("ck_whos_scoring", "ck2", "but who's actually scoring the goals", 1),
    ("om_bruno", "om2", "bruno", 1),
    ("br_sorry_what", "br1", "sorry what", 1),
    ("om_efficient", "om2", "he's already here so technically that's efficient recruitment", 1),
    ("br_crossing", "br1", "so who am i crossing the ball to", 1),
    ("js_bruno", "js1", "bruno", 1),
    ("br_me", "br1", "me i'm taking the corner", 1),
    ("br_midfielder", "br1", "i'm a midfielder", 1),
    ("js_perfect", "js2", "perfect we've got loads of midfielders", 1),
    ("br_brilliant", "br1", "brilliant absolutely brilliant", 1),
    ("ck_left_back", "ck2", "and the left back", 1),
    ("js_luke", "js2", "we've got luke", 1),
    ("ck_luke", "ck2", "luke for the whole season", 1),
    ("js_next_question", "js2", "next question", 1),
    ("jr_bigger_issues", "jr1", "we need to focus on the bigger issues facing britain", 1),
    ("br_monaco", "br3", "jim you live in monaco", 1),
    ("jr_yes_monaco", "jr2", "yes i live in monaco", 1),
    ("jr_perspective", "jr2", "it gives me an outside perspective", 1),
    ("ck_no_striker", "ck3", "right so no striker", 1),
    ("om_no_striker", "om3", "no striker", 1),
    ("ck_no_left_back", "ck3", "no left back", 1),
    ("js_no_left_back", "js2", "no left back", 1),
    ("ck_but_three", "ck3", "but three midfielders", 1),
    ("js_three_mids", "js2", "three midfielders", 1),
    ("om_three_mids", "om3", "three midfielders", 1),
    ("jr_good_meeting", "jr3", "good meeting", 1),
    ("br_sunshine", "br2", "saudi arabia offered me sunshine", 1),
    ("br_saudi", "br2", "i should have gone to saudi", 1),
    ("nar_title", "nar", "this is all or something", 1),
]
SR = 48000
# pauses inside a line longer than this are shortened to it (Shorts pacing: no dead air); per-line overrides
MAXGAP, GAP = 0.20, {"ck_two_things": 0.32, "jr_yes_monaco": 0.36, "br_me": 0.30, "ck_luke": 0.30}
# every line is played 6 % faster (ffmpeg atempo: pitch unchanged) to keep the Short's pace
TEMPO = 1.08
# Bruno's Monaco line is not recorded yet: any clip named like this is used when it appears
MISSING = {"br3": ("bruno-fernandes/bruno_03_*.mp3", 1.25)}


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
            pat, dur = MISSING[clip]
            found = sorted(glob.glob(A + pat))
            if not found:
                # no recording yet: the line plays as a silent reaction beat (mouth closed) until it is added
                sf.write(f"build/lines/{lid}.wav", np.zeros(int(dur * SR), np.float32), SR)
                out[lid] = dict(speaker=spk, clip=None, dur=dur, text=text, words=[], phones=[], missing=True)
                print(f"{lid:20s} NO RECORDING -> {dur:.2f}s silent beat: {text}")
                continue
            import align
            key = found[0][len(A):]
            ph[key] = align.align(found[0], text)
            path = found[0]
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
