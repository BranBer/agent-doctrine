import { existsSync } from 'node:fs';
import { delimiter, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { hasPyrightConfig, hasRuffConfig } from './stacks.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const WIN = process.platform === 'win32';
const RUFF = 'ruff@0.17.2';

/* winget puts its command-line tools here, and a shell opened before the
   install has no PATH entry for it yet. */
const EXTRA_PATHS = WIN && process.env.LOCALAPPDATA ? [join(process.env.LOCALAPPDATA, 'Microsoft', 'WinGet', 'Links')] : [];

export function which(name) {
  const dirs = [...(process.env.PATH ?? '').split(delimiter), ...EXTRA_PATHS];
  const exts = WIN ? ['.exe', '.cmd', '.bat', ''] : [''];
  for (const dir of dirs) for (const ext of exts) if (dir && existsSync(join(dir, name + ext))) return join(dir, name + ext);
  return null;
}

const bin = (name) => join(HERE, 'node_modules', '.bin', WIN ? `${name}.cmd` : name);
const ESLINT_CONFIG = join(HERE, 'eslint.config.mjs');
const IGNORE = '**/node_modules/**,**/dist/**,**/build/**,**/coverage/**,**/.venv/**,**/venv/**,**/__pycache__/**,**/*.min.js';

const INSTALL = {
  gitleaks: 'winget install --id Gitleaks.Gitleaks -e',
  'osv-scanner': 'winget install --id Google.OSVScanner -e',
  uvx: 'install uv: https://docs.astral.sh/uv/',
  pyright: 'npm install -g pyright',
  python: 'install Python 3',
};

const need = (key, cmd) => (which(cmd) ? null : `${INSTALL[key] ?? `install ${cmd}`}`);

/* One step per tool per project folder. A step is either runnable -
   { key, name, cmd, args, cwd, gate, env?, summary? } - or skipped with the
   line that fixes it: { key, name, skip }. */
export function steps(root, stacks) {
  const out = [];
  const add = (step) => out.push(step);

  for (const s of stacks.js) {
    const at = s.rel === '.' ? '' : ` (${s.rel})`;
    const tsconfig = existsSync(join(s.dir, 'tsconfig.json'));
    if (s.typescript && tsconfig) {
      if (!s.installed) add({ key: 'types', name: `types${at}`, skip: `node_modules missing - run npm install in ${s.rel}` });
      else if (s.scripts.typecheck) add({ key: 'types', name: `types${at}`, cmd: 'npm', args: ['run', 'typecheck'], cwd: s.dir, gate: true });
      else {
        const local = join(s.dir, 'node_modules', '.bin', WIN ? 'tsc.cmd' : 'tsc');
        add({ key: 'types', name: `types${at}`, cmd: existsSync(local) ? local : bin('tsc'), args: ['--noEmit', '-p', 'tsconfig.json'], cwd: s.dir, gate: true });
      }
    }
    const eslint = { cmd: bin('eslint'), cwd: s.dir };
    add({ key: 'cycles', name: `import cycles${at}`, ...eslint, args: ['-c', ESLINT_CONFIG, '.'], env: { HEALTH_ONLY: 'cycles' }, gate: true });
    add({ key: 'lint', name: `lint and smells${at}`, ...eslint, args: ['-c', ESLINT_CONFIG, '-f', 'json', '.'], gate: false, summary: 'eslint' });
    if (s.installed) add({ key: 'unused', name: `unused code${at}`, cmd: bin('knip'), args: ['--no-progress'], cwd: s.dir, gate: false });
    else add({ key: 'unused', name: `unused code${at}`, skip: `node_modules missing - run npm install in ${s.rel}` });
  }

  for (const s of stacks.python) {
    const at = s.rel === '.' ? '' : ` (${s.rel})`;
    const uvx = need('uvx', 'uvx');
    const ruffArgs = ['check', ...(hasRuffConfig(s.dir) ? [] : ['--config', join(HERE, 'ruff.toml')]), '.'];
    add(uvx ? { key: 'ruff', name: `ruff${at}`, skip: uvx } : { key: 'ruff', name: `ruff${at}`, cmd: 'uvx', args: [RUFF, ...ruffArgs, '--statistics'], cwd: s.dir, gate: false });
    const pyright = need('pyright', 'pyright');
    add(pyright ? { key: 'types', name: `types${at}`, skip: pyright } : { key: 'types', name: `types${at}`, cmd: 'pyright', args: ['.'], cwd: s.dir, gate: hasPyrightConfig(s.dir) });
    add(uvx ? { key: 'unused', name: `unused code${at}`, skip: uvx } : { key: 'unused', name: `unused code${at}`, cmd: 'uvx', args: ['vulture', '.', '--min-confidence', '80', '--exclude', '.venv,venv,node_modules'], cwd: s.dir, gate: false });
    const python = need('python', 'python');
    add(python ? { key: 'cycles', name: `import cycles${at}`, skip: python } : { key: 'cycles', name: `import cycles${at}`, cmd: 'python', args: [join(HERE, 'pycycles.py'), '.'], cwd: s.dir, gate: true });
  }

  const reactDirs = stacks.js.filter((s) => s.react).flatMap((s) => ['--react', s.dir]);
  add({ key: 'sizes', name: 'file sizes', cmd: process.execPath, args: [join(HERE, 'sizes.mjs'), root, ...reactDirs], cwd: root, gate: false });
  add({ key: 'duplication', name: 'duplication', cmd: bin('jscpd'), args: [root, '--ignore', IGNORE, '--min-tokens', '70', '--reporters', 'console', '--silent', '--exit-code', '1'], cwd: root, gate: false });

  const gitleaks = which('gitleaks');
  if (!gitleaks) add({ key: 'secrets', name: 'committed secrets', skip: INSTALL.gitleaks });
  else if (!stacks.git) add({ key: 'secrets', name: 'committed secrets', skip: 'not a git repository - gitleaks scans committed history' });
  else add({ key: 'secrets', name: 'committed secrets', cmd: gitleaks, args: ['git', root, '--no-banner', '--redact', '--verbose', '--log-level', 'warn'], cwd: root, gate: true });

  const osv = which('osv-scanner');
  add(osv ? { key: 'deps', name: 'vulnerable dependencies', cmd: osv, args: ['scan', 'source', '-r', '--format', 'json', '--verbosity', 'error', root], cwd: root, gate: false, summary: 'osv' } : { key: 'deps', name: 'vulnerable dependencies', skip: INSTALL['osv-scanner'] });

  add(which('uvx')
    ? { key: 'semgrep', name: 'security patterns', cmd: 'uvx', args: ['semgrep', 'scan', '--config', 'p/default', '--metrics=off', '--quiet', '--error', '--exclude', 'node_modules', '--exclude', 'dist', root], cwd: root, gate: false }
    : { key: 'semgrep', name: 'security patterns', skip: INSTALL.uvx });

  return out;
}
