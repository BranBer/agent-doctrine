import { spawnSync } from 'node:child_process';
import { existsSync, lstatSync, mkdirSync, readdirSync, readlinkSync, renameSync, symlinkSync, unlinkSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

/* Links every skill in skills/ into each agent's skill folder, so this repo is
   the one copy and every session reads it.

     node install.mjs            link (backing up any real folder it replaces)
     node install.mjs --remove   unlink everything that points into this repo

   The links are directory junctions, which need no admin rights on Windows.
   A recursive delete follows a junction and empties what it points at - this
   repo - so links are only ever removed with unlink, never rm -r. */
const REPO = dirname(fileURLToPath(import.meta.url));
const SKILLS = join(REPO, 'skills');
const HOMES = [join(homedir(), '.claude', 'skills'), join(homedir(), '.agents', 'skills')];
const BACKUP = join(homedir(), '.claude', 'skills-backup', new Date().toISOString().slice(0, 10));
const remove = process.argv.includes('--remove');

const isLink = (path) => existsSync(path) && lstatSync(path).isSymbolicLink();
const pointsAt = (path, target) => isLink(path) && resolve(readlinkSync(path)) === resolve(target);
const intoRepo = (path) => isLink(path) && resolve(readlinkSync(path)).startsWith(resolve(SKILLS));

const report = { linked: [], kept: [], 'backed up': [], removed: [] };
const names = readdirSync(SKILLS, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name);

for (const home of HOMES) {
  mkdirSync(home, { recursive: true });
  if (remove) {
    for (const name of readdirSync(home)) {
      const path = join(home, name);
      if (intoRepo(path)) {
        unlinkSync(path);
        report.removed.push(path);
      }
    }
    continue;
  }
  for (const name of names) {
    const target = join(SKILLS, name);
    const path = join(home, name);
    if (pointsAt(path, target)) {
      report.kept.push(path);
      continue;
    }
    if (isLink(path)) unlinkSync(path);
    else if (existsSync(path)) {
      mkdirSync(BACKUP, { recursive: true });
      const saved = join(BACKUP, `${home.includes('.agents') ? 'agents-' : ''}${name}`);
      renameSync(path, saved);
      report['backed up'].push(`${path} -> ${saved}`);
    }
    symlinkSync(target, path, 'junction');
    report.linked.push(path);
  }
}

if (!remove) {
  for (const name of names) {
    const scripts = join(SKILLS, name, 'scripts');
    if (!existsSync(join(scripts, 'package.json'))) continue;
    const r = spawnSync('npm', ['install', '--no-audit', '--no-fund'], { cwd: scripts, stdio: 'inherit', shell: true });
    if (r.status !== 0) console.log(`npm install failed in ${scripts}`);
  }
}

for (const [label, list] of Object.entries(report)) {
  if (list.length) console.log(`${label} (${list.length}):\n${list.map((line) => `  ${line}`).join('\n')}`);
}
