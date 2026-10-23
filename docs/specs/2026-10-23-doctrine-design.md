# Doctrine: one standard for every stack

Status: approved 23 Oct 2026, revised the same day (skills only; the folder
model; a general health skill). Builds on the design agreed in the games
session on 17 Oct (core + stack packs; React, games, Python and Node packs;
this repo as master; installed for Claude and other agents), with the size
rule raised from 200 to 400 lines and given an exception model.

**Skills, with tools - not machinery.** The doctrine is guidance agents apply
while they build and reviewer agents check against. The one script is a
health runner, like `react-health`'s: it hooks free, open-source linters and
scanners into any project and prints what they find. It is rudimentary on
purpose; deeper security review is for agents the user orchestrates.

## 1. What this is

A local repo, `Desktop/Projects/doctrine`, holding the skills every Claude
session (and other agents) use to keep projects decoupled, readable and
basically secure, whatever the language.

```
install.mjs              links every skill into ~/.claude/skills and ~/.agents/skills
skills/doctrine/         the rules and the folder model, any language; how a reviewer checks them
skills/architecture/     how to find seams and where split-out code goes
skills/health/           the runner: free OSS linters and scanners for any project
skills/react-doctrine/   React pack - today's five React skills, ported; rules
skills/react-architecture/  that are now general point back to the core
skills/react-health/
skills/react-theming/
skills/react-cross-browser/
skills/games-doctrine/   TS web games: Phaser / Three.js + Vite
skills/python-doctrine/
skills/node-doctrine/    Node/TS services and APIs
```

The React skills keep their names, so CLAUDE.md files that name them keep
working. Project-level copies (the React skills inside `CPR/boomi`) are left
alone.

## 2. The core rules

Each rule in `doctrine` carries its reason and a line per stack showing what it
looks like there.

1. **One unit, one public entry point.** A unit is a file until it needs a
   second one; then it becomes a folder named for it, whose entry
   (`index.ts`, `__init__.py`) is the only thing outside it imports.
2. **Size: 400 code lines per hand-written file**, with the exception model in
   section 4.
3. **Logic does not import the framework.** A game's simulation imports no
   Phaser or Three.js; React logic lives in plain functions its hooks call; a
   service's domain code imports no HTTP framework.
4. **Dependencies point from specific to general.** A unit may import shared
   code; shared code (`utils/`, a component library) never imports a unit
   that uses it. No import cycles. Platform SDKs (ads, payments, analytics,
   storage) sit behind an adapter the app owns.
5. **Comments explain why**, and never point at files the reader will not have.
6. **A raw value used in two units gets a name.**
7. **A module's contract lives inside it** - nothing a caller must remember to
   wrap, order or key.
8. **Data has one door**: one client, typed where it enters, one copy of each
   fact.
9. **Types at every boundary.**
10. **Project-specific decisions go in the project's `PROJECT.md`.**
11. **Checking tools never become a dependency of the shipped project.**

## 3. The folder model

React made this easy because a component is already a folder. Every stack
gets the same two levels, without the bloat of a folder per file.

**Level 1 - purpose folders**, named for what the code is for: `routes/`,
`services/`, `models/`, `utils/` in a service; `sim/`, `systems/`, `scenes/`
in a game; `components/`, `hooks/` in React. Each pack lists its own. Code
lives in the purpose folder that says what it does.

**Level 2 - units inside a purpose folder.** A unit starts as one file:
`routes/orders.ts`, `services/billing.py`. When it outgrows its limit, or
grows parts only it uses, it becomes a folder of the same name:

```
routes/orders.ts                    routes/orders/
                          →           index.ts        the entry: the unit's public surface
                                      handlers.ts     private parts, imported only by index.ts
                                      validation.ts   and each other
```

```
services/billing.py                 services/billing/
                          →           __init__.py     the entry, with __all__
                                      invoices.py
                                      proration.py
```

**What the size limit is for: deciding where split-out code goes.** When a
file passes its limit, each piece that comes out goes one of two ways:

- **It serves only this unit** - it speaks the unit's own types and
  vocabulary. It stays inside the unit's folder, private.
- **It is general purpose** - it takes plain values and knows nothing about
  the unit: dates, money, retries, string formatting. It goes to `utils/`,
  where any unit may use it.

A private part that a second unit starts needing is promoted to `utils/` at
that moment, not before.

