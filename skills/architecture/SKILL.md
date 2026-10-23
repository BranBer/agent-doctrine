---
name: architecture
description: How to decompose code under the doctrine - find the seam before splitting, the five-step split test, then where each piece goes - private to its unit (the unit becomes a folder) or general purpose (a subject unit in utils). Covers a registry instead of a switch, a pure core inside an effectful shell, entry points per language, promotion to utils on the second user, and when a size waiver is legitimate. Use when a file is over its limit, when splitting or extracting code, or when deciding where code belongs.
---

# Architecture

How to take code apart well. `doctrine` sets the limits and the folder model;
this is the procedure for meeting them without making things worse. The
language packs show the templates for each stack.

A split is good when each piece has one reason to change, nothing imports past
an entry point, and no two pieces import each other. A split that only moves
lines around - two halves that call into each other - is worse than the file it
came from.

## The procedure

1. **Find the seams** with the split test below.
2. **Place each piece** - private to its unit, or a subject in `utils/`.
3. **Give the unit an entry** - the one file outsiders import.
4. **Check the result** against `doctrine`'s Reviewing table.

If step 1 finds no seam at all, the file may be one of the legitimate long
ones (see "Waivers"). That is rare; look harder first.

## The split test

Walk these in order. Each one that applies is a seam.

### 1. Different reasons to change

Group the code by *who* or *what* would ask for a change to it. Parts that
change for different reasons belong in different files.

**Before** - a game scene, 553 code lines, with input, camera, effects, sound
cues and the end-of-run flow in one class:

```
scenes/Play.ts      create, update, readInput, tick, juice, juiceView, sfx,
                    hazardSounds, crusherSounds, fitCamera, follow, shakePx,
                    bank, onWreck, onFinish, showResults, skip, toLevels …
```

**After** - five reasons to change, five files; the scene keeps the lifecycle
and delegates:

```
scenes/play/
  index.ts          the Play scene: create, update, the run lifecycle
  sounds.ts         sfx, hazardSounds, crusherSounds   (speaks SimEvent: private)
  effects.ts        juice, juiceView                    (speaks SimEvent: private)
  results.ts        bank, onWreck, onFinish, showResults
systems/camera.ts   fitCamera, follow, shake            (takes a pose and a delta: general)
```

The camera follow knows nothing about this scene - it takes a position and a
time step - so it goes to a shared purpose folder where the next scene can use
it. The sound cues read this scene's events, so they stay private.

### 2. Pure core, effectful shell

Move decisions into plain functions that take values and return values. What
is left - reading input, touching the framework, writing to the network or the
screen - is a thin shell that calls them.

```ts
// before: the decision is buried in the handler
router.post('/orders', async (req, res) => {
  /* 60 lines deciding price, discount and tax, then saving and responding */
});

// after: the decision is a plain function; the route is the shell
router.post('/orders', async (req, res) => {
  const quote = priceOrder(parseOrder(req.body), await rates.current());
  res.json(await orders.save(quote));
});
```

`priceOrder` is now testable without a server, and the route fits on a screen.

### 3. Data apart from code

A table the rest of the code reads - levels, prices, copy, a lookup - is data.
Move it out, ideally to `.json`, or to a data-only module. A data-only file is
exempt from the size limit; the code that reads it is not.

### 4. Variants behind a registry

A `switch` over a closed set of kinds becomes a registry. The compiler still
checks that every kind is handled, and each handler gets its own file.

```ts
// before: every new hazard edits this function
function applyHazard(h: Hazard, world: World) {
  switch (h.kind) {
    case 'crusher': /* 40 lines */
    case 'ball':    /* 35 lines */
    case 'spikes':  /* 30 lines */
  }
}

// after: hazards/index.ts
import { crusher } from './crusher';
import { ball } from './ball';
import { spikes } from './spikes';

const HANDLERS: Record<Hazard['kind'], HazardHandler> = { crusher, ball, spikes };
export const applyHazard = (h: Hazard, world: World) => HANDLERS[h.kind](h, world);
```

