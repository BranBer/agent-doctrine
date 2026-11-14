---
name: combat-feel
description: Use when combat, hits or kills feel flat, weightless or unsatisfying, or when adding hit feedback to an action game - hit-stop, screen shake, hit flash, knockback, enemy hit reactions, deaths by damage type, debris, gibs, blood, dismemberment, wound decals, damage numbers, impact and enemy pain sounds, or a gore setting that keeps a teen-rated build one switch away. Use it for "juice", "game feel", "make it feel alive", "make it satisfying", or "like Diablo".
---

# Combat feel

A satisfying hit is several pieces of feedback landing together, and studios plan each one.
Diablo IV's art team gave every monster a "skeletal and muscular structure designed for these
kills" and let the killing skill choose the death. Its sound team recorded a separate cast,
flight and impact for the fire bolt. This skill breaks a hit into its parts, ranks the
techniques by return, and keeps gore behind one setting.

Numbers marked *(sourced)* come from a named source; the rest are starting values to tune with
the game's tuning panel.

## A hit has four beats

| Beat | What the player gets | Example |
|---|---|---|
| **Attack** | their own action, readable before it lands | swing whoosh, cast sound, muzzle flash, a small camera kick |
| **Impact** | the reward; gets priority over everything else | hit-stop, flash, impact sound, sparks or chips at the contact point |
| **Reaction** | the enemy's answer | flinch, stagger, knockback, a pain sound |
| **Aftermath** | what stays | a death by damage type, debris, corpses, decals |

Each beat has a visual and a sound, and each comes from a sim event: hit, kill, damage type,
hit location, overkill. Presentation never guesses what happened.

## Ranked: do these in this order

| # | Technique | Return | Effort | Starting values |
|---|---|---|---|---|
| 1 | Layered, varied impact sounds, separate from the attack sound | very high | low | 3 layers, 4–6 variants, pitch ±6%, gain ±1.5 dB, never the same variant twice running |
| 2 | Hit flash | high | low | additive white, 66 ms; 33 ms on armour |
| 3 | Hit-stop, scaled by damage and capped | high | low | light 33–50 ms, heavy 83–100 ms, kill 100–133 ms, cap 133 ms; the victim vibrates 2–3 px |
| 4 | Knockback and flinch scaled by damage over mass | high | low | 0.2–0.6 m over 120–180 ms, easing out; flinch 100–200 ms |
| 5 | Shake (trauma model) with a slider | med–high | low | +0.08 light, +0.25 heavy, +0.5 big spells; decay 1.5/s; max 0.3 m and 1.2° roll |
| 6 | Death decided by the killing damage type | very high | med | shatter 8–14 pieces over 0.8–1.2 s; ice = freeze then shatter; fire = char; heavy blow = launch |
| 7 | Enemy pain and death sounds, rationed | high | med | per-type cooldown 150–300 ms; at most 4–6 enemy voices at once; 3 death variants |
| 8 | Voice cap, priority and ducking | high with a crowd | med | 24 voices total; the player's impacts duck the crowd 3–6 dB for 150 ms |
| 9 | Impact particles (sparks, dust, chips) | med–high | low | 6–12 per hit, 0.3–0.5 s, pool of 512 |
| 10 | Damage numbers | med | low | merge an enemy's hits within 100 ms; show only the player's, crits and kills |
| 11 | Time-slow on rare big kills | med | low | render only, 60–100 ms at 0.3× speed; bosses and multi-kills only |
| 12 | Corpses and debris that stay, with a cap | med | med | 100–150, fading over 8–12 s, in a ring buffer |
| 13 | Blood spray and decals (gore setting 1+) | high, mature build | med–high | spray from the impact point along the hit direction; 96 decals in a ring |
| 14 | Wounds and dismemberment (gore setting 3) | high | high | per-instance wound mask; at most 2 wounds per enemy *(Valve, L4D2)* |
| 15 | Real ragdolls | med | very high | skip in a browser; fake with a ballistic arc and spin |

Work in this order: 1, 2, 3, 4, 5, 6, 7, 8, then the rest. Gore layers (13–14) come only after
the gore setting exists.

## Hit-stop

