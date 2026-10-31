"""Clear the Air: the mix's stems, as 32-bit float, each at the level it plays at in build/episode_audio.wav
(before the limiter): dialogue (the clean lines, nothing under them), effects (the room, the city, the foley) and
music. Together they make the mix to within the limiter's last fraction of a dB.
python3 -c "from studio.film import ep; ep.use('clear-the-air'); import sys; sys.path.insert(0, str(ep.DIR));
            from film.stems import main; main()"  ->  build/stems/*.wav"""
import numpy as np
import soundfile as sf

from studio.film import audio as A
from studio.film import ep
from film import sound as S


def main(target=-14.0):
    dlg, amb, fx, mus = A.Bus(), A.Bus(), A.Bus(), A.Bus()
    A.dialogue(dlg, room_s=0.3, room_db=-24)
    S.ambience(amb)
    S.foley(fx)
    S.music(mus)
    ld = A.lufs(dlg.x)
    e = (amb.x + fx.x) * A.db(A.FX_DB)
    e = e * A.rider(e, ld + A.FX_CEIL)[:, None]
    m = mus.x * A.db(A.MUSIC_DB)
    m = m * (A.rider(m, ld + A.MUSIC_CEIL) * A.duck(dlg))[:, None]
    mix = dlg.x + e + m
    g = A.db(target - A.lufs(mix))
    lim = A.soft_limit(mix * g)
    g *= A.db(target - A.lufs(lim))
    out = ep.path("stems")
    out.mkdir(exist_ok=True)
    for name, x in (("dialogue", dlg.x), ("effects", e), ("music", m)):
        y = (x * g).astype(np.float32)                  # 32-bit float: a transient over 0 dBFS survives
        sf.write(str(out / f"{name}.wav"), y, A.SR, subtype="FLOAT")
        print(f"{out / name}.wav  {A.lufs(y):.1f} LUFS  peak {20 * np.log10(np.abs(y).max() + 1e-9):.1f} dBFS")
