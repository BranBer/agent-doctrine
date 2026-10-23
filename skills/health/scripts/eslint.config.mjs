import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { includeIgnoreFile } from '@eslint/compat';
import { createTypeScriptImportResolver } from 'eslint-import-resolver-typescript';
import { importX } from 'eslint-plugin-import-x';
import sonarjs from 'eslint-plugin-sonarjs';
import tseslint from 'typescript-eslint';

/* The project's own ESLint config is never read: this runs from the health
   skill's folder against whatever project is the working directory.

   HEALTH_ONLY=cycles runs the import-cycle rule alone, so it can gate while
   the wider scan is only read. Inline directives are ignored, because a
   project's `eslint-disable` comments name rules from plugins this config
   does not load, and ESLint reports each of those as an error. */
const CYCLES_ONLY = process.env.HEALTH_ONLY === 'cycles';
// Build output and anything else the project does not track is not its code.
const GITIGNORE = join(process.cwd(), '.gitignore');

export default tseslint.config(
  { ignores: ['**/node_modules/**', '**/dist/**', '**/build/**', '**/coverage/**', '**/*.min.js', '**/*.d.ts'] },
  ...(existsSync(GITIGNORE) ? [includeIgnoreFile(GITIGNORE)] : []),
  {
    files: ['**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}'],
    // One parser for every file: it reads TS by extension and JSX in .js too.
    languageOptions: { parser: tseslint.parser, parserOptions: { ecmaFeatures: { jsx: true } } },
    plugins: { 'import-x': importX },
    linterOptions: { noInlineConfig: true, reportUnusedDisableDirectives: 'off' },
    settings: {
      // Without these, import-x treats a .ts import as a file it cannot parse
      // and follows nothing through it - every TS cycle passes unseen.
      'import-x/extensions': ['.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs'],
      'import-x/parsers': { '@typescript-eslint/parser': ['.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs'] },
      'import-x/resolver-next': [createTypeScriptImportResolver({ alwaysTryTypes: true, project: process.cwd() })],
    },
    rules: { 'import-x/no-cycle': ['error', { ignoreExternal: true }] },
  },
  ...(CYCLES_ONLY ? [] : [...tseslint.configs.recommended, sonarjs.configs.recommended]),
);
