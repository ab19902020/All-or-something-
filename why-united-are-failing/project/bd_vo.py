"""the breakdown's voice track: each chosen take trimmed, its inner pauses capped, lines joined with short gaps
-> vo.wav (48 kHz mono) and vo_times.json [(id, start, end)]"""
import json, sys, numpy as np, librosa, soundfile as sf
d = sys.argv[1]
pick = json.load(open(f"{d}/pick.json"))
order = ["V01", "V02", "V03", "V04", "V05", "V07", "V08", "V09", "V10", "V11"]
SR = 48000
GAP_IN, GAP = 0.22, {"V03": 0.3, "V05": 0.22, "V07": 0.22, "V08": 0.35, "V10": 0.25, "V11": 0.3}
out, times, t = [np.zeros(int(0.35 * SR), np.float32)], [], 0.35
for lid in order:
    y, _ = librosa.load(f"{d}/takes/{pick[lid]}", sr=SR)
    iv = librosa.effects.split(y, top_db=40, frame_length=1024, hop_length=256)
    segs = []
    for k, (a, b) in enumerate(iv):
        a, b = max(0, a - int(0.03 * SR)), min(len(y), b + int(0.04 * SR))
        if segs:
            gap = (a - prev_b) / SR
            if gap > GAP_IN:
                segs.append(np.zeros(int(GAP_IN * SR), np.float32))
            else:
                segs.append(y[prev_b:a])
        segs.append(y[a:b])
        prev_b = b
    line = np.concatenate(segs)
    n = min(int(0.006 * SR), len(line) // 4)
    line[:n] *= np.linspace(0, 1, n)
    line[-n:] *= np.linspace(1, 0, n)
    pre = GAP.get(lid, 0.14) if times else 0.0
    out.append(np.zeros(int(pre * SR), np.float32)); t += pre
    times.append((lid, round(t, 3), round(t + len(line) / SR, 3)))
    out.append(line); t += len(line) / SR
out.append(np.zeros(int(0.2 * SR), np.float32)); t += 0.2
vo = np.concatenate(out)
sf.write(f"{d}/vo.wav", vo, SR, subtype="PCM_24")
json.dump(times, open(f"{d}/vo_times.json", "w"), indent=1)
print("voice track", round(t, 2), "s")
for x in times: print(x)
