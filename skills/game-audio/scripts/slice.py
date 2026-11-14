"""Cuts library files that hold many takes into one-shots, measures each take, and keeps the best.

    uv run --no-project --with numpy --with scipy --with soundfile python -I slice.py <plan.json> <out dir>

plan.json maps a sound name to where its takes come from:
    {"blade-hit": {"src": ["<wav>", ...], "keep": 5, "max_len": 0.8, "prefer": "sharp",
                   "licence": "Sonniss GDC 2026 bundle licence v2.0"}, ...}
prefer is "sharp" (the quickest attacks: impacts), "long" (whooshes, voices) or "loud".
Optional per sound: "gap" (silence in s that separates takes, default 0.12), "floor_db" (how far
under the file's peak counts as silence, default -40), "skip_start" (s to drop at the start of
each take), "from_peak" (s of lead-in kept before each take's loudest moment: a hit must land
on the hit, not after a swing), "lowcut" (Hz high-pass), "tune_to" (pitch classes such as
["D"] or ["F", "A"]: each kept take is resampled by the smallest shift that puts its strongest
partial on one of them, for tonal sounds the game will never pitch-randomise), "loop" (s of
equal-power crossfade that turns a long take into a seamless loop: a bed such as a crowd murmur).

Writes <out dir>/<name>-<n>.ogg (mono, 48 kHz, peak -1 dBFS, a 30 ms fade at the end),
measures.json (every take found, with what it measured and whether it was kept) and
provenance.json (each kept file's source and offsets). A person still has to listen: the
measures only shortlist.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

RATE = 48000
NOTES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def mono48(path: Path) -> np.ndarray:
    try:
        x, rate = sf.read(path, always_2d=True, dtype="float64")
    except sf.LibsndfileError:
        # Some library WAVs carry a chunk libsndfile rejects (a bad PEAK chunk); SciPy skips it.
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


def env_db(x: np.ndarray, hop: int) -> np.ndarray:
    n = len(x) // hop
    return 10 * np.log10(np.maximum((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1), 1e-14))


def takes(x: np.ndarray, gap: float, floor_db: float) -> list[tuple[int, int]]:
    """Regions louder than the file's peak + floor_db, split where it stays quiet for `gap` seconds."""
    hop = int(0.005 * RATE)
    env = env_db(x, hop)
    loud = env > env.max() + floor_db
    out, start, quiet = [], None, 0
    for i, on in enumerate(loud):
        if on:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * hop >= gap * RATE:
                out.append((max(0, start * hop - int(0.003 * RATE)), (i - quiet + 1) * hop))
                start, quiet = None, 0
    if start is not None:
        out.append((max(0, start * hop - int(0.003 * RATE)), len(x)))
    return out


def measure(t: np.ndarray) -> dict:
    hop = int(0.001 * RATE)
    env = env_db(t, hop)
    peak_i = int(env.argmax())
    attack = next((i for i, v in enumerate(env) if v >= env[peak_i] - 3), peak_i)
    f, p = signal.welch(t, RATE, nperseg=min(4096, len(t)))
    total = p.sum() + 1e-20
    return {
        "length_s": round(len(t) / RATE, 3),
        "attack_ms": attack,
        "peak_db": round(20 * np.log10(np.abs(t).max() + 1e-12), 1),
        "rms_db": round(10 * np.log10(np.mean(t**2) + 1e-14), 1),
        "centroid_hz": round(float((f * p).sum() / total)),
        "low_share": round(float(p[f < 150].sum() / total), 3),
    }


def collect(spec: dict) -> list[dict]:
    """Every take in the spec's source files, cut and measured."""
    found = []
    for src in spec["src"]:
        x = mono48(Path(src))
        if spec.get("lowcut"):
            x = signal.sosfilt(signal.butter(2, spec["lowcut"], "highpass", fs=RATE, output="sos"), x)
        for a, b in takes(x, spec.get("gap", 0.12), spec.get("floor_db", -40)):
            a += int(spec.get("skip_start", 0) * RATE)
            if "from_peak" in spec:
                # Start just before the loudest moment: a hit sound must land on the hit, not after a swing.
                pk = a + int(np.abs(x[a:b]).argmax())
                a = max(a, pk - int(spec["from_peak"] * RATE))
            b = min(b, a + int(spec.get("max_len", 1.0) * RATE))
            if b - a < int(0.04 * RATE):
                continue
            found.append({"src": src, "start_s": round(a / RATE, 3), "end_s": round(b / RATE, 3), **measure(x[a:b]), "_t": x[a:b].copy()})
    return found


