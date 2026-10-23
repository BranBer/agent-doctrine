---
name: react-health
description: Code-health, antipattern and accessibility (WCAG) checks for React projects - build, inline JSX functions (react-doctrine 13), SonarJS/hooks/effect antipatterns, jsx-a11y markup lint, unused code (knip), comment pointers, repeated raw Tailwind values, axe-core scans and overflow checks in Chromium and WebKit. Use when asked to review code health, audit accessibility, check for antipatterns or dead code, or before calling a React change done.
---

# React health

Run the general `health` skill as well: it covers import cycles, file sizes,
duplication, secrets and dependency scans for any stack. These scripts are
React's own - inline JSX functions, hook rules, markup accessibility.

Tools live in `~/.claude/skills/react-health/scripts/` with their own
`node_modules`, so no app ever ships them (react-doctrine 11). First use on a
machine:

```bash
cd ~/.claude/skills/react-health/scripts && npm install && npx playwright install chromium webkit
```

Paths below use `$RH` for that folder:
`RH=~/.claude/skills/react-health/scripts`.

## Static: run from the app's folder

```bash
cd <app> && node $RH/health.mjs [--ban "QA-LOG|MOTION-PLAN"]
```

| step | fails the run? | what it is |
|---|---|---|
| build | yes | `npm run build` (for Vite + TS that is `tsc -b`) |
| inline JSX functions | yes | a function or `.bind` written in a JSX attribute (doctrine 13) |
| antipatterns | no, read it | SonarJS, React Compiler hook rules, you-might-not-need-an-effect |
| a11y lint | no, read it | oxlint `jsx-a11y` on the markup |
| unused code | no, read it | knip: unused files, exports, dependencies |
| comments | yes | a comment pointing outside the app (doctrine 4); `--ban` adds the project's working-file names |
| repeated values | yes | an arbitrary value or hex used in two component folders (doctrine 7) |

Each script also runs alone:

```bash
$RH/node_modules/.bin/eslint -c $RH/eslint.config.mjs src          # full antipattern scan
REACT_HEALTH_ONLY=doctrine $RH/node_modules/.bin/eslint -c $RH/eslint.config.mjs src
node $RH/comments.mjs src --since HEAD~1 --ban "PROJECT-NOTES"      # lists comment lines added since
node $RH/repeats.mjs src --roots components,features
```

**Reading the "read it" steps.** Start from the count on the project's last
clean round and look only at what moved, as antipattern backlogs are usually
large and mostly systemic (e.g. SonarJS `prefer-read-only-props` on every
component). A finding in a file you touched is yours; when a rule is wrong for
the codebase, say so and move on rather than bending the code. The effect
rules flag effects that are legitimately effects (history sync, a timer
started elsewhere); note those in the project's case-law so the next round
doesn't relitigate them.

**The memoisation half of doctrine 13 is a review, not a lint.** For each
`useCallback`/`useMemo`, name the case it serves (a `memo` child, a hook
dependency, a hook's or context's return). For each prop on a `memo`
component, confirm it is stable: follow it back to a state setter, a
`useCallback`, or a provider's wrapped action. Check whether the React
Compiler is on before recommending either way.

## Runtime: needs the app served

Serve the production build (`npm run build && npm run preview`), then:

```bash
node $RH/axe-scan.mjs http://localhost:4173/ [more urls] --widths 375,768,1440 --json axe.json [--exclude footer]
node $RH/overflow.mjs http://localhost:4173/ --widths 320,375,768,1024,1440
```

`--exclude` leaves out markup the project doesn't own, such as a footer copied
from the client's site; list what it hides in the report as the owner's.

Both run Chromium and WebKit (`--engine chromium|webkit` narrows), and both
only see the state a URL loads into. An app whose content appears after
interaction (steps, tabs, modals, accordions) needs a project script that
drives it there and then calls `new AxeBuilder({ page }).analyze()`. Keep
those scripts in a harness folder beside the app, never in it.

Stop the preview server when the round is done.

## What axe does not see

Automated checks catch roughly a third of WCAG failures. Before calling an app
accessible, a project harness should also check, by driving the page:

- **Keyboard:** every control reachable, in order, with a visible focus ring;
  focus moved sensibly when content changes (a new step, a closed dialog).
- **Focus not obscured (2.4.11):** Shift+Tab under any sticky header; fix with
  `scroll-padding-top`.
- **Text over images (1.4.3):** axe skips it. Capture the region with and
  without the text, compare only the glyph pixels, and judge the worst 2%.
- **Non-text contrast (1.4.11) and colour alone (1.4.1):** indicators, focus
  rings, current-step markers.
- **Headings and landmarks (1.3.1):** styled text that should be a heading;
  one `main`; a skip link target.
- **Target size (2.5.8):** 24×24 minimum.
- **Reflow and text spacing (1.4.10, 1.4.12):** 320px wide, and the WCAG
  spacing overrides.
- **Forced colours:** state shown only by a background disappears; use
  `forced-colors:` variants with `Highlight`/`HighlightText`.
- **Reduced motion:** run the moves with `prefers-reduced-motion: reduce`;
  the check must fail with it off, or it isn't looking.
- **WebKit parity:** the same checks in WebKit (doctrine 11). Its Windows
  build has no `OffscreenCanvas` and runs slow frames; wait on state, never on
  fixed delays.

## Reporting

Write findings for the people who fix them: the rule in plain words, what
happens on the page, why that breaks the rule, how certain the finding is,
and the fix with an owner (dev, design, client). Screenshots are captured
from the viewport and cropped, as a clipped Playwright screenshot renders
beyond the viewport and moves sticky and fixed elements.