- Sakurai *(sourced)*: both attacker and victim freeze, the freeze grows with damage, each attack
  has its own multiplier, and there's a hard cap. The victim vibrates while the attacker creeps
  on slightly. The flinch blends in over a few frames.
- Smash Ultimate's hit-lag is floor(damage × 0.65 + 6) frames, capped at 30 *(sourced)*. A horde
  game hits far more often, so stay well under that.
- **Freeze only the two parties, not the world.** A global freeze lets everyone else "move in
  and strike" (Sakurai), and in co-op it pauses your teammates too.
- **In a deterministic sim:** give each entity a hit-stop tick counter that skips its movement
  and cooldowns, derived from damage so it replays identically. The vibration is cosmetic, in
  the renderer. A rare full-screen micro-freeze for a huge kill can be render-only.

## Shake

- The trauma model (Eiserloh, GDC 2016): events add trauma, clamped to 1, which decays over
  time. Shake = trauma² × smooth noise, applied to the camera's offset and roll.
- Apply it to the render camera only, never the sim.
- **Your own events shake hard; your allies' shake gently.**
- **Always ship a slider.** God of War (2018) cut shake right down for readability and put the
  weight into sound and animation instead.

## Enemy reactions and deaths

- **The reaction ladder:** flash → flinch → stagger, which cancels the attack → knockback or
  knockdown → stun → launch → death. Pick the rung from damage against the enemy's mass or
  armour.
- **Flinch by chance, in bands:** Diablo II (per D2MOO, a decompilation of its logic) compares a
  hit's damage with a fraction of the target's life that depends on the kind of attack (1/8 to
  1/64), and steps the flinch chance 0 → 37.5% → 75% → 100% above it. Heroes and monsters share
  the rule, and a stunned target flinches on every hit. Banded chance keeps a crowd from
  stun-locking under chip damage while big hits always land a reaction.
- **Direction matters:** react away from the impact point, in four buckets (front, back, left,
  right).
- **Death by damage type** (Diablo IV, "skill-driven deaths"): the killing skill picks the
  death. Fire chars, ice shatters, a crushing blow launches, a blade cuts, lightning blows the
  body apart. Diablo III launched skeletons across the screen and disintegrated enemies with
  holy magic, and Blizzard credits those deaths for much of its feel.
- **Horde-scale tricks for 100+ on screen:**
  - one instanced mesh per enemy type;
  - per-instance attributes for hit flash, state and wound mask;
  - reactions as transform offsets (recoil, squash, lean), not animation clips;
  - debris and corpses from pooled instanced meshes with caps;
  - vertex-animation textures for walk cycles.
- **Instance colour multiplies the albedo,** so it can't brighten past the texture's own
  colour. A bright flash needs an added emissive term per instance.

## Combat sound

- **Layer each impact:**
  - transient: the crack or click, 0–20 ms;
  - body: the thump or clang, out to about 150 ms;
  - tail: debris or ring, 200–600 ms;
  - sweetener: magic crackle, bone rattle, wet layer.

  Build a set per material pair, such as blade on bone, shield on plate, or fire on flesh.
- **The attack and the impact are different sounds.** Diablo IV's fire bolt has a cast
  one-shot, a looping flight and an impact *(sourced)*.
- **The impact sound starts on the impact.** Library takes often hold the swing before the hit;
  cut them to start a few milliseconds before their peak, or the reward lands a tenth of a second
  late.
- **Enemy voices:** attack grunts, pain, death. Keep fewer of them than hits: pain on a quarter
  of hits with 350 ms between, deaths 150 ms apart (Diablo II plays attack sounds by chance, not
  every time).
- **Reward a crowd, not each body.** Several of the player's kills at once play as one kill
  sound, two semitones higher per extra kill; a combo or chain climbs a scale, Peggle style.
- **Silence before a big hit.** DOOM's Gauss rifle cuts to near silence for an instant before
  the shot; a slam or a meteor lands harder after a short dip in everything else.
- **A sound the player makes constantly sits high and short.** A low blip on every shot, three
  times a second, became most of a mix's mud.
