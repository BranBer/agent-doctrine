---
name: react-doctrine
description: The React standard for every React project (React 19 + TypeScript + Vite + Tailwind v4 + motion) - folder per thing, the 200-line component ceiling, comments, providers, animation, Tailwind theming, breakpoints, WebKit QA, component contracts, naming and memoising handlers, and the data layer (RTK Query, Context, Zustand). Load it before writing, reviewing or refactoring React code.
---

# React doctrine

Load `doctrine` first; this pack is what its rules look like in React 19 +
TypeScript + Vite + Tailwind v4 + motion, and it tightens one of them: a
component's size.

The React standard, independent of what is being built with it. React 19 +
TypeScript + Vite + Tailwind v4 + motion. Anything specific to one product -
its screens, its design-file transcriptions, the decisions behind them - lives
in that project's own case-law file (`PROJECT.md` by convention), never here.

Companion skills: `react-architecture` (copy-paste templates),
`react-theming` (styling and motion), `react-health` (code-health, antipattern
and accessibility checks). A project may carry a copy of this file as its
`AGENTS.md` for agents that cannot read skills; this skill is the master.

## 1. Everything is a folder

`doctrine`'s one-unit-one-entry rule, in React's shape: a component is a
folder from the start, because it always has at least its props type beside it.

Components, hooks and providers each own a folder. No loose `.tsx` in a shared directory.

```
src/components/Button/
├── Button.tsx     # the component
├── types.ts       # ButtonProps and any local types
└── index.ts       # export { Button } from './Button'
```

- Props live in a sibling `types.ts`, never `Button.ts` — `./Button` would resolve to it ahead of `Button.tsx`.
- **Not `.d.ts`.** `skipLibCheck` skips every `.d.ts`, the project's own included, so an error in one is never reported and the broken type quietly becomes `any`. A `.d.ts` describes JavaScript that has no types; a component's props are not that.
- Import them as `import type { ButtonProps } from './types'`. `verbatimModuleSyntax` is on, so `import type` is mandatory.
- `types.ts` holds types only. Runtime values (constants, enums) go in `constants.ts` in the same folder.
- Cross-folder imports go through the alias and the barrel: `@/components/Button`, never `@/components/Button/Button`.

## 2. 200-line component ceiling

A component (`.tsx`) stays within 200 code lines - tighter than `doctrine`'s
400 - and **takes no waiver**: there is always a hook, a util or a child
component to move out. Every other file - hooks, utils, providers, data slices
- takes the core's 400, tests 600. A code line is neither blank nor
comment-only. A component over 200 gets split. Where the piece lands:

- **Used only by its parent** → nested folder inside the parent, same three-file shape: `Card/CardHeader/{CardHeader.tsx,types.ts,index.ts}`.
- **Reusable or generic** → its own folder under `src/components/`.

Check yourself: the `health` skill's file-size step lists every file over its limit, components at 200 and the rest at 400.

## 3. Split state, not just markup

Most files blow past 200 lines because of hook soup, not JSX. Lift `useState`/`useMemo`/`useEffect`/`useCallback`/`useLayoutEffect` clusters into hooks:

```
src/hooks/useDrawer/
├── useDrawer.ts
├── types.ts       # only if the hook has a real signature to name
└── index.ts
```

Component-specific hooks stay in the component's folder (`Card/useCardMetrics/`). Shared hooks go to `src/hooks/`.

A hook over 400 code lines means the pure logic isn't pure-logic-shaped yet — move it to `src/utils/`:

- `src/utils/` holds subjects, and a subject is a file until it needs a second one: `formatCurrency` goes in `src/utils/money.ts`, not a file of its own.
- A subject that grows several files gets a folder with a barrel: `src/utils/dates/{parse.ts,format.ts,diff.ts,index.ts}`.

## 4. Comments earn their line

`doctrine`'s comment rule, with the cases React work keeps meeting.

Explain *why*, never *what*. No JSDoc blocks on obvious props, no section banners,
no restating the code below. If a comment is longer than what it describes, delete it.

