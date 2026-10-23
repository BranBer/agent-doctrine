---
name: doctrine
description: The engineering standard for every project, any language or framework - one unit one entry point, the two-level folder model (purpose folders, units that grow into folders, utils as a shelf of subjects), the 400-line size rule and its exceptions, logic free of the framework, dependencies from specific to general, comments, named values, contracts, one data door, typed boundaries, PROJECT.md case-law, and how a reviewer checks them. Load it before writing, reviewing or refactoring code, then load the pack for the stack (react-doctrine, games-doctrine, python-doctrine, node-doctrine).
---

# Doctrine

The standard for keeping a codebase decoupled and readable, whatever it is
written in. It says what good structure is and why; the pack for the stack
says what it looks like there:

| Stack | Pack |
|---|---|
| React 19 + TypeScript + Vite + Tailwind | `react-doctrine` (and `react-architecture`, `react-theming`) |
| TypeScript web games (Phaser, Three.js) | `games-doctrine` |
| Python | `python-doctrine` |
| Node/TypeScript services and APIs | `node-doctrine` |

Companion skills: `architecture` for where split-out code goes, `health` for
the free tools that check a project.

**Precedence.** A pack may tighten a rule here, never loosen it. A project's
own case-law file (`PROJECT.md` by convention) wins on anything specific to
that product.

## The rules

### 1. One unit, one public entry point

A unit is a file until it needs a second one; then it becomes a folder named
for it, and its entry is the only thing anyone outside imports.

*Why:* the entry is the unit's contract. Everything behind it can be split,
renamed or rewritten without a caller noticing, which is what lets a unit
grow without its neighbours growing with it.

- React: a component is a folder from the start - `Button/{Button.tsx, types.ts, index.ts}`.
- Games / Node: `routes/orders.ts` becomes `routes/orders/index.ts` plus its parts.
- Python: `billing.py` becomes `billing/__init__.py` with `__all__`, plus its parts.

### 2. Size: 400 code lines per hand-written file

Tests 600; React components 200. Section "The size rule" below has what
counts, the exceptions and the waiver.

### 3. Logic does not import the framework

Decisions live in plain functions and data; the framework is a thin shell that
calls them.

*Why:* logic that never touches the framework can be tested without it, run
somewhere else, and survives the framework being upgraded or replaced.

- React: the logic is a plain function in `utils/` or a hook's own helper; the hook only wires it to state.
- Games: the simulation imports no Phaser or Three.js and runs headless.
- Node: `domain/` imports no HTTP framework.
- Python: domain code imports no Flask, FastAPI or Django.

### 4. Dependencies point from specific to general

A unit may import shared code. Shared code - `utils/`, a component library, a
`kit/` - never imports a unit that uses it. No import cycles. Platform SDKs
(ads, payments, analytics, storage) sit behind an adapter the app owns.

*Why:* when general code reaches into specific code, the two can no longer
change separately, and the "shared" folder quietly becomes the place every
feature depends on every other feature through.

- Any stack: if `utils/money` imports from `services/billing`, the dependency runs the wrong way - move the shared part down, or the specific part out.

### 5. Comments explain why

Explain *why*, never *what*. The test for a comment: would removing it let
someone break something invisibly? Interlocking state, an ordering that
matters, a value that two places must agree on - those earn a sentence.
Provenance (which ticket, which design node, what a value used to be) belongs
in the project's case-law, not beside the code.

Never point at something the reader will not have: a rule number from this
skill, a working file outside the repo, a design-file node id. Give the reason
itself, or nothing.

### 6. A raw value used in two units gets a name

A colour, a duration, a limit, a URL - the second time it appears in a
different unit, it becomes a named constant or token in one place.

*Why:* two copies of one fact drift; the second copy is always the stale one.

- React: a Tailwind theme token or `@utility`.
- Games / Node / Python: a constant in the unit that owns the concept, or in `utils/` if no unit does.

### 7. A module's contract lives inside it

Nothing a caller must remember to wrap, order, initialise or key. If using a
unit correctly takes a step the caller can forget, absorb the step and expose
a parameter instead; where it genuinely cannot be absorbed, make forgetting it
loud (throw, fail the type check) rather than silent.

