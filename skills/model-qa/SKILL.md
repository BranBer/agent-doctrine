---
name: model-qa
description: Use when building or checking a 3D model (three.js, glTF or GLB, Blender, image-to-3D output) against its concept art or an orthographic turnaround or blueprint sheet - matching proportions, silhouettes and colours, deciding whether a model is done, or iterating a model until it matches its concept.
---

# Model QA

Check a model against its orthographic concept sheet the way blueprint modellers work: the same
views, at one shared scale, measured. The checks have three layers:

- **Scores catch shape and paint.**
- **A calibration shows which faults the scores can see on this asset.**
- **A hero render, read by eye, catches the rest.**

The sheet comes from `concept-art`.

## Tools

The tools live in `~/.claude/skills/model-qa/scripts`, with their own dependencies. Never install
them into a project. Run them from the project root.

| Step | Command |
|---|---|
| Export a code-built three.js model | `node <scripts>/glb.mjs <module> <out.glb>` |
| Render side, front, back, top and hero, and count triangles | `node <scripts>/views.mjs <model.glb> <dir> [--hero x,y,z]` |
| Find the views on a sheet | `python -I <scripts>/compare.py components <sheet.png>` |
| Check the sheet against itself | `python -I <scripts>/compare.py check <concept.json>` |
| Score and gate | `python -I <scripts>/compare.py <concept.json> <renders> <out> [--outline N] [--gate side,front] [--bar bar.json]` |
| Calibrate the bar for this asset | `node <scripts>/calibrate.mjs <module> <concept.json> <out> [--gate side,front,top]` |
| Check symmetry about X = 0 | `node <scripts>/symmetry.mjs <model.glb> <dir>` |

**The model's frame** is glTF's: +Y up, front toward +Z, units in metres.

- The side view shows the model's left side, front pointing left.
- The top view also has the front pointing left.

## The loop

1. **Check the sheet before you model.**
   - Run `components`, then write `art/views/<asset>.json` with one rectangle per view. Leave about
     8 px of bare background around each.
   - Run `check`. It names any view more than 3% from the median: that's the sheet drifting, so
     leave the view out of `--gate`.
   - It exits 1 only when side and front disagree on height by more than 5%. Then get a new sheet.
   - **Master views:** side for length and height, front for width. When views disagree about one
     part, follow the master view for that dimension and note the choice.
2. **Measure, then build.**
   - Measure from the sheet, never by eye. Gridded enlargements and row or column scans of the view
     masks give wheel centres, the ground line, rooflines and part extents.
   - Keep the numbers in sheet pixels in the code, with one pixel-to-metre mapping per view.
   - Anchor the scale on a large part, never a small one at an extreme. Rear bolt heads 3 px short
     read as +1.8% height everywhere.
3. **Mind the ink.**
   - The concept's mask includes its outline. Find the line's width by profiling lightness across a
     straight edge.
   - If the model carries its own ink shell, score with `--outline 0`.
   - If not, score with `--outline <width>` and pull every measured edge in by that width. On the
     Sweeper, skipping this left the model 2 px oversize all round and cost 0.02 IoU.
   - An ink shell doubles the triangle count. The project's budget must say whether it includes the
     shell.
4. **Build what the game needs.**
   - Name the parts that can be damaged or detached, with unique names: one name per side.
   - Take colours from the palette tokens and stay within the triangle budget.
   - **Build mirrored parts from one function.** The sheet shows only the left side, so nothing can
     check the right side.
   - **Centre the middle parts on X = 0 exactly.** Take a centred part's width as one half-width
     from the master view's centre line, never as two edges read off a view that may be drawn
     off-centre.
5. **Score, read the sheet, fix.**
   - In the overlay, red is concept only and blue is model only. Fix the largest patch first.
   - One loop takes about 2 s.