`Record<Hazard['kind'], …>` fails to compile if a kind is missing - the
exhaustiveness the switch gave, kept. In Python the same shape is a dict of
callables keyed by an `Enum` or a `Literal`, checked by pyright.

### 5. A sub-concept with its own name

Look for something you could name and test on its own that is currently
inline: a few fields and the functions that always travel with them.

**Before** - a simulation class, 567 code lines, whose private methods fall
into families:

```
sim/sim.ts      step, grounded, truckPose
                add, remove, place, spawnDebris, spawnScrap, addPart, spawnPanel, spawnHubcap
                burst, breakCar, breakWall, shatter, releaseBlocks
                contact, recordImpact, recordBodyHit, applyDamage, hitSpeed
                forces (crusher and ball motion), aimAt, aimLead, trackAir, drive
```

**After** - each family is a named concept with its own file, and the class
that remains orchestrates one step:

```
sim/world/
  index.ts        the Sim class: step, grounded, truckPose - and nothing else
  spawning.ts     placing and removing entities, debris, scrap, parts
  destruction.ts  bursts, breaking cars and walls, shattering, releasing blocks
  contacts.ts     contact handling, impacts, damage
  hazards.ts      hazard forces (crusher, ball)
  steering.ts     drive, aim, air tracking
```

The pieces take the world state they act on as a parameter rather than
reaching into the class, so none of them imports `index.ts` - no cycle.

## Placing each piece

For every piece that comes out, ask one question: **does it speak the unit's
own types and vocabulary?**

| Answer | It goes | Example |
|---|---|---|
| Yes - it reads the unit's events, types or state | Inside the unit's folder, private | `scenes/play/sounds.ts` reads this scene's `SimEvent`s |
| No - it takes plain values and returns plain values | A subject unit in `utils/` (or a shared purpose folder such as `systems/`) | `utils/dates.ts`, `utils/money/`, `systems/camera.ts` |

**Promotion.** A private piece that a second unit starts needing moves to
`utils/` at that moment - not before. Copying it into the second unit instead
is two copies of one fact.

**`utils/` subjects.** Name a util for its subject, never for its role:
`utils/money/` yes, `utils/helpers.ts` no. If a new util fits no existing
subject, it starts a new one.

## Entry points

The entry is the unit's public surface. Outsiders import the entry; files
inside the unit import each other directly.

| Language | Entry | Outsiders write |
|---|---|---|
| TypeScript / JavaScript | `index.ts` re-exporting the public names | `import { Sim } from '@/sim/world'` |
| Python | `__init__.py` with `__all__` listing the public names | `from app.sim.world import Sim` |

An entry that re-exports everything behind it is not a contract, just a
second copy of the folder listing. Export what callers use.

## Waivers

Some files are long for a reason no split fixes - `doctrine` lists the
categories. Generated files, data tables and modules-less languages need no
waiver. The other two do, as one line at the top of the file:

| Category | When | Example |
|---|---|---|
| **D1** mutual recursion | Splitting would make the parts import each other | a recursive-descent parser whose `parseExpr`, `parseTerm` and `parseFactor` call one another |
| **D2** shared private state | One algorithm's steps share mutable state that should not be exported | a tokenizer's cursor, buffer and position table |
| **D3** spec transcription | The code is checked line for line against a published spec | a hash or colour-space conversion copied from its standard |
| **E** measured hot path | A split measurably slows something that runs every frame | a physics step, with the benchmark that showed it |

```ts
// doctrine-allow size: D1 - recursive descent; productions are mutually recursive
```

The waiver names its category; an E waiver names its benchmark. **800 lines is
the ceiling** even with a waiver. React components never take one.

## Checking the result

- Every file within its limit, or carrying a valid waiver.
- Nothing imports past an entry.
- No two files import each other, directly or around a loop.
- Nothing in `utils/` imports from a purpose folder.
- No folder holding a single file; nothing called `misc`, `helpers` or `common`.

`health` runs the import-cycle check and lists files by size.
