# Stylised environments in Three.js: what fits and what it costs

For a small arena seen from a high camera, with a few hundred enemies already on screen. "Sourced"
means a named studio or the Three.js docs describe it; "ours" is a planning figure to profile with
`renderer.info.render`, not a measurement.

| Need | Technique | Number or cost | Status |
|---|---|---|---|
| Colour without tiling | One palette or gradient atlas shared by every piece, or vertex colour alone | 128 to 256 px | Technique sourced (Alba, Bruno Simon's portfolio, KayKit); size ours |
| Crisp aged edges | Real chips and bevels in the geometry, under flat shading | `flatShading` is a material flag | Sourced |
| Soft variation | A low-frequency term in world space; a small value offset a slab, inside the floor's band | One extra term in the shader, or vertex colour | Technique sourced; band ours |
| Ground zones | One floor mesh with an RGBA mask (paving, sand, wear, darkening) | 512 to 1024 px | Pattern sourced (Alba's four splats); size ours |
| Shade in joints and at wall feet | Vertex shade or one baked map, tinted cool, never black | An edge loop 10 to 20 cm above the ground | Technique sourced; height ours |
| Broken paving | Lay big cells, then cut each through its middle, square to its longest side and a little askew, meeting each side away from its corners; repeat to size. Cut on the ground, not in ring coordinates, where a straight cut curls into a spiral | Joints meet three at a time; no fans, no splinters | Ours: a critic ranked fans and honeycomb cells as the top fault before it |
| Stains, soot, sand, cracks | Alpha-tested decals merged into one mesh on one atlas | 1 draw call | Sourced; merging ours |
| Rubble and props | `InstancedMesh` a shape for 2 to 4 shapes, `BatchedMesh` beyond that | 1 to 4 draw calls | Sourced |
| The sun's static shadow | Bake it, or freeze the map with `shadow.autoUpdate = false` | No cost a frame once frozen | Flag sourced; baking ours |
| Actor shadows | Blob shadows, or one small map of actors only, fitted to the arena | 1024 px over 30 m is about 3 cm a texel | Blobs sourced; sizing ours |
| Depth from a high camera | Fog by horizontal distance, patched in with `onBeforeCompile`; built-in fog uses camera distance and fogs the near ground | One uniform a frame | Sourced (three.js forum) |
| Grade | In the materials, or one merged pass (tone map, LUT, vignette) | One full-screen pass | Merge sourced (pmndrs) |
| Screen-space shade | N8AO's Performance preset at half resolution; off on phones and 4 GB machines | 8 samples; 2 to 4 times faster at half size | Presets sourced; tiering ours |
| Whole environment | Merged ground and walls, props, decals, backdrop | 5 to 10 draw calls, 20k to 50k triangles, 1 to 3 MB | Ours |

## What gives depth, in order of effect

Shadows that sit things on the ground, then haze with distance, then shade in joints and corners.
A flat-shaded style needs all three: without them it reads as unfinished, and a ruin most of all.
One developer of a low-poly ruin world began with flat colour only and had to add noise, then
ambient shade, then hand-made texture before it read as a ruin.

## Generated and kit pieces

- Image-to-3D output is dense, soft-edged and drifts toward realism. Use it for irregular lumps.
- Before one stands beside code-built stone: cut it to its triangle target, throw away its
  texture, map its faces onto the shared palette, shade its vertices, and draw it with the
  scene's own material. Then check it with `model-qa`.
- CC0 kits built on one gradient atlas (Kenney, KayKit, Poly Haven) fit with the least work.

## Textures cost memory, not just download

A PNG, JPEG or WebP is unpacked on the graphics card at about width x height x 4 x 1.33 bytes: a
4096 px texture takes about 90 MB whatever its file size. KTX2 cuts that four to eight times, and
its ETC1S mode suits flat colour. A palette atlas avoids the question.

## Capture traps

A wrong screenshot poisons every judgement after it.

- A headless browser may fall back to a software renderer: read the WebGL renderer string and say
  so in the report when it is one.
- Capture after the game has set a ready flag, with the loop held and stepped by a fixed time.
- Take every review picture from the game's own camera at game zoom, from fixed places, with the
  real HUD. A beauty shot from a free camera proves nothing about play.
