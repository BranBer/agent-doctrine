---
name: concept-art
description: Use when making AI concept art for a game or app asset - mood images, hero concepts, vehicle, robot, character or prop sheets, orthographic turnarounds or blueprints to model from - through OpenRouter or another image model, or when recording how an asset was made (provenance) so that no AI image ships.
---

# Concept art

Concepts settle a look. The asset that ships is usually built by a person or in code from them,
which keeps it consistent and keeps it the developer's own work: in the US, purely AI-generated
output can't be copyrighted. This skill makes concepts that share one look, records every image
and every choice, and produces orthographic sheets clean enough to model from. `model-qa` then
checks the model against them.

Whether any AI output may ship as is (music, textures, icons) is the project's call. The common
bar is that nothing reading as AI slop ships, and anything AI-made that does ship passes the same
review as hand-made work and is logged.

## Set up once per project

- **`art/house-style.md`** holds rendering rules only: the medium, shading, outline, palette
  tokens with hex values, proportions, and what the rating forbids. Every prompt carries it, so
  every concept shares one look. Subjects belong in the prompt, never in the style file.
- **The tool.** Run it from the project root:

  ```
  python -I ~/.claude/skills/concept-art/scripts/concept.py <slug> "<prompt>" --n 2 [--aspect 4:3] [--ref <file>]... [--model M] [--dry-run]
  python -I ~/.claude/skills/concept-art/scripts/concept.py pick <file> "<reason>"
  ```

  It writes `art/concept/<slug>-N.png` and never overwrites earlier images. It logs every call,
  with each file's sha256, and every pick to `art/provenance.jsonl`.
- **The key** is read from `OPEN_ROUTER_API_KEY` and never printed.
- **Cost:** about $0.14 an image (gemini-3-pro-image, October 2026). Use `--dry-run` to review a
  prompt for free.

## The chain for one asset

1. **Anchor.** Generate one three-quarter hero view, two variants.
   - State the parts, the proportions in metres, the colours by token, and that it must read at
     thumbnail size.
   - Pick one and log it with `pick`. The reason names what the other variant got wrong.
   - Before you pick, look for likeness. One hatchback variant was a VW Golf Mk1, and robot
     variants with a box head and a slit visor read as faces.
2. **Orthographic sheet.** Generate two variants with the anchor as `--ref`, at 16:9, using the
   template below.
   - Split each sheet with `model-qa`'s `components` and `check` commands.
   - Pick the sheet that splits cleanly and agrees with itself. Log the check numbers in the
     reason.
3. **Pin the model with `--model`** across one asset's chain. Falling back to another model in
   the middle mixes looks.
4. **Change the prompt instead of re-rolling.** Name what failed, then say so in the prompt.

## The orthographic sheet prompt

> Orthographic turnaround sheet of the exact `<subject>` in the reference image: same parts and
> colours. Four views of this one `<subject>` at exactly the same scale, laid out like a
> technical blueprint on a plain flat light grey (#EEEEEE) background with nothing else on it:
>
> - top-left, the SIDE view of its left side, front pointing left;
> - top-right, the FRONT view, face on;
> - bottom-left, the TOP view straight down, directly below the side view, front pointing left,
>   lined up so the length matches;
> - bottom-right, the BACK view, below the front view.
>
> True orthographic projection, with no perspective and the camera level and square to each
> face. Height is identical in the side, front and back views, and width is identical in the
> front, back and top views. Generous empty space between the views; no view touches another.
> No ground lines, no horizon lines, no shadows, no smoke, no labels, no text, no dimension
> lines.

These are the things that went wrong on the first two sheets:

| Seen | What to do |
|---|---|
| Labels such as "LEFT SIDE" despite "no text" | Leave them. They are separate specks that the masks drop. |
| Ground lines drawn under the views | Forbid them. They join a whole row into one blob. |
| One view's antenna touching another view | Ask for space. Otherwise split the views by hand in `concept.json`. |
| One view per sheet drawn about 4% off scale (the back on one, the top on the other) | Expect it. Model from side and front, and leave the drifting view out of the gate. |
| Shadows or smoke puffs | Forbid them. They enter the silhouette. |

If side and front disagree by more than 5%, regenerate. Make the side view alone first, on a
grid with stated sizes ("the wheel is exactly 2 squares"). Then derive each other view from it
as a reference.

## Never

- Let an exploration concept ship by accident. Add a build check that fails when a file in the
  build matches one in `art/concept/` by hash. Crimson Desert's 2026 apology began with AI
  exploration art that slipped into the release.
- Put brand, product or game names in prompts.
- Turn on OpenRouter prompt logging. Opting in grants OpenRouter a perpetual licence to the
  prompts and outputs.
- Leave a pick unlogged. The log is the record of human selection that copyright and portal
  questions ask for.