**`utils/` is a shelf, not a drawer.** It holds subject units -
`utils/dates.ts`, `utils/money/`, `utils/http/` - each with one entry and one
subject. Nothing is named `misc`, `helpers` or `common`, and a util never
imports from a purpose folder (rule 4).

**Against bloat:**

- No folder for a single file, and no folder whose only file is its entry.
- No file per function unless that function is a unit in its own right.
- Units nest at most two levels below their purpose folder
  (`routes/orders/refunds/`); deeper, and the purpose folder is hiding a
  second purpose.

## 4. The size rule

### The limit, and what counts

**400 code lines** per hand-written source file: lines that are neither blank
nor comment-only. Comments are excluded on purpose - counting them would make
deleting a "why" comment the cheapest way to fit.

**Tests: 600.** A test file past 600 says the unit under it does too much.

**Packs may tighten, never loosen.** React components (`.tsx`) stay at
**200, with no waiver** - there is always a hook, a util or a child component
to move out. Everything else in a React project takes the core's 400.

### Why a line limit at all

The limit stands for the **S** in SOLID - one reason to change per module - and
it is the one SOLID property anyone can check at a glance. On its own it would
reward the cheapest split (`sim.ts` into `sim-a.ts` and `sim-b.ts`, importing
each other), so it always comes with the folder model above, which says where
split-out code goes, and the review questions below, which catch a split that
only moved lines around.

### When a file genuinely needs more than 400 lines

Only when decomposing further makes the code *worse*:

| # | Category | Why splitting fails | Example | How it is allowed |
|---|---|---|---|---|
| A | **Generated** | The generator is the source | GraphQL / OpenAPI types, Prisma client, Junk Rally's `daily-table.ts` (1,191 lines, written by a script) | Exempt; a generated-file header says so. |
| B | **Data, not behaviour** | A table split by line count scatters one fact | level tables, copy and i18n catalogs, fixtures | Exempt while it holds no logic. Prefer `.json`. |
| C | **The language has no modules** | Nothing to split into | GLSL/WGSL shaders, SQL migrations | Exempt. |
| D | **Inseparable cohesion** | Every split leaks internals or creates a cycle | (1) mutual recursion, as in a recursive-descent parser; (2) one algorithm whose steps share private mutable state; (3) a transcription of a spec, verified line for line | Waiver. |
| E | **Measured hot path** | A split costs real time every frame | a physics step, a codec | Waiver, naming its benchmark. |

**A waiver is one line at the top of the file**, so anyone opening it sees why
it is long:

```ts
// doctrine-allow size: D1 - recursive descent; productions are mutually recursive
```

**800 is a hard ceiling** even with a waiver. React components take no waiver.

### What is not an exception

- **"It's all related."** Related by topic is not related by change.
- **"Splitting just adds files."** Files are free; reading 600 lines to change
  one behaviour is not.
- **"It's one big switch."** It becomes a registry - `Record<Kind, Handler>`, a
  dict of callables - which keeps exhaustiveness and lets each handler live in
  its own file.
- **"It's the scene / the manager / the main component."** That is the god
  object the rule exists to catch. Junk Rally's `Play.ts` (553) and `sim.ts`
  (567) are this.
- **"It was already this big."** It may shrink, it may not grow, and touching
  it is the moment to split it.

### The split test

Before splitting, find the seam; before waiving, show there is none:

1. **Different reasons to change** - which parts change for different people
   or features?
2. **Pure core, effectful shell** - can the decisions move into plain
   functions, leaving a thin layer that touches the framework or the world?
3. **Data apart from code** - is part of it a table the rest reads?
4. **Variants behind a registry** - is there a switch over kinds?
5. **A sub-concept with its own name** - is there something you could name,
   and test on its own, that is currently inline?

Each seam found is then placed by the folder model: private to the unit, or
general purpose in `utils/`.

### Reviewing

| Principle | The bad split it catches | Review question |
|---|---|---|
| **S** | the oversized file; the function doing too much | Is any hand-written file over its limit without a valid waiver? Is any function over about 80 code lines? |
| **O** | a dispatcher edited for every new kind | Does adding a kind mean editing a switch, where a registry would not? |
| **L** | an implementation that narrows its interface | Does every implementation honour the full contract it implements? |
| **I** | a split that exposes internals so the halves can talk | Does anything import past a unit's entry? Does an entry export far more than its callers use? |
| **D** | logic reaching for the framework, shared code reaching into a unit | Does logic import the framework or an SDK outside its adapter? Does anything in `utils/` import a unit? |
| (all) | `a.ts` and `b.ts` importing each other | Is there an import cycle? |
| folders | a drawer, or bloat | Is anything in `misc`/`helpers`/`common`? Is there a folder holding one file? |