Most of this app is ordinary layout, styling and motion work, and ordinary work
needs no commentary — a Figma node id next to a padding value, a note that a
colour was measured, a sentence explaining what `object-cover` does, all of that
is noise. Default to none.

What does earn a comment is the thing that will bite the next person: interlocking
state and effects, where changing one value cascades into another. `layoutDependency`
and its scroll-clamp trap, the two animations that take turns via each other's
durations, a `-z-10` that has to escape its parent's stacking context, a value
latched during render so a child never sees the intermediate. Those are worth a
sentence, because they are invisible in the code and expensive to rediscover.

**The test is whether removing it lets someone break something invisibly.** If
the answer is no, it is provenance — which node it came from, what was measured
to get it, what it used to be — and provenance belongs in the case-law file, not
beside the value. Write the consequence, not the derivation.

**Write for whoever receives the repo, and the repo ships alone.** That reader
has the code and nothing else: not this file, not the case-law, not the QA log,
and no guarantee of access to the design file. A comment citing a rule number, a
Figma node id or a past round is a pointer they cannot follow, which is worse
than noise — it reads as though something is missing. Give the reason itself, or
give nothing.

This is also what makes comments multiply. Written to a colleague who has the
working files open, every finding looks worth a note; written to the person the
work is handed to, most of them are someone else's history.

That distinction is hardest to apply at the moment of writing, when the fact has
just been discovered and every part of it feels load-bearing. It is easy a week
later, which is why this one is worth re-reading rather than trusting: comments
only ever accumulate, because nothing in the work of fixing a bug removes the
note left by the last one.

## 5. Providers

One folder per context under `src/providers/`:

```
src/providers/MyContext/
├── context.ts             # createContext, not exported past index.ts
├── types.ts               # MyContextValue, MyContextProviderProps
├── MyContextProvider.tsx   # the wrapper component
├── useMyContext.ts        # throws if no parent provider
└── index.ts
```

`useMyContext` throws when the context is undefined — that's the guard, don't return a fallback object.

## 6. Animation: framer-motion

All animation goes through framer-motion (`motion` package, `import { motion } from 'motion/react'`). Install it if it's missing. No hand-rolled CSS keyframes or `requestAnimationFrame` loops for UI transitions.

## 7. Tailwind: theme, not one-offs

Repeated style groups become Tailwind v4 `@utility` rules in `src/styles/theme.css` - typography variants especially (`heading-xl`, `body-sm`, `label-caps`). Colors, fonts and spacing come from `@theme` tokens. Never paste the same 8-class typography string into two components.

**And placement, not only duplication: if CSS can express it, TypeScript may
not.** The paragraph above is about repetition, which is why it misses the thing
that appears exactly once. No class string assembled from variables, no colour,
gradient or shadow built by a helper, no constant spread into `style={{ }}` that
a `@utility` could carry. A value earns `style` only when the browser cannot
know it at build time: a measured height, a drag offset, a scroll position.

**Two components is the threshold.** A raw value that appears in two component
folders has stopped being a coincidence and earns a name: colours, widths and
spacing go to `@theme`, a repeated class group to `@utility`, and a media query
no `--breakpoint-*` can express to `@custom-variant`. One use stays where it
is - naming a value nothing else shares only moves it away from the eye that
reads it. Count folders, not lines: a component and its own nested child are one
place, and a number written six times inside one component is one style applied
six times.

Re-typing a value that already has a token is the same mistake with an extra
step, whatever the count. If `max-w-copy` exists, `max-w-[1000px]` is wrong on
its first use.

A value another system owns gets globalized too, just not into ours. Mirroring
a third party's CSS means its steps take a namespace of their own, so no design
work can reach one by accident and a number the two happen to share stays a
coincidence rather than a dependency.

Breakpoints are the same rule. A component that **restyles** across one uses
`tablet:` and `desktop:` variants and asks nothing. Only a component that has to
**swap** - different DOM, not different paint - may branch on `useBreakpoint()`.
Two gradients picked in TypeScript and one utility with two variants paint the
same pixels, but the first spreads the breakpoints across two files and the
second cannot.

