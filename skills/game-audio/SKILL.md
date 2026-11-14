---
name: game-audio
description: Use when adding, sourcing, designing or mixing sound effects or music for a game, especially a web game - where to get SFX and music and on what licence (free libraries, Sonniss, Freesound, Kenney, AI generators like ElevenLabs or Stable Audio, AI music like Eleven Music, Lyria or Suno), cutting multi-take library files into one-shots, attribution and provenance, Steam's AI disclosure, a Web Audio engine (unlock, buses, voice limits, priority, ducking, variation, loudness, formats, Safari and iOS), mixing a dense game (distance falloff from the player's hero, panning, rationing a crowd, music under the effects), checking a mix without ears by recording and measuring it, or an adaptive score that follows combat intensity (stems, layers, AI-made intensity stems, bar-quantised changes, stingers). Use it whenever sound is "overwhelming", "muddy", "too loud", "not satisfying" or "all at once".
---

# Game audio

Sound is half of how a hit feels, and a score that follows the fight makes a run feel alive.
This skill covers where sounds come from and on what terms, the engine that plays them in a
browser, the mix, how to check a mix you can't hear, and an adaptive score.

| File | Holds |
|---|---|
| `references/sourcing.md` | the licence table, AI tool terms, the provenance schema |
| `references/mixing.md` | the full mix spec, the probe contract, the checks and what they found |
| `references/adaptive-music.md` | AI intensity stems: tools, the pipeline, the stem checks |
| `scripts/mixcheck.py` | measures a recorded mix against the checks |
| `scripts/slice.py` | cuts multi-take library files into measured one-shots |
| `scripts/sfxgen.py` | generates sound effects with ElevenLabs from a prompt plan, logging each take's provenance |

## Sourcing: free first, AI to fill gaps

| Need | First choice | To fill gaps |
|---|---|---|
| UI, pickups | Kenney (CC0) | none |
| Swings, whooshes, weapon and armour impacts | Sonniss GDC bundles, 99Sounds, Freesound filtered to CC0 | ElevenLabs sound effects, layered |
| Bone, debris, collapse | Sonniss, Freesound CC0, your own foley | ElevenLabs, Stable Audio 3 Small SFX (local) |
| Gore (mature setting) | your own wet foley (celery, cabbage, wet towel), CC0 | ElevenLabs (paid plan) |
| Magic, explosions | Sonniss, Kenney | ElevenLabs or Stable Audio, layered with CC0 booms |
| Creature voices | Sonniss creature libraries, Freesound CC0, heavy processing | ElevenLabs; avoid text-to-speech |
| Music | a pack with intensity stems | Eleven Music: generate the full intense mix, then split it downward into stems (`references/adaptive-music.md`); Lyria only for ideas |

**Sonniss GDC bundles:**
- The download links sit behind a Cloudflare browser check that refuses curl, so open them in
  the user's own browser.
- Each library gives only two to four files, and many files hold several takes. Cut them with
  `scripts/slice.py`. It splits on silence, starts each hit just before its peak (a hit must land
  on the hit, not after a swing), and keeps the sharpest varied takes. It also logs where every
  take came from. A person still listens to the shortlist.
- The licence (v2.0) forbids supplying the sounds on their own and any AI training or use. So
  never push a repo that holds them to a public host, never publish them in a page of their own,
  and never feed them to an AI tool.

**Rules that keep a commercial game safe:**
- Never use **non-commercial** (CC BY-NC) material in an ad-supported game. That rules out
  Meta's AudioGen weights.
- Avoid **share-alike** (CC BY-SA) and **GPL** in a closed game.
- **Log every attribution** and generate the credits screen from the log.
- **AI tools on free plans are non-commercial.** ElevenLabs' terms say "The free plan does not
  include a commercial license". Generate on a paid month, download everything, keep the
  invoice, then cancel.
- **Eleven Music excludes "Studio Games"** but defines an Indie Game by revenue, so a solo game
  likely qualifies. Get that in writing from their support first.
- **Suno is half-settled** (Universal and Sony are still suing), and Udio can't be downloaded
  from. Don't ship either.
