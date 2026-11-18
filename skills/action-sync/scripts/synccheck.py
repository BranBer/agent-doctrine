"""Measures, from a probe's recording, how far each sound's arrival is from the moment the game asked for it.

    uv run --no-project --with numpy --with soundfile python -I synccheck.py <capture dir> [--bus player]
        [--sync sync.json] [--late 40] [--strict]

The capture dir holds <bus>.wav (a bus stem recorded from the first frame of the capture) and trace.json
with "sampleRate" and "starts": [{"name", "bus", "call", "at"}, ...] - one entry per sound the engine
started on that bus, in seconds from the start of the recording: "call" is when the game asked, "at" is
when the engine scheduled the source to begin.

For each start with no other start on the bus from 150 ms before to 250 ms after, it finds where the
stem rises (first reaches -12 dB of that window's peak) and reports, per sound, in milliseconds:
    wait     at - call: how long the engine held the sound (0 unless scheduled ahead)
    arrive   rise - call: what a player gets, before the device's own output delay
    file     the sound's own onset from transients.py's sync.json, when given: arrive should be wait + file
A sound whose median arrival is over --late ms is a WARN (FAIL with --strict): late by more than a hit
tolerates. A negative arrival means the stem rose before the call: another sound was playing, so read
that row as contaminated. This measures the engine's output, not what reaches the ear: device and
Bluetooth delay come after it. It prints what it measured and what it could not.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def rise(x: np.ndarray, rate: int) -> float | None:
    """Seconds into x where it first reaches -12 dB of its peak; None when x is silent."""
    win = max(1, rate // 500)
    env = np.sqrt(np.convolve(x.astype(np.float64) ** 2, np.ones(win) / win, mode="same"))
    top = float(env.max())
    return None if top < 1e-4 else int(np.argmax(env >= top * 10 ** (-12 / 20))) / rate


def isolated(starts: list[dict], before=0.15, after=0.25) -> list[dict]:
    return [s for s in starts if not any(o is not s and -before <= o["at"] - s["at"] <= after for o in starts)]


def main(argv: list[str]) -> int:
    import soundfile as sf

    opt = lambda name, default: argv[argv.index(name) + 1] if name in argv else default
    if not argv or argv[0].startswith("--"):
        raise SystemExit(__doc__)
    cap, bus, late = Path(argv[0]), opt("--bus", "player"), float(opt("--late", 40))
    trace = json.loads((cap / "trace.json").read_text())
    if "starts" not in trace:
        print("NOT RUN: trace.json has no \"starts\"; the probe did not log when sounds were asked for")
        return 1
    stem_path = cap / (bus + ".wav")
    if not stem_path.exists():
        print("NOT RUN: %s is missing" % stem_path)
        return 1
    x, rate = sf.read(str(stem_path), always_2d=True)
    x = x.mean(axis=1)
    files = json.loads(Path(opt("--sync", "")).read_text()) if "--sync" in argv else {}
    starts = [s for s in trace["starts"] if s["bus"] == bus]
    alone = isolated(starts)
    by: dict[str, list[tuple[float, float]]] = {}
    silent = 0
    for s in alone:
        a, b = int((s["call"] - 0.03) * rate), int((s["at"] + 0.3) * rate)
        if a < 0 or b > len(x):
            continue
        r = rise(x[a:b], rate)
        if r is None:
            silent += 1
            continue
        by.setdefault(s["name"], []).append((1000 * (s["at"] - s["call"]), 1000 * (r - 0.03)))
    print("%-20s %4s %7s %8s %8s %8s %6s" % ("sound", "n", "wait", "arrive", "p10", "p90", "file"))
    warns = 0
    for name, rows in sorted(by.items()):
        wait, arrive = np.array(rows).T
        med = float(np.median(arrive))
        flag = ""
        if med > late:
            flag, warns = "  WARN arrives %.0f ms after the call" % med, warns + 1
        f = files.get(name, {}).get("onset")
        print("%-20s %4d %7.1f %8.1f %8.1f %8.1f %6s%s" % (name, len(rows), float(np.median(wait)), med,
              float(np.percentile(arrive, 10)), float(np.percentile(arrive, 90)), "-" if f is None else "%.1f" % f, flag))
    print("%d starts on the %s bus; %d stood alone and were measured across %d sounds; %d were silent in the stem; %d warnings"
          % (len(starts), bus, len(alone), len(by), silent, warns))
    if not by:
        print("NOT RUN: no start stood alone; capture a quieter stretch")
        return 1
    return 1 if "--strict" in argv and warns else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
