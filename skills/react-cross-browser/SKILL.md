---
name: react-cross-browser
description: Cross-engine and pixel checks for any web app - hold WebKit (Safari's engine) to Chromium on words, images, fonts, overflow, layout boxes and clustered pixel differences across every state and width; compare two screenshots honestly; catch device-pixel snapping that headless browsers hide; and tell a baked-in gradient from a clean photo. Use when asked whether a change is safe in Safari, when a screenshot diff needs reading, when something looks a pixel off on one machine and not another, or before calling a visual change done.
---

# Cross-browser and pixel checks

**A round validated in one engine is not validated** (react-doctrine 11).
Safari the application is macOS-only; **the engine is not** - Playwright ships a
WebKit build that runs on Windows and Linux, so this needs no Mac, no VM and no
Docker. Keep it out of the deliverable: it is QA scaffolding, and the shipped
repo should not carry a browser dependency for it.

Tools live in `~/.claude/skills/react-cross-browser/scripts/` with their own
`node_modules`. First use on a machine:

```bash
cd ~/.claude/skills/react-cross-browser/scripts
npm install && npx playwright install chromium webkit
```

Paths below use `$CB` for that folder:
`CB=~/.claude/skills/react-cross-browser/scripts`.

**The Playwright MCP is Chromium only.** That is the trap: it is right there,
it is Playwright, and it will happily QA the whole app in an engine no client
uses for Safari. Setting `browser: webkit` on it is accepted and ignored. Check
`browserType().name()` before trusting a round.

## The walk: one driver, both engines

The app's own knowledge - where things are, how to reach a state - lives in a
**driver module** the project supplies. Everything else is here. Copy
`$CB/driver.example.mjs` into a harness folder beside the app (never inside
it), fill in `url`, `widths`, `boxes` and `states`, then:

```bash
cd <app> && npm run build && npm run preview     # terminal 1
node $CB/sweep.mjs qa/driver.mjs chromium        # terminal 2
node $CB/sweep.mjs qa/driver.mjs webkit
node $CB/compare.mjs --fonts "Inter"
```

`sweep.mjs` walks every state at every width in one engine and writes
`qa/sweep/<engine>.json` plus two screenshots per state - the top of the page
and a screen further down. Per state it records the words showing, every image
and whether it decoded, the font faces that loaded, anything past the window,
links with no destination, console and page errors, and the named boxes.

`compare.mjs` then holds the second engine to the first and reports content
faults in either - a broken image is a failure whichever engine broke it. Run
the two sweeps apart from anything timing-sensitive; screenshots slow frames.

Useful flags: `--widths`, `--url`, `--out` on the sweep; `--base`, `--other`,
`--tolerance` (box px, default 1.5), `--cluster` (fail %, default 0.05),
`--erode` (window radius, default 4 for 9x9) and `--fonts` (families that must
have loaded) on the compare.

### Three things get compared, because no one of them is enough

- **Geometry** - the same boxes measured in each engine, catching layout maths
  one engine rounds differently.
- **Content** - the words, the images, the fonts, the overflow. An engine that
  silently fell back to a system font, or left an image undecoded, looks fine
  in a screenshot diff of a page whose layout did not move.
- **Pixels**, with the catch below.

### The raw pixel difference is not the signal

Chasing it wastes a day. The two engines rasterise glyphs differently, so every
letter edge on the page differs - reliably 1-3% of all pixels, in 1px outlines,
on a page that is completely correct.

What matters is whether the difference **clusters**. Eroding the diff with a
9x9 window makes text disappear (body strokes are about 2px, a 48px headline
about 7px) while anything wider survives: a mask that never painted, a gradient
that banded, a card that moved. **Render the map and look at it before
believing any number.** A map that traces letter shapes is antialiasing; a map
with solid blocks is a defect.

```bash
node $CB/pixdiff.mjs a.png b.png --map diff.png
```

It prints the raw and clustered percentages, the bounding box of what survived
erosion, and the horizontal bands it falls into - the bands are usually enough
to name the component without opening the map. Magenta is what survived, pale
pink what the erosion cleared.

### Two things the instrument teaches

`innerText` is not the same in the two engines: WebKit leaves out a closed,
`inert` subtree that Chromium reads. The sweep compares the DOM's words with
`inert` and `aria-hidden` subtrees removed, which is why a collapsed accordion
does not read as a content difference.

An element that mounts or unmounts part-way through a move has no start or end
of its own - its first and last values are wherever that engine's frame caught
it. Judge those on when they come and go, never on a frame count: headless
engines tick `requestAnimationFrame` at different rates, and Chromium reports
three times as many samples as WebKit across the same 600ms move.

### The erosion window follows the type, not the width

9x9 clears body text and a headline up to about 40px. **A phone screen
carrying display type needs a wider one**, because a 48px bold headline has
7px strokes that survive 9x9 - and it fills a much larger share of a 375px
screen than of a 1440px one, so the same correct page reads as 0.2% clustered
there and 0% wide. Measured on one app: at 375 the default flagged four of
five states, worst 0.23%, and every map traced letters; at `--erode 7` (15x15)
all five agreed with **nothing** surviving.

So raise the window, not `--cluster`. Raising the threshold hides a real block
of the same size; widening the window removes strokes and keeps blocks, which
is the distinction the check exists to make. A round is only honest if the
window is named beside the number, which is why the summary line prints it.

### Two differences that are the instrument's, not the app's

**A live region.** What it holds is whatever was last announced, cleared on a
timer the two engines do not share, so comparing it compares a race. The sweep
drops `[aria-live]` along with `[inert]` and `[aria-hidden]`.

**Which font weights loaded.** That follows what has been rendered and how
eagerly each engine fetches faces - one engine pulling a 600 the other
synthesises is normal. Only a whole *family* present in one and absent in the
other fails; a weight difference prints as a note. `--fonts` names the
families that must be there, which is the check worth having: a silent
fallback to a system font looks fine in a screenshot diff of a page whose
layout did not move.

## Pixel snapping, which headless browsers hide

A background box is rasterised as `round(top + height) - round(top)`, so its
painted height depends on the **top's** fraction. Where the device pixel ratio
puts an element's offset on a half device pixel, that element is snapped a
pixel thinner and visibly lighter than its siblings. It bites the things drawn
as a set: a three-line hamburger, a row of dividers, a hairline rule.

Two reasons nothing else catches it. It only shows at ratios whose fraction is
`.25` or `.75` - Windows at 125% or 175% display scaling, which is where a
great many people actually are - and **headless Playwright
coverage-antialiases where a real browser snaps**, so both engines report the
fault as clean at every ratio a normal sweep runs.

```bash
node $CB/snap.mjs http://localhost:4173/ '.hamburger' --driver qa/driver.mjs --state menu-open
```

It runs headed Chromium at each ratio with `--force-device-scale-factor`,
measures the ink per device row inside the element, groups the inked rows into
bands and fails when a band is more than 10% off the median. Bands print as
`rows/ink`, so `4r/66 3r/65 4r/66` is even and `4r/62 2r/42 4r/62` is the
middle one snapping.

**The fix is compositing, not arithmetic.** No choice of pitch survives an
arbitrary ratio; promoting each element (`will-change: transform`) rasterises
it from its own origin and takes all of them off the grid. `contain: paint`
works too but leaves a clip contract on the element, which is the wrong thing
to hang on anything that rotates. Firefox snaps as well, in the opposite
direction at some ratios, and ignores every compositing hint - out of scope
for a two-engine contract, worth a note rather than a fight.

## A shipped photo may already have its fades painted on

Before adding a scrim to any backdrop, check whether the asset has one baked
in. An export of a design frame carries the frame's gradients; the app then
draws its own on top and the result is roughly twice the intended density.
Correct at the width it was exported at, and invisible until a narrower frame
adds a fade of its own. A design review catches it; a diff against your own
last screenshot does not.

```bash
node $CB/baked-check.mjs figma-raw.png shipped-asset.jpg
```

Both images are stretched to one box, so only the *shape* of the ratio matters:
a smooth ramp from about 0.2 to 1.0 is a baked mask, a flat 1.0 is a clean
photo.

## Where the line sits

Keep the clustered-pixel failure at 0.05%. On small screens a handful of states
sit just over it, at up to 0.09%, because a bold headline fills more of a
narrow screen - every one of those maps traces letters and none has a solid
block. Read the map before moving the line.

Anything the project itself owns - the order its levels sit in, the copy it
checks against a content document, the moves it films frame by frame - belongs
in the project's own harness beside the driver, not here.
