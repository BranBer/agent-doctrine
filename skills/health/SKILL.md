---
name: health
description: General code-health and basic security checks for any project, using free open-source tools - type checks, lint and smells, import cycles, unused code, duplication, file sizes, committed secrets, vulnerable dependencies and security patterns, for TypeScript/JavaScript and Python. Gates only type errors, import cycles and committed secrets. Use before calling a change done, or when asked for a health or security pass; deeper security review is for dedicated agents.
---

# Health

One command that runs free, open-source checkers over a project and prints
what they find. It is deliberately basic: it catches what tools catch
reliably, and leaves judgement - and any deeper security review - to people
and to reviewer agents. Pair it with `doctrine`, whose Reviewing section is
what a reviewer reads the results against.

Nothing is installed into the project and nothing is written to it. The
JavaScript tools live in this skill's own `node_modules`; the rest are machine
installs.

## Setup, once per machine

```bash
cd ~/.claude/skills/health/scripts && npm install     # ESLint, typescript-eslint, SonarJS, import-x, knip, jscpd, TypeScript
winget install --id Gitleaks.Gitleaks -e               # committed secrets
winget install --id Google.OSVScanner -e               # vulnerable dependencies
```

Python checks run through `uvx` (from [uv](https://docs.astral.sh/uv/)), which
fetches ruff, vulture and Semgrep on first use. `pyright` comes from
`npm install -g pyright`. A missing tool is reported as SKIP with the line that
installs it; it never fails the run.

## Running it

From the project's root:

```bash
node ~/.claude/skills/health/scripts/health.mjs [dir] [--only key,key] [--skip key,key]
```

It finds every JS/TS and Python project up to three folders deep - a web app
with a Python `tools/` folder gets both sets - and prints a section per step,
then a summary:

```
PASS  types
FAIL  import cycles
READ  lint and smells
SKIP  vulnerable dependencies  - winget install --id Google.OSVScanner -e
```

Exit code 1 means a gate failed; 0 means none did. `--skip semgrep` saves a
minute or two when the security-pattern scan is not wanted.

## What runs

| Key | Step | Tool | Stacks | Fails the run? |
|---|---|---|---|---|
| `types` | type check | the project's `typecheck` script, else `tsc --noEmit` on its `tsconfig.json` - or on each config a Vite-style root references; pyright | TS; Python | yes, when the project configures types (`tsconfig.json`, `pyrightconfig.json` or `[tool.pyright]`) |
| `cycles` | import cycles | ESLint `import-x/no-cycle` (resolving `@/` aliases through the project's tsconfig; fails on cycles only, and lists files it could not parse); `pycycles.py` (ignoring `if TYPE_CHECKING:` imports) | JS/TS; Python | yes |
| `lint` | lint and smells | ESLint with typescript-eslint and SonarJS rules, summarised by rule and file | JS/TS | no |
| `ruff` | lint, smells, security | ruff, including bandit's `S` security rules and `C90` complexity; the project's own ruff config if it has one | Python | no |
| `unused` | unused code | knip; vulture | JS/TS; Python | no |
| `sizes` | file sizes | the doctrine's limits - 400 source, 600 tests, 200 React components, 800 waived | any | no |
| `duplication` | copy-paste | jscpd, listing each clone | any | no |
| `secrets` | committed secrets | gitleaks, over the git history | any git repo | yes |
| `deps` | vulnerable dependencies | OSV-Scanner, reading the lockfiles (npm, PyPI and more, no account) | any | no |
| `semgrep` | security patterns | Semgrep Community Edition, `p/default` rules, metrics off | any | no |

**Why only three gates.** A type error, an import cycle and a committed secret
are never a matter of judgement, and a project should not pass with one. Every
other finding depends on context - a smell may be deliberate, a vulnerable
dependency may be unreachable - so it is printed for someone to decide.

**ESLint ignores the project's own config and its inline `eslint-disable`
comments.** This is a second opinion, not the project's linter, and a
project's directives name rules from plugins this config does not load.

**Type checking needs the project's dependencies installed.** Without
`node_modules` the type and unused-code steps are skipped with a note rather
than reporting every import as missing.

## Reading the results

- **FAIL** - fix before calling the change done.
- **READ** - a person or a reviewer agent decides. For sizes, check
  `doctrine`'s exceptions and the `architecture` skill's split test; for lint,
  the rule summary shows where the weight is.
- **SKIP** - a tool is missing or cannot run here; the line says how to fix it.

For a review, run it, then give the reviewer the summary and the READ sections
rather than the whole log.

**A secret that is not a secret.** gitleaks judges by pattern and entropy, so
a storage key or a test fixture can look like an API key. Confirm by reading
the line (the output names file, line and commit, with the value redacted),
then list the finding's fingerprint in the project's `.gitleaksignore`, one per
line. A real secret is rotated first, then removed from history - deleting the
line in a new commit leaves it in every clone.

**Lint and sizes read only what git tracks.** Build output, bundles and
anything else in the project's `.gitignore` are skipped.

## React projects

Run `health` for these checks, and `react-health` for React's own: inline JSX
functions, hook rules and markup accessibility.

## Sonatype (optional)

Sonatype's free tier is now Sonatype Guide, used through `auditjs`. It needs a
free account at guide.sonatype.com and a token, and its API is metered by
credits, so it is not part of the default run. With a token:

```bash
npx auditjs@latest guide --token <token>
```

OSV-Scanner covers the same ground without an account.