## 8. Aliased imports

`@/*` → `src/*`. No `../../..` chains. Relative imports only inside the same folder (`./types`, `./Button`).


## 9. Pages own the product, the library stays generic

`src/components/` is the library, and nothing in it knows which page it is on.
`src/sections/` is where that knowledge is allowed to live: one folder per page
holding its copy, its arrangement and whatever is unique to it, plus a shell
that sequences them. The test for where something belongs is whether it survives
the page change. If it does, it is not the page's.

A page may reach the shell only through props - the shell imports every page, so
reaching back is a cycle. Anything a page and some other consumer both need, but
no page owns, goes to `src/utils/`.

## 10. Mobile-first, and the breakpoint numbers exist once

Base styles are the narrowest frame the design draws, and every wider frame is a
variant on top of it. Clear Tailwind's default breakpoints and name only the
steps the design actually has, so nothing can reach for one that was never
drawn.

The numbers live in `@theme static` and nowhere else. A hook that needs one
reads it back from the CSS variable through `matchMedia` rather than repeating
the literal.

**An undesigned width still has to fit.** Below the narrowest frame drawn, using
the nearest frame's layout is licence; ceasing to be responsive is not. The only
contract at a width nobody drew is that the page fits it - nothing fixed,
nothing `min-w`, nothing that cannot shrink may make the document wider than the
window.

Never answer sideways scroll with `overflow-x: hidden` on `html`/`body`. It
hides the symptom, and it makes the body a scroll container, which kills every
`position: sticky` on the page: a second bug traded for a concealed first one.
Fix the element that does not fit. Sideways scroll is worth the care because it
truncates the whole page rather than one component - the body paints its ink to
the full scroll width while every `w-full` block stops at the window, so the
layout ends up in a column with a gutter beside it and nothing looks locally
wrong.

## 11. QA is not done until WebKit agrees

Every rendered component and every animation must tell the same visual story in
WebKit - Safari's engine - as it does in Chromium. A round validated in one
engine is not validated.

**The Playwright MCP is Chromium only.** That is the trap: it is right there, it
is Playwright, and it will happily QA the whole app in an engine no client uses
for Safari. Setting `browser: webkit` on it is accepted and ignored. Check
`browserType().name()` before trusting a round.

Getting a real WebKit is easier than it sounds. Safari the application is
macOS-only; **the engine is not** - Playwright ships a WebKit build that runs on
Windows, so this needs no Mac, no VM and no Docker:

```
npm i playwright && npx playwright install webkit
```

Keep it out of the deliverable: it is QA scaffolding, not product code, and the
shipped repo should not carry a browser dependency for it.

Three things get compared, because no one of them is sufficient:

- **Geometry** - the same boxes measured in each engine, catching layout maths
  one engine rounds differently.
- **Animation** - sampled frame by frame, compared on its endpoints and whether
  it is monotonic. Never on frame count: headless engines tick
  `requestAnimationFrame` at different rates, and Chromium reports three times
  as many samples as WebKit across the same 600ms move. A screenshot at rest
  cannot see a transition that arrives in the right place by the wrong route.
- **Pixels**, with the catch below.

**The raw pixel difference is not the signal, and chasing it wastes a day.** The
two engines rasterise glyphs differently, so every letter edge on the page
differs - reliably 1-3% of all pixels, in 1px outlines, on a page that is
completely correct. What matters is whether the difference *clusters*: erode the
diff with a 9x9 window and text disappears (body strokes ~2px, the 48px headline
~7px) while anything wider survives - a mask that never painted, a gradient that
banded, a card that moved. Render the diff map and look at it before believing
any number. A map that traces letter shapes is antialiasing; a map with solid
blocks is a defect.

## 12. What the caller can forget belongs inside the component

A component that only behaves when its caller remembers to wrap it, order it or
key it has put its contract somewhere it cannot defend. Absorb the machinery and
expose a prop instead: `Scrim` holds its own `AnimatePresence` and takes `open`,
rather than asking every caller to declare presence around it and hand it a key.

