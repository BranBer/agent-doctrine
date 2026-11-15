# The judged set

A measure of a sound is worth trusting only when it agrees with the playtester's ear on sounds they
have already judged. This file keeps those verdicts and how each measure did against them. The
sounds themselves live in the project's private sound library (`sound-library/judged/`, with
`judged.json` holding each set's verdict in the player's words), never in a public repo.

## The verdicts so far

| Set | Verdict | The player's words | What it was |
|---|---|---|---|
| torture | bad (v3.2) | "the battle mage autoattack is ear torture, it feels like screeching in my ears" | a 0.6–0.8 s fire cast and a 0.8–2 s burst every 0.6 s, plus a synthesised noise sweep |
| flick | bad (v4) | "casting sound effect is meh for battle mage. it plays and finishes abruptly" | the cast cut to 0.145 s; three of six cut 2–15 dB under their peak with a 36 ms fade |
| impact | kept (v4) | not mentioned in the play that named the cast | the fire bolt's burst, made from the player's own prompt |

Add a row, and the files, every time the person judges a sound.

## How each measure did

| Measure | torture | flick | impact | Agrees? |
|---|---|---|---|---|
| Cut while sounding (the slicer's `cut_db` and release) | – | three of six cut within 15 dB of the peak, 72 ms to die away: fails | whole | yes |
| Level where the final quarter begins, from the file alone | – | −7 to −29 dB | −11 dB and under | no: bone cracks, horns and long cries sit higher, at 0 to −8 dB |
| Final fade length, from the file alone | – | 25–30 ms | – | no: bow-air and bone cracks fade as fast and are fine |
| Exposure: seconds of the sound a second, from length × rate | cast 1.2, burst 2.3 | 0.24 | 0.75 | yes, on two sets: over 1 was torture |
| Sharpness, DIN 45692 (MoSQITo), loudness-weighted mean | 1.3–1.7 acum | 1.8–2.3 | 1.8–2.2 | no: torture measured least sharp |
| Mud share, 200–500 Hz | 0.36–0.46 (cast) | 0.10–0.16 | 0.17–0.39 | partly: the cast was muddy, the kept impact is too |
| Audiobox Aesthetics, enjoyment (CE) | 2.3 (cast), 1.5 (burst) | 3.5 | 3.0 | half: torture lowest, but the abrupt flick highest |
| Audiobox Aesthetics, production quality (PQ) | 5.5 (cast), 4.6 (burst) | 7.2 | 5.9 | half, the same way |

The torture verdict was about the whole attack in the mix, so per-file numbers can only partly
explain it. Exposure explains it best: no file was harsh on its own, but the files piled up. The
exposure figures for the torture set were worked out from take lengths and the 0.6 s cooldown, not
measured from a capture; `mixcheck.py` check 14 measures them from a capture now.

## Running the learned model

Audiobox Aesthetics (Meta, 2025, CC BY 4.0) scores speech, music and sound on four axes from 1 to
10: production quality (PQ), production complexity (PC), content enjoyment (CE) and content
usefulness (CU). Version 0.0.4 was read before it ran. It makes one outbound call, to fetch its
weights from Hugging Face as safetensors, and reads no environment and uploads nothing. It pulls in
torch, about 2.5 GB in uv's cache.

```python
# uv run --no-project --with audiobox_aesthetics --with soundfile python -I score.py <files>
import sys, numpy as np, soundfile as sf, torch
from audiobox_aesthetics.infer import initialize_predictor

pred = initialize_predictor()
batch = []
for f in sys.argv[1:]:
    x, r = sf.read(f, always_2d=True, dtype="float32")
    x = x.mean(axis=1) * 10 ** (-1 / 20) / (np.abs(x).max() + 1e-12)
    batch.append({"path": torch.from_numpy(x[None, :].copy()), "sample_rate": r})
for f, row in zip(sys.argv[1:], pred.forward(batch)):
    print(f, row)
```

Use it only to rank takes that already pass the defect checks, and only on files a licence lets
an AI tool touch: never on a Sonniss sound.