6. **Check the symmetry** of a model that should be bilaterally symmetric.
   - **Why it exists:** the scores compare whole silhouettes, so a small part off the centre line
     passes them. The hatchback's roof rack sat 56 mm to one side, its rails measured off a top view
     the sheet drew off-centre, and every score passed. The user saw it in the first play.
   - `symmetry` mirrors the front and top renders about X = 0 and scores the mirrored silhouette's
     IoU. It reads every named part's box: a `*-left` / `*-right` or `*_L` / `*_R` part is paired
     with its twin, and every other part must be centred.
   - **It passes** when both IoUs are at least 0.995, every unpaired part is centred within 5 mm of
     X = 0, and every pair mirrors within 5 mm on each face of its box.
   - **Declare a part that is one-sided by design** (an exhaust, an antenna) with
     `userData.oneSided = true`, which glTF carries as the node's extras. The check renders without
     it, lists it, and judges everything else.
   - It renders without antialiasing: multisampling's sample pattern isn't mirror-symmetric, and it
     puts a symmetric model's two edges a pixel apart.
7. **Calibrate once the default bar passes.** Then gate every later round with `--bar` (see below).
8. **It is done when** the calibrated bar passes, `symmetry` passes on a symmetric model, and the
   hero review lists nothing you'd still fix.

## What the scores can and cannot see

| Column | Means | Blind to |
|---|---|---|
| `iou`, `w`, `h`, `p95` | Silhouette overlap, size error, and the 95th-percentile outline distance. p95 is the most sensitive to small parts. | Anything inside the silhouette |
| `hull` | The concept against its own convex hull: what a featureless blob scores | — |
| `cmiss` | The share of the overlap whose paint differs by more than ΔE 25. It catches missing or wrong panels, doors and windows. | Dark parts against dark backgrounds. Its baseline differs by view, because shading and detail differ. |

**Rely on other views where IoU is within about 0.03 of `hull`.** That's typical of
near-rectangular top views, where IoU can't tell right from wrong.

**The default bar** (IoU ≥ 0.94, sizes within 3%, p95 within 3%) catches gross faults only. On the
hatchback:

- roof 15% low: caught;
- 10% too narrow: caught, but only from front and top;
- ram removed: caught;
- 11 of 53 scripted faults in all.

**Calibrate for this asset.** `calibrate.mjs` breaks the model: every named part 15% smaller,
every named part removed, and the whole model 10% long, narrow and low. It scores every fault and
writes `bar.json`, a per-view bar set just inside the good model's own numbers.

- On the hatchback it caught 26 of 53.
- **Gate every later round with `--bar bar.json`.** Any regression of that size then fails.
- **Read its "no view sees" list.** Those faults go to the hero review, or are prevented by
  construction. On the hatchback the list was:
  - right-side parts, which `symmetry` now holds to their left twins;
  - the tailgate, visible only in the back view, which isn't gated;
  - dark flares over dark tyres;
  - 15% shrinks of small parts.

## The hero review

Put `hero.png` beside the hero concept. Use `--hero x,y,z` to match the concept's angle. List
concrete differences: missing parts, wrong shapes, the outline, treads, bolts, and everything in
the "no view sees" list. Never give a score.

- **Why it's needed:** silhouettes scoring 0.96 sat alongside a missing windshield, missing
  headlights and the missing ink outline.
- **Where the hero and the sheet disagree on geometry, the sheet wins.** The hero guides style
  only. An open-frame push-bar read off the hero cost 0.02 IoU, and the sheet showed a solid
  plate.

## three.js pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A back-face outline shell comes back from GLB as solid ink | glTF has no back-face-only material | Reverse the shell's triangle winding and draw it front-side |
| Glass and patches hidden, everything 3–4 px too big | ExtrudeGeometry's bevel grows the outline by `bevelSize` | `bevelOffset: -bevelSize` |
| Panels sink into the body after a taper | Moving the vertices of one large cap face tilts the whole face | Clip the polygon at the taper line and taper only the upper piece |
| Tyres notched in the side view | Too few, too deep tread blocks | About 20 shallow blocks |

## Keep the record

Keep these with the asset: `concept.json`, the sheet, `bar.json`, the last `report.json` and the
hero comparison. Note each iteration's main change and its numbers, in a commit message or a log
file.
