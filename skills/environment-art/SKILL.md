---
name: environment-art
description: Use when building, dressing, polishing or reviewing a game level or environment against concept art - floors, walls, ruins, gates, props, set dressing, light and backdrop - or when an environment looks generated, tiled, uniform, flat, noisy, distracting, empty or lazy; when placing damage, decay, wear, repairs or overgrowth; when a place needs to look built by people and aged by time; or when setting up builder and critic agents for level art.
---

# Environment art

A place looks hand-made when three things hold. It was built big to small on a layout that has
been played. Every mark of age has a cause, and the cause decides where it sits. Contrast and
detail are spent only where the player's eye is not needed for the fight.

A capable agent already knows most of this and still ships the opposite: it builds before it has
studied the reference, tunes until "it shows" where it should tune until "it matches", scatters
by random number, and grades its own work. So this skill is a sequence of gates, each with
something written down or measured that the next step needs. Do them in order.

Background and sources: `reports/Game environment art and ruins.md` in the profit repo.

## The gates

| # | Gate | What exists when it is passed |
|---|---|---|
| 1 | **Reference breakdown** | `templates/reference-breakdown.md` filled in, its measured fields from `envcheck.py measure`, its "how it is achieved" fields from enlarged crops of each element |
| 2 | **History** | `templates/history.md`: what the place was, how it was built, three to five events in order with a location each, who uses it now. The person approves it: it is lore |
| 3 | **Zones** | The plan divided into play floor, floor edge, rim and backdrop, each with its allowance (below) |
| 4 | **One corner first** | One wall section with its floor taken to final quality, timed, compared with the target by the critic. Nothing else is dressed until it passes |
| 5 | **Defect plan** | `templates/defect-plan.md`: every defect with type, cause, anchor, size tier and carrier, laid in time order. See `wear.md` |
| 6 | **Passes, big to small** | Structure, then event damage, then slow wear, then deposits, repairs and present use. A capture from the game camera after each |
| 7 | **Critic's verdict** | A fresh-context critic (`agents/environment-critic.md`) has ranked the deviations on clean captures; one to three are fixed a round; a round that regresses is reverted |
| 8 | **Side by side** | Target and game from the game camera, deviations listed, each closed or accepted by the person |

A gate with nothing written down has not been passed. A check that did not run is reported as not run.

## Study how, not only what

Crop the reference to one element at a time and enlarge it before building that element. Write
down how the picture achieves it: what carries the form (line, relief, value, colour), how
large the shapes are, where the detail stops. A floor of the same pale stone with thin joints
and a raised edge is a different build from a floor of different-coloured stones, and both are
"flagstones".

Measure what can be measured, on the reference and on the game, with the same tool:

```bash
python -I ~/.claude/skills/environment-art/scripts/envcheck.py measure \
  "concept floor=art/concept/mood.png:70,560,330,740" "game floor=shots/wave2.png:300,430,520,560"
python -I ~/.claude/skills/environment-art/scripts/envcheck.py pair art/concept/mood.png shots/wave2.png out/pair.png
python -I ~/.claude/skills/environment-art/scripts/envcheck.py grid shots/wave2.png out/grid.png   # cells A1..F4 for locating notes
```

The numbers are evidence. A low number needs an explanation, never noise added to move it.

**When something does not show, find out why before raising its contrast.** Raised contrast is
how a quiet floor becomes a checkerboard.

## The four zones

Every studio that publishes on readability ranks the environment last, after the interface,
effects and characters. From a high camera that becomes four zones:

| Zone | Allowance |
|---|---|
| **Play floor** | One tone. A narrow light-to-dark spread. Large soft shapes. Nothing above ankle height. Wear only as quiet marks: a worn route, sand in joints, a repair in a close value |
| **Floor edge** | The one firm step in value or tone: it marks where play ends |
| **Rim and walls** | The detail, the saturated accents, the story props, the loud damage (a breach, a rubble fan, soot) |
| **Backdrop** | Free for spectacle, but dimmed, desaturated or hazed |

Pick one separation and hold it: ground lighter than the actors, or darker. On a pale ground the
actors carry the dark, saturated values, and the floor needs a ceiling as well, so a telegraph
or a flash still has room above it. Extremes of value and the telegraph's hue are kept for play.

Tests, all from the game camera at game zoom with a fight on screen:

