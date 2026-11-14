---
name: intensity-director
description: Use when designing or building the pacing of a wave, horde or co-op action game - an AI director like Left 4 Dead's, tracking each player's intensity, build-up / peak / relax cycles, when enemies spawn inside a wave, bursts and lulls, special enemies that punish players who stray, mercy rules, boss timing, or music that follows how hard the fight is. Use it even when the user only says a game feels flat, samey or predictable, or asks to "keep the player on their toes".
---

# Intensity director

A director watches how hard the fight is for each player and decides *when* the next
threat arrives. Left 4 Dead's director is the reference: it changes **pacing, not
difficulty**. "Amplitude (difficulty) is not changed, frequency (pacing) is" (Michael Booth,
Valve, 2009). The result is peaks the players remember and lulls where they laugh about it,
without anyone tuning a spawn list by hand.

This skill gives the model, the cycle, how to fit it inside fixed waves, and the fairness
rules. Values marked *(L4D)* are Valve's documented defaults; everything else is a starting
value to tune with the game's tuning panel.

## The intensity model

One number per player, 0 to 1.

| Raises it | L4D | Starting value for a wave game |
|---|---|---|
| Damage taken | in proportion to the damage | +1.5 × damage / max health, capped at +0.5 per hit |
| Going down | jumps to 1 on the first incapacitation | set to 1 |
| Pulled, pushed or grabbed by an enemy | "pulled/pushed off of a ledge by the Infected" is its own input | +0.35 when a pin or grab starts |
| An enemy dying near you | more the closer it is | +0.03 × (1 − d / 10 m); a boss nearby +0.25 |
| The objective taking damage | (not in L4D) | +1.5 × damage / objective max, to everyone |

- **Decay:** hold for a few seconds after the last impulse, then fall linearly to zero. In
  L4D it holds 5 s and falls over 30 s (`intensity_decay_time 30`). For waves of a minute or
  two, start at a 4 s hold and a 20 s fall.
- **No decay while an enemy is actively attacking that player** *(L4D)*.
- **Team intensity = the maximum over players**, not the average *(L4D)*. One player in trouble
  is the team in trouble.
- The director reads the instant value. Music reads its own smoothed copy (below).

## The cycle

| State | What spawns | Leaves when | L4D value |
|---|---|---|---|
| **Build up** | Everything: the full population | team intensity ≥ peak threshold, and a minimum build time has passed | threshold 0.9 |
| **Sustain peak** | Keeps spawning | a short timer runs out | 3–5 s |
| **Peak fade** | Nothing new; what's out keeps fighting | intensity < relax threshold **and** a natural break: few enemies near anyone | relax threshold 0.9 |
| **Relax** | Nothing, or only harmless stragglers | a timer, or the players move on | 30–45 s |

- **Peak fade exists so the current fight finishes** before the relax timer starts. Without it,
  relax gets eaten by the tail of the fight.
- **Bosses ignore the cycle** *(L4D)*. They come on their own schedule because they change the
  pacing anyway.
- **The L4D director never pushes harder when players are bored.** It only takes threat away.
  "Keep them on their toes" needs the bored push below.

## Inside discrete waves

Most wave games have a designed list per wave. Keep the list and let the director decide
*when* to spend it:

- **A fixed budget per wave.** Wave *n* has a credit budget and a roster. The director never
  changes the budget for pacing; it only times the spending. *(Risk of Rain 2 spends credits on
  weighted cards; borrow that.)*
- **Packets, not single spawns:** a weighted pick of affordable cards every 3–6 s in build up,
  every 2–4 s in the peak, ±25% jitter from the director's own RNG. None in fade or relax.
- **Telegraph every packet** about 2 s ahead: the gate glows, a horn sounds, a marker shows.
  Anticipation is deliberate in L4D (music, Tank footsteps, doors breaking).
- **The bored push:** if intensity has stayed under 0.15 for 10 s in build up and budget is
  left, buy the next packet now and one size bigger. *(Intensity steered toward a target curve
  is the sourced precedent: C. Thomas, "Using intensity to drive player engagement", 2017.)*
- **Mercy:** at peak, if the objective is under 30% or half the team is down, skip the
  sustained peak and go straight to fade. After a player goes down, no spawns near them for
  8 s.
- **Boss waves:** the boss arrives at half the budget, not gated by intensity. Nudge it up to
  10 s to avoid landing in a mercy window, telegraph it 4 s ahead, and while it lives send
  only a thin trickle of small packets and no specials.
