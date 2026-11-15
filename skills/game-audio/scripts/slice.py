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
equal-power crossfade that turns a long take into a seamless loop: a bed such as a crowd murmur),
"release" (s of fade for a take cut while sounding; default a quarter of its length, 200-400 ms).

max_len is a ceiling, not a length: a take ends where it falls silent. One that runs past the
ceiling is cut at its quietest moment in the last third before it (a breath between cries) and
dies away like a real decay. A take still loud at the cut (within 20 dB of its peak) is kept only
when no whole take is left, and it gets at least 200 ms to die away; one too short for that fails
the run, so raise its max_len. A battle-mage's cast cut to 0.145 s, from -2 dB with a 36 ms fade,
"plays and finishes abruptly". Voices especially: a cry cut mid-breath sounds like a bug.

Writes <out dir>/<name>-<n>.ogg (mono, 48 kHz, peak -1 dBFS), measures.json (every take found,
with what it measured and whether it was kept) and provenance.json (each kept file's source and
offsets). A person still has to listen: the measures only shortlist.

    python -I slice.py --check <dir>

lists the files there of 0.2 s or more that stop while still sounding. A seamless loop ends loud on
purpose. A shorter file can't be judged from its ending: a bone crack ends as fast as a cut flame,
so the cut is judged here, while cutting, where the source shows whether the sound went on.

    python -I slice.py --audit <provenance.json> <source dir>...

