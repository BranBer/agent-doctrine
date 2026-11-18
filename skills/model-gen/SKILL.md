---
name: model-gen
description: Use when generating a 3D game model with an AI image-to-3D or multiview-to-3D service such as Tripo (or Meshy, Rodin) - turning a concept or orthographic sheet into a GLB, choosing a model version, face budget or texture settings, rigging and animating a generated character, splitting one into parts or swappable gear, estimating or controlling credit spend, or when a generated model comes back sideways, over budget, untextured or unriggable.
---

# Model generation

The link between `concept-art` and `model-qa`: a picked orthographic sheet goes in, a GLB comes out, and
`model-qa` decides whether it matches. We rent the generator one API call at a time and own the flow:
the plan, the consent to spend, the record, the checks. A vendor's agent canvas is the same flow behind
their website, and their terms forbid scripting the website.

## Before spending anything

- **API only.** Tripo's terms ban automated access to its web pages, Agentic Canvas included. Web plan
  credits don't work through the API key; API credits are bought separately. Read a new vendor's terms
  on automation before planning around its site, and before the user buys anything.
- **Every paid call is the user's yes.** `tripo.py run` prints the estimate and stops; `--yes` spends.
  Give a batch plan with its total before the first `--yes` of a session. Never swap model or settings
  and resubmit after a failure without saying so.
- **Never ship free-tier output** (Tripo waives it to the public), and never strip the AI identifiers
  or metadata in a vendor's files. Steam needs an AI disclosure; `art/provenance.jsonl` is its source.

## Route each asset

| Asset | Route |
|---|---|
| Characters, creatures, organic props | Generate |
| Buildings, walls, weapons, gems, anything parametric or thin | Code it in three.js or Blender; generators blob thin parts and straight edges |
| Gear that comes off a character | See "Swappable gear" |

## Inputs

From a `concept-art` sheet, crop each view into `art/tripo-in/<asset>/{front,left,back}.png`, padded on
a plain background. **The sheet's side view, figure facing left, is Tripo's `left`.** Add a mirrored
`right` only if the figure is truly symmetric. One clean figure per image; no labels or extra poses.

For anything to be rigged, the sheet shows A-pose, standing straight, snug clothes, limbs clear of the
body. Capes and coat tails come out as separate gear: loose cloth gets weighted to the nearest leg.

## Recipe

Tank pilot, 2026-11-15, one sheet three ways, scored with `model-qa --ref front:h` (IoU front/side/back):

| Recipe | Triangles | Credits | Front | Side | Back |
|---|---|---|---|---|---|
| **P2, face_limit 8000** | 8,337 | 110 | 0.958 | 0.941 | 0.968 |
| H3.1 smart_low_poly, face_limit 8000 | 12,248 | 40 | 0.951 | 0.928 | 0.955 |
| H3.1 generate_parts, untextured | 19,040 in 14 parts | 40 | - | - | - |

P2 wins on every view and holds the budget; H3.1 smart_low_poly overshot its face limit by half. Default:

```json
{"model": "P2-20260801", "face_limit": 8000, "texture": true, "pbr": false,
 "texture_version": "v3.5-20260815", "delight": false, "auto_size": true}
```

- `face_limit`: about 8k for heroes, 3-5k for horde enemies. Top-down play reads silhouettes, not density.
- **Set `pbr` explicitly**: the API defaults it to true. Stylised toon shading wants base colour only.
- `delight` strips the lighting painted into the concept, and with it the colour: on a flat-shaded
  stylised sheet it left the tank grey-blue and pink-brown. For toon sheets set `"delight": false`.
  To fix a dull model without regenerating, repaint it: `models/texture` (10 credits) on the task with
  `--tex-view front=... --tex-view left=... --tex-view back=...` and `"delight": false`. Run on a rig
  task, it kept the 65-joint skin.
