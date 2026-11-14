---
name: game-audio
description: Use when adding, sourcing or mixing sound effects or music for a game, especially a web game - where to get SFX and music and on what licence (free libraries, Sonniss, Freesound, Kenney, AI generators like ElevenLabs or Stable Audio, AI music like Eleven Music, Lyria or Suno), attribution and provenance, Steam's AI disclosure, a Web Audio engine (unlock, buses, voice limits, priority, ducking, variation, loudness, formats, Safari and iOS), or an adaptive score that follows combat intensity (stems, layers, bar-quantised changes, stingers).
---

# Game audio

Sound is half of how a hit feels, and a score that follows the fight makes a run feel alive.
This skill covers where sounds come from and on what terms, the engine that plays them in a
browser, and an adaptive score. `references/sourcing.md` has the full licence table, the AI tool
terms and the provenance schema.

## Sourcing: free first, AI to fill gaps

| Need | First choice | To fill gaps |
|---|---|---|
| UI, pickups | Kenney (CC0) | none |
| Swings, whooshes, weapon and armour impacts | Sonniss GDC bundles, 99Sounds, Freesound filtered to CC0 | ElevenLabs sound effects, layered |
| Bone, debris, collapse | Sonniss, Freesound CC0, your own foley | ElevenLabs, Stable Audio 3 Small SFX (local) |
| Gore (mature setting) | your own wet foley (celery, cabbage, wet towel), CC0 | ElevenLabs (paid plan) |
| Magic, explosions | Sonniss, Kenney | ElevenLabs or Stable Audio, layered with CC0 booms |
| Creature voices | Sonniss creature libraries, Freesound CC0, heavy processing | ElevenLabs; avoid text-to-speech |
| Music | a pack with intensity stems | Eleven Music, then stem-split and edited by hand; Lyria only for ideas |

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
  is a gain node, and a limiter goes on the master.
- **The voice cap:** about 24 voices in total, with a cap per sound and per bus. When full,
  steal the lowest-priority voice. Priority runs player impacts first, then threats to the
  player, then the crowd, then ambience.
- **Variation:** 4–6 variants per sound, never the same one twice running, pitch ±6% (through
  `playbackRate`), and gain ±1.5 dB.
- **Ducking:** the player's impacts duck the crowd 3–6 dB for about 150 ms. Big spells and
  stingers duck the music.
- **Loudness:**
  - no browser standard exists, so aim for −16 to −18 LUFS for music and a true peak of −1 dBTP;
  - normalise short sound effects by peak and trim them by ear against the music;
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
  stabs on the same bar clock) prove the system works before money is spent on stems.

## Testing

- **Test browsers are silent** (see `games-doctrine`): wrap the context's output in a gain
  of zero.
- **Log the music tier and the bus voice counts** to a trace, and replay a recorded intensity
  trace through the music offline.
- **Listen on laptop speakers and a phone,** where most players will be.

## Related skills

- `combat-feel` covers what each hit should sound like.
- `intensity-director` drives the score.
- `crazygames-publishing` has the portal's audio rules ("Audio levels are consistent") and size caps.
