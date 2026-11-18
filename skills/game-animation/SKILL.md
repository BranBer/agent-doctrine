---
name: game-animation
description: Use when adding, sourcing, retargeting or playing character animation in a web game (three.js, glTF) - attack animations, combo chains, a combat stance, transitions between actions, playing a pack's clips on a generated or differently named rig, attaching a weapon to a hand - or when a character snaps back to idle after an attack, feels like a clip playing instead of fighting, has stretched or twisted limbs after sharing clips, or an attack reads as sluggish or weightless.
---

# Game animation

Combat reads as a character fighting when each attack is a short chain of timed beats the simulation
owns, and every channel (pose, sound, trail, hit-stop) shows the same beat at the same instant. It reads
as a clip playing when a long animation runs to its end and blends home to idle.

**Author a move, not a clip.** A move is a few timing points: commit, hit (or release), cancel, end.
The clip is cut and re-timed to serve them. A clip with no hit frame, no early exit and no stance to
return to cannot be fixed by blending. Sound follows the same sheet: use `action-sync`.

## The move sheet

One record per attack or ability. The simulation owns the times; the renderer plays to them.

| Field | Meaning |
|---|---|
| `hit` | Sim ticks from commit to the blow landing or the projectile spawning. 0 when the sim acts on the press. |
| `cancel` | Sim ticks from commit until the next attack, a step or a dodge may cut in. The recovery after it only plays if the player stops. Start at 200 to 300 ms after the hit, or about half the clip, and tune in play. |
| `clip`, and the clip's own hit time | Which clip, and the second in it that shows contact or release: for a swing, where the weapon hand moves fastest; for a bow or a cast, where the drawing or casting hand does, checked by eye on the sheet page. |
| `chain` | The next move when the player attacks again inside the rhythm window. |

`templates/moves.ts` is the smallest version: a sim that hits on the press, so each clip is entered two
frames before its contact pose and left at its cancel point. Its wind-up is never shown.

## What makes it read as fighting

Marked **[P]** practitioner convention, **[I]** our inference. None is measured for a top-down game.

- **The strike is tiny**: 50 to 170 ms. Weight comes from holding the anticipation and follow-through
  poses, never from a longer swing. [P]
- **Answer the press on the next frame.** 50 to 100 ms press-to-motion is good; 170 to 200 is sluggish.
  Player attacks get little anticipation; enemy attacks get a long one, because it is the tell. [P]
- **Give control back at a marked frame.** Follow-through that movement cannot cancel is the usual
  cause of "sluggish". Dodge and block cancel almost anything; attacks cancel after the hit. [P]
- **Repeated attacks advance a chain** of two or three swings that alternate direction, with a heavier
  finisher. Never restart one clip from frame 0. [P]
- **Never pass through relaxed idle mid-fight.** Chain tails end in a stance with the weapon up. A
  separate relaxed set is a between-fights nicety; no source showed top-down games investing in one. [I]
- **Enter fast, leave soft**: a 0 to 50 ms blend in, 100 to 200 ms out. The pop people notice is the
  return to idle. [P]
- **Attacks play in place; code moves the body.** A lunge is a sim velocity, not root motion. [P]
- **Hit-stop is per actor**, never a world freeze, and not on every light swing. See `combat-feel`.
- **At 45 pixels** the player reads the weapon, its trail arc, the body's lean, the facing and the
  timing. A swing with no weapon in the hand is unreadable: attach one before judging a move. [I]

## Where clips come from

Read the licence before planning around a source, and check its automation terms.

| Source | Terms | Notes |
|---|---|---|
| KayKit character packs | CC0 | 76 clips on a chibi rig: four one-handed swings, block, crossbow, casts, hits, deaths, dodges. No bow. Proven on generated chibi rigs with the template below. |
| Quaternius Universal Animation Library 1 and 2 | CC0 | Sword combos split into hits and recoveries. Realistic proportions; not yet tried here. |
| Mixamo | Free, but no scripted download and no stand-alone redistribution | A person downloads by hand. |
| A generator's presets (Tripo) | Paid per clip | Long and not combat-shaped: look before wiring. See `model-gen`. |
| Authored in code, below | Ours | For the move no source has: a bow's draw, a reload drill, a carry. |

## Playing one rig's clips on another

Sharing clips by bone name only works between rigs with the same rest pose and bone lengths. Otherwise
use `templates/retarget.ts` (three.js, runs at load or in a build step, tested by `retarget.test.ts`):

```ts
const matched = plan(source.scene, target.scene, KAYKIT_TO_MIXAMO, Math.PI / 2); // yaw: source facing onto target facing
const clips = retargetClips(matched, source.animations);                         // rotations per mapped bone, hips position
const at = socket(matched, 'handslotr');                                         // where a carried prop sits on the target
```

- It copies each bone's turn away from rest **in world space**, so local axes, bone roll and A-pose
  against T-pose stop mattering. Unmapped bones keep their rest pose.
- The map lists parents before children, with names as GLTFLoader gives them (it strips `: . [ ] /`,
  so `mixamorig:Hips` is `mixamorigHips` and `upperarm.l` is `upperarml`).
- **A bone needs a mapped child to be aligned.** Without a finger mapped under each hand, the hand kept
  its own rest angle and the sword pointed 30 degrees low.
- **Size carried props by the skeleton's spread, not hip height.** Chibi hips ride low: by hip height
  the shield came out twice too big.
- Pin the hips' sideways travel when the sim moves the character.
- Look before trusting it: copy `templates/retarget-sheet.html` into the project's dev-only scripts.
  It draws the source above the target frame by frame, hangs props with `&carry=`, shows a move's
  window with `Clip@from-to`, and `&mark=<hand bone>` prints when that bone moves fastest, which is the
  swing's contact time for the move sheet.