- Pass dated model names (`P2-20260801`), never aliases. Triangles, not quad: quad forces FBX output.
- Never set `export_orientation`: later rig and convert steps go wrong silently.
- Keep the task's `model_seed`. If the shape passes and the paint fails, rerun the same seed with a new
  `texture_seed` instead of a new model.

## Commands

From the project root. The key comes from `TRIPO_API_KEY`, never printed.

```bash
S=~/.claude/skills/model-gen/scripts
python -I $S/tripo.py balance
python -I $S/tripo.py run tank-p2 generation/multiview-to-model '<json>' \
  --view front=art/tripo-in/tank/front.png --view left=art/tripo-in/tank/left.png \
  --view back=art/tripo-in/tank/back.png            # estimate only; add --yes to spend
python -I $S/tripo.py run tank-rig animations/rig-check '{}' --from <generation task_id> --yes   # free
python -I $S/tripo.py run tank-rig animations/rig '{"model":"v3.0-20260909","rig_type":"biped","spec":"mixamo"}' --from <generation task_id>
python -I $S/tripo.py wait <asset> <task_id>        # resume after exit 3; never rerun
python -I $S/tripo.py recent                        # last 10 tasks with times; match by time and type
python -I $S/orient.py <model.glb> <oriented.glb>   # Tripo faces +X; glTF and model-qa want +Z
python -I $S/parts.py <parts.glb> <exploded.glb>    # colour and spread parts to see the split
python -I $S/test_tripo.py                          # fake API, spends nothing
```

The commands are Git Bash; in PowerShell, put the JSON body in single quotes too. Prices (credits,
$0.01 each): P2 100 untextured, 110 textured; H3.1 multiview 30 textured; rig-check free; rig 25;
retarget 10 a clip; convert 5, or 10 with options. `tripo.py` refuses an endpoint it has no price for.

`run` uploads, creates, polls, downloads every output into `art/gen/<asset>/<task_id>/` with
`task.json` (URLs expire in about five minutes), and logs inputs' hashes, body, estimate and actual
credits to `art/provenance.jsonl`. Exit codes: 2 not confirmed, 3 still running, 4 failed, 5 API error.

**A create is retried only on 429.** A 500 or a timeout may hide a task that exists and is billed:
run `recent` before anything else. Out of credits (2010) means stop and tell the user.

## After each model

1. `orient.py`, then `model-qa`'s views and compare on the oriented file. For a character, score with
   `--ref front:h`: the default scale anchors on side-view length, which for a person is chest depth.
2. Read the triangle count off the render. Look for sideways output, missing texture, extra limbs.
3. Put the hero render beside the concept and judge it at game zoom. Scores can't see a wrong face.
4. **Put the first model of a cast in the game before paying for the rest.** At a top-down game's zoom a
   hero is about 45 px tall. The tank passed its sheet and still lost to a chibi placeholder: a 1/5 head
   and a narrow body leave a sliver from above, bronze on a brown floor has no contrast, and the role
   colour sat under the coat. Those are sheet faults, so fix the sheets (big head, wide shoulders, role
   colour on the head and shoulders, values lighter than the ground) before generating more. Redrawn two
   and a half heads tall with a blue helmet and shoulders, the same tank read as well as the placeholder.
   An image model keeps adult proportions unless the prompt opens with "super-deformed chibi, two and a
   half heads tall"; "head one third of height" alone was ignored.
5. Only a passing model goes to rigging. A failing one is regenerated from a fixed sheet, not patched.

## Rigging and animation

- `animations/rig-check` is free; run it on the generation task, then rig **that** task id, never the
  check's. Not riggable means the sheet's pose is the problem: fix it (A-pose, limbs clear) and regenerate.
- Rig with `model: "v3.0-20260909"`, `spec: "mixamo"`: the API default is still v1.0.
- Retarget takes the rig task: `preset:idle`, `walk`, `run`, `slash`, `shoot`, `hurt` ... at 10 credits
  each, five per call, `animate_in_place` for locomotion.