Where it genuinely cannot be absorbed, make the omission loud - that is what
`useMyContext` throwing is for, and why it must not return a fallback object.

The case to design out is the third one, where the thing renders, looks right at
rest, and misbehaves only in motion. A missing `AnimatePresence` throws nothing:
the element simply vanishes on the first frame of its exit instead of fading,
and no screenshot of a settled page will ever show it. Rule 11 is the same
observation from the QA side; this is the version that stops it being possible.

## 13. Handlers are named before the return, and memoised only for a reason

A function handed to a JSX element is declared above the `return` and passed
by name: `onClick={handleSelect}`, never `onClick={() => onSelect(id)}`. That
covers event handlers, callbacks passed to children, render props
(`summary={renderSummary}`), and a function picked by a condition
(`const handleClick = isFull ? () => onSelect(id) : undefined`). The markup
then reads as structure, and every function the component creates sits in one
place where its memoisation can be decided.

```tsx
export function Row({ item, onSelect }: RowProps) {
  const handleSelect = () => onSelect(item.id);

  return <button onClick={handleSelect}>{item.label}</button>;
}
```

**Inside a list, the handler belongs to the item.** When a handler needs the
row's data, extract the row into its own component, which declares its handler
from its own props. `.bind(...)` and a curried `onClick={handle(item.id)}` are
the inline function in disguise; don't use either.

What this does not cover: callbacks that run during render rather than being
passed (`items.map((item) => <Row ... />)`), and callbacks that aren't JSX props
(`useEffect`, `setState((prev) => ...)`).

### Whether to wrap it: `useCallback` / `useMemo`

Naming a function is not memoising it. The default is a plain `const`.
Stabilising a reference only matters when something compares it, so a
`useCallback` is justified by exactly one of these:

1. **It goes to a `memo` component.** A fresh function each render is a changed
   prop, and the memo re-renders anyway. Check the whole prop list: one
   unstable prop defeats it just as well.
2. **It is a dependency** of `useEffect`, `useLayoutEffect`, `useMemo` or
   another `useCallback`. Unstable, it re-runs the effect every render, or
   loops.
3. **It leaves a custom hook or goes into a context value.** Consumers may do
   either of the above with it, and they cannot see how it was made. Every
   function a hook returns or a provider exposes is wrapped.

**Not otherwise.** A native element (`<button onClick>`) and a component that
isn't `memo` never compare props, so `useCallback` there buys nothing and
costs a dependency array and a comparison on every render. Don't wrap by
habit.

`useMemo` caches a value, not a function. Use it for a computation that is
measurably expensive, or for an object or array whose identity is compared,
in the same three situations: a `memo` component's prop, a dependency, a
context value. A cheap derivation is recomputed, not memoised.

**Check for the React Compiler first** (`babel-plugin-react-compiler` in the
build). Where it is on, it inserts this memoisation itself: write plain
functions and keep manual `useCallback`/`useMemo` for identity the compiler
cannot see, such as a value handed to a non-React API.

The first half is linted (`react-health`: `no-restricted-syntax` flags a
function or `.bind` written directly in a JSX attribute, including under `?:`
and `&&`). The second half is a review question: every `useCallback` names
which of the three it serves, and every prop on a `memo` component is checked
for stability.

## 14. The data layer is a layer, and hooks are its only door

### Which tool, and the question that decides it

**Is there a server?** Server data is not state. It is a cache of someone
else's state, and it arrives with loading, error, staleness, refetch,
invalidation, retry and request races attached to it. Rebuilding that in
`useEffect` is the most reliable way to rot a React codebase, and it is never
finished: the version that works is the one that also handles the second
component asking for the same thing, the user leaving before the response, and
the mutation that has to make three lists stale.

So if the app talks to an API, the data layer is **RTK Query**, and that is
decided once for the whole app on its first endpoint - not per feature, and
not revisited because one screen "only needs a fetch".

Why that rather than a fetch hook: **REST and live data are the same cache.**
A query subscribes to a websocket or an SSE stream in `onCacheEntryAdded` and
writes into the cache entry the REST route filled, so a component reading a
list never learns whether the last change arrived by request or by push. A
REST-only fetcher makes streaming a second system, with a second cache and a
second set of loading states, and the two drift the first time a socket
message arrives while a refetch is in flight.

