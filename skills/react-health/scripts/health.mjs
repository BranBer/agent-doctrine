import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

/* The static half of react-health, run from the app's folder:

     cd <app> && node ~/.claude/skills/react-health/scripts/health.mjs [--ban "…"]

   Build, inline JSX functions, antipatterns, markup-level a11y, unused code,
   comment pointers and repeated raw values. Extra arguments are passed to
   comments.mjs. Build, inline functions, comments and repeats fail the run;
   antipatterns, a11y lint and knip are printed for a person to read, since a
   finding there is a judgement and most projects start with a backlog. */
const HERE = dirname(fileURLToPath(import.meta.url));
const bin = (name) => join(HERE, 'node_modules', '.bin', process.platform === 'win32' ? `${name}.cmd` : name);
if (!existsSync(bin('eslint'))) {
  console.error(`dependencies missing: run "npm install" in ${HERE}`);
  process.exit(2);
}
const extra = process.argv.slice(2);
const hasBuild = existsSync('package.json') && /"build"\s*:/.test(readFileSync('package.json', 'utf8'));

const steps = [
  hasBuild && { name: 'build', cmd: 'npm', args: ['run', 'build'], gate: true },
  { name: 'inline JSX functions', cmd: bin('eslint'), args: ['-c', join(HERE, 'eslint.config.mjs'), 'src'], env: { REACT_HEALTH_ONLY: 'doctrine' }, gate: true },
  { name: 'antipatterns', cmd: bin('eslint'), args: ['-c', join(HERE, 'eslint.config.mjs'), 'src'], gate: false },
  { name: 'a11y lint', cmd: bin('oxlint'), args: ['--jsx-a11y-plugin', '-W', 'jsx-a11y', 'src'], gate: false },
  { name: 'unused code', cmd: bin('knip'), args: ['--no-progress'], gate: false },
  { name: 'comments', cmd: process.execPath, args: [join(HERE, 'comments.mjs'), 'src', ...extra], gate: true },
  { name: 'repeated values', cmd: process.execPath, args: [join(HERE, 'repeats.mjs'), 'src'], gate: true },
].filter(Boolean);

const summary = [];
for (const step of steps) {
  console.log(`\n=== ${step.name}`);
  const r = spawnSync(step.cmd, step.args, {
    stdio: 'inherit',
    // Windows runs npm and the .cmd shims through a shell; node itself must not be, or a `|` in --ban is a pipe.
    shell: process.platform === 'win32' && step.cmd !== process.execPath,
    env: { ...process.env, ...step.env },
  });
  const ok = r.status === 0;
  summary.push({ ...step, ok });
}

console.log('\n=== summary');
for (const s of summary) console.log(`${s.ok ? 'PASS' : s.gate ? 'FAIL' : 'READ'}  ${s.name}`);
process.exit(summary.some((s) => s.gate && !s.ok) ? 1 : 0);