- **Steam:** any AI audio that ships counts as Pre-Generated AI content, so declare it.
  Generating music live in a browser game is impractical, and it adds Steam's guardrail duty.
- **Copyright:** raw AI output most likely has none. Layering, editing and arrangement add human
  authorship, so keep the project files.
- **Keep a provenance record for every shipped sound** (schema in the reference). Note it as
  AI or not, with the plan, prompt and edits.

The sourcing research was done in November 2026. Prices and terms change, so re-read a
licence page before you rely on it.

## The engine in Web Audio

- **One AudioContext,** created or resumed inside the first click or key press. Listen to
  `statechange`.
- **On iOS and Safari:**
  - an "interrupted" context may not come back on `resume()` without a gesture, so check that
    `currentTime` advances;
  - set `navigator.audioSession.type = 'playback'` inside a try/catch, or the silent switch
    mutes everything;
  - suspend when the tab is hidden and during ads.
- **Buses:** master ← music, SFX and UI, with SFX split into player, enemies and world. Each bus
  is a gain node for its level, then a duck stage. A limiter on the master is only a safety.
- **The voice cap:** 32 voices on desktop, 24 on mobile, with a cap of 3 per sound and a 30 ms
  gap between copies of one sample. When full, steal the lowest priority, then the quietest after
  distance. Priority runs the player's own sounds first, then threats to the player, then the
  crowd, then ambience. Count steals of the player's sounds: any means the cap is too low.
- **Variation:** 4–6 variants per sound, never the same one twice running, pitch ±6% (through
  `playbackRate`), and gain ±1.5 dB.
- **Ducking:** on each bus's duck stage, taking the deepest duck, never the sum. Ducking a
  bus's own gain from its current value drifts: overlapping ducks leave it stuck low.
- **Loudness:**
  - no browser standard exists; aim for −16 LUFS ±2 for the whole mix and a true peak of −1 dBTP;
  - normalise short sound effects by peak, and set their levels by measuring the mix (below);
  - normalise a cue's full mix, then apply the same gain to all of that cue's stems.

  ffmpeg's `loudnorm` does this in two passes; the commands are in the reference.
- **Formats:**
  - Ogg Opus first, with an MP3 fallback for Safari before 18.4;
  - mono sound effects at 32–48 kbps; music stereo at 64–96 kbps;
  - short sound effects packed into sprites;
  - music loaded after gameplay starts.

  CrazyGames caps the initial download at 50 MB, or 20 MB for the mobile home page.
- **Loops:** MP3 and AAC pad the start and end, which makes loop seams audible. Loop in Opus
  with `loopStart`/`loopEnd`, and test the seam in all three browser engines.

## The mix

A horde game's first mix failed its playtest: "all the sounds play all at once regardless of how
close i am to the origin. its overwhelming." `references/mixing.md` has the full spec. In short:

- **Place every sound, measuring distance from the player's hero, not the camera.** A camera
  37 m up makes the whole field sound equally near. Each kind of sound gets a falloff curve: the
  player's own at full, allies and enemies quieter toward the screen's edge and silent past it,
  big blasts carrying further. Threats, such as a champion, the objective or a grabbed ally, have a
  floor so they're heard from anywhere. Distant sounds lose their highs. Pan by the screen,
  capped at 0.6.
- **Ration the crowd.** One sound per tick for crowd deaths, from the nearest; pain cries on a
  quarter of hits, then 350 ms of quiet; several of the player's kills at once climb in pitch.
- **The hierarchy, by measurement:** the player's own hits at least 3 dB over everything else;
  the music 8 ±2 LU under the effects in combat and forward in lulls; each music tier
  level-matched, so intensity comes from density, not volume.
- **Watch the frequent sounds.** One 320 Hz blip on every arrow, three times a second, was most
  of a mix's mud. A sound the player triggers constantly should be short and sit high.
- **Compress only where the peaks are.** A gentle, fast compressor on the player's bus lets the
  mix come up. On the crowd it raised the crowd's average against the player's hits.

## Checking a mix without ears

Claude can't hear the game. A mix built by reading code shipped to a player overwhelming and
unsatisfying, and the player stopped playing. So no sound change is done until it's measured:

