import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';

export const SKIP_DIRS = new Set([
  'node_modules', 'dist', 'build', 'out', 'coverage', '.git', '.venv', 'venv', 'env',
  '__pycache__', '.next', '.turbo', '.cache', 'vendor', '.pytest_cache', '.mypy_cache', '.ruff_cache',
]);

const readJson = (path) => {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return {};
  }
};

const PY_MARKERS = ['pyproject.toml', 'requirements.txt', 'setup.py'];

/* Every JS/TS and Python project under root, three levels deep, so a repo
   holding a web app and a Python tools folder gets both sets of checks. */
export function detectStacks(root) {
  const js = [];
  const python = [];
  const visit = (dir, depth) => {
    const names = readdirSync(dir);
    if (names.includes('package.json')) {
      const pkg = readJson(join(dir, 'package.json'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };
      js.push({
        dir,
        rel: relative(root, dir) || '.',
        typescript: Boolean(deps.typescript) || names.includes('tsconfig.json'),
        react: Boolean(deps.react),
        scripts: pkg.scripts ?? {},
        installed: names.includes('node_modules'),
      });
    }
    if (PY_MARKERS.some((m) => names.includes(m))) python.push({ dir, rel: relative(root, dir) || '.' });
    if (depth === 3) return;
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory() && !SKIP_DIRS.has(entry.name) && !entry.name.startsWith('.')) visit(join(dir, entry.name), depth + 1);
    }
  };
  visit(root, 0);
  return { js, python, git: existsSync(join(root, '.git')) };
}

export const hasPyrightConfig = (dir) =>
  existsSync(join(dir, 'pyrightconfig.json')) ||
  (existsSync(join(dir, 'pyproject.toml')) && readFileSync(join(dir, 'pyproject.toml'), 'utf8').includes('[tool.pyright]'));

export const hasRuffConfig = (dir) =>
  existsSync(join(dir, 'ruff.toml')) ||
  existsSync(join(dir, '.ruff.toml')) ||
  (existsSync(join(dir, 'pyproject.toml')) && readFileSync(join(dir, 'pyproject.toml'), 'utf8').includes('[tool.ruff'));
