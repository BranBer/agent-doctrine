"""Measures where each sound file's sync point sits, so an engine can land it on an animation's beat.

    uv run --no-project --with numpy --with soundfile python -I transients.py <audio dir | files...>
        [--out sync.json] [--max-lead 15] [--strict]
    uv run --no-project --with numpy --with soundfile python -I transients.py --selftest

For every file it prints and writes, in milliseconds:
    lead    silence before anything is heard (the envelope first reaches -34 dB of its peak)
    onset   where the sound arrives (first reaches -12 dB of its peak)
    peak    where it is loudest
    kind    "hit" when the peak follows the onset within 30 ms: line its ONSET up with the event.
            "swell" otherwise (a whoosh, a charge): line its PEAK up with the motion's fastest point.
Takes of one sound (name-1.ogg, name-2.ogg) are grouped; the group's value is the median, and a
spread over 10 ms between takes is flagged, because the engine picks a take at random (sounds
longer than 1.5 s are left out of that check: a bed or a stinger is not lined up with a frame).

A hit whose onset is later than --max-lead ms lands late by that much when started on the event:
trim the file, or start it early by its onset where the event is known ahead. WARN lines mark those;
--strict turns any WARN into exit code 1. What was read and what was skipped is printed at the end.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

EXTS = {".ogg", ".wav", ".flac", ".mp3"}


def measure(x: np.ndarray, rate: int) -> dict:
    """x is mono samples. Times are ms from the start of the file."""
    win = max(1, rate // 500)  # 2 ms
    env = np.sqrt(np.convolve(x.astype(np.float64) ** 2, np.ones(win) / win, mode="same"))
    top = float(env.max())
    if top <= 0:
        return {"lead": 0.0, "onset": 0.0, "peak": 0.0, "length": 1000 * len(x) / rate, "kind": "silent"}
    first = lambda level: 1000 * int(np.argmax(env >= top * level)) / rate
    onset, peak = first(10 ** (-12 / 20)), 1000 * int(np.argmax(env)) / rate
    return {"lead": round(first(10 ** (-34 / 20)), 1), "onset": round(onset, 1), "peak": round(peak, 1),
            "length": round(1000 * len(x) / rate, 1), "kind": "hit" if peak - onset <= 30 else "swell"}


def family(path: Path) -> str:
    return re.sub(r"[-_]\d+$", "", path.stem)


def selftest() -> None:
    rate = 48000
    click = np.zeros(rate // 2)
    click[int(0.040 * rate):int(0.040 * rate) + 200] = np.hanning(400)[200:]  # a hit 40 ms in
    m = measure(click, rate)
    assert m["kind"] == "hit" and abs(m["onset"] - 40) < 3, m
    t = np.arange(rate // 2) / rate
    swell = np.sin(2 * np.pi * 300 * t) * np.exp(-((t - 0.25) / 0.08) ** 2)  # loudest at 250 ms
    m = measure(swell, rate)
    assert m["kind"] == "swell" and abs(m["peak"] - 250) < 15, m
    print("selftest ok")


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        selftest()
        return 0
    import soundfile as sf

    opt = lambda name, default: argv[argv.index(name) + 1] if name in argv else default
    max_lead, out = float(opt("--max-lead", 15)), opt("--out", None)
    skip = {opt("--out", ""), opt("--max-lead", "")}
    paths = [Path(a) for a in argv if not a.startswith("--") and a not in skip]
    files = sorted(f for p in paths for f in (p.iterdir() if p.is_dir() else [p]) if f.suffix.lower() in EXTS)
    if not files:
        raise SystemExit(__doc__)
    groups: dict[str, list[dict]] = {}
    unread = []
    for f in files:
        try:
            x, rate = sf.read(str(f), always_2d=True)
        except Exception as e:  # an unreadable file is a gap to name, not a pass
            unread.append("%s (%s)" % (f.name, e))
            continue
        groups.setdefault(family(f), []).append({"file": f.name, **measure(x.mean(axis=1), rate)})
    warns, result = 0, {}
    print("%-22s %5s %-6s %7s %7s %7s  %s" % ("sound", "takes", "kind", "lead", "onset", "peak", ""))
    for name, takes in sorted(groups.items()):
        kinds = [t["kind"] for t in takes]
        kind = max(set(kinds), key=kinds.count)
        med = lambda k, takes=takes: float(np.median([t[k] for t in takes]))
        point = "onset" if kind == "hit" else "peak"
        spread = max(t[point] for t in takes) - min(t[point] for t in takes)
        notes = []
        if kind == "hit" and med("onset") > max_lead:
            notes.append("WARN hit lands %.0f ms late: trim it or start it early" % med("onset"))
        # A long bed or stinger is not lined up with a frame, so its takes may differ freely.
        if spread > 10 and med("length") <= 1500:
            notes.append("WARN takes differ by %.0f ms at the %s" % (spread, point))
        if len(set(kinds)) > 1:
            notes.append("WARN takes disagree on kind: %s" % ", ".join(sorted(set(kinds))))
        warns += len(notes)
        result[name] = {"kind": kind, "lead": med("lead"), "onset": med("onset"), "peak": med("peak"),
                        "sync": med(point), "spread": round(spread, 1), "takes": takes}
        print("%-22s %5d %-6s %7.1f %7.1f %7.1f  %s" % (name, len(takes), kind, med("lead"), med("onset"), med("peak"), "; ".join(notes)))
    if out:
        Path(out).write_text(json.dumps(result, indent=1))
        print("wrote", out)
    print("read %d files in %d sounds; %d warnings; %d unreadable%s" % (
        len(files) - len(unread), len(groups), warns, len(unread), ": " + "; ".join(unread) if unread else ""))
    return 1 if unread or ("--strict" in argv and warns) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