### 8. Data has one door

One client for each data source, typed where data enters, and one copy of each
fact. Server data is a cache, not state - never copied into a store or a
context.

- React: RTK Query for an API, Context for shared client state, Zustand only for high-frequency state.
- Node: one data-access layer under `data/`; services never talk to the database driver directly.
- Python: one client module per external source; the rest import it.

### 9. Types at every boundary

Every function a unit exports, every message that crosses a process, every
config value: typed, and validated where it comes from outside.

- TypeScript: `strict`, and no `any` at an exported signature.
- Python: type hints on every public function, checked by pyright.

### 10. Project-specific decisions go in `PROJECT.md`

This skill is generic. Why a product's screen behaves the way it does, which
design frame a value came from, which client asked for what - that is the
project's case-law, in its own file beside the code.

### 11. Checking tools never become a dependency of the shipped project

Linters, scanners and test browsers live on the machine or in a skill's own
folder, never in the project's dependencies.

## The folder model

Two levels everywhere, without a folder per file.

**Level 1 - purpose folders**, named for what the code is for: `routes/`,
`services/`, `models/`, `utils/` in a service; `sim/`, `systems/`, `scenes/`
in a game; `components/`, `hooks/` in React. Each pack lists its own. Code
lives in the purpose folder that says what it does.

**Level 2 - units inside a purpose folder.** A unit starts as one file. When
it outgrows its limit, or grows parts only it uses, it becomes a folder of the
same name:

```
routes/orders.ts           →    routes/orders/
                                  index.ts        the entry: the unit's public surface
                                  handlers.ts     private parts, imported only inside the folder
                                  validation.ts

services/billing.py        →    services/billing/
                                  __init__.py     the entry, with __all__
                                  invoices.py
                                  proration.py
```

**The size limit decides where split-out code goes.** When a file passes its
limit, each piece that comes out goes one of two ways:

- **It serves only this unit** - it speaks the unit's own types and
  vocabulary. It stays inside the unit's folder, private.
- **It is general purpose** - it takes plain values and knows nothing about
  the unit: dates, money, retries, string formatting. It goes to `utils/`.

A private part that a second unit starts needing is promoted to `utils/` at
that moment - not before.

**`utils/` is a shelf, not a drawer.** It holds subject units -
`utils/dates.ts`, `utils/money/`, `utils/http/` - each with one entry and one
subject. Nothing is named `misc`, `helpers` or `common`, and a util never
imports from a purpose folder.

**Against bloat:**

- No folder for a single file, and no folder whose only file is its entry.
- No file per function, unless that function is a unit in its own right.
- Units nest at most two levels below their purpose folder
  (`routes/orders/refunds/`). Deeper, and the purpose folder is hiding a
  second purpose.

## The size rule

### The limit, and what counts

**400 code lines** per hand-written source file. A code line is neither blank
nor comment-only. Comments are excluded on purpose: counting them would make
deleting a "why" comment the cheapest way to fit.

**Tests: 600.** A test file mirrors one unit and table-driven cases run long;
past 600, the unit under it does too much.

**Packs may tighten.** React components stay at 200 with no waiver.

### Why a line limit at all

It stands for single responsibility - one reason to change per module - and
it is the one part of that anyone can check at a glance. A file past 400
lines nearly always has several reasons to change.

On its own it would reward the cheapest split: `sim.ts` into `sim-a.ts` and
`sim-b.ts`, each importing the other. That fits the limit and makes things
worse. So the limit always comes with the folder model, which says where
split-out code goes, and the review questions below, which catch a split that
only moved lines around.

### When a file genuinely needs more than 400 lines

Only when decomposing further makes the code worse. Five cases:

