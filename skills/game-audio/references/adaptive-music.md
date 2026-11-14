# Adaptive music from AI: intensity stems, and checking that they blend

Researched 2026-11-14. Prices and terms change; re-read them before spending.

## The answer in short

AI can make usable intensity stems, but no tool hands you bar-exact layers by role. The most
coherent cheap route is to **generate the full, most intense mix and split it downward into
stems**. Stems separated from one mix share tempo, phase, key and chords by construction, and
they add back up to the original. Separately generated layers rarely line up.

## Tools

| Tool | Gives | Commercial use | Price | Verdict |
|---|---|---|---|---|
| ElevenLabs Eleven Music v2.5 | full mixes with composition plans (tempo and key in the prompt), inpainting, a stem-separation API (6 stems) | the music terms (2026-10-09) allow an "Indie Game" (under $500k revenue a game, $1M across your games); paid plans only | Starter $6 a month ($1 the first), Creator $22 ($11 the first) | the cheapest credible path; ask support to confirm the indie terms in writing |
| AIVA Pro | arrangements with MIDI and stems; you own the copyright | yes | €33 a month | the best-quality path's arranger |
| ACE-Step 1.5 (local) | generation and per-layer additions in context of the others | MIT code and weights; training data undisclosed | free; under 4 GB of GPU memory | fine for a prototype; decide before Steam |
| Stable Audio 3 | open weights, clips | Stability Community Licence, free under $1M revenue | free locally | untested on music for us |
| Google Lyria 2 / RealTime | clips, live steering | terms unclear for distribution | API | ideas only |
| Suno | stems in Suno Studio | ownership wording unclear; Universal and Sony still suing | | don't ship |
| Udio | | downloads off since late 2025 | | don't ship |
| MusicGen, YuE2, MiniMax Music 3, popular RoFormer splitters | | non-commercial weights | | never in a commercial game |

**Separation:** the ElevenLabs stem API for shipping. Demucs (`htdemucs_ft`) is free and its code
is MIT, but its weights carry no stated licence: prototype only. Separation artefacts show most in
the calm tier, because it plays alone.

**Steam:** any shipped AI music is Pre-Generated AI content, so declare it. Taste and the "not AI
slop" bar stay with the user's ears.

## The pipeline

1. **A manifest per cue:** 120 BPM, 4/4, 8 or 16 bars, the key, which stems are harmonic or
   percussive, and the tier map.
2. **Generate** 3–5 takes of a 32-bar cue, with "120 BPM, D minor, instrumental, steady, no intro,
   no ending" and the full band up front.
3. **Pick and conform:** find the downbeats, choose the 8 or 16 bars that loop best, measure the
   real tempo, and stretch the mix (±2% at most) to exactly the bar length in samples.
4. **Separate** into stems, and make the last stem the residual (the mix minus the others) so they
   sum to the mix exactly.
5. **Map stems to tiers:** calm = the pads, low-passed and softened; pulse = + bass and kick;
   drive = + the full drums; intense = + choir or lead; overwhelmed = the full mix plus one extra
   layer; boss = an extra layer over the bed. Extra layers are MIDI written on the detected chords.
6. **Fold the loop's tail into its head, then encode** Opus at 96 kbps (mono for bass and pads):
   about 1.5 MB a cue, far under CrazyGames' 50 MB.
7. **Run the stem checks below,** then render a tier walk (calm, each tier up, overwhelmed, back
   down) for the user to judge on laptop speakers and a phone. Log provenance per
   `sourcing.md`.

**Best quality instead:** write the arrangement as MIDI first (by hand or with AIVA), render every
layer with the same instruments, and use AI only for textures or choir, generated against a guide
render so they inherit the grid. A person mixes it, leaving 1–5 kHz for the effects. With MIDI as
the truth, the harmony checks become exact.

## What makes layers and transitions blend

- One tempo, meter, key and length for every stem of a cue; loops cut on bar lines.
- Each tier adds density and brightness, not level: the full stack at most about 3 LU over the
  bed (see `mixing.md`), and each step +1 to +4 LU.
- Layers come up on the next bar and go down on a 4-bar phrase; horizontal changes between cues
  either stay within one step on the circle of fifths or use a transition segment or stinger.