## The move no pack has

"No clip for it" is where the work starts, not a gap to report or a reason to pay a generator.
Say where each hand is at each beat and bake that to a clip with `templates/pose.ts` (three.js, runs
at load, tested by `pose.test.ts`). An archer's draw and loose built this way was judged "the
smoothest attack animation in the game".

```ts
const hand = gripOf(slot);                                 // at rest: which way the hand points, its palm, its grip
const clip = bake('Bow_Shot', BEATS.drawn, bones, (t) => {
  turn(chest, yaw(-turned(t)));                            // the torso first: it carries the shoulders
  hold(upper, lower, hand, gripAt(t), points, palm, elbowToward);
});
```

- **Name the beats in seconds, and write each hand's path between them.** For a sim that acts on
  the press, the clip opens at the contact pose, or two frames before it when the blow needs a
  sweep to read, and ends on the pose held between attacks, so a repeat needs no blend.
- **Two hands on one prop:** pose the hand that carries it, then put the other hand's grip on a
  point of the prop read in the world for that frame.
- **Keep targets in reach.** Measure shoulder to wrist at rest first. An arm reaches toward a target
  it cannot touch, and whatever it holds lands short of where the other hand expects it.
- **Arms over moving legs is two actions with no bone in common.** Cut each gait to its hips and
  legs (`Legs_<gait>`) and play the arms' clip above it. Two actions on one bone are averaged, not
  layered. Carry the stride's time across when a gait and its legs-only twin swap. A one-shot left
  clamped on its last frame is the held pose; a pose held with no one-shot can be one merged clip.
- **A prop that bends follows the skeleton in code,** each frame after the mixer: a bowstring to the
  hand that draws it. Drive its state from the clip with a track on an empty node inside the prop
  (`BowDraw.position`), so it fades with the action. Retargeting drops such tracks: carry them over.
- **A hand that carries something long gets its own carry pose** under every other clip. Strip that
  arm's tracks from the pack's clips, and its hand slot's: packs turn the slot from clip to clip.
- **Pose for the game's camera.** From above, an upright bow is seen end-on and a big head hides
  the chest. Lay the prop where the camera shows it, then check what it now passes through.
- A retargeted arms-only clip comes back with legs standing at rest. Strip them.
- **A sweep the model hides reads through its streak.** A wide hat hid a whole wand arc from above;
  the strip its tip had just swept, drawn over everything and fading (templates/trail.ts), made it read
  from every facing. The sheet page draws it with &trail=<hex colour>.
- **A launch in mid-gesture needs no change to the rules.** When the sim sends a projectile on the
  press, give the gesture a fast first half and draw the projectile only once the gesture reaches its
  launch point. At 70 ms and 22 m/s the bolt is then about where the tip is.
- **Attacks in a row are strokes of one gesture.** Each clip opens on the pose the last one ended
  on and goes the way the arm can go from there: after a sweep that leaves the arm out to the
  side, the next stroke comes down and forward. The last stroke ends pointed at the target, which
  is also the pose the first opens on, so the chain resets with no blend. A third stroke that
  swung the wrong way was corrected on the player's first look.

## three.js traps

- No animation events, layers or bone masks. Timed cues come from the sim or from comparing
  `action.time` with markers; an upper-body attack over running legs means two clips with disjoint
  bone tracks.
- A fade to zero weight disables the action. `reset()` does not restore weight or time scale.
  `makeClipAdditive` rewrites the clip in place. A track whose node name is not found only warns.
- Start a move mid-clip by setting `action.time` after `reset()`.

## Checking

- **Before reporting any animation or carried prop, render the move sheet and read it.** Copy
  `templates/move-sheet.html` into the project's dev-only scripts, point its two loader lines at the
  project's own rigs, and run it with `templates/sheet.mjs`. It draws the game's rig frame by frame,
  from the game camera facing three ways and square on, and counts the points of the prop that are
  inside the body or under the ground, drawing them red. Under the ground means more than 3 cm
  below the floor; a prop meant to rest on it will show a few percent, and the report says so.
  - Run it for every clip the character plays, not only the new one, and on every model set.
    `templates/qa-moves.mjs` does that in one command for a table of roles, with an allowance per
    carried thing, and fails when a clip is over it. Its first run found five clipping pack clips
    nobody had looked at.
  - Report the share per clip. A sheet that was not rendered is reported as not rendered.
  - `templates/moves-gate.mjs` is a Claude Code Stop hook that makes the run hard to forget: when a
    file it watches is newer than the stamp `qa-moves.mjs` leaves, it sends Claude back once to run
    the check, and tells the user "NOT RUN" if the turn ends without it. List the project's own
    animation files in it, and register it under `hooks.Stop` in the project's
    `.claude/settings.json` only with the user's yes.
  - Stills at the game's size are not this check. A bow that hung through the body and never drew
    passed four of them, and the player found both faults in seconds.
- **List every state and action the sim has before calling a character animated,** and give each a
  clip or a written reason for none. Read the list off the sim's types, not off the events the
  renderer already handles. Held states (a raised guard, a channel, an aim, a stun, a pin) raise no
  event, so animation wired to events misses them: a tank shipped two rounds with a guard that was
  only a floor marker, in a pack that had four block clips.
- A held pose over moving legs is one merged clip: the walk's hip and leg tracks plus the pose's
  other tracks.
- Unit-test the retarget on a two-bone chain; the template's test shows how.
- The sheet shows poses. Judge motion and feel by playing: stepping a game's frames by hand
  under a headless browser to film a swing did not work in three tries.
- Not built yet: a relaxed set, a sim-side wind-up.

Background and sources: `reports/Combat animation and sound sync.md` in the profit repo.
