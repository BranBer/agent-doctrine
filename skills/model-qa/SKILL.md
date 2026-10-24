---
name: model-qa
description: Use when building or checking a 3D model (three.js, glTF or GLB, Blender, image-to-3D output) against its concept art or an orthographic turnaround or blueprint sheet - matching proportions, silhouettes and colours, deciding whether a model is done, or iterating a model until it matches its concept.
---

# Model QA

Check a model against its orthographic concept sheet the way blueprint modellers work: the same
views, at one shared scale, measured.

- **Scores catch shape.** They don't catch style.
- **A hero render, read by eye, catches style.** Both are needed.

The sheet comes from `concept-art`.

## Tools

The tools live in `~/.claude/skills/model-qa/scripts`, with their own dependencies. Never
install them into a project. Run them from the project root.

| Step | Command |
|---|---|
| Export a code-built three.js model | `node <scripts>/glb.mjs <module> <out.glb> [--args json]` |
| Render the side, front, back and top views, plus a hero | `node <scripts>/views.mjs <model.glb> <dir>` (it also prints the triangle count) |
| Find the views on a sheet | `python -I <scripts>/compare.py components <sheet.png>` |
| Check the sheet against itself | `python -I <scripts>/compare.py check <concept.json>` |
| Score | `python -I <scripts>/compare.py <concept.json> <renders> <out> [--outline N] [--gate side,front]` |

**The model's frame** is glTF's: +Y up, front toward +Z, units in metres.

- The side view shows the model's left side, front pointing left.
- The top view also has the front pointing left.

## The loop

1. **Check the sheet before you model.**
   - Run `components`, then write `art/views/<asset>.json` with one rectangle per view. Leave
     about 8 px of bare background around each.
   - Run `check`. A view more than 3% from the median is the sheet drifting, not your model.
     Leave it out of `--gate`, and take length, height and width from side and front.
   - If side and front disagree by more than 5%, get a new sheet.
2. **Measure, then build.**
   - Measure from the sheet, never by eye. A gridded enlargement of each view, or a column scan
     of its mask, gives the key coordinates: wheel centres and radius, the ground line, rooflines,
     part extents.
   - Keep those numbers in sheet pixels in the model's code, with one pixel-to-metre mapping per
     view. Then every number can be checked against the sheet it came from.
   - State the scale anchor, for example "tyre 128 px = 0.89 m".
3. **Build what the game needs.**
   - Name the parts that can be damaged or detached.
   - Take colours from the palette tokens.
   - Stay within the project's triangle budget.
4. **Render, score, read the sheet, fix.**
   - In the overlay, red is concept only and blue is model only. Fix the largest patch first,
     then score again.
   - If the model has no ink outline and the concept does, pass `--outline` = the concept line's
     width outside the silhouette, about 2 px on a 1K sheet. If the model carries its own
     outline, pass 0.
5. **It is done when both of these hold:**
   - every gated view passes, with IoU clearly above its `hull` floor;
   - the hero review lists nothing you would still fix.

## The pass bar is calibrated

**The defaults:** IoU at least 0.94, width and height errors within 3%, and outline distance p95
within 3%.

They come from breaking a good hatchback in known ways. A good model scores about 0.96.

| Fault | What caught it |
|---|---|
| Roof 15% low | side IoU 0.88, height −9% |
| Wheels 15% small | side IoU 0.92, p95 6.3% (size errors stay under 3%) |
| Wheelbase 10% long | side IoU 0.92, p95 4.3% |
| 10% too narrow | front and top only; the side view still scored 0.959 |
| Ram removed | every view; the length anchor moved, so every height read +9% |

That gives two rules:

- **Always gate the front view as well as the side view.** A width error is invisible from the
  side.
- **Recalibrate for a new kind of asset or sheet resolution.** Script four or five known faults and
  confirm that each one fails.

**`hull` is the IoU of the concept against its own convex hull,** which is what a featureless
blob would score. Where a model's IoU is within about 0.03 of it, that view can't tell right from
wrong, which is typical of near-rectangular top views. Rely on the other views there.

## The hero review

Put `hero.png` beside the hero concept and list concrete differences: missing parts, wrong
shapes, the outline, treads, bolts. Never give a score.

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

Keep these with the asset: `concept.json`, the sheet, `report.json` from the last scoring run and
the hero comparison. Note each iteration's main change and its numbers; a commit message is
enough.
