---
name: sound-design
description: Use when designing, choosing, generating or judging a game's sound effects - what makes a sound satisfying (transient, body, layers, sub on laptop speakers, length, size, saturation, timing against the frame, variation, fatigue, how many takes, letting a sound finish), how the sounds become one world (sonic pillars, a palette, sound families with shared DNA, one shared space, one processing chain, frequency slots by role, effects in the music's key and on its beat, a motif, telegraphs, silence and contrast over a run), matching sound to visual effects, and prompting AI sound generators such as ElevenLabs so takes come out as one family. Use it for "sound design", "make it sound good", "satisfying sounds", "sonic identity", "audio direction", "sound palette", or before generating or buying any sound effects.
---

# Sound design

A sound is satisfying when it lands with weight at the instant of the hit, and a game sounds like
one world when its sounds share materials, a space, a key and a few habits. This skill covers
designing the sounds; `combat-feel` covers the beats of a hit and its visuals, and `game-audio`
covers sourcing, the engine, the mix and how to measure it.

Most claims come from shipped games' sound designers (Halo, Darktide, Helldivers 2, DOOM, Diablo
III and IV, Overwatch, League, Hi-Fi Rush, Journey, Left 4 Dead) and from perception research;
the numbers marked "ours" are our own starting values. Sources are at the end.

## One sound that satisfies

- **Weight lives in the body, not the click.** A 5 ms tone needs 10–19 dB more level to sound as
  loud as a 200 ms one; the ear sums over about 100–200 ms. Cut every hit to its first peak with a
  fade-in of 1 ms or less. Halo Infinite's new hits have "a sharp attack and begins to decay
  quickly"; its old ones stayed "at the peak for too long".
- **Layer in time and in band** (ours; no shipped game publishes a table):

  | Layer | Time | Band | Notes |
  |---|---|---|---|
  | Click | 0–15 ms | above 2 kHz | the identity; keep its pitch stable |
  | Body | 10–150 ms | 150 Hz–1.5 kHz | carries loudness on laptops; saturate here |
  | Sub | 0–120 ms | 40–120 Hz, plus a saturated twin at 100–400 Hz | big hits only |
  | Tail | 150–600 ms | the material's ring or debris | dry in the file; the room comes from the shared send |
  | Sweetener | any | any | magic crackle, bone rattle, a tonal ping in key |

  Chuck Russom's rule: if you keep one layer, keep the body; "less is always more".
- **Saturate the body and the sub's twin, never the click or a metal ring.** Over-compressed,
  over-saturated hits were Halo's "very fatiguing experience over time".
- **Most players have no sub.** Laptop speakers stop at about 100–200 Hz and a phone's resonates
  near 900 Hz. Give every sub layer a saturated twin at 100–400 Hz, and check each big hit
  through a 200 Hz high-pass (laptop) and a 600 Hz one (phone).
- **Length follows how often it plays.** At 120 BPM an eighth note is 250 ms: frequent hits stay
  inside it; a nova, a meteor or a boss slam may ring for a bar. Decay rate is the ear's main cue
  to material: wood and bone die in milliseconds, glass in about a tenth of a second, steel rings.
- **Let it finish.** Shorten a sound by choosing a shorter take, never by cutting a long one while
  it still sounds: a death scream cut at 1 s with a 30 ms fade read to a playtester as "they scream
  in anguish and then it stops". When a cut is unavoidable, make it at a quiet moment, such as a
  breath, and let it decay exponentially over a quarter of its length, never under 200 ms. A
  battle-mage's cast cut from near full level with a 36 ms fade "plays and finishes abruptly", and
  so did its impact's hiss with 111 ms; the cast recut with 200 ms did not. A sound whose tail runs
  long, such as a hiss, takes a longer release, not a shorter take. Cries and lines play whole or
  not at all.
- **Size by formants, not just pitch.** Formant spacing tracks body size; listeners notice about
  8% difference. Shift a boss's formants down 20% or more, and keep variants of one enemy within 4%.
- **Hyper-real for what the player causes, near-real for the world, real material processed for
  magic** ("even magical sounds should be organic", Darktide).
- **Anticipation, then release.** A wind-up, a short dip in everything else, then the payoff
  (Helldivers 2: "reserve the headroom for the things that must feel loud"). A sound up to about
  60 ms before contact makes a collision feel firmer.
- **Start the hit on the contact tick,** the first frame of hit-stop. One frame early is fine;
  waiting out a 4–6 frame freeze (67–100 ms) breaks broadcast sync limits and feels late.
