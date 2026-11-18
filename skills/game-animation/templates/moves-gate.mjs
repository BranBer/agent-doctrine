// A Claude Code Stop hook. When a file that shapes a hero's moves is newer than the last move check
// that read a sheet, it sends Claude back once to run scripts/qa-moves.mjs before the turn ends. If
// the turn ends anyway, the user is told the check did not run.
//
//   node scripts/moves-gate.mjs          (reads the hook's JSON on stdin; always exits 0)

import { readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
/** Written by qa-moves.mjs when a run has read at least one sheet. */
const STAMP = 'evidence/moves/last-run.txt';
/** What a clip, a carried prop or the sheet itself is made from. */
const WATCHED = [
  'src/render/pose.ts', 'src/render/archery.ts', 'src/render/casts.ts', 'src/render/bow.ts',
  'src/render/acting.ts', 'src/render/models.ts', 'src/render/moves.ts', 'src/render/trail.ts',
  'scripts/move-sheet.html', 'scripts/qa-moves.mjs',
];

const changed = (file) => {
  try {
    return statSync(join(root, file)).mtimeMs;
  } catch {
    return 0;
  }
};

let hook = {};
try {
  hook = JSON.parse(readFileSync(0, 'utf8'));
} catch {
  // Run by hand with nothing piped in: report as if it were the first ask.
}

const checked = changed(STAMP);
const stale = WATCHED.filter((file) => changed(file) > checked);
if (stale.length) {
  const what = `${stale.join(', ')} changed since the last move check`;
  // Ask once. A second block in the same stop would loop when the check cannot run at all.
  console.log(JSON.stringify(hook.stop_hook_active
    ? { systemMessage: `Move check NOT RUN: ${what}.` }
    : { decision: 'block', reason: `${what}. From game-three/prototype, with the dev server up, run: node scripts/qa-moves.mjs <playwright module path>. Report each clip's share, and say so plainly if it cannot run.` }));
}
