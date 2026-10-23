---
name: react-theming
description: Styling and animation conventions for React projects - Tailwind v4 theme tokens and `@utility` rules for typography/variant styles, and motion (framer-motion) for every UI animation, including layout-animation pitfalls. Use when styling a component, adding or changing a colour/type/spacing token, noticing a repeated class string, or animating anything (enter/exit, layout, gestures, scroll).
---

# Theming and motion

The rules are doctrine 6, 7 and 10 (`react-doctrine`). A project's actual
tokens - its palette, font, type ramp and house hover - belong in a
project-level skill or its `PROJECT.md`, not here.

## Tailwind v4: tokens, then utilities

Entry stylesheet is `src/index.css`; the system lives in `src/styles/theme.css`.

```css
/* src/index.css */
@import 'tailwindcss';
@import './styles/theme.css';
```

### Tokens come from the design file

- **Colour:** every colour is a design variable in `@theme`, never a hex in a
  component. Clear the Tailwind scales the design doesn't use
  (`--color-gray-*: initial`) so `gray-20` can't be confused with `gray-200`.
  If `bg-gray-500` doesn't exist, the guardrail is working - pick a real token.
- **Breakpoints:** clear the defaults and name only the steps the design
  draws (`--breakpoint-tablet`, `--breakpoint-desktop`), in `@theme static`, so
  a hook can read them back through `matchMedia`.
- **Font:** self-host the licensed files the client supplies, with
  `font-display: swap` and the fallback stack their live site uses. Never pull
  a commercial face from a CDN.
- **Spacing:** check whether the design's values land on Tailwind's 4px scale.
  If they all do, add no spacing tokens; a value off the scale is a design
  question, not a `[13px]` arbitrary.
- **Containers:** page width, copy column and similar go in
  `--container-*`, wrapped in one `@utility layout-page`. Full-bleed
  backgrounds go on the outer element, `layout-page` on the inner.

### Type ramp

One `@utility` per text style in the design, named `type-*`, carrying size,
weight and leading, and switching size with the design's own breakpoint
variant where the frames differ. **Colour is never baked into a type
utility**: the same step runs white on a dark hero and ink on a light panel,
so the colour is paired at the call site (`className="type-eyebrow text-gray-40"`).
Adding a step means the design added a text style - check the design file
first; don't invent an intermediate size.

### A surface sets its own text colour

When the page's default text is light (a dark site), any component that paints
its own light surface sets the dark text colour on the same element. Otherwise
it renders white on white, which no build or lint catches.

### When to add a utility

- Same class group in two component folders → `@utility`.
- A raw hex or px value in a component → it belongs in `@theme` first.
- One-off layout (grid spans, gaps, positioning) stays inline. Don't
  `@utility` a single use.
- Styles that differ by breakpoint are variants inside one utility, not two
  class strings picked in TypeScript.

### Shared components stay brand-neutral

A component shared with another project takes its theme through `className`
props (`summaryClassName="accordion-summary"`) rather than hardcoding one
brand's tokens.

## Motion: `motion/react` only

```bash
npm i motion   # framer-motion's current package name
```

```tsx
import { AnimatePresence, motion } from 'motion/react';
```

Imported code often arrives importing `framer-motion`. Repoint it at
`motion/react`: `framer-motion` is only a transitive dependency, so those
imports break the day the package restructures.

No CSS keyframes, no `requestAnimationFrame` loops, no `setTimeout` fades for UI
transitions. Exit animations need `<AnimatePresence>` - a conditional render
alone won't animate out - and a component that animates out owns its presence
(doctrine 12).

```tsx
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 8 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )}
</AnimatePresence>
```

Timings shared across folders live in one file (`src/utils/motion.ts` or
similar), written as independent delays from the trigger rather than chained
durations, so retuning one beat moves only that beat.

Always honour reduced motion: `<MotionConfig reducedMotion="user">` at the
root handles most of it. Anything animated by hand, or timed against a
positional value, needs `useReducedMotion()` checked as well.

Animation config that grows past a few lines belongs in a hook
(`useDrawerMotion/`), not inline in a 200-line component.

### Layout animation pitfalls

- **One transition for the whole chain.** A motion element with no
  `transition` falls back to motion's default spring, so a tweened container
  arrives before its sprung children. Give every element in a layout move the
  same transition (or wrap it in `MotionConfig`); elements with their own
  timing pass an explicit one.
- **Text warps under a non-uniform scale.** `layout` animates size with
  `transform: scale()`. Text gets `layout="position"`; square boxes can take
  `layout`. The correction must exist at every level of the chain: one plain
  `<div>` in the middle reintroduces the skew below it.
- **Border radius must be a numeric motion value** to be scale-corrected. A
  `rounded-full` class or a `'50%'` string renders as an ellipse mid-move.
- **Don't read the matrix to check for warp.** A corrected child shows a
  non-unit scale - that is the correction. Compare `getBoundingClientRect`
  against the resting size.
- **`layoutDependency` on sticky elements.** `layout` re-projects on every
  commit; a page-height change clamps the scroll and a sticky element reads
  that as movement. Tie projection to the value that actually changes
  geometry.
- **No `layoutRoot` on a wrapper that should travel.** It snaps the wrapper
  and lets children fake the move with a scale.
- **A wrapper as tall as a sticky child cages it.** Sticky only travels within
  its parent; make the wrapper `display: contents` once the child is pinned.
- **Motion applies its FLIP transform at commit** and only defers the tween,
  so an exiting child is scaled by its parent's change on frame one. If
  something must be gone before the layout moves, delay the state change,
  not the transition.
- **`exit` does not cross a nested `AnimatePresence`.** A child with its own
  presence needs to be told it is leaving (`useIsPresent()` passed down as a
  prop).
- **A value read by `AnimatePresence` must be derived during render.** An
  effect lands a frame late and the first transition runs the wrong way.
  `custom` is the only value an exiting child still receives.
- **Check travel on every element in the chain**, sampled frame by frame, and
  in WebKit too. A screenshot at rest shows none of this.
