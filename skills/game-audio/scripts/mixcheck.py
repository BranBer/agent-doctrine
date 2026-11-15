"""Measures a game's mix from a probe's recording: the checks in references/mixing.md.

    uv run --no-project --with numpy --with scipy --with soundfile --with pyloudnorm --with matplotlib \\
        python -I mixcheck.py <capture dir> [--cap 32] [--reference <capture dir>]

The capture dir holds master.wav (required) and, recorded in the same run, any of music.wav,
player.wav and crowd.wav (bus stems) and trace.json:
    {"sampleRate": 48000, "trace": [{"t", "tick", "phase", "voices", "steals", "highSteals",
                                     "culled", "reduction", "tier"}, ...],
     "plays": {"<sound>": {"plays", "variants", "fixed", "seconds", "own"}, ...}}
"plays" counts each sampled sound played while recording, with how many takes it has; "fixed" marks
a cue meant to sound the same every time (a tuned bell), which the repetition check leaves out;
"seconds" adds up how long each play lasted (a take's length over its playback rate), which the
exposure check reads; "own" marks a sound played on the player's own bus.
"phase" is "wave" while enemies come and anything else in a lull. It prints one line per check -
PASS, WARN, FAIL, INFO or NOT RUN with the reason - writes report.json and saves spectrogram.png
and loudness.png for a person or an agent to look at. Exit code 1 when a check failed.

The thresholds are starting values from published practice (see the reference), not truths: the
density, contrast and mud checks only mean much once calibrated against a capture of a game the
user rates well (--reference).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

try:
    import pyloudnorm as pyln
    from pyloudnorm.iirfilter import IIRfilter
except ImportError:  # pragma: no cover - the run command installs it
    sys.exit("needs pyloudnorm: see the run command at the top of this file")

results: list[dict] = []


def report(num: str, name: str, status: str, detail: str, **values) -> None:
    results.append({"check": num, "name": name, "status": status, "detail": detail, **values})
    print(f"{status:<8}{num:>3}  {name:<28}{detail}")


def load(path: Path) -> tuple[np.ndarray, int] | None:
    if not path.exists():
        return None
    x, rate = sf.read(path, always_2d=True, dtype="float64")
    return x, rate


def kweight(x: np.ndarray, rate: int) -> np.ndarray:
    """BS.1770 K-weighting: the high shelf, then the high-pass."""
    y = x
    for f in (IIRfilter(4.0, 1 / np.sqrt(2), 1500.0, rate, "high_shelf"), IIRfilter(0.0, 0.5, 38.0, rate, "high_pass")):
        y = signal.lfilter(f.b, f.a, y, axis=0)
    return y


def loudness_series(x: np.ndarray, rate: int, win: float = 3.0, hop: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """Short-term loudness (LUFS) every `hop` seconds, each over the `win` seconds before it."""
    p = (kweight(x, rate) ** 2).sum(axis=1)
    c = np.concatenate([[0.0], np.cumsum(p)])
    w, h = int(win * rate), int(hop * rate)
    if len(p) < w:
        return np.array([]), np.array([])
    starts = np.arange(0, len(p) - w + 1, h)
    ms = (c[starts + w] - c[starts]) / w
    return (starts + w) / rate, -0.691 + 10 * np.log10(np.maximum(ms, 1e-12))


def lra(st: np.ndarray) -> float:
    """Loudness range (EBU Tech 3342) from short-term values."""
    g = st[st > -70]
    if len(g) < 10:
        return float("nan")
    rel = 10 * np.log10(np.mean(10 ** (g / 10))) - 20
    g = g[g > rel]
    return float(np.percentile(g, 95) - np.percentile(g, 10))


def rms_db(x: np.ndarray) -> float:
    return float(10 * np.log10(max(np.mean(x**2), 1e-14)))


def onsets_flux(mono: np.ndarray, rate: int) -> np.ndarray:
    """Onset times (s) by positive spectral flux over an adaptive threshold: what the ear hears as separate hits."""
    hop = 256
    _, _, z = signal.stft(mono, rate, nperseg=1024, noverlap=1024 - hop)
    mag = np.log1p(100 * np.abs(z))
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    fps = rate / hop
    k = max(3, int(0.5 * fps) | 1)
    thresh = signal.medfilt(flux, k) * 1.5 + np.percentile(flux, 50) * 0.5 + 1e-9
    gap = int(0.03 * fps)
    out, last = [], -gap
    for i in range(1, len(flux) - 1):
        if flux[i] > thresh[i] and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1] and i - last >= gap:
            out.append(i / fps)
            last = i
    return np.array(out)


def onsets_energy(mono: np.ndarray, rate: int) -> np.ndarray:
    """Onsets in a sparse stem: the 10 ms level jumping 6 dB above the quietest of the 50 ms before it."""
    n = int(0.01 * rate)
    frames = len(mono) // n
    env = 10 * np.log10(np.maximum((mono[: frames * n].reshape(frames, n) ** 2).mean(axis=1), 1e-14))
    out, last = [], -10
    for i in range(5, frames):
        if env[i] > -50 and env[i] - env[i - 5 : i].min() > 6 and i - last >= 5:
            out.append(i * n / rate)
            last = i
    return np.array(out)


def band(x: np.ndarray, rate: int, lo: float, hi: float) -> np.ndarray:
    sos = signal.butter(4, [lo, hi], btype="bandpass", fs=rate, output="sos")
    return signal.sosfilt(sos, x)


def phase_mask(times: np.ndarray, trace: list[dict], want_wave: bool) -> np.ndarray:
    if not trace:
        return np.ones(len(times), bool) if want_wave else np.zeros(len(times), bool)
    tt = np.array([r["t"] for r in trace])
    wave = np.array([r["phase"] == "wave" for r in trace])
    idx = np.clip(np.searchsorted(tt, times) - 1, 0, len(tt) - 1)
    return wave[idx] == want_wave


def third_octave(mono: np.ndarray, rate: int) -> tuple[np.ndarray, np.ndarray]:
    f, pxx = signal.welch(mono, rate, nperseg=8192)
    centres = 1000 * 2 ** (np.arange(-17, 14) / 3)
    centres = centres[centres < rate / 2.2]
    levels = []
    for c in centres:
        sel = (f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))
        levels.append(10 * np.log10(max(pxx[sel].sum(), 1e-20)))
    return centres, np.array(levels)


def mud_index(mono: np.ndarray, rate: int) -> float:
    c, lv = third_octave(mono, rate)
    return float(lv[(c >= 200) & (c <= 500)].mean() - lv[(c >= 100) & (c <= 8000)].mean())


@dataclass
class Capture:
    """One probe recording: the master, the bus stems (mono, or None if not recorded) and the trace."""

    dir: Path
    rate: int
    master: np.ndarray
    music: np.ndarray | None
    player: np.ndarray | None
    crowd: np.ndarray | None
    trace: list[dict]
    plays: dict[str, dict]

    @property
    def mono(self) -> np.ndarray:
        return self.master.mean(axis=1)

    @property
    def seconds(self) -> float:
        return len(self.master) / self.rate


def load_capture(cap_dir: Path) -> Capture | None:
    m = load(cap_dir / "master.wav")
    if m is None:
        return None
    stems = {n: load(cap_dir / f"{n}.wav") for n in ("music", "player", "crowd")}
    trace_path = cap_dir / "trace.json"
    doc = json.loads(trace_path.read_text()) if trace_path.exists() else {}
    mono = {n: (s[0].mean(axis=1) if s else None) for n, s in stems.items()}
    return Capture(cap_dir, m[1], m[0], mono["music"], mono["player"], mono["crowd"], doc.get("trace", []), doc.get("plays", {}))


def check_realtime(c: Capture) -> None:
    """The sim must keep real time against the audio clock, or every density number is too low."""
    if len(c.trace) < 2:
        report("0", "real time", "NOT RUN", "no trace.json")
        return
    t = c.trace
    tps = (t[-1]["tick"] - t[0]["tick"]) / max(1e-9, t[-1]["t"] - t[0]["t"])
    report("0", "real time", "PASS" if tps >= 54 else "WARN", f"sim at {tps:.0f} ticks/s (60 is real time)", ticks_per_s=tps)


def check_loudness(c: Capture) -> None:
    integ = pyln.Meter(c.rate).integrated_loudness(c.master)
    tp = 20 * np.log10(max(np.abs(signal.resample_poly(c.master, 4, 1, axis=0)).max(), 1e-12))
    _, st = loudness_series(c.master, c.rate)
    rng = lra(st) if len(st) else float("nan")
    ok = -18 <= integ <= -14 and tp <= -1 and 6 <= rng <= 15
    report("3", "loudness", "PASS" if ok else "FAIL",
           f"{integ:.1f} LUFS (want -16 +/-2), true peak {tp:.1f} dBTP (<= -1), LRA {rng:.1f} LU (6-15)",
           integrated=integ, true_peak=tp, lra=rng)
    plr = tp - integ
    report("4", "peak to loudness", "PASS" if plr >= 10 else "FAIL", f"PLR {plr:.1f} dB (want >= 10; less means crushed)", plr=plr)


def check_limiter(c: Capture) -> None:
    if not c.trace:
        report("5", "limiter as safety", "NOT RUN", "no trace.json")
        return
    red = np.array([r.get("reduction", 0) for r in c.trace])
    over1, over3, top = (red > 1).mean(), (red > 3).mean(), red.max()
    ok = over1 <= 0.05 and over3 <= 0.01 and top <= 6
    report("5", "limiter as safety", "PASS" if ok else "FAIL",
           f"> 1 dB in {over1:.0%} of frames (<= 5%), > 3 dB in {over3:.0%} (<= 1%), max {top:.1f} dB (<= 6)",
           over1=over1, over3=over3, max=top)


def check_player(c: Capture) -> None:
    others = [s for s in (c.crowd, c.music) if s is not None]
    if c.player is None or not others:
        report("6", "player stands out", "NOT RUN", "needs player.wav and crowd.wav or music.wav")
        return
    n = min(len(c.player), *(len(s) for s in others))
    rest = sum(s[:n] for s in others)
    win = int(0.15 * c.rate)
    starts = (onsets_energy(c.player[:n], c.rate) * c.rate).astype(int)
    diffs = [rms_db(c.player[i : i + win]) - rms_db(rest[i : i + win]) for i in starts if i + win <= n]
    if not diffs:
        report("6", "player stands out", "NOT RUN", "no own-hit onsets found in player.wav")
        return
    med, share = float(np.median(diffs)), float(np.mean(np.array(diffs) >= 0))
    report("6", "player stands out", "PASS" if med >= 3 and share >= 0.95 else "FAIL",
           f"own hits {med:+.1f} dB over the rest (median, want >= +3), >= 0 dB on {share:.0%} (want 95%), {len(diffs)} onsets",
           median=med, share=share, hits=len(diffs))


def check_music(c: Capture) -> None:
    sfx_parts = [s for s in (c.player, c.crowd) if s is not None]
    if c.music is None or not sfx_parts:
        report("7", "music under SFX", "NOT RUN", "needs music.wav and player.wav or crowd.wav")
        return
    n = min(len(c.music), *(len(s) for s in sfx_parts))
    music, sfx = c.music[:n], sum(s[:n] for s in sfx_parts)
    t_m, l_m = loudness_series(music[:, None], c.rate)
    _, l_s = loudness_series(sfx[:, None], c.rate)
    fight = phase_mask(t_m, c.trace, True) & (l_s > -60)
    if fight.sum() <= 20:
        report("7", "music under SFX", "NOT RUN", "too little combat in the capture")
    else:
        gap = l_s[fight] - l_m[fight]
        share = float(np.mean((gap >= 6) & (gap <= 10)))
        report("7", "music under SFX", "PASS" if share >= 0.9 else "FAIL",
               f"music {np.median(gap):.1f} LU under SFX in combat (median; want 8 +/-2 for 90% of it: {share:.0%})",
               median_gap=float(np.median(gap)), share=share)
        mb, sb = band(music, c.rate, 1000, 4000), band(sfx, c.rate, 1000, 4000)
        win = int(0.15 * c.rate)
        bd = [rms_db(sb[i : i + win]) - rms_db(mb[i : i + win]) for i in (onsets_energy(sfx, c.rate) * c.rate).astype(int) if i + win <= n]
        if bd:
            report("7b", "music clear of hits", "PASS" if np.median(bd) >= 6 else "FAIL",
                   f"1-4 kHz: music {np.median(bd):.1f} dB under SFX at SFX onsets (median, want >= 6)", median=float(np.median(bd)))
    check_tiers(c, t_m, l_m)


def check_tiers(c: Capture, t_m: np.ndarray, l_m: np.ndarray) -> None:
    """Layers should add density, not level: compare the music where each tier held for a whole window."""
    if not c.trace or "tier" not in c.trace[0]:
        report("7c", "layers add density", "NOT RUN", "no tier in trace.json")
        return
    tt = np.array([r["t"] for r in c.trace])
    tiers = np.array([r["tier"] for r in c.trace])
    idx = np.clip(np.searchsorted(tt, t_m) - 1, 0, len(tt) - 1)
    held = np.array([len(set(tiers[max(0, j - 30) : j + 1])) == 1 for j in idx])
    per = {int(k): float(np.median(l_m[held & (tiers[idx] == k)])) for k in np.unique(tiers[idx]) if (held & (tiers[idx] == k)).sum() >= 5}
    if len(per) < 2:
        report("7c", "layers add density", "NOT RUN", f"only {len(per)} tier(s) held for 3 s")
        return
    base = per[min(per)]
    rise = max(v - base for v in per.values())
    report("7c", "layers add density", "PASS" if rise <= 3 else "FAIL",
           "music by tier, LU over the lowest heard: " + ", ".join(f"{k}: {v - base:+.1f}" for k, v in sorted(per.items())) + " (top <= +3)",
           tiers=per)


def check_voices(c: Capture, voice_cap: int) -> None:
    if not c.trace:
        report("8", "voices", "NOT RUN", "no trace.json")
        return
    first, last = c.trace[0], c.trace[-1]
    p95 = float(np.percentile([r.get("voices", 0) for r in c.trace], 95))
    high, culled, steals = (last.get(k, 0) - first.get(k, 0) for k in ("highSteals", "culled", "steals"))
    report("8", "voices", "PASS" if p95 <= 0.8 * voice_cap and high == 0 else "FAIL",
           f"p95 {p95:.0f} of {voice_cap} (<= 80%), own-sound steals {high} (0); {steals} stolen, {culled} culled",
           p95=p95, high_steals=high, steals=steals, culled=culled)


def check_density(c: Capture) -> None:
    on = onsets_flux(c.mono, c.rate)
    secs = np.arange(int(c.seconds))
    per_s = np.array([((on >= s) & (on < s + 1)).sum() for s in secs])
    fight = phase_mask(secs + 0.5, c.trace, True)
    dens = float(np.percentile(per_s[fight] if fight.any() else per_s, 95))
    report("9", "onset density", "PASS" if dens <= 12 else "FAIL", f"p95 {dens:.0f} onsets a second in combat (<= 12; uncalibrated)", p95=dens)


def check_repetition(c: Capture) -> None:
    """How soon the same take comes back: takes x seconds / plays, per sound, cues left out. Each layer
    of a layered sound counts on its own, so this is the strict reading."""
    every = {k: v["variants"] * c.seconds / v["plays"] for k, v in c.plays.items() if v["plays"] > 0 and not v.get("fixed")}
    if not every:
        report("13", "repetition", "NOT RUN", "no plays in trace.json")
        return
    worst = sorted(every.items(), key=lambda kv: kv[1])[:5]
    low = worst[0][1]
    detail = "; ".join(f"{k} {c.plays[k]['plays']} plays of {c.plays[k]['variants']} takes, one every {s:.1f} s" for k, s in worst)
    report("13", "repetition", "FAIL" if low < 2 else "WARN" if low < 4 else "PASS",
           f"the same take back no sooner than every 4 s on average (2 fails; ours). Worst: {detail}", worst=dict(worst))


def check_exposure(c: Capture) -> None:
    """Seconds of each sound per second of play. Over 1, a sound overlaps itself on average and stops
    being a series of events: a battle-mage's 0.6-0.8 s cast and 1.4 s burst, each every 0.6 s, came to
    about 1.2 and 2.3, and the attack was "ear torture". Its v4 cast and burst, at 0.24 and 0.75, were not.
    Only the player's own sounds can fail: a crowd's cries ran at 1.2-1.3, quieter with distance and
    rationed, and no verdict says that hurt. The rest are listed."""
    share = {k: v["seconds"] / c.seconds for k, v in c.plays.items() if v.get("seconds")}
    if not share:
        report("14", "exposure", "NOT RUN", "no seconds in trace.json's plays")
        return
    own = sorted(((k, s) for k, s in share.items() if c.plays[k].get("own")), key=lambda kv: -kv[1])[:5]
    rest = sorted(((k, s) for k, s in share.items() if not c.plays[k].get("own")), key=lambda kv: -kv[1])[:3]
    detail = "; ".join(f"{k} {s:.2f}" for k, s in own) or "none of the player's own"
    report("14", "exposure", "FAIL" if own and own[0][1] > 1 else "PASS",
           f"none of the player's own sounds plays more than 1 s of itself a second (ours). Own: {detail}. "
           f"Others: {'; '.join(f'{k} {s:.2f}' for k, s in rest)}", own=dict(own), rest=dict(rest))


def check_contrast(c: Capture) -> None:
    st_t, st = loudness_series(c.master, c.rate)
    wave, lull = phase_mask(st_t, c.trace, True), phase_mask(st_t, c.trace, False)
    if not len(st) or wave.sum() < 30 or lull.sum() < 30:
        report("10", "contrast", "NOT RUN", "needs 3 s each of combat and lull in the capture")
        return
    con = float(np.percentile(st[wave], 90) - np.median(st[lull]))
    report("10", "contrast", "PASS" if 4 <= con <= 12 else "FAIL", f"combat p90 is {con:.1f} LU over the lull median (4-12)", contrast=con)


def check_mud(c: Capture, ref_dir: Path | None) -> None:
    mud = mud_index(c.mono, c.rate)
    ref = load(ref_dir / "master.wav") if ref_dir else None
    if ref is None:
        report("11", "mud", "INFO", f"200-500 Hz sits {mud:+.1f} dB against 100 Hz-8 kHz; no reference to judge it by", index=mud)
        return
    delta = mud - mud_index(ref[0].mean(axis=1), ref[1])
    report("11", "mud", "PASS" if delta <= 4 else "FAIL", f"200-500 Hz {delta:+.1f} dB against the reference (<= +4)", delta=delta)


def pictures(c: Capture) -> None:
    """The spectrogram and the loudness of every bus on one chart, for a person or an agent to look at."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.specgram(c.mono, NFFT=2048, Fs=c.rate, noverlap=1536, cmap="magma", vmin=-120)
        ax.set_yscale("symlog", linthresh=500)
        ax.set_ylim(40, c.rate / 2)
        ax.set(xlabel="seconds", ylabel="Hz", title="master: gaps between hits should show; a flat full-band smear is mud")
        fig.tight_layout()
        fig.savefig(c.dir / "spectrogram.png", dpi=90)
        fig, ax = plt.subplots(figsize=(14, 4))
        st_t, st = loudness_series(c.master, c.rate)
        ax.plot(st_t, st, label="master short-term", color="k")
        for name, s in (("music", c.music), ("player", c.player), ("crowd", c.crowd)):
            if s is not None:
                ax.plot(*loudness_series(s[:, None], c.rate), label=name, alpha=0.7)
        for prev, row in zip(c.trace, c.trace[1:], strict=False):
            if row["phase"] != "wave":
                ax.axvspan(prev["t"], row["t"], color="0.9", lw=0)
        ax.axhline(-16, ls=":", color="g")
        ax.set_ylim(-60, 0)
        ax.set(xlabel="seconds (grey: lull)", ylabel="LUFS")
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(c.dir / "loudness.png", dpi=90)
        report("12", "pictures", "INFO", f"saved spectrogram.png and loudness.png in {c.dir}")
    except Exception as e:  # pictures are advisory; a missing font must not lose the numbers
        report("12", "pictures", "NOT RUN", f"plotting failed: {e}")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    voice_cap = int(args[args.index("--cap") + 1]) if "--cap" in args else 32
    ref_dir = Path(args[args.index("--reference") + 1]) if "--reference" in args else None
    c = load_capture(Path(args[0]))
    if c is None:
        print(f"no master.wav in {args[0]}")
        return 2
    stems = ", ".join(n for n in ("music", "player", "crowd") if getattr(c, n) is not None) or "none"
    print(f"capture: {c.seconds:.1f} s at {c.rate} Hz, stems: {stems}, trace: {len(c.trace)} rows\n")
    check_realtime(c)
    report("1", "falloff curves", "NOT RUN", "a unit test in the project, not a capture check")
    report("2", "distance capture", "NOT RUN", "needs a scripted single-sound capture at 2/10/20/30 m")
    check_loudness(c)
    check_limiter(c)
    check_player(c)
    check_music(c)
    check_voices(c, voice_cap)
    check_density(c)
    check_contrast(c)
    check_mud(c, ref_dir)
    check_repetition(c)
    check_exposure(c)
    pictures(c)
    (c.dir / "report.json").write_text(json.dumps(results, indent=1, default=float))
    failed = [r for r in results if r["status"] == "FAIL"]
    print(f"\n{len(failed)} failed, {sum(r['status'] == 'PASS' for r in results)} passed, {sum(r['status'] == 'NOT RUN' for r in results)} not run")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