| # | Category | Why splitting fails | Example | Allowed by |
|---|---|---|---|---|
| A | **Generated** | The generator is the source | GraphQL / OpenAPI types, an ORM client, a level table written by a script | A generated-file header (`// Generated by …`, `@generated`) |
| B | **Data, not behaviour** | A table split by line count scatters one fact | level tables, copy and i18n catalogs, fixtures | Holding no logic. Prefer `.json`. |
| C | **The language has no modules** | Nothing to split into | GLSL/WGSL shaders, SQL migrations | Its file type |
| D | **Inseparable cohesion** | Every split leaks internals or creates a cycle | D1 mutual recursion (a recursive-descent parser); D2 one algorithm whose steps share private mutable state; D3 a transcription of a spec, verified line for line | A waiver |
| E | **Measured hot path** | A split costs real time every frame | a physics step, a codec | A waiver naming its benchmark |

A waiver is one line at the top of the file, so anyone opening it sees why it
is long:

```ts
// doctrine-allow size: D1 - recursive descent; productions are mutually recursive
```
```python
# doctrine-allow size: E - bench: bench/step_bench.py shows 18% slower split
```

**800 is a hard ceiling**, waiver or not: past it, the cohesive unit is itself
too big, and the answer is a smaller unit. React components take no waiver.

### What is not an exception

- **"It's all related."** Related by topic is not related by change. A game
  scene handles input, camera, HUD and spawning - four reasons to change.
- **"Splitting just adds files."** Files are free; reading 600 lines to change
  one behaviour is not.
- **"It's one big switch."** It becomes a registry - `Record<Kind, Handler>`,
  a dict of callables - which keeps exhaustiveness and lets each handler live
  in its own file. Adding a kind then never means editing the dispatcher.
- **"It's the scene / the manager / the main component."** That is the god
  object this rule exists to catch.
- **"It was already this big."** It may shrink, it may not grow, and touching
  it is the moment to split it.

### The split test

Before splitting, find the seam; before waiving, show there is none. The
`architecture` skill walks each step with examples.

1. **Different reasons to change** - which parts change for different people or features?
2. **Pure core, effectful shell** - can the decisions move into plain functions?
3. **Data apart from code** - is part of it a table the rest reads?
4. **Variants behind a registry** - is there a switch over kinds?
5. **A sub-concept with its own name** - is there something you could name and test on its own?

Each seam found is placed by the folder model: private to its unit, or a
subject in `utils/`.

## Reviewing

What a reviewer checks, and the bad split each question catches:

| Principle | The bad split it catches | Review question |
|---|---|---|
| Single responsibility | the oversized file; the function doing too much | Is any hand-written file over its limit without a valid waiver? Is any function over about 80 code lines? |
| Open/closed | a dispatcher edited for every new kind | Does adding a kind mean editing a switch, where a registry would not? |
| Substitution | an implementation that narrows its interface | Does every implementation honour the full contract it implements? |
| Interface segregation | a split that exposes internals so the halves can talk | Does anything import past a unit's entry? Does an entry export far more than its callers use? |
| Dependency inversion | logic reaching for the framework; shared code reaching into a unit | Does logic import the framework, or an SDK outside its adapter? Does anything in `utils/` import a unit? |
| (all) | `a.ts` and `b.ts` importing each other | Is there an import cycle? |
| Folders | a drawer, or bloat | Is anything in `misc`, `helpers` or `common`? Is there a folder holding one file? |

**Listing files by size** takes one command per stack, run from the project
root. They are a quick count and read slightly high - docstrings and the inside
of block comments count as code here - and generated files and data tables
show up too. `health`'s file-size step is the exact count, with exemptions and
waivers applied.

TypeScript / JavaScript:

```bash
find . \( -name node_modules -o -name dist -o -name build -o -name .git \) -prune -o -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.mjs' \) -print \
  | while read -r f; do printf '%6d %s\n' "$(grep -cvE '^\s*($|//|/\*|\*)' "$f")" "$f"; done | sort -rn | head -20
```

Python:

```bash
find . \( -name .venv -o -name venv -o -name __pycache__ -o -name .git -o -name node_modules \) -prune -o -type f -name '*.py' -print \
  | while read -r f; do printf '%6d %s\n' "$(grep -cvE '^\s*($|#)' "$f")" "$f"; done | sort -rn | head -20
```

The `health` skill runs the exact count, plus the project's linters and
scanners, in one pass.
