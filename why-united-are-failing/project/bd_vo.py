"""the breakdown's voice track: each chosen take whole (nothing cut inside a line), trimmed only at its quiet ends
with soft fades, lines joined by short natural gaps over a faint room tone -> vo.wav (48 kHz mono), vo_times.json"""
import json, sys, numpy as np, librosa, soundfile as sf
d = sys.argv[1]
pick = json.load(open(f"{d}/pick.json"))
order = ["V01", "V02", "V03", "V04", "V05", "V07", "V08", "V09", "V10", "V11"]
SR = 48000
GAP = {"V03": 0.3, "V08": 0.35, "V10": 0.22, "V11": 0.3}
lines = []
for lid in order:
    y, _ = librosa.load(f"{d}/takes/{pick[lid]}", sr=SR)
    _, (a, b) = librosa.effects.trim(y, top_db=45, frame_length=1024, hop_length=128)
    a, b = max(0, a - int(0.04 * SR)), min(len(y), b + int(0.16 * SR))
    seg = y[a:b].copy()
    fi, fo = int(0.015 * SR), int(0.12 * SR)
    seg[:fi] *= np.linspace(0, 1, fi) ** 2
    seg[-fo:] *= np.linspace(1, 0, fo) ** 2
    lines.append((lid, seg))
times, t = [], 0.35
for k, (lid, seg) in enumerate(lines):
    if k:
        t += GAP.get(lid, 0.12)
    times.append((lid, round(t, 3), round(t + len(seg) / SR, 3)))
    t += len(seg) / SR
n = int((t + 0.2) * SR)
rng = np.random.default_rng(2)
room = rng.standard_normal(n).astype(np.float32)
room = np.cumsum(room) * 0.02                       # a soft, dark room tone under everything (-60 dB or so)
room -= np.convolve(room, np.ones(4801) / 4801, mode="same")
room *= 10 ** (-60 / 20) / (np.sqrt(np.mean(room ** 2)) + 1e-9)
vo = room.copy()
for (lid, a, b), (_, seg) in zip(times, lines):
    i = int(round(a * SR))
    vo[i:i + len(seg)] += seg
sf.write(f"{d}/vo.wav", vo, SR, subtype="PCM_24")
json.dump(times, open(f"{d}/vo_times.json", "w"), indent=1)
print("voice track", round(t + 0.2, 2), "s")
