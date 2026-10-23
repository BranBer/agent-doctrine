import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectStacks } from './stacks.mjs';
import { summarize } from './summaries.mjs';
import { steps } from './tools.mjs';

/* General code-health and basic security checks for any project.

     node health.mjs [dir] [--only key,key] [--skip key,key]

   Keys: types, cycles, lint, unused, ruff, sizes, duplication, secrets, deps,
   semgrep. Runs each free tool that is installed and prints PASS, FAIL, READ
   or SKIP per step. Only type errors (where the project configures types),
   import cycles and committed secrets fail the run; everything else is for a
   person or a reviewer to read. Nothing is installed into or written to the
   project. */
const HERE = dirname(fileURLToPath(import.meta.url));
if (!existsSync(join(HERE, 'node_modules'))) {
  console.error(`dependencies missing: run "npm install" in ${HERE}`);
  process.exit(2);
}

const args = process.argv.slice(2);
const listArg = (flag) => {
  const i = args.indexOf(flag);
  return i === -1 ? null : args[i + 1].split(',');
};
const only = listArg('--only');
const skip = listArg('--skip') ?? [];
const root = resolve(args.find((a, i) => !a.startsWith('--') && !['--only', '--skip'].includes(args[i - 1])) ?? '.');

const stacks = detectStacks(root);
console.log(`project: ${root}`);
console.log(`stacks:  ${[...stacks.js.map((s) => `${s.typescript ? 'TypeScript' : 'JavaScript'}${s.react ? '/React' : ''} (${s.rel})`), ...stacks.python.map((s) => `Python (${s.rel})`)].join(', ') || 'none detected'}`);

const summary = [];
for (const step of steps(root, stacks)) {
  if ((only && !only.includes(step.key)) || skip.includes(step.key)) continue;
  console.log(`\n=== ${step.name}`);
  if (step.skip) {
    console.log(`skipped: ${step.skip}`);
    summary.push({ ...step, status: 'SKIP' });
    continue;
  }
  const r = spawnSync(step.cmd, step.args, {
    cwd: step.cwd,
    stdio: step.summary ? ['ignore', 'pipe', 'inherit'] : 'inherit',
    encoding: 'utf8',
    maxBuffer: 256 * 1024 * 1024,
    // Windows runs npm, uvx and the .cmd shims through a shell; node itself must not be.
    shell: process.platform === 'win32' && step.cmd !== process.execPath,
    env: { ...process.env, ...step.env },
  });
  if (step.summary) summarize(step.summary, r.stdout ?? '', root);
  const ok = r.status === 0;
  summary.push({ ...step, status: ok ? 'PASS' : step.gate ? 'FAIL' : 'READ' });
}

console.log('\n=== summary');
for (const s of summary) console.log(`${s.status.padEnd(4)}  ${s.name}${s.status === 'SKIP' ? `  - ${s.skip}` : ''}`);
if (stacks.js.some((s) => s.react)) console.log('\nReact project: also run react-health for React-specific checks.');
process.exit(summary.some((s) => s.status === 'FAIL') ? 1 : 0);
