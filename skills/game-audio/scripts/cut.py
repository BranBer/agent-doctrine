"""Cuts takes at explicit times from library files, for sounds the slicer can't find on its own (several
events inside one take, a whoosh that runs into its own thud). Signal processing only.

    uv run --no-project --with numpy --with scipy --with soundfile python -I cut.py <plan.json> <out dir>

plan.json: {"<name>": {"src": "<wav>", "cuts": [[from_s, to_s], ...], "rate": 1, "lowcut": 0,
            "release": 0.2, "meta": {provenance fields}}, ...}

rate < 1 plays the take lower and longer (it is resampled, as a slower playback would). Each cut
starts with a 1 ms fade-in; at its end the source keeps playing under an exponential release of
`release` seconds, at least 200 ms when the take is still within 30 dB of its peak there (the line
`slice.py --audit` judges by), so no take stops while sounding. A cut that runs to the source's own
end keeps the take to it, and its provenance says so. Peaks go to -1 dBFS; files are mono 48 kHz
Ogg Vorbis. Writes <out>/<name>-<n>.ogg and <out>/provenance.json. Run `slice.py --audit` on that
provenance afterwards.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

RATE = 48000


def mono48(path):
    try:
        x, rate = sf.read(path, always_2d=True, dtype="float64")
    except sf.LibsndfileError:
        from scipy.io import wavfile

        rate, raw = wavfile.read(path)
        x = raw.astype(np.float64)
        if raw.dtype.kind == "i":
            x /= np.iinfo(raw.dtype).max
        x = x.reshape(len(x), -1)
    x = x.mean(axis=1)
    if rate != RATE:
        g = np.gcd(int(rate), RATE)
        x = signal.resample_poly(x, RATE // g, int(rate) // g)
    return x


def db_at(y, i, win=240):
    seg = y[max(0, i - win) : i + 1]
    return 20 * np.log10(np.sqrt(np.mean(seg**2)) + 1e-12)


def cut_one(x, a, b, spec):
    release = float(spec.get("release", 0.2))
    rate = float(spec.get("rate", 1))
    ia, ib = int(a * RATE), int(b * RATE)
    peak_db = 20 * np.log10(np.max(np.abs(x[ia:ib])) + 1e-12)
    # A take still sounding where it is cut gets at least 200 ms to die away.
    loud = db_at(x, ib) > peak_db - 30
    rel = max(release, 0.2) if loud else release
    n = int(rel * RATE)
    y = x[ia : ib + n].copy()
    if spec.get("lowcut"):
        sos = signal.butter(2, float(spec["lowcut"]), "highpass", fs=RATE, output="sos")
        y = signal.sosfiltfilt(sos, y)
    y[: int(0.001 * RATE)] *= np.linspace(0, 1, int(0.001 * RATE))
    tail = len(y) - (ib - ia)
    # The source ends before the release would: the take is kept to its end, and says so.
    ended = tail < n
    if tail > 0:
        # Exponential, as a real decay: down 60 dB over the release.
        y[ib - ia :] *= np.exp(np.linspace(0, np.log(1e-3), tail))
    if rate != 1:
        y = signal.resample(y, int(len(y) / rate))
    y *= 10 ** (-1 / 20) / (np.max(np.abs(y)) + 1e-12)
    return y, max(tail, 0) / RATE, bool(loud), ended


def main():
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    prov = []
    sources = {}
    for name, spec in plan.items():
        for n, c in enumerate(spec["cuts"], 1):
            # A cut is [from, to], or {"at": [from, to], "src": ..., "rate": ..., "meta": {...}} to override its sound's own.
            c = c if isinstance(c, dict) else {"at": c}
            one = {**spec, **c, "meta": {**spec.get("meta", {}), **c.get("meta", {})}}
            a, b = one["at"]
            x = sources.setdefault(one["src"], mono48(one["src"]))
            y, rel, loud, ended = cut_one(x, a, b, one)
            spec_meta = one["meta"]
            f = out / f"{name}-{n}.ogg"
            sf.write(f, y.astype(np.float32), RATE, format="OGG", subtype="VORBIS")
            edits = ["mono", "48 kHz"]
            if one.get("lowcut"):
                edits.append(f"high-passed at {one['lowcut']} Hz")
            edits.append("cut")
            if ended:
                edits.append("kept to the end of the source")
            else:
                edits.append(f"{rel * 1000:.0f} ms exponential release" + (" (still sounding at the cut)" if loud else ""))
            if one.get("rate", 1) != 1:
                edits.append(f"played at {one['rate']}x (resampled)")
            edits.append("peak -1 dBFS")
            prov.append({"file": f.name, "role": name, **spec_meta, "cut_s": [round(a, 3), round(b, 3)], "edits": ", ".join(edits), "via": "cut.py, explicit cuts (game-audio rules: no take stops while sounding)", "sha256": hashlib.sha256(f.read_bytes()).hexdigest()})
            print(f"{f.name:20s} {a:7.3f}-{b:7.3f} s  {len(y) / RATE:5.3f} s long  {'to the end of the source' if ended else f'release {rel * 1000:3.0f} ms'}{'  (loud at cut)' if loud else ''}")
    (out / "provenance.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False), encoding="utf-8")


main()