- **The last stand:** lock the tempo, as L4D2's `LockTempo` does for finales, so there's no
  relax. Give it two short breathers at about 35% and 70% of the budget, because constant combat
  wears people out.
- **A time cap per wave:** past it, drop relax and halve packet intervals so the budget always
  finishes.
- Expect one to three peak-and-valley cycles per wave, with relax taking 15–40% of the wave.

Starting values: peak threshold 0.9; relax threshold 0.6 (lower than L4D because decay is
shorter); minimum build 6 s; peak hold 3–5 s; fade fail-safe 15 s; relax 6–12 s; wave cap
120 s.

## Specials against stragglers: the co-op glue

In L4D the special infected punish a player who wanders off, and only a teammate can free
them. That is what makes players stick together. The fairness rules matter more than the
special itself:

- **Isolated** means the nearest ally has been more than about 12 m away for 4 s.
- Target only isolated players whose intensity is below 0.6, who aren't down, aren't in a
  mercy window, and weren't targeted in the last 25 s. If nobody qualifies, spend that budget
  on a normal packet.
- Spawn at least 15 m from every player and out of their sight *(L4D)*, with a 2 s telegraph.
- A pin waits 1 s before it deals damage, and any ally in reach can break it.
- No specials before wave 2, none in the first 12–20 s of a wave, none during a boss. At most
  half the player count (rounded up) alive at once.

## Determinism

The director decides spawns, so it is part of the simulation:

- It runs inside the sim, reads sim state only, and steps at 10 Hz with integer-tick timers.
- It has its **own seeded RNG stream** (seed plus wave number), so its draws never shift combat
  rolls.
- It uses only arithmetic in sim maths: `Math.pow`, `exp` and `sin` are approximated
  differently across engines.

The music never feeds back into the sim.

## Driving the music from the same intensity

Music is per player in L4D: what *this* player is going through, not a global slider
(Morasky: music follows "what the player is actually experiencing, not what we want them to
experience").

- **Target:** max(own intensity, 0.85 × team intensity, 0.8 × objective danger), with a floor
  per director state (build up 0.35, peak 0.8, fade 0.5, relax 0.25).
- **Smoothing:** a one-pole filter with a fast attack (0.3 s) and a slow release (8–10 s).
- **Tiers with hysteresis**, each with an up and a down threshold:

  | Tier | Up | Down |
  |---|---|---|
  | Calm | 0.15 | 0.10 |
  | Uptempo | 0.35 | 0.27 |
  | Intense | 0.65 | 0.55 |
  | Overwhelmed | ≥ 0.9 plus real danger | 0.7 |

  Stay at least 1 bar before going up and 4 bars before going down.
- `game-audio` covers how to play this: stems, bar clocks and stingers.

## Testing

- **Record a trace in the replay:** tick, state, each player's intensity, packets and specials.
- **Assert in a headless soak:**
  - every wave finishes before its cap;
  - no special breaks the fairness rules;
  - relax takes 15–40% of each wave;
  - the same seed gives the same trace.
- **Feed a recorded trace to the music offline** to tune its tiers without playing.

## Other directors, one idea each

- **Vermintide 2:** the same four states, intensity per hero, and "intervention" against
  stragglers.
- **Risk of Rain 2:** a credit budget spent on weighted cards. Spawns fail at 40 alive, at no
  cost.
- **Deep Rock Galactic:** swarms announced by mission control, smaller pressure waves between
  them, and no swarm while a boss lives.
- **Back 4 Blood:** the director adds rule cards the players can see and play around.

## Sources

- M. Booth, "The AI Systems of Left 4 Dead" (Valve, 2009), slides 78–87: the intensity model (80),
  the cycle (81), what each state allows (82), and graphs of intensity against the live population
  (84–87): https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- M. Booth, "Replayable Cooperative Game Design: Left 4 Dead" (GDC 2009): https://cdn.fastly.steamstatic.com/apps/valve/2009/GDC2009_ReplayableCooperativeGameDesign_Left4Dead.pdf
- Valve's decompiled L4D2 director scripts and cvar dumps, which hold the tunable names and defaults: https://github.com/jacob404/Official-Vscripts-Decompiled
- Mike Morasky on L4D2's music (2011): https://www.audiogang.org/interview-with-valves-mike-morasky/
- Risk of Rain 2's director: https://riskofrain2.wiki.gg/wiki/Director
- C. Thomas, "Using intensity to drive player engagement" (2017): https://gamedeveloper.com/design/using-intensity-to-drive-player-engagement

## Related skills

- `game-audio` plays the music this drives.
- `combat-feel` makes each peak land.
- `games-doctrine` keeps the director headless and deterministic.
