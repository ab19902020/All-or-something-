"""Checks on the finished mix: levels at the moments that matter (the music stopping dead before "Probably", the
full-time burst and the silence after it, the chant, the dead-quiet room, the hopeful music dying, the title, the
loop point) and, with --words, a re-transcription of every line from the mix (Whisper turbo) to prove each one is
intelligible over the music and effects.
python3 check_audio.py [--words]"""
import sys, json, numpy as np, soundfile as sf
from timeline import TL

x, sr = sf.read("build/episode_audio.wav")
x = x.mean(1)
M = TL["marks"]


def rms(a, b):
    s = x[int(a * sr):int(b * sr)]
    return 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9)


L0 = TL["lines"]
for name, a, b in [("exterior, music", 0.3, 2.8), ("just before the stop", M["music_stop"] - 0.3, M["music_stop"]),
                   ("after the stop", M["music_stop"] + 0.02, M["music_stop"] + 0.4),
                   ("dressing room, no one talking", M["cut_br1"] + 0.1, M["cut_ck4"] - 0.05),
                   ("full-time burst", M["cut_score"] + 0.05, M["cut_score"] + 0.5),
                   ("silence after it", M["cut_score"] + 0.75, L0["nar_knew"]["start"] - 0.1),
                   ("the chant", M["chant"] + 0.3, M["cut_post_wide"] - 0.1),
                   ("post-match silence", M["cut_post_wide"] + 0.1, L0["ck_positives"]["start"] - 0.05),
                   ("hopeful music", L0["sh_good_news"]["end"] + 0.2, M["cut_sh7"]),
                   ("after it dies", L0["sh_ipswich"]["end"] + 0.05, L0["mn_ipswich"]["start"] - 0.05),
                   ("black", M["cut_black"] + 0.05, M["cut_title"] - 0.02),
                   ("title boom", M["cut_title"], M["cut_title"] + 0.3),
                   ("Tigers ending", M["cut_tigers"] + 0.2, TL["total"] - 0.1),
                   ("last 0.3 s", TL["total"] - 0.3, TL["total"])]:
    print(f"{name:30s} {rms(a, b):6.1f} dB")
print(f"{'whole mix':30s} {rms(0, TL['total']):6.1f} dB   peak {20 * np.log10(np.abs(x).max()):.1f} dBFS")

if "--words" in sys.argv:
    import librosa, sherpa_onnx
    Mo = "models/sherpa-onnx-whisper-turbo/turbo-"
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=Mo + "encoder.int8.onnx", decoder=Mo + "decoder.int8.onnx",
                                                     tokens=Mo + "tokens.txt", language="en", task="transcribe", num_threads=4)
    y16 = librosa.resample(x.astype(np.float32), orig_sr=sr, target_sr=16000)
    L = json.load(open("build/lines.json"))
    for lid, v in TL["lines"].items():
        if L[lid].get("missing"): print(f"{lid:20s} (no recording yet)"); continue
        seg = y16[int((v["start"] - 0.05) * 16000):int((v["end"] + 0.05) * 16000)]
        s = rec.create_stream(); s.accept_waveform(16000, seg); rec.decode_stream(s)
        print(f"{lid:20s} want: {L[lid]['text']:55s} heard: {s.result.text.strip()}")