- **Vary impacts, fix cues.** Vary each layer of an impact separately (body and tail most, the
  click's pitch least) and never play the same take twice running. Rewards and threat cues barely
  vary (Overwatch's "minimal variation" rule), so the player learns them.
- **Enough takes for how often it plays** (ours): 6–8 for what plays every second, such as attacks,
  kills and crowd cries, 4–5 for what plays every few seconds, 1–3 for rare sounds and cues, so the
  same take comes back no sooner than every 4 s. One bow string heard every 0.4 s, and two death
  cries, made a build "repetitive". Layers multiply: five takes in each of three layers make 125
  sounds. But every take must belong, because one odd take stands out each time it comes round
  (B. Jacobsen). `game-audio`'s mix check measures this.
- **The thousandth-repeat test.** Loop the most frequent sound for two minutes at game rate. What
  survives is short, mid-to-high, free of lows, quieter than the rare sounds, and less bright under
  sustained fire (Helldivers 2). Juice is an inverted U: none and extreme both test worse than
  medium.

## One world

- **3–5 sonic pillars and a "not this" list,** with a source set per family (Darktide: "oversized
  realism", "even magical sounds should be organic", not "high-tech"). Hold one idea: Journey is
  "all about sand and cloth".
- **Sound families with shared DNA.** Each class, faction or material gets a material, a band, a
  tonal centre and a character. Build a family from one source scaled up and down (Diablo IV's
  Firebolt and Inferno share fire takes; Hollow Knight puts one sheet of paper in every winged
  enemy). Abilities that do the same job share audio traits (League's shields, heals, stuns).
- **One shared space, chosen.** A short dark send for the whole world, or none on purpose. For a
  top-down camera (ours): decaying noise as the impulse, about 0.6–0.9 s, 10 ms pre-delay, band
  300 Hz–5 kHz; the player's own sounds 5–10% wet, others 15–25% and wetter with distance; the
  objective, UI and music dry. Big outdoor reverbs sound wrong from above (League's Volibear).
- **One processing chain for every file:** trim to the first peak, high-pass by role, tilt-EQ to
  one reference per family, light shared saturation, peak to −1 dBTP, a loudness class. Monument
  Valley 2's four plugins "would have touched every sound in the game".
- **A band per role.** Separate threats by timbre, pitch and length, not by being louder, so cues
  can play at once and still read (Darktide); Left 4 Dead gave each special "a distinct tonal range".
- **In the music's key, on its beat.** Tonal effects take the score's key, or the current chord
  for long ones, and are never pitch-randomised. Never quantise the onset of a player's action;
  snap only detached layers (a kill sweetener, a pickup ladder, a wave horn) to the next eighth,
  or stretch a travel time so the impact lands on a beat (Hi-Fi Rush, Rez). The root and the fifth
  are the safe notes over most chords in a minor key.
- **One motif of three notes or fewer,** shared by UI, wave cues and the objective (Left 4 Dead's
  horde call is "the most simple 3 note figure"). No cue gets two meanings.
- **Every special enemy has a telegraph:** an idle or lurk call before it acts, and a sting when
  it grabs (Vermintide 2 added cues once foley alone failed at high intensity; L4D2 added idle calls
  when testers knew the Charger only by its attack).
- **Silence and contrast across the run.** Each wave builds, peaks and relaxes with the music
  forward; a beat of near-silence before a boss; the crowd is one bed, not a hundred voices.

## Sound and picture

| Visual | Sound |
|---|---|
| bigger | lower pitch and formants, a longer tail, slower falloff |
| brighter flash | louder, more highs, a sharper attack |
| warm and jagged (fire) | noisy, crackling, harsh |
| cold, pure, round (holy light) | a tonal bell or glass, a soft bloom |
| lasts longer | a tail as long; cut the sound when the effect dies |
| pulses | the sound pulses on the same clock, the beat |

Sound changes felt weight: a hammer-on-marble sound made a hand feel heavier, but only in sync.
Moving a visual effect's trigger means re-checking its sound.

## AI-generated sounds

- **ElevenLabs Sound Effects:** set `eleven_text_to_sound_v3` explicitly (v2 is the default until
  its removal on 2027-03-01). Lengths 0.5–30 s through the API, no seed, prompt influence 0.3 by
  default. Looping is v2 only, so loop a v3 take by crossfading it.
- **One sound per prompt,** in this order: the core sound, its material and action, size and
  distance, then the family's style phrase verbatim ("close-miked studio foley, dry, brittle dry
  bone"). Prefer positive words ("dry, close-miked") to "no reverb"; name a layer's band ("only the
  sharp crack"); a named key is a hint, so measure and re-tune.
- **Generate layers separately** and combine them yourself. Take 10–12 of a frequent layer and
  keep the 6–8 that share a spectrum and envelope, or derive variants from one hero take.
- **Ask for a longer take than you need, by 30–50%,** and say how it ends ("trails off into a last
  breath and fades to silence"). A take stops at the length asked for, often mid-sound.
- **A family's style phrase names material and texture, never intensity.** The fire family's
  "roaring torch flame", appended to every fire prompt, made a battle-mage's twice-a-second attack
  "ear torture". The event's tier (`player-vignette`) adds the intensity word: subtle, soft, small for
  bread-and-butter; huge only for a climax. The player's own prompt that worked: "Crackling, whooshing
  firebolt impact with a subtle, satisfying hiss."
- **Quiet in the mix, never weak in the file.** A cast prompted as "a tiny soft flick of flame
  leaving a fingertip, a brief muffled puff of fire, subtle and quiet" came back thin, and the
  playtester called it "meh" (its takes were also cut short, so both played a part). Their own
  prompt sounded better to them: "mage casts firebolt initial casting ignition, smooth, subtle, but
  stern". It names who acts and the moment in the action, and pairs a word of restraint with a word
  of weight. Keep a frequent sound in its tier by level, length and rate, and ask the take for body.
- **Expect** leading silence, late quiet peaks (one test peaked 98 ms in), dead air, tails into
  room tone and warble. Process every take through the family chain; reject warble rather than
  repair it. A library click is the most reliable transient over an AI body.
- **Licences:** paid plans only for commercial use; log every prompt and take (`game-audio`'s
  `sfxgen.py` does). Never feed a licence-restricted library file, such as Sonniss, to an AI tool.
  A person picks what ships, and AI sounds that ship are declared on Steam.

## A palette file per game

Write it before generating or buying sounds, beside the game's other design notes:

- the pillars and the "not this" list;
- a table of families (each class, enemy faction, the objective, special mechanics, UI): material
  and source, the band it owns, its tonal centre, its character;
- the motif, and how it's varied (reversed, detuned, a tritone down);
- each family's style phrase for prompts;
- the tuning rules for the score's key.

## Checklist

**Before making sounds:** pillars and a "not this" list; a band, tonal centre and style phrase per
family; one motif; a shared space chosen.

**Each sound:** peaks at once; layered in time and band; keeps its weight through a 200 Hz and a
600 Hz high-pass; length suits its rate; ends on its own or on a decaying release, never cut while
sounding; size cues agree; saturation on the body only; cues fixed and impacts varied, with enough
takes for its rate; tonal sounds tuned and never pitch-randomised; through the family chain.

**Timing:** starts on the contact tick; the player's input never quantised; big moments get a
wind-up and a dip.

**Over a session:** every special has a telegraph; sound and visual match; a loudness plan of
build, peak and relax; the thousandth-repeat test passed.

**Done means measured** with `game-audio`'s mix check, then a person listens on laptop speakers
and a phone.

## Related skills

- `player-vignette`: write or read an event's record before designing its sound. Its tier sets
  the prompt's intensity word and its number of takes; a family's style phrase sets only material.
- `combat-feel`: the four beats of a hit, hit-stop, reactions and gore.
- `game-audio`: sourcing and licences, the Web Audio engine, the mix, `mixcheck.py`, `slice.py`
  and `sfxgen.py`.
- `intensity-director`: the build, peak and relax the run's loudness follows.

## Sources

- 343, "Inside Infinite", March 2021: https://www.halowaypoint.com/news/inside-infinite-march-2021
- Fatshark, "Darktide 101: The Sound of Darktide", 2024-10-23 (Fatshark forums)
- J. Walden on Helldivers 2, A Sound Effect, 2024-04-26; on Ghost of Yotei, 2025-11-06: https://www.asoundeffect.com/
- M. Isaza, interview with Chuck Russom, Designing Sound, 2010-04-29
- S. Lawlor and T. Neumann, "Overwatch: The Elusive Goal: Play by Sound", GDC 2016
- Riot Games, "The Stories Behind League's SFX", 2018-07-13; "/dev: A Storm is Brewing", 2020-04-10
- Valve developer commentary, Left 4 Dead (2008) and Left 4 Dead 2 (2009)
- S. Johnson, "The Sound of Journey", Game Developer, 2012-10-10
- Hi-Fi Rush at CEDEC 2023 and Unreal Fest Tokyo 2023 (Tango Gameworks)
- A-S. Mongeau on Monument Valley 2, A Sound Effect, 2017-11-14
- Florentine, Buus and Poulsen 1996 (JASA 99:1633), short-tone loudness; Fitch 1997 (JASA 102:1213), formants and size; Vroomen and Keetels 2020 (Cognition 204:104340), sound before contact; ITU-R BT.1359 and EBU R37, sync limits; Moliner, Ramo and Valimaki 2020 (DAFx), small-speaker bass
- ElevenLabs Sound Effects docs and the v3 announcement, 2026-10-29: https://elevenlabs.io/docs/overview/capabilities/sound-effects
- N. Garcia and J. Reiss, practitioners on AI sound effects, AES 2026 (arXiv 2605.27174)
- B. Jacobsen, "Game audio immersion" (layered variation, the nuisance score), A Sound Effect: https://www.asoundeffect.com/game-audio-immersion/