**Is there client state that is nobody's but ours?** Only then a store, and
the ladder is short. `useState` first. Lift to a **Context provider** (rule 5)
when separate branches need the same value. Reach for **Zustand** only when
the value changes many times a second, or is read by many unrelated subtrees:
a context re-renders every consumer on every change, which is exactly what
makes a drag offset or a live cursor a store's job and a theme, a session or
an open menu a provider's.

**Never hold one fact in two of them.** Copying a query result into a store or
a context is how two sources of truth start, and the copy is always the one
that goes stale. A component that needs server data and client state reads
both hooks; it does not merge them into a third place.

### The shape, which is rule 1 again

A slice owns a folder, three files at minimum, exactly as a component does:

```
src/data/
├── baseQuery.ts            # the transport: auth, headers, error shape
├── api.ts                  # createApi: base query and the tag list, no endpoints
├── store.ts                # registers the reducer and the middleware
├── index.ts                # the barrel the store imports - see the trap below
└── assignments/
    ├── assignments.ts      # api.injectEndpoints
    ├── documents.ts        # the queries and mutations, or the REST paths
    ├── types.ts            # the endpoint inputs and responses
    └── index.ts            # export the hooks, and nothing else
```

`src/data/`, not `src/redux/` or `src/store/`: the folder is named for what it
holds, not for the library that happens to implement it this year. Everything
rule 1 says applies - `types.ts` beside the slice rather than in a shared
`types/` folder, runtime values in `constants.ts` rather than `types.ts`, cross-folder
imports through the barrel.

### One api, and slices injected into it

`createApi` is called **once**. Every slice is `api.injectEndpoints`, so routes
of different natures compose into one client, one cache and one middleware
without one file growing to hold them all. A slice imports the api, declares
its endpoints against its own documents and types, and exports the hooks that
come back.

**The tag list is the one thing that cannot be split.** `tagTypes` is declared
at `createApi`, because the invalidation graph is built from the whole list
before any slice has been injected, while `providesTags` and `invalidatesTags`
belong to the endpoints in the slices. That split looks wrong and is correct;
a tag used by a slice and missing from the list fails silently, invalidating
nothing.

**A slice exists only if something imports it.** `injectEndpoints` runs as a
side effect of its module, so a slice nothing imports contributes no
endpoints, and its hook is `undefined` at the call site. This is worse than it
sounds: the app can work in development, where the barrel is pulled in wholesale,
and break in production, where a bundler drops the module it can prove nothing
uses. So the store imports the barrel and the barrel re-exports every slice,
which gives one file that keeps them all alive and one place to look when a
hook comes back undefined.

### Hooks are the only door

A component, a hook or a provider imports `useGetAssignmentsQuery`. It never
imports `api`, never imports a slice, never dispatches an endpoint's action and
never selects raw cache state. That is what makes the layer a layer: the
transport, the cache keys, the invalidation and the library itself can all be
replaced behind a hook signature that does not move.

A **provider may consume a data hook and expose it further** - that is the one
place a query result is legitimately re-exposed, because the provider is
passing it rather than copying it. A provider that stores what a hook returned
into its own `useState` has made the copy this rule exists to prevent.

### Types are required, and they say what the API sends

Both generics on every endpoint: `builder.query<Response, Input>`. An endpoint
that takes no argument takes `void`, never `{}` - `{}` accepts every object and
turns the argument into an unchecked hole. The response type is the API's
shape, not the shape a component would prefer.

Where those differ, `transformResponse` closes the gap, so the reshaping happens
once in the slice rather than in every consumer, and the cache holds the useful
form. A component that needs one field of a large entry reads it through
`selectFromResult`, so a row does not re-render when a sibling in the same
response changes.

The response types are generated from the schema where the API has one
(GraphQL codegen, an OpenAPI generator). A generated type that disagrees with
the server is a bug in one of them; a hand-written one that disagrees is a bug
nobody finds until production.