- **Priority:** the player's impacts first, then threats to the player, then the crowd. A
  voice cap with stealing and ducking keeps 100 enemies from turning into mud. Diablo IV and
  Overwatch both run an "importance" system.
- **Place every sound from the player's hero.** Without distance falloff, a fight across the map
  is as loud as one beside you, and a horde is "overwhelming". `game-audio` has the curves and the
  measured checks; no sound change is done until the mix is measured.
- `game-audio` covers the engine: buses, the voice cap, loudness and sourcing.

## The gore setting

Keep one integer setting, read when an effect spawns. The sim emits the same semantic events
at every level, and gameplay never reads the setting.

| Level | Shows | Fits |
|---|---|---|
| 0 | bloodless: shatter, dust, sparks, puffs | PEGI 7–12 |
| 1 | blood and ichor on fantasy creatures | PEGI 12 |
| 2 | blood and realistic reactions on human-like characters | PEGI 16 |
| 3 | gibs, dismemberment, wounds | PEGI 16–18 |

- **Author the safe version of every effect first,** and add gore as layers on top: blood
  becomes dust or sparks, gibs become bone or plate shards, wound decals become cracks or scorch,
  dismemberment becomes shattering, and wet sounds become bone or stone clatter.
- **Keep timing, hit-stop, shake and sound weight the same at every level,** so lowering it
  doesn't change the feel.
- **A truly rated build ships without the gore assets.** Strip them with a build flag, because
  a rating can count content that's merely switched off.
- **CrazyGames requires PEGI 12** ("Your game must be PEGI 12 compliant"), so its build uses
  level 1 at most. Steam can default higher.
- **PEGI's wording:** 12 allows "violence of a slightly more graphic nature towards fantasy
  characters". 16 is "increasingly more realistic-looking violence". 18 is "gross violence".
  Decapitation or dismemberment with much blood is gross; enemies that vanish in a puff of smoke
  are not. Skeletons may count as human-like, so check before relying on level 1 for them.
- WoW's `violenceLevel` (0–5) is the precedent for a single integer setting.

## Budgets for a browser at 60 fps

These starting budgets should hold on a 4 GB Chromebook:
- 150 draw calls;
- 1.5 ms of CPU per frame for effects;
- 600 live particles;
- 300 debris pieces;
- 96 decals;
- 24 audio voices;
- no allocation per hit: pool everything.

Test with the CPU throttled to 4× and on a real low-end device.

## Sources

- D2MOO, a decompilation of Diablo II 1.10f's game logic (MIT, partly verified against the original): https://github.com/ThePhrozenKeep/D2MOO
- Sakurai on hit-stop (Famitsu vol. 490, 2015 translation): https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/
- Smash hit-lag formulas: https://www.ssbwiki.com/Hitlag
- Diablo IV art, skill-driven deaths (Dec 2021): https://news.blizzard.com/en-us/article/23746639/diablo-iv-quarterly-updatedecember-2021
- Diablo IV audio (Oct 2021): https://news.blizzard.com/en-us/article/23731236/diablo-iv-quarterly-updateoctober-2021
- Diablo III corpses and deaths: https://gamesbeat.com/creating-corpses-making-bodies-matter-in-diablo-3/
- Valve, L4D2 wounds (GDC 2010): https://media.steampowered.com/apps/valve/2010/gdc2010_vlachos_l4d2wounds.pdf
- DOOM's glory kills and animation length: https://gamedeveloper.com/design/-i-doom-s-i-glory-kill-animations-nearly-cost-the-game-its-chainsaw
- Eiserloh, "Juicing Your Cameras With Math" (GDC 2016): https://gdcvault.com/play/1023146/Math-for-Game-Programmers-Juicing
- Jonasson & Purho, "Juice It or Lose It" (GDC Europe 2012): https://gdcvault.com/play/1016487/Juice-It-or-Lose
- PEGI labels: https://pegi.info/what-do-the-labels-mean

## Related skills

- `game-audio` covers sound sourcing and the engine.
- `sound-design` covers what makes each sound satisfying and the palette that makes them one world.
- `intensity-director` decides when the peaks come.
- `games-doctrine` covers pools, instancing and keeping cosmetic effects out of the sim's hash.