goes back to the source of every cut take a provenance file names (a game's list, or this
script's own record) and lists the sounds whose takes were still within 30 dB of their peak where
they were cut, with less than 200 ms to die away. Run it whenever these rules change, over
everything already shipped: fixing the one take a playtester heard left nine other sounds cut the
same way.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

RATE = 48000
# A take cut while still sounding gets at least this long to die away. A playtester heard 36 ms
# (a cast) and 111 ms (an impact's hiss) as stopping; 200 ms (the recut cast) and 250-400 ms (cries)
# as ending.
MIN_CUT_RELEASE = 0.2
STILL_SOUNDING_DB = -20
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


def quiet_cut(x: np.ndarray, a: int, cap: int) -> int:
    """Where to end a take that runs past its ceiling: its quietest moment in the last third before it."""
    hop = int(0.01 * RATE)
    lo = a + (cap - a) * 2 // 3
    if cap - lo < 2 * hop:
        return cap
    return lo + int(env_db(x[lo:cap], hop).argmin()) * hop + hop // 2


def level_at(x: np.ndarray, a: int, b: int) -> float:
    """How loud the 10 ms before b are against the loudest 10 ms of x[a:b], in dB."""
    hop = int(0.01 * RATE)
    env = env_db(x[a:b], hop)
    return round(float(env_db(x[max(a, b - hop) : b], hop).max() - env.max()), 1) if len(env) else 0.0


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
            cap = a + int(spec.get("max_len", 1.0) * RATE)
            if b > cap:
                b, cut = quiet_cut(x, a, cap), True
            else:
                # A take that ends still loud was stopped by its file, not finished: an AI take often
                # stops mid-sound at the length it was asked for, and MP3 pads that with silence.
                b = a + int(np.flatnonzero(np.abs(x[a:b]) > 1e-4)[-1]) + 1
                cut = level_at(x, a, b) > -30
            if b - a < int(0.04 * RATE):
                continue
            found.append({"src": src, "start_s": round(a / RATE, 3), "end_s": round(b / RATE, 3), **measure(x[a:b]),
                          "cut_db": level_at(x, a, b) if cut else None, "_t": x[a:b].copy()})
    return found


def choose(found: list[dict], spec: dict) -> list[dict]:
    """The best takes by the spec's preference, spread across its sources so the variations differ."""
    loudest = max(f["rms_db"] for f in found)
    # A take far quieter than the rest is usually a tail or a breath, not a variation.
    usable = [f for f in found if f["rms_db"] >= loudest - 15] or found
    key = {"sharp": lambda f: (f["attack_ms"], -f["rms_db"]), "long": lambda f: -f["length_s"], "loud": lambda f: -f["rms_db"]}
    # Whole takes first: one cut while still sounding is kept only when nothing whole is left.
    ranked = sorted(usable, key=lambda f: (still_sounding(f), key[spec.get("prefer", "sharp")](f)))
    want, per_src = spec.get("keep", 5), max(1, len(spec["src"]))
    kept, by_src = [], {}
    for f in ranked:
        if len(kept) < want and by_src.get(f["src"], 0) <= len(kept) // per_src:
            kept.append(f)
            by_src[f["src"]] = by_src.get(f["src"], 0) + 1
    kept += [f for f in ranked if f not in kept][: want - len(kept)]
    return kept


def still_sounding(f: dict) -> bool:
    return f["cut_db"] is not None and f["cut_db"] > STILL_SOUNDING_DB


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
            # A take that fell silent on its own needs only a short fade; one cut while sounding gets a
            # release long enough to die away. Both decay exponentially, as a real sound does (-60 dB).
            secs = 0.03 if f["cut_db"] is None else spec.get("release", min(0.4, max(MIN_CUT_RELEASE, 0.25 * len(t) / RATE)))
            fade = min(len(t) // 2, int(secs * RATE))
            t[-fade:] *= 10 ** (-3 * np.linspace(0, 1, fade))
            f["release_ms"] = 1000 * fade // RATE
        t *= 10 ** (-1 / 20) / (np.abs(t).max() + 1e-12)
        fn = f"{name}-{i}.ogg"
        # Written in blocks: libsndfile's Vorbis encoder overflows the stack on Windows when handed
        # many seconds in one call (an 18 s loop crashed it; 3 s did not).
        with sf.SoundFile(out / fn, "w", RATE, 1, format="OGG", subtype="VORBIS") as w:
            for i in range(0, len(t), 16384):
                w.write(t[i : i + 16384].astype(np.float32))
        provenance[fn] = {"source": Path(f["src"]).name, "library": Path(f["src"]).parent.name, "start_s": f["start_s"],
                          "end_s": f["end_s"], "cut_db": f["cut_db"], "licence": spec.get("licence", ""),
                          "edits": "mono, 48 kHz, " + (f"high-passed at {spec['lowcut']} Hz, " if spec.get("lowcut") else "") + "cut, "
                          + (f"tuned {cents:+d} cents, " if cents else "") + ("crossfaded into a loop, " if spec.get("loop") else f"{1000 * fade // RATE} ms fade, ")
                          + "peak -1 dBFS"}
    return provenance


def check(d: Path) -> int:
    """Lists files of 0.2 s or more still within 24 dB of their peak 30-50 ms before they end: cut, not finished.
    Shorter files are clicks and hits, all attack, and are left to the ear."""
    bad = 0
    for f in sorted(d.glob("*.ogg")):
        x, rate = sf.read(f, always_2d=True)
        x = x.mean(axis=1)
        if len(x) < 0.2 * rate:
            continue
        seg = x[len(x) - int(0.05 * rate) : len(x) - int(0.03 * rate)]
        db = 20 * np.log10(np.sqrt(np.mean(seg**2)) / (np.abs(x).max() + 1e-12) + 1e-12)
        if db > -24:
            bad += 1
            print(f"{f.name}: {db:.0f} dB under its peak 40 ms before the end ({len(x) / rate:.2f} s): it stops while still sounding")
    print(f"{bad} files end abruptly" if bad else "no file ends abruptly")
    return 1 if bad else 0


def audit(prov_path: Path, roots: list[Path]) -> int:
    """Each cut take checked against its source: how loud the source was where the cut fell."""
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    entries = prov if isinstance(prov, list) else [{"file": k} | v for k, v in prov.items()]
    found: dict[str, Path] = {}
    bad: dict[str, list[tuple[float, int]]] = {}
    missing = set()
    for e in entries:
        name = e.get("take") or e.get("pack_file") or e.get("source")
        if "cut_s" not in e and "start_s" not in e or "loop" in e.get("edits", ""):
            continue
        if name not in found:
            hit = next((f for r in roots for f in r.rglob(name)), None)
            if hit is None:
                missing.add(name)
                continue
            found[name] = hit
        a, b = (int(v * RATE) for v in e.get("cut_s") or (e["start_s"], e["end_s"]))
        fade = int(m.group(1)) if (m := re.search(r"(\d+) ms fade", e.get("edits", ""))) else 0
        x = mono48(found[name])
        if hp := re.search(r"high-passed at (\d+) Hz", e.get("edits", "")):
            x = signal.sosfilt(signal.butter(2, int(hp.group(1)), "highpass", fs=RATE, output="sos"), x)
        at = level_at(x, a, min(b, len(x)))
        if at > -30 and fade < 1000 * MIN_CUT_RELEASE:
            bad.setdefault(e.get("role") or e["file"].rsplit("-", 1)[0], []).append((at, fade))
    for role, rs in sorted(bad.items(), key=lambda kv: -max(r[0] for r in kv[1])):
        print(f"{role}: {len(rs)} takes cut while sounding, up to {-max(r[0] for r in rs):.0f} dB under their peak, with {sorted({r[1] for r in rs})} ms fades")
    if missing:
        print(f"no source found for {len(missing)}: {', '.join(sorted(missing)[:5])}")
    print(f"{len(bad)} sounds stop while sounding" if bad else "no cut take stops while sounding")
    return 1 if bad else 0


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        return check(Path(sys.argv[2]))
    if len(sys.argv) >= 4 and sys.argv[1] == "--audit":
        return audit(Path(sys.argv[2]), [Path(a) for a in sys.argv[3:]])
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    measures, provenance, abrupt = {}, {}, []
    for name, spec in plan.items():
        found = collect(spec)
        if not found:
            print(f"{name}: no takes found")
            continue
        kept = choose(found, spec)
        provenance |= write(name, kept, spec, out)
        measures[name] = [{k: v for k, v in f.items() if k != "_t"} | {"kept": f in kept} for f in found]
        print(f"{name}: {len(found)} takes found, kept {len(kept)}: " + ", ".join(f"{f['length_s']}s/{f['attack_ms']}ms/{f['centroid_hz']}Hz" for f in kept))
        for f in kept:
            if not still_sounding(f) or spec.get("loop"):
                continue
            msg = f"{Path(f['src']).name} at {f['start_s']}s was cut {-f['cut_db']:.0f} dB under its peak, still sounding, with {f['release_ms']} ms to die away"
            if f["release_ms"] < 1000 * MIN_CUT_RELEASE:
                abrupt.append(f"{name}: {msg}")
            print(f"  {msg}")
    (out / "measures.json").write_text(json.dumps(measures, indent=1))
    (out / "provenance.json").write_text(json.dumps(provenance, indent=1))
    if abrupt:
        print(f"\nFAIL: {len(abrupt)} kept takes stop while sounding, too short to die away. Raise max_len to at least {2 * MIN_CUT_RELEASE} s:")
        print("\n".join(f"  {a}" for a in abrupt))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