def choose(found: list[dict], spec: dict) -> list[dict]:
    """The best takes by the spec's preference, spread across its sources so the variations differ."""
    loudest = max(f["rms_db"] for f in found)
    # A take far quieter than the rest is usually a tail or a breath, not a variation.
    usable = [f for f in found if f["rms_db"] >= loudest - 15] or found
    key = {"sharp": lambda f: (f["attack_ms"], -f["rms_db"]), "long": lambda f: -f["length_s"], "loud": lambda f: -f["rms_db"]}
    ranked = sorted(usable, key=key[spec.get("prefer", "sharp")])
    want, per_src = spec.get("keep", 5), max(1, len(spec["src"]))
    kept, by_src = [], {}
    for f in ranked:
        if len(kept) < want and by_src.get(f["src"], 0) <= len(kept) // per_src:
            kept.append(f)
            by_src[f["src"]] = by_src.get(f["src"], 0) + 1
    kept += [f for f in ranked if f not in kept][: want - len(kept)]
    return kept


def strongest_hz(t: np.ndarray) -> float:
    """The strongest partial between 80 Hz and 2 kHz in the first half second: the note a listener hangs a bell on."""
    seg = t[: int(0.5 * RATE)] * np.hanning(min(len(t), int(0.5 * RATE)))
    spec = np.abs(np.fft.rfft(seg, n=1 << 16))
    f = np.fft.rfftfreq(1 << 16, 1 / RATE)
    band = (f >= 80) & (f <= 2000)
    return float(f[band][spec[band].argmax()])


def tune(t: np.ndarray, classes: list[str]) -> tuple[np.ndarray, float]:
    """Resamples by the smallest shift (at most 6 semitones) that lands the strongest partial on a wanted pitch class."""
    hz = strongest_hz(t)
    midi = 69 + 12 * np.log2(hz / 440)
    targets = [NOTES[c] for c in classes]
    shift = min((((tc - midi) % 12 + 6) % 12 - 6 for tc in targets), key=abs)
    ratio = 2 ** (shift / 12)
    # Playing back faster raises the pitch: keep `len / ratio` samples.
    out = signal.resample(t, max(1, int(round(len(t) / ratio))))
    return out, round(100 * shift)


def seamless(t: np.ndarray, xfade: float) -> np.ndarray:
    """Folds the take's last `xfade` seconds over its start with an equal-power crossfade, so it loops without a seam."""
    n = int(xfade * RATE)
    k = np.linspace(0, np.pi / 2, n)
    y = t[: len(t) - n].copy()
    y[:n] = t[:n] * np.sin(k) + t[len(t) - n :] * np.cos(k)
    return y


def write(name: str, kept: list[dict], spec: dict, out: Path) -> dict:
    """Writes the kept takes as OGG and returns their provenance entries."""
    provenance = {}
    for i, f in enumerate(kept, 1):
        t, cents = f["_t"], 0
        if spec.get("tune_to"):
            t, cents = tune(t, spec["tune_to"])
        if spec.get("loop"):
            t = seamless(t, spec["loop"])
        else:
            fade = min(len(t) // 4, int(0.03 * RATE))
            t[-fade:] *= np.linspace(1, 0, fade)
        t *= 10 ** (-1 / 20) / (np.abs(t).max() + 1e-12)
        fn = f"{name}-{i}.ogg"
        # Written in blocks: libsndfile's Vorbis encoder overflows the stack on Windows when handed
        # many seconds in one call (an 18 s loop crashed it; 3 s did not).
        with sf.SoundFile(out / fn, "w", RATE, 1, format="OGG", subtype="VORBIS") as w:
            for i in range(0, len(t), 16384):
                w.write(t[i : i + 16384].astype(np.float32))
        provenance[fn] = {"source": Path(f["src"]).name, "library": Path(f["src"]).parent.name, "start_s": f["start_s"],
                          "end_s": f["end_s"], "licence": spec.get("licence", ""),
                          "edits": "mono, 48 kHz, cut, " + (f"tuned {cents:+d} cents, " if cents else "") + ("crossfaded into a loop, " if spec.get("loop") else "30 ms fade, ") + "peak -1 dBFS"}
    return provenance


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    measures, provenance = {}, {}
    for name, spec in plan.items():
        found = collect(spec)
        if not found:
            print(f"{name}: no takes found")
            continue
        kept = choose(found, spec)
        provenance |= write(name, kept, spec, out)
        measures[name] = [{k: v for k, v in f.items() if k != "_t"} | {"kept": f in kept} for f in found]
        print(f"{name}: {len(found)} takes found, kept {len(kept)}: " + ", ".join(f"{f['length_s']}s/{f['attack_ms']}ms/{f['centroid_hz']}Hz" for f in kept))
    (out / "measures.json").write_text(json.dumps(measures, indent=1))
    (out / "provenance.json").write_text(json.dumps(provenance, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