## 5. The health skill

A runner script, `skills/health/scripts/health.mjs`, used like
`react-health`'s: run from a project's folder, it detects the stack and runs
whichever of these are available, then prints a `PASS / FAIL / READ` summary.
Every tool is free and open source, installed on the machine or in the
skill's own `node_modules` - never in the project (rule 11). A missing tool is
reported with its one-line install command, not treated as a failure.

| Area | Tool | Stacks | Gate or read |
|---|---|---|---|
| Types | `tsc --noEmit` (or the project's `build`); pyright | TS; Python | gate where the project has a config, else read |
| Lint and smells | ESLint + typescript-eslint + SonarJS rules; ruff (with its bandit `S` security rules and `C90` complexity) | TS; Python | read |
| Import cycles | ESLint `import-x/no-cycle`; ruff has none, so a small Python import scan | TS; Python | gate |
| Unused code | knip; vulture | TS; Python | read |
| Duplication | jscpd | any | read |
| File sizes | the code-line count, files over their limit without a waiver | any | read |
| Secrets | gitleaks | any | gate |
| Vulnerable dependencies | OSV-Scanner (npm, PyPI and more, no account) | any | read |
| Security patterns | Semgrep Community Edition, when installed | any | read |

Gates are kept to what is never a judgement call: the project does not
type-check, an import cycle, a committed secret. Everything else is printed
for a person or a reviewer agent to read.

**Sonatype is optional, not the default.** Its free tier (Sonatype Guide,
through `auditjs guide`) now needs an account and a token and is metered by
credits, so the skill documents it as an add-on for a project that already has
an account. OSV-Scanner covers the same ground with no account.

**React projects** run `health` for the general checks and `react-health` for
React's own (inline JSX functions, hook rules, a11y).

## 6. The packs

- **React** - the five current skills, moved in. `react-doctrine`'s size rule
  becomes "components 200, no waiver; everything else the core's 400", and
  rules now in the core open with a pointer to it. `react-health`'s scripts
  stay as they are.
- **Games (TS + Vite, Phaser / Three.js)** - purpose folders `sim/`,
  `systems/`, `scenes/`, `render/`, `platform/`, `levels/`; a simulation that
  runs headless and never imports the renderer; a fixed-step loop; seeded
  randomness; pools; platform adapters behind one interface.
- **Python** - purpose folders inside the package (`routes/` or `api/`,
  `services/`, `models/`, `utils/`), modules growing into packages by the
  folder model, `__all__` as the entry, typed boundaries, scripts as thin
  entry points over importable modules.
- **Node/TS backend** - purpose folders `routes/`, `services/`, `domain/`,
  `data/`, `config/`, `utils/`; routes thin, services hold the logic, one
  data-access layer, config validated at startup, the HTTP framework kept out
  of `domain/`.

## 7. Install

- `install.mjs` links each `skills/<name>` into `~/.claude/skills/` and
  `~/.agents/skills/` with **directory junctions** (no admin rights on
  Windows), and installs each skill's script dependencies.
- Before replacing a real folder it moves it to
  `~/.claude/skills-backup/<date>/`.
- **Uninstall removes the junction, never what it points at.** On Windows a
  recursive delete follows a junction and empties the target - here, this
  repo. `install.mjs --remove` unlinks the link alone, and the README says why.
- First, confirm Claude Code follows a junction when it scans
  `~/.claude/skills`; if it does not, install by copying instead.
- The global `CLAUDE.md` "React work" section becomes "Code work": load
  `doctrine`, then the pack for the stack, and run `health`.

## 8. Decided

1. React components stay at 200, and take no waiver (23 Oct).
2. 800 is a hard ceiling, waiver or not (23 Oct).
3. Function length over 80 is a review question, not a rule (23 Oct).
4. A waiver is the annotation at the top of the file alone (23 Oct).
5. No custom checker, baseline or test suite; reviewer agents check against
   the doctrine (23 Oct).
6. Two-level folder model: purpose folders, then units that grow from a file
   into a folder; split-out code is private to its unit or general purpose in
   `utils/` (23 Oct).
7. A general `health` skill running free OSS tools, gating only type errors,
   import cycles and secrets (23 Oct).