- **Greyscale:** still reads at a glance.
- **Blur:** greyscale, blur, see where the eye lands. It lands on the fight or the test fails.
- **Worst case:** most enemies, largest telegraphs, each actor on each kind of ground.
- **Per zone:** floor spread narrower than rim spread; floor line and edge density below the rim's.
- **Marks on the ground:** a pool, a ring or a telegraph lies unbroken across every kerb, joint and
  flag. Floor relief stays under the plane those marks are drawn on: a kerb standing 6 cm proud cut
  every pool that crossed it into stripes.

## Causes, not scatter

Every defect names its cause and its anchor, or it is moved or removed. `wear.md` has the
taxonomy: for each kind of damage, what makes it in reality, where it therefore belongs, and how
it reads at small size. The short form:

- Chips and knocked corners sit on free edges and corners, on the side traffic or impact came from.
- A crack runs from an edge or joint to another edge, joint or crack.
- A stain has its source at its top; a star crack has a fitting or a strike at its centre.
- Wear follows the routes people walked and peaks at pinch points. Repairs sit on the peaks.
- Sand and dust lie on horizontals, in corners, joints and sockets.
- Fallen stone lies under the gap it fell from, largest pieces nearest.
- Loss alone reads as demolition. Age needs build-up and at least one repair.
- Keep straight and regular what the builders made. Bend only what time did.
- Layer in time order: built whole, event damage, slow wear, deposits, repairs, present use.
- A dry, sunny place has no moss, long streaks or black crust. Sand takes water's place.

Generation is allowed for base courses and for jitter inside a placed feature. Features
themselves are placed from a written list. Seed everything, so a reviewed picture stays true.
Scatter clumps that were composed by hand, never single props, and vary both the size of the
clumps and the gaps between them.

## What says "generated"

Even scatter. One frequency of noise. Stones all of one size. Chips of one shape. Cracks of one
length, or crossing separate stones unchanged. The same damage from wall foot to wall top. Dirt in
every recess. A stain in the middle of an empty face. Rubble of one size. Mirrored damage. Every
stone a different colour. Lines of one weight everywhere. Glow, fog or bloom standing in for form.
Cells all of one shape (a honeycomb). Joints meeting in fans. Splinters. One recipe repeated at even gaps.

## Builder and critic

The builder keeps its context and does not grade its own milestone. The critic starts fresh,
gets the target, the breakdown and clean captures, and cannot edit. Role files to copy into a
project's `.claude/agents/`: `agents/environment-builder.md` and `agents/environment-critic.md`.

- The critic scores clean captures only. Marks drawn on an image inflate a vision model's score.
- It answers "is this round closer than the last" as well as scoring: pairwise comparison tracks
  a person's ranking far better than an absolute score.
- It returns ranked deviations, each with a grid cell and one line of evidence, split into
  blocking mismatches and optional polish. The builder takes the top one to three.
- Stop after five rounds on one milestone and take what is left to the person.

Fresh eyes are the point. Two unguided agents shown a yard its builder thought finished each
named faults the builder had missed: joints too dark, a wall a third as thick as the target's, a
surround the same value as the floor, a centrepiece too large.

## In the browser

`browser.md` lists what fits a web budget in Three.js and what each costs. In short: colour from
one small shared palette, edges and chips as real geometry under flat shading, shade in joints
and at wall feet by vertex colour or one bake, a few alpha-tested decals on one atlas, props
instanced, the static sun shadow baked. Nothing tiles, so nothing repeats.

Generated models (`model-gen`) suit irregular lumps: boulders, rubble, broken drums, pots. Walls,
steps and paving stay code-built, because generators blunt the crisp edges the style needs. A
generated prop is cut to its triangle target and repainted from the shared palette before it
stands beside code-built stone.

## Quick reference

| Symptom | Likely cause | Go to |
|---|---|---|
| "Too distracting" | Contrast or detail on the play floor | The four zones |
| "Looks generated" | Scatter with no cause; one size of everything | Causes, not scatter; `wear.md` |
| "Flat" | No relief, no shade at joints or wall feet, no shadow | `browser.md` |
| "Low fidelity to the concept" | Built from the idea of the thing, not the picture | Study how, not only what |
| "Empty" | Rim undressed, no present-use trace, backdrop missing | The four zones; history |
| Looks right to the builder, wrong to the person | Self-graded | Builder and critic |
