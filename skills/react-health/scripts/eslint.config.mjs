import tseslint from 'typescript-eslint';
import sonarjs from 'eslint-plugin-sonarjs';
import reactHooks from 'eslint-plugin-react-hooks';
import noEffect from 'eslint-plugin-react-you-might-not-need-an-effect';

/* The antipattern scan, run against whichever app is the working directory:

     cd <app> && <this folder>/node_modules/.bin/eslint -c <this folder>/eslint.config.mjs src

   SonarJS for general smells, the React Compiler's hook rules, the
   you-might-not-need-an-effect rules, and the doctrine's own rule 13. */

/* A function written directly in a JSX attribute - including one picked by
   `?:` or `&&` - or a `.bind` there. Declared above the return and passed by
   name, it is allowed; a callback that runs during render (`items.map`) is not
   a JSX attribute and is not matched. */
const INLINE = 'Declare this function above the return and pass it by name (react-doctrine 13).';
const value = 'JSXAttribute > JSXExpressionContainer';
const inlineFunction = [
  `${value} > :matches(ArrowFunctionExpression, FunctionExpression)`,
  `${value} > :matches(ConditionalExpression, LogicalExpression) > :matches(ArrowFunctionExpression, FunctionExpression)`,
  `${value} > CallExpression[callee.property.name="bind"]`,
].map((selector) => ({ selector, message: INLINE }));

/* REACT_HEALTH_ONLY=doctrine runs the doctrine rule alone, so it can gate a
   build while the wider scan is only read. */
const DOCTRINE_ONLY = process.env.REACT_HEALTH_ONLY === 'doctrine';

export default tseslint.config(
  { ignores: ['**/dist/**', '**/node_modules/**'] },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: { projectService: true, tsconfigRootDir: process.cwd() },
    },
    linterOptions: { reportUnusedDisableDirectives: 'off' },
  },
  ...(DOCTRINE_ONLY
    ? []
    : [
        sonarjs.configs.recommended,
        reactHooks.configs.flat['recommended-latest'] ?? reactHooks.configs['recommended-latest'],
        noEffect.configs.strict,
      ]),
  {
    files: ['**/*.tsx'],
    rules: { 'no-restricted-syntax': ['error', ...inlineFunction] },
  },
);
