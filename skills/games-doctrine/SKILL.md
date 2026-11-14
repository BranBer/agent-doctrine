---
name: games-doctrine
description: How to build TypeScript web games with Phaser or Three.js and Vite under the doctrine - purpose folders (sim, systems, scenes, render, platform, levels), a headless simulation that never imports the renderer, scenes as thin shells over systems, a fixed-step loop, seeded randomness, pools, platform SDKs behind one adapter, the prototype lane before a game is proven fun, and which check proves which change. Use when writing or reviewing game code, including a first prototype.
---

# Games doctrine

Load `doctrine` first. This pack is what its rules look like in a TypeScript
web game built with Vite and Phaser or Three.js. It specialises rule 1 (units
and entry points), rule 3 (logic free of the framework) and rule 4
(dependencies and adapters), and gives the purpose folders.

## Purpose folders

```
src/
  game/
    sim/          the simulation: physics, entities, rules, scoring. Plain TS, runs headless.
    systems/      reusable behaviour shared by scenes: camera, input mapping, tweens, audio cues
    scenes/       one unit per screen (Play, Title, Results) - thin shells over sim and systems
    render/       drawing: sprites, meshes, materials, particles. Reads sim state, never writes it.
    platform/     adapters for the outside world: ads, storage, leaderboards, analytics
    levels/       level data and the code that loads it
  utils/          subject units: math, rng, easing, time
  assets/         art and audio, imported by render/ and systems/
```

A unit grows from a file into a folder exactly as `doctrine` describes:
`scenes/Play.ts` becomes `scenes/play/` with `index.ts` (the scene) and its
private parts - `sounds.ts`, `effects.ts`, `results.ts` - beside it. A part
that knows nothing about the scene (a camera follow that takes a pose and a
time step) goes to `systems/` instead.

## The simulation never imports the renderer

`sim/` imports no Phaser, no Three.js and nothing from `scenes/` or `render/`.
It takes inputs and a time step, and returns state and events.

*Why:*

- **Testable headless.** The simulation runs in a plain test with no canvas,
  and a test can step it a thousand ticks in milliseconds.
- **Replayable.** Same seed, same inputs, same result: a bug report becomes a
  recording you can replay.
- **Portable.** Swapping Phaser for Three.js, or running the sim on a server
  to check a score, touches nothing in `sim/`.

```ts
// sim/world/index.ts - the whole contract with the outside
export class Sim {
  step(input: Input): SimEvent[] { … }   // advance one fixed tick
  state(): Readonly<WorldState> { … }    // what render/ draws
}
```

The scene owns the loop and the framework; it feeds input in and hands state
and events to `render/` and `systems/`:

```ts
update(_time: number, delta: number) {
  for (const tick of this.clock.advance(delta)) {
    for (const event of this.sim.step(this.input.read())) this.cues.play(event);
  }
  this.view.draw(this.sim.state());
}
```

