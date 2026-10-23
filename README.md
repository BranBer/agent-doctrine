# doctrine

Skills that keep any project decoupled, readable and basically secure. A
language-neutral core - `doctrine` (the rules and the folder model),
`architecture` (where split-out code goes) and `health` (free open-source
checks) - plus a pack per stack: React, games, Python and Node.

This repo is the one copy. `install.mjs` links each skill into
`~/.claude/skills` and `~/.agents/skills`, so every Claude session and every
other agent reads the same files, and an edit here reaches all of them.

```bash
node install.mjs            # link every skill; a real folder in the way is backed up first
node install.mjs --remove   # remove the links (the repo is untouched)
```

Backups of anything the installer replaced are in
`~/.claude/skills-backup/<date>/`.

## Warning

The installed skills are **directory junctions** pointing into this repo. On
Windows a recursive delete (`rm -rf`, `Remove-Item -Recurse`, deleting the
folder in Explorer) follows a junction and empties what it points at - this
repo. Remove the links with `node install.mjs --remove`, which unlinks them
and touches nothing else.

## Layout

```
skills/<name>/SKILL.md     one folder per skill
skills/<name>/scripts/     a skill's tools, with their own node_modules
docs/specs/                the design
docs/plans/                the build plan
```