- The score leaves 1–5 kHz to the effects in combat.

## Stem checks

Starting thresholds, to be calibrated before they are trusted: the placeholder synth stems must
pass, and each seeded fault must fail its named check (one stem shifted 30 ms, one stem up a
semitone, a loop cut a beat short, the last bar faded, one tier +6 dB, a stinger in the wrong
key). Not scripted yet: build `scripts/stemscheck.py` when the first real stems arrive, with
librosa or madmom for beats, chroma with Krumhansl-Schmuckler for key, and pyloudnorm for
loudness. A missing input is a failed step, never a skip.

| # | Check | Pass |
|---|---|---|
| 1 | Sample rate, channels, and length identical across stems, equal to bars × beats × 60 / BPM × rate | within 1 sample |
| 2 | The shipped Opus decodes to the same length and still passes 1 and 8 | within 1 ms |
| 3 | First downbeat from sample 0 | ≤ 10 ms |
| 4 | Beats against the ideal grid | median ≤ 8 ms, max ≤ 20 ms; tempo within 1% |
| 5 | Each stem's onsets in phase with the reference | ≤ 5 ms |
| 6 | Chroma energy inside the manifest's scale, each harmonic stem and the sum; key estimate agrees | ≥ 80%; key exact or a fifth away |
| 7 | Per-bar harmony: each harmonic stem against the sum, each tier's chords against the top tier's | median cosine ≥ 0.6, worst bar ≥ 0.3; chords agree on ≥ 75% of bars |
| 8 | The seam, with the loop played twice: no jump, flux or level change bigger than at the loop's own bar lines | flux ≤ 1.5× the bar-line median; level within ±2 dB |
| 9 | Loudness by tier | rising, +1 to +4 LU a step; top tier −16 to −18 LUFS |
| 10 | Every stem plus the boss layer at once | true peak ≤ −1 dBTP |
| 11 | Separated stems sum back to the mix | residual ≤ −40 dB |
| 12 | Onset density and brightness by tier | never falling |
| 13 | Music in 1–5 kHz against the effects | ≥ 6 dB under |
| 14 | Each tier change, rendered through the engine's ramps | flux ≤ 1.5× the bar-line median; cue changes ≤ 1 step on the fifths circle without a bridge |
| 15 | Stingers: in the key of every cue they can fire over, sync point on a whole beat | ≥ 80% in scale, ≤ 10 ms |

Blind key detectors are wrong about a quarter of the time on some material, which is why these
checks compare stems with the manifest and with each other rather than trusting one detector.

**What they can't judge:** taste, whether it reads as AI slop, how a layer feels in a fight, and
artefacts that measure fine but sound bad. Those need the user's ears on the tier walk.

## Sources

- ElevenLabs Music overview, composition plans, stem separation API and music terms (2026-10-09): https://elevenlabs.io/docs/overview/capabilities/music , https://elevenlabs.io/docs/api-reference/music/separate-stems , https://elevenlabs.io/music-terms
- AIVA pricing: https://www.aiva.ai/pricing
- ACE-Step 1.5: https://github.com/ace-step/ACE-Step-1.5 ; paper https://arxiv.org/html/2602.00744
- Stable Audio 3: https://stability.ai/news-updates/meet-stable-audio-3-the-model-family-built-for-artistic-experimentation-with-open-weight-models
- Suno ownership terms, 2025-12-26: https://www.musicinafrica.net/magazine/suno-adjusts-ai-music-ownership-terms-after-warner-music-partnership ; Udio downloads: https://www.digitalmusicnews.com/2025/10/31/udio-downloads-disabled-umg-deal/
- Demucs: https://github.com/facebookresearch/demucs
- Steam AI disclosure, January 2026: https://www.pcgamer.com/software/ai/steam-updates-ai-disclosure-form-to-specify-that-its-focused-on-ai-generated-content-that-is-consumed-by-players-not-efficiency-tools-used-behind-the-scenes/
- W. Phillips on vertical layering (GDC 2021; Game Developer 2015, 2021): https://www.gamedeveloper.com/blogs/pure-vertical-layering-for-game-music-composers-from-spyder-to-sackboy-gdc-2021- , https://gamedeveloper.com/audio/arrangement-for-vertical-layers-pt-1
