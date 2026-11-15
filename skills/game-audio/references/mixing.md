# Mixing a dense game, and checking it without ears

Researched and measured 2026-11-14 on a top-down horde game: camera about 37 m from the hero,
a field about 40 m wide, up to 140 enemies. Numbers are starting values from published practice
and our geometry; the measured results at the end show which ones held. Adjust distances in
proportion for another camera.

Its first playtest ("all the sounds play all at once regardless of how close i am to the
origin. its overwhelming") came from an engine that placed nothing, and a mix nobody had
measured. Both are covered here.

## 1. Place every sound

- **The listener is the player's hero, not the camera.** With the camera 37 m away, a sound at
  the screen's edge is only about 1 dB quieter than one under the hero, so a camera listener
  sounds like no falloff at all. Unreal and CRI measure distance from the character and take
  panning from the camera. Diablo II sizes falloff in screen units: short sounds are silent at
  half a screen.
- **Use plain GainNode and StereoPannerNode, driven by a pure function** you can unit-test
  (`gainDb(curve, distance)`). PannerNode's defaults are wrong for a top-down game.
- **A curve per kind of sound,** linear in dB between points, nothing started past the edge:

  | Curve | 0 dB until | at 20 m (screen edge) | at 30 m | Silent past | Use |
  |---|---|---|---|---|---|
  | Own | always 0 dB | | | never | the player's attacks, hits, kills, damage taken |
  | Ally | 6 m | −6 | −16 | 34 m | other heroes and bots |
  | Enemy | 4 m | −9 | −24 | 30 m | enemy hits, deaths, cries |
  | Big | 8 m | −5 | −14 | 45 m | explosions, slams |
  | Threat | 10 m | −4 | −8 | 60 m, floor −10 dB | champion, the gem, a grabbed ally: heard from anywhere |

- **Dull distant sounds:** a low-pass open to 12 m, then 18 kHz down to 3 kHz at 30 m. A
  distant hit loses its transient and stops masking near ones.
- **Pan by the screen's left and right, capped at 0.6,** blended to centre inside 3 m. The
  player's own sounds pan at most 0.1. Music and UI stay as authored.

## 2. Keep the crowd from turning into mud

- **32 voices on desktop, 24 on mobile;** music on its own pool. Steal the lowest priority
  first, then the quietest after distance, then the oldest. Count steals of the player's own
  sounds: any at all means the cap is too low.
- **A voice stopped early fades out,** never stops dead: 50 ms when stolen, 120 ms when a newer
  copy replaces it at the per-sound cap, 80 ms when choked. A cry plays whole or not at all: at its
  cap the new one is skipped, and it is stolen only after every other voice of its priority.
- **Priority, highest first:** the player's damage taken, downs and wave stingers; the player's
  own attacks and hits; threats aimed at the player; ally actions and big events on screen;
  enemy hits and deaths near the player; the same farther away; foley.
- **Ration by rule:**

  | Sound | Rule |
  |---|---|
  | Any one sample | a 30 ms gap; a second copy inside it is skipped |
  | Enemy hit | 50 ms |
  | Enemy pain cry | a 25% chance on a hit, then 350 ms |
  | Enemy death cry | 250 ms, and played whole |
  | Crowd deaths | all the deaths in one tick play as one sound, a little bigger, from the nearest |
  | The player's kills | several at once play as one, two semitones higher for each extra, up to seven |
  | The player's own hits | one impact a tick: a swing or a burst that catches five enemies is one sound |
  | The player being hit | at most every 250 ms; a duck only for a blow over 6% of their health or below 40% health |

- **Ducks take the deepest, never the sum,** capped at 9 dB, on a stage after each bus so they
  always return to the bus's level. Ducking a bus's own gain from its current value drifts:
  overlapping ducks leave it stuck low.

  | Trigger | Ducks | Hold, release |
  |---|---|---|
  | The player's hit | enemies −4 dB, world −2 | 40 ms, 150 ms |
  | The player is hurt | enemies −6, world −4, music −3 | 0, 350 ms |
  | A big blast on screen | music −4, enemies −3 | 0, 500 ms |

  The player's own bus is never ducked by play (DOOM: weapons were "never ducked by anything").

## 3. The balance

- **The player over the crowd:** in the 150 ms after each of the player's hits, their bus sits at
  least 3 dB over everything else.
- **Music under the fight:** in combat, the music's short-term loudness sits 8 ±2 LU under the
  effects; between waves it comes forward about 3 dB.
- **Layers add density, not level:** the full stack at most about 3 LU over the bed. Trim each
  tier's level on the same bar as its layers change. Prototype 2's mix notes describe music,
  effects and voice all going big at the same moment; an adaptive score does exactly that unless
  trimmed.
- **Music EQ:** a high-pass at 40 Hz, a −4 dB low shelf under 80 Hz so the low thump belongs to
  impacts, and a −3 dB dip around 3 kHz where hits live.
- **Loudness:** −16 LUFS ±2 integrated (the game-audio guild's mobile figure), true peak no more
  than −1 dBTP, a loudness range of 6–15 LU. No browser or portal standard exists.
- **The limiter is a safety:** threshold −3 dB, ratio 20, 1 ms attack, 100 ms release, then 1 dB
  of trim. Over 1 dB of reduction in more than 5% of frames means the mix is being made by the
  limiter.
- **Bus compression only where the peaks are:** a gentle, fast compressor (−12 dB, 4:1, 2 ms,
  80 ms) on the player's bus shaves their hits' peaks. On the crowd it backfired: compressing
  the crowd raised its average against the player's hits, and the player-over-crowd check fell
  from +4 to +0.7 dB.

## 4. Check it without ears

Claude can't hear the game, and the player can't be asked to judge every change. So the mix is
measured from a recording of real play, then a person listens to what passed.

**The project supplies a probe** (a driver, as in `react-cross-browser`). It plays a scripted
stretch of a real run in a silent headless browser and saves, into one folder:

- `master.wav`: the destination, captured by a tap in an init script;
- `music.wav`, `player.wav`, `crowd.wav`: each bus after its duck stage, so the engine exposes
  them;
- `trace.json`: every 100 ms, `{t, tick, phase, voices, steals, highSteals, culled, reduction,
  tier}`, with "phase" equal to "wave" while enemies come; and once, `plays`: for each sampled
  sound, `{plays, variants, fixed, seconds}` counted while recording, "fixed" marking a cue meant
  to sound the same every time and "seconds" adding up each play's length over its playback rate.

Record with an **AudioWorklet**, not a ScriptProcessorNode. The ScriptProcessor runs on the busy
main thread and dropped about 30% of its blocks, so the stems no longer lined up. Start every
recorder on the same sample frame. The script should play the way a player does: attacking
during waves, stopping in lulls (a probe that kept firing in the lull made the contrast check
fail). Headless Chromium's audio clock ran slower than the wall clock under load, but the sim
kept pace with it, so judge timing by the audio clock and record the sim's ticks a second.

**The skill measures it:**

```bash
uv run --no-project --with numpy --with scipy --with soundfile --with pyloudnorm --with matplotlib \
  python -I ~/.claude/skills/game-audio/scripts/mixcheck.py <capture dir> [--cap 32] [--reference <dir>]
```

| # | Check | Pass |
|---|---|---|
| 0 | The sim kept real time against the audio clock | ≥ 54 ticks a second |
| 3 | Integrated loudness, true peak, loudness range | −16 ±2 LUFS; ≤ −1 dBTP; 6–15 LU |
| 4 | Peak to loudness ratio | ≥ 10 dB; less is crushed |
| 5 | Limiter reduction | over 1 dB in ≤ 5% of frames, over 3 dB in ≤ 1%, never over 6 dB |
| 6 | The player's hits over the rest, 150 ms after each | median ≥ +3 dB, ≥ 0 dB on 95% |
| 7 | Music under the effects in combat | 8 ±2 LU for 90% of combat |
| 7b | Music clear of hits, 1–4 kHz, at effect onsets | ≥ 6 dB under |
| 7c | Music level by tier | the top tier ≤ 3 LU over the lowest heard |
| 8 | Voices | p95 ≤ 80% of the cap; no steals of the player's own sounds |
| 9 | Onsets a second in combat (spectral flux) | p95 ≤ 12 (uncalibrated) |
| 10 | Combat against the lull | p90 of combat 4–12 LU over the lull's median |
| 11 | Mud: 200–500 Hz against 100 Hz–8 kHz | with `--reference`, ≤ +4 dB over a game the user rates well |
| 12 | spectrogram.png and loudness.png | look at them: separate hits should show as separate lines |
| 13 | Repetition: how soon the same take comes back, takes × seconds ÷ plays, cues left out | ≥ 4 s for every sound; under 2 s fails (ours) |
| 14 | Exposure: seconds of each sound played a second | ≤ 1 for every sound (ours): over 1, it overlaps itself |

Check 13 counts each layer of a layered sound on its own, so it is the strict reading: two layers
of seven takes each come back together only once in 49 plays. Check 14 is the pile-up behind an
"ear torture" verdict: a cast and a burst at about 1.2 and 2.3, worked out from their lengths and
cooldown (`takes.md`). Endings are judged when cutting, not in a capture: `slice.py` fails a take
cut while sounding with no room to die away, and `slice.py --check <dir>` lists files of 0.2 s or
more that stop while sounding.

Checks 1 (the falloff curves) and 2 (a single sound placed at 2, 10, 20 and 30 m) belong in the
project's own tests. A check that did not run is reported as not run.

**Read the pictures.** The loudness plot shows each bus on one chart. Its first run here showed
the crowd 10 dB over the player, and the music only 2 LU under the effects. The spectrogram
shows mud as a flat, warm smear where separate hits should be.

**Take two captures.** The player's input follows the wall clock, so no two runs play the same
fight; one capture's numbers moved by up to 3 dB from the next. A change is real when both agree.

**An AI model as a second ear is advisory only.** Gemini's API mixes audio down to mono at a low
bitrate, so it can't hear panning, and no published case shows a model judging a game mix well.

**The person listens last,** on laptop speakers and a phone, to what passed.

## 5. What the measurements found, so far

| Found | Fix |
|---|---|
| No falloff: a fight across the map as loud as one beside the player | the curves in section 1 |
| The crowd 10 dB over the player's own sounds | bus levels: player ×1.5, crowd ×0.45 |
| The music 2 LU under the effects | music ×0.73 with tier trims, about 7.5 LU under |
| Most of the 200–500 Hz mud from one sound: the archer's 320 Hz shot blip, three times a second | a short, high snap and air instead; the band fell from +7.9 to about +1 dB |
| The pulse layer added 5.6 LU to the score | tier trims of 0, −3, −4, −4, −4 dB |
| Peaks from the player's hits, from a level over 1 | the player-bus compressor; master at 0.9 |
| −19.4 LUFS, 1.4 dB under the target, to keep the true peak at −1.2 dBTP | left for the user's ears: louder needs the hits squashed |
| "They scream in anguish and then it stops": 21 files cut while sounding, at a fixed length with a 30 ms fade, and voices stopped dead at the cap | takes end where they fall silent or on a long exponential release; early stops fade; cries play whole |
| "Some of the sounds are repetitive": the bow string had one take, heard every 0.4 s; the death and pain cries and the tank's swing had two | 7–8 takes each and a shuffle that avoids the last half; the same take now every 3–15 s |
| A tank now hit all the time (enemies fight the body in their road): a hurt thud and a duck on every hit buried the music 14 LU deep, and the mix ran at −13.7 LUFS | hurts rationed, ducks only for heavy blows or low health, one impact per tick, the swing itself quieter; −16.0 LUFS and lull contrast 7–9 LU, but the music still sits 12 LU under in a tank run |
| The player bus over full scale (+2.4 dBFS) with few voices playing: the mage's nova at 0.9 on a bus trimmed ×1.5 | signature moments set lower on the player's bus, and its trim cut to ×1.25; true peak −1.2 to −1.4 dBTP, with one tank capture at −0.8 |
| The mud band up from −0.3 to +4.3 dB in a mage run: its cast and impact, heard twice a second, put 35–43% of their energy in 200–500 Hz | high-passed at 700 Hz and 400 Hz; +2.2 dB |
| A fuller cast (0.4–0.55 s, from the player's own prompt) at the old flick's level: the mix up 2 LU, the music 10.5 LU under, mud +3.9 dB | the cast from 0.3 to 0.18; −18.9 LUFS, the music 8.2–8.5 LU under, mud +3.3 dB, the cast at 0.53 s a second |
| Ten sounds re-cut so they die away, the impact among them: its new takes peak at the hit and then fall away into a 0.3 s hiss, so the mage's mix fell 1.5 LU and its own hits cleared the rest less often (89–90%, from 93%) | the impact from 0.5 to 0.6; −19.2 to −19.6 LUFS, own hits 90–94%. Archer and tank runs matched the old files' runs |

## Sources

- Unreal Engine, Spatialization Overview: https://dev.epicgames.com/documentation/unreal-engine/spatialization-overview-in-unreal-engine
- CRI Middleware, "Focus Point", 2022-09-02: https://blog.criware.com/index.php/2022/09/02/focus-point/
- Blizzard, Diablo II Data Text File Guide (sounds and monsounds tables), mirrored at https://d2runewizard.com/game-files/guide.html
- Dolby, "A 2D game with 3D sound: Ori and the Will of the Wisps": https://professional.dolby.com/gaming/gaming-blog/a-2d-game-with-3d-sound-ori-and-the-will-of-wisps
- R. Bridgett, "Notes from the Mix: Prototype 2", Game Developer, 2012-06-20: https://www.gamedeveloper.com/audio/notes-from-the-mix-i-prototype-2-i-
- Factorio, sound aggregation (later copies at (x+1)^-2): Factorio's modding docs, `aggregation` on sound definitions
- Path of Exile 2, "Skill Sound Design" (D. Downing), 2025: https://devtrackers.gg/pathofexile/p/6f7c2b28-skill-sound-design-in-path-of-exile-2
- DICE, HDR audio in Frostbite (the loudness window that culls quiet sounds), GDC talks 2009–2011
- Game Audio Network Guild, recommended loudness for mobile: −16 LUFS ±2, −1 dBTP
- W3C Web Audio API (DynamicsCompressorNode.reduction, PannerNode models): https://www.w3.org/TR/webaudio/
- Audiokinetic community Q&A: shuffle "avoid repeating last 10" over 15 footsteps (https://blog.audiokinetic.com/qa/1388/saving-state-of-random-container); the short fixed kill fade (https://blog.audiokinetic.com/qa/6387/kill-voice-fade-out); killing the newest instance so lines never overlap (https://www.audiokinetic.com/qa/6770/instance-limiting-newest-remove-killed-object-random-container)
- B. Jacobsen, "Game audio immersion", A Sound Effect: https://www.asoundeffect.com/game-audio-immersion/