1. **Record real play.** The project supplies a probe: a silent headless browser that plays a
   scripted stretch of a run and records the master, each bus and a trace of voices, limiter
   reduction, the music tier and the game phase. Use AudioWorklet recorders that all start on the
   same frame. The contract is in `references/mixing.md`.
2. **Measure it** with `scripts/mixcheck.py`: loudness and true peak, the limiter as a safety,
   the player over the rest, the music under the effects, tier levels, voices, onset density,
   lull contrast and mud. A check that didn't run says so.
3. **Look at the pictures** it saves: the loudness plot puts every bus on one chart, and the
   spectrogram shows mud as a warm smear where separate hits should be.
4. **Take two captures.** No two runs play the same fight; a change is real when both agree.
5. **Then the person listens,** on laptop speakers and a phone. An AI model as a second ear is
   advisory at most: Gemini's API hears in mono at a low bitrate.

## The adaptive score

The two building blocks are **vertical layering** (stems that play together, with each
layer's volume following a parameter) and **horizontal re-sequencing** (switching sections at
bar lines). Stingers are short one-shots on the beat grid. FMOD and Wwise are these same ideas
behind a GUI. In a browser it takes about 200 lines.

- **Authoring:** one tempo (about 120 BPM), one key, and every stem the same length, such as 8
  bars (16 s). "Uptempo" comes from busier rhythm, not a faster tempo: `playbackRate` changes
  pitch along with speed.
- **Stems:** bed, pulse, drive, intense and overwhelmed, plus a boss layer on the bed and a
  separate two-stem loop for the rest between waves.
- **Sample-locked start:**
  - decode every stem;
  - make one buffer source each, all set to loop;
  - call `start(t0)` on all of them in one synchronous block with a single `t0` slightly in the
    future.

  From then on, never restart a layer; move only its gain. Stems must be decoded buffers,
  because media elements aren't locked to the audio clock.
- **The bar clock:** schedule from `AudioContext.currentTime`, never from timers, with a
  100 ms look-ahead on a 25 ms tick. The next bar is t0 + ceil((now + look-ahead − t0) / bar) ×
  bar.
- **Changes:**
  - layers come up at the next bar over a 1-bar ramp (half a bar when things get intense);
  - layers go down only at the next 4-bar phrase, over 2 bars;
  - different material crossfades at equal power;
  - avoid exponential ramps to zero and use `setTargetAtTime` instead;
  - cancel scheduled values before re-targeting.
- **The parameter:** a smoothed intensity with tiers and hysteresis, from `intensity-director`.
- **Stingers, quantised:**
  - wave warning: next beat;
  - boss arrives and wave cleared: next bar;
  - a player goes down: next eighth note, ducking the drive layers;
  - last stand: a riser one bar before.
- **Memory:**
  - decoded audio is Float32: 21 MB a minute for stereo at 44.1 kHz;
  - five 16 s stems plus a boss stem, the between-wave loop and stingers come to about 50 MB
    decoded;
  - on mobile, use mono beds or shorter loops.
- **Placeholders before real music:** layers synthesised in Web Audio (drone, pulse, drums and
  stabs on the same bar clock) prove the system works before money is spent on stems. Keep them
  quiet and high-passed: a placeholder that is too loud ruins the playtest it was meant to serve.
- **Real stems from AI:** generate the full intense mix and split it into stems, so the layers
  share tempo, key and chords by construction. Then check that they blend: the same length to the
  sample, in phase, in key bar by bar, clean loop seams, and loudness rising 1–4 LU a tier.
  `references/adaptive-music.md` has the tools, the pipeline and the checks.

## Testing

- **Test browsers are silent** (see `games-doctrine`): wrap the context's output in a gain
  of zero. A probe that records still silences the output after its tap.
- **Unit-test the placement** (`gainDb` for each curve at a few distances) and record a mix
  capture for every sound change (above).
- **Listen on laptop speakers and a phone,** where most players will be.

## Related skills

- `combat-feel` covers what each hit should sound like.
- `intensity-director` drives the score.
- `crazygames-publishing` has the portal's audio rules ("Audio levels are consistent") and size caps.