- `animate_in_place` clips don't travel, but each holds the hips at its own fixed offset from the rest
  pose (the tank's run sits 0.86 m ahead). In the game, overwrite the hips track's x and z with the rest
  pose's, or the model stands off its position.
- Look at a preset before wiring it to an action. They are long and not combat-shaped: `slash` is a
  6.6 s overhead chop that folds the body double, `hurt` a 13.9 s kneeling loop, `fall` a 3 s collapse.
  `clips.mjs --clip slash --cols 12` finds the usable window; cut it with `AnimationUtils.subclip`.
- After a retarget, `node $S/clips.mjs <animated.glb> <sheet.png>` lays out four frames of every clip.
  Look for collapsed limbs, a scaled head, torn cloth. v1.0 retarget GLBs collapsed twist bones; the
  v3.0 GLB of the tank (65 `mixamorig:` joints; idle, walk, run) came out clean.

## Swappable gear

Rigging each dressed variant separately does not give swappable gear. Each rig fits joints to its own
mesh, so the bone names match but the bind poses don't. One rig has to own the skeleton:

1. Generate and rig a **base body** once (snug, no gear). Its Mixamo skeleton is the canonical one.
2. Generate each gear piece as its own model from a gear sheet, or split a dressed model.
3. Rigid gear (helmet, shoulder plates, shield) is **attached to a bone** in three.js
   (`headBone.add(helmet)`), no skinning. Cloth (coat, cape) gets weights copied from the body in
   headless Blender, then is rebound by bone name onto the body's skeleton at runtime, with the body
   region under it hidden.

What `generate_parts` gave on the tank, seen with `parts.py`: helmet, both shoulder plates and the belt
came out as their own parts; the coat split into chest and skirt; bracers fused to the forearms; under
the helmet is a face shell, not a head. So parts can supply rigid gear, but not the body underneath.
Parts need H3.1 untextured (`"texture": false, "pbr": false, "generate_parts": true`; smart_low_poly
gives no parts), so they need a texture pass after.

Proven on the tank (bare body and dressed body each rigged, gear from a third, parts run):

- Rigid gear follows its bone through idle, walk and run: helmet on `mixamorig:Head`, shoulder plates
  on `LeftArm` and `RightArm`.
- **Fit gear by bones, never by overall height.** `auto_size` makes every model 1.8 m, crest included,
  so a dressed model is a smaller man than the bare one and its gear sinks into him. Place the piece in
  the dressed rig's bone space (`dressedBone.attach(piece)`), move it to the same bone of the body
  (`bodyBone.add(piece)`), and scale its position and size by the two head bones' height ratio (1.10 here).
- Clips retargeted for one rig play on another `spec: mixamo` rig by bone name, so one set of clips
  can serve every humanoid, even one of very different build (a 1.8 m man's clips on a chibi). Two rules, or
  the body distorts: keep only the rotation tracks plus the hips' position (a clip's other position
  tracks are its own body's bone lengths, and stretched a 0.35 m archer's limbs fourfold), and scale
  the hips' height by the two rigs' rest hip heights. `auto_size` does not give a cast one scale (the
  six came out 0.3 to 1.2 m tall), so fit each model to its game height on load.

Not built yet: the Blender weight copy for cloth (coat, cape), and a texture pass for parts.

## Lessons from other people's pipelines

- Code for parametric shapes, a generator for organic ones.
- One clean reference per object; consistent lighting across views.
- Scale uniformly and never apply transforms to a generated mesh before rigging.
- Retopologise before texturing, never after.
- Cel shading hides texture flaws; our toon ramp is forgiving.
- Don't stack auto-rigs (Tripo, then Mixamo, then Blender): pick one authoritative pass.

Sources and the full notes: the asset-pipeline report and `tripo-agentic-practice.md` in the profit
repo's `research_notes/AI 3D game asset pipeline/`.