Physics engines are the one exception worth naming: a physics library that is
not a renderer (Rapier, Planck, Matter's core) belongs inside `sim/`, behind
the sim's own types so the rest of the game never sees it.

## A fixed-step loop

The simulation advances in fixed ticks (60 per second is usual), whatever the
frame rate. The scene accumulates real time and runs as many ticks as fit;
render interpolates between the last two states if it needs smoothness.

*Why:* a variable step makes physics depend on frame rate - a fast machine and
a slow one play a different game, and replays stop matching.

## Seeded randomness

All randomness in `sim/` comes from a seeded generator in `utils/rng`, passed
in, never from `Math.random()`. Daily challenges, replays and tests all depend
on it.

## Pools

Anything spawned and destroyed many times a second - bullets, particles,
debris - comes from a pool that resets objects instead of allocating new ones.
The pool lives with what it pools (`render/particles/pool.ts`), not in a
general `pools/` drawer.

A pool that recycles its oldest piece should shrink that piece out over a
fraction of a second. One that vanishes in a frame reads as a bug.

## A feel slice must read in the game

A grey-box slice can't be judged on feel unless the player can read what it is.
One failed a feel gate as "low quality" with its physics fine, because nothing
on screen said what to do. Before asking anyone to judge feel:

- **Goal, threat and controls show in the game,** without a page to read.
- **The first frame shows the place.** A chase camera that looks at the car at
  rest points at the floor; a look-ahead floor brings the world into frame.
- **Breakage shows.** What the sim says happened (a part off, a robot wrecked)
  appears on screen and is heard.
- **The controller looks at every picture as a player would,** beside the
  concept. Builds that pass every test have still looked wrong.

## The prototype lane

Until the user has played a game's core loop and said to keep it, its build is
a throwaway that answers one question: is this fun? One game got a 733-line
spec, 31 reviewed tasks and full test suites before its first feel gate, and
failed two.

- **A one-page brief, approved before the build.** It holds:
  - the question the prototype answers, and what would kill the idea;
  - the pitch in one sentence, and the user's own words, verbatim;
  - the core loop in two to four bullets, the goal and the fail state;
  - at most seven features, what is out of scope, and the build order, riskiest first;
  - the first minute of play.

  Mark anything Claude filled in as a guess.
- **Relaxed:** the size and folder rules, comment density, test depth and
  per-task reviews.
- **Kept, so checks can attach later:** the headless sim behind `step` and
  `state`, the fixed step, seeded randomness, every tuning number in one data
  file, and silent test browsers.
- **Kept apart:** the code lives in `prototype/`, each file starts with
  `// PROTOTYPE - NOT FOR PRODUCTION`, and nothing outside imports it.
- **Placeholder art is CC0 and not AI-made,** such as Kenney or KayKit packs.
  [patch.gg](https://patch.gg)'s index finds them (`license=CC0-1.0&ai=false`).
  Download each from its original source and record it in a provenance file.
  Grey boxes do as well, so long as the player can tell who is who.
- **Timebox:** playable within two or three days. Two hours with nothing
  playable means the question is too big; shrink it.
- **After each play, the user's verdict:** proceed, pivot or kill, with a few
  lines on what happened in their words. Three pivots on one concept force a
  kill decision. A build nobody has played is not assessed, never passed.
- **Proceed means rewrite.** The real game starts fresh under the full
  doctrine, with what the prototype taught and none of its code.

The lane, the verdicts and the check table below adapt ideas from Claude Code
Game Studios (MIT).

## Which check proves which change

| Change | Proof |
|---|---|
| A sim rule | A headless test. |
| Anything the player sees | Launch at a fixed size, reach the state by URL, take a screenshot and open it. Report OBSERVED, or NOT VERIFIED and why. It covers the look, not the feel. |
| What the sim does over a run | A seeded replay compared with the last accepted one. |
| Performance | A bench under CPU throttling. |
| Feel, balance, a whole session | The user playing it. Never automated, and no feel verdict before they have played. |

In the prototype lane only the second and last rows are required. A check that
did not run is reported as not run, never as passed.

## What keeps a 3D scene believable

- **The key light is never behind the chase camera.** Lit from behind the camera,
  every face the player sees takes the same light and the forms go flat.
- **A collider encloses whatever can touch it.** A wheel, roof or corner that can
  meet the ground needs collider there, or it clips through on a wreck. The other
  way round, anything drawn outside a collider must be out of reach: inside the
  box, or high enough that a car passes under it. Test it against the car's own
  geometry.
- **A chase camera stays inside the walls, and keeps its pitch.** Clamp its spot
  into the bounds on each axis, then lower it in proportion to the boom left on
  the ground, with a floor over the roof. Sliding along the boom is the usual
  answer, but it collapses in one step for a car scraping a wall.
- **Decoration stays out of the play space,** or a car drives through it. Things in
  the play space can be hit.
- **Spawned effects bought with draw calls run out.** Draw burst pieces as extra
  instances of the instanced meshes already on screen, and merge static scenery
  into one vertex-coloured mesh. One project went from 26 scenery calls to 3.
- **An inverted-hull outline** pushes in device pixels after projection, or its
  width changes with aspect. A smooth normal bisects a corner, so push √2 times
  the width near by and taper to 1 toward the fog, or distant actors turn to ink.
  Scale the push by an instance's own scale, or shrinking pieces end as dots.
- **Cosmetic physics stays out of the sim's hash,** in a world of its own, with a
  test that the hash is the same with and without it. Step it once per sim tick
  with that tick's state, so a hit-stop freezes it and a kinematic stand-in moves
  at its true speed. A stand-in that jumps further than a tick's travel is placed,
  not swept, or it launches what it passes.
- **Warm shaders when the run is built.** `renderer.compile` walks hidden meshes
  too, and a material turned transparent to fade is a second program. Check with
  `renderer.info.programs` that the first hit compiles nothing new.

## Feel, pacing and sound

Three skills carry what makes a playable loop feel alive:

- `combat-feel` covers hit feedback, enemy reactions and the gore setting.
- `intensity-director` covers when threats arrive, inside waves.
- `game-audio` covers sourcing, the Web Audio engine and the adaptive score.

Like the rest of the sim, the director runs headless and deterministic. Hit-stop counters belong
to the sim; shake, flash, debris and music belong to render.

**A change meant to add quality, done badly, takes fun away.** One prototype's second build
added a director, an adaptive score, a combat-feel pass and new mechanics at once, and its
player stopped early: "the edits made the game less enjoyable". From that:

- **Measure what Claude can't sense before it ships.** Sound was built by reading code and never
  heard; the mix that reached the player had every sound at full volume from anywhere. Record and
  measure it with `game-audio`'s mix check, then let the person listen.
- **An upgrade never takes control away.** A multishot card fanned arrows away from the aim
  point, so every shot missed what the player pointed at. Spread is a gap at the target, and the
  aimed shot stays on the aim line. Diablo II's own controller multishot had the same bug.
- **A cost the player never sees is no cost.** A hungry upgrade drained a villager the player
  never saw: "why should they care?" Put a trade-off on the field, where the player already
  looks. There, the enemies glow with the power the player took. Diablo II shows a curse on its
  target, not in a menu.
- **Give each new feel or system change a switch in the tuning panel,** so a player who finds the
  game worse can turn them off one by one and say which one did it.

## Test browsers are silent

A test browser plays through the machine's speakers, and neither engine's mute
covers it. Every e2e case takes a shared fixture whose init script puts each
`AudioContext` destination behind a zero gain, and every probe, bench or
screenshot browser adds the same script. Spy on playback by wrapping that stub.

## Platform SDKs behind one adapter

Ads, storage, leaderboards and analytics differ per portal (Poki, CrazyGames,
YouTube Playables, itch). The game talks to one interface in `platform/`; each
portal is one implementation; a no-op implementation is the default, so the
game runs locally and in tests with no SDK at all.

```ts
// platform/index.ts
export interface Platform {
  gameplayStart(): void;
  gameplayStop(): void;
  rewardedAd(): Promise<boolean>;
  save(key: string, value: string): Promise<void>;
}
export const platform: Platform = pickPlatform(); // poki | crazygames | noop
```

Nothing outside `platform/` imports a portal SDK.

A portal's own rules decide much of the build: download size, key bindings,
legibility at DPR 1, ad timing, progress save and covers. Load the portal's
publishing skill before writing the game, not just before submitting it. For
CrazyGames, that is `crazygames-publishing`. Each rule there becomes a test.

Art follows the same order. Make concepts and orthographic sheets with `concept-art`, which
keeps AI images out of the build. Check every model against its sheet with `model-qa` before
calling it done.

## The legitimate big files

- **Generated level tables** - a script writes a year of daily levels into one
  file. It carries a `// Generated by …` header and is exempt (category A).
- **Hand-tuned level data** with no logic is data (category B); prefer `.json`.
- **A physics step** that measurably slows when split may take an E waiver,
  naming its benchmark. Measure first.

The big scene and the big simulation class are not on this list: they are the
god objects the size rule exists to catch. `architecture` walks both splits.

## Health

`health` runs TypeScript, import cycles (which catch `sim/` and `render/`
importing each other), lint, unused code, duplication, sizes, secrets and
dependency scans. Check by hand, or have a reviewer check, that nothing in
`sim/` imports `phaser`, `three`, `scenes/` or `render/`:

```bash
grep -rnE "from ['\"](phaser|three)|from ['\"].*/(scenes|render)(/|['\"])" src/game/sim
```
