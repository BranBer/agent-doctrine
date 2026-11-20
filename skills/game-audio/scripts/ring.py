"""Finds metal in a take: how long anything in it rings at one pitch.

Steel rings for hundreds of milliseconds at one pitch; bone, wood and flesh knock and die in tens;
air never holds a pitch. Per file: the longest run of 5.8 ms frames in which one partial (a bin,
allowing a bin of drift) stays 12 dB or more over the spectrum's own trend (a 35th percentile over
61 bins), between 900 Hz and 9 kHz, counting only frames within 35 dB of the file's loudest.

    uv run --no-project --with numpy --with soundfile --with scipy python -I ring.py <file>...

RINGS at 120 ms or more, "rings a little" from 60 ms. Judged against the playtester (takes.md,
"clank" and "air"): every take they heard as "the clanking of a sword when it should swish" rang
160-540 ms; the set that replaced it, which they kept, 16-58 ms; air made in-house, 16-75 ms. Signal
measures only, so it may run on any file, Sonniss included.
"""

import sys

import numpy as np
import soundfile as sf
from scipy.ndimage import maximum_filter1d, percentile_filter, uniform_filter1d
from scipy.signal import stft

HOP = 256


def ring(x, sr):
    f, _, z = stft(x, sr, nperseg=2048, noverlap=2048 - HOP, boundary=None)
    p = uniform_filter1d(np.abs(z) ** 2, 3, axis=1) + 1e-20  # about 17 ms
    db = 10 * np.log10(p)
    ex = db - percentile_filter(db, 35, size=(61, 1), mode="nearest")
    ex[~((f >= 900) & (f <= 9000))] = 0
    frame = 10 * np.log10(p.sum(axis=0))
    hot = (ex >= 12) & (frame >= frame.max() - 35)[None, :]
    hot = maximum_filter1d(hot.astype(np.uint8), 3, axis=0).astype(bool)  # a bin of drift
    best, at, fr = 0, 0, 0.0
    run = np.zeros(len(f), dtype=int)
    for j in range(hot.shape[1]):
        run = np.where(hot[:, j], run + 1, 0)
        k = int(run.argmax())
        if run[k] > best:
            best, at, fr = int(run[k]), j, float(f[k])
    return best * HOP / sr, (at - best + 1) * HOP / sr, fr


def main():
    worst = 0.0
    for path in sys.argv[1:]:
        x, sr = sf.read(path, always_2d=True)
        secs, start, fr = ring(x.mean(axis=1), sr)
        worst = max(worst, secs)
        tag = "RINGS" if secs >= 0.12 else ("rings a little" if secs >= 0.06 else "")
        print(f"{path.replace(chr(92), '/').split('/')[-1]:28} longest ring {secs * 1000:4.0f} ms from {start:4.2f} s at {fr / 1000:5.2f} kHz  {tag}")
    print(f"read {len(sys.argv) - 1} files; the longest ring {worst * 1000:.0f} ms")
    sys.exit(1 if worst >= 0.12 else 0)


main()
