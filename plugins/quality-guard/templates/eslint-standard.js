// Code quality standard for any TypeScript project (ESLint flat config). Reasons: the quality-guard code-standard skill.
// Copy this file into the project unchanged. Put what differs per project (folder dependency rules, contract names
// that must stay as they are) in the project's own eslint.config.js, not here.
import js from '@eslint/js';
import stylistic from '@stylistic/eslint-plugin';
import tseslint from 'typescript-eslint';

const MAX_FUNCTION_LINES = 50;
const MAX_FILE_LINES = 300;
const MAX_LINE_LENGTH = 120;
const MAX_PARAMETERS = 4;
const MAX_COMPLEXITY = 10;
const MAX_NESTING = 2;

const SOURCE_FILES = ['**/*.ts', '**/*.tsx'];
const TEST_FILES = [
  '**/test/**/*.{ts,tsx}', '**/tests/**/*.{ts,tsx}', '**/__tests__/**/*.{ts,tsx}', '**/*.{test,spec}.{ts,tsx}',
];

// Abbreviations make the reader expand them. Established terms (id, url) are not on the list, so they stay allowed.
const ABBREVIATIONS = [
  'tx', 'req', 'res', 'ctx', 'cfg', 'conf', 'msg', 'err', 'dev', 'db', 'repo', 'svc', 'ctrl', 'btn', 'idx', 'val',
  'num', 'str', 'obj', 'arr', 'fn', 'cb', 'tmp', 'prev', 'curr',
];
// Matches only when one word of a camelCase, PascalCase, snake_case or UPPER_SNAKE name equals an abbreviation
// (so "postgres" does not match "res")
const lowerWords = ABBREVIATIONS.join('|');
const capitalizedWords = ABBREVIATIONS.map(word => `${word[0].toUpperCase()}${word.slice(1)}`).join('|');
const upperWords = ABBREVIATIONS.map(word => word.toUpperCase()).join('|');
const abbreviationAsWord = [
  `^(${lowerWords})([A-Z0-9_]|$)`,
  `[a-z0-9_](${capitalizedWords})([A-Z0-9_]|$)`,
  `^(${capitalizedWords})([A-Z0-9_]|$)`,
  `(^|_)(${upperWords}|${lowerWords})(_|$)`,
].join('|');

const noAbbreviation = { regex: abbreviationAsWord, match: false };

export function codeStandard({ tsconfigRootDir }) {
  return tseslint.config(
    { ignores: ['**/node_modules/**', '**/dist/**', '**/coverage/**', '**/*.config.{js,ts}'] },
    js.configs.recommended,
    ...tseslint.configs.recommendedTypeChecked.map(config => ({ ...config, files: SOURCE_FILES })),
    stylistic.configs.customize({ indent: 2, quotes: 'single', semi: true, commaDangle: 'always-multiline', arrowParens: false }),
    {
      files: SOURCE_FILES,
      languageOptions: { parserOptions: { projectService: true, tsconfigRootDir } },
      rules: {
        // Safety: types and async code you can trust
        '@typescript-eslint/no-explicit-any': 'error',
        '@typescript-eslint/no-non-null-assertion': 'error',
        '@typescript-eslint/no-floating-promises': 'error',
        '@typescript-eslint/switch-exhaustiveness-check': 'error',
        '@typescript-eslint/consistent-type-imports': ['error', { fixStyle: 'inline-type-imports' }],
        'eqeqeq': ['error', 'always'],
        'no-console': 'error',

        // Reading: short, shallow functions with few parameters
        'max-lines-per-function': ['error', { max: MAX_FUNCTION_LINES, skipBlankLines: true, skipComments: true }],
        'max-lines': ['error', { max: MAX_FILE_LINES, skipBlankLines: true, skipComments: true }],
        'max-depth': ['error', MAX_NESTING],
        'max-params': ['error', MAX_PARAMETERS],
        'complexity': ['error', MAX_COMPLEXITY],
        'no-nested-ternary': 'error',
        'no-else-return': 'error',
        'no-param-reassign': 'error',
        'prefer-const': 'error',
        'curly': ['error', 'all'],
        'no-empty': ['error', { allowEmptyCatch: false }],
        'no-magic-numbers': ['error', { ignore: [0, 1, -1, 2], ignoreArrayIndexes: true, enforceConst: true }],
        '@stylistic/max-len': ['error', { code: MAX_LINE_LENGTH, ignoreUrls: true, ignoreStrings: true, ignoreTemplateLiterals: true, ignoreRegExpLiterals: true, ignoreComments: true }],

        // Names: no abbreviations, no single letters, booleans start with is/has/can/should
        'id-length': ['error', { min: 2, exceptions: ['_'], properties: 'never' }],
        '@typescript-eslint/naming-convention': [
          'error',
          { selector: ['variable', 'parameter', 'function', 'method', 'class', 'typeLike'], format: null, custom: noAbbreviation },
          { selector: 'variable', types: ['boolean'], format: ['PascalCase'], prefix: ['is', 'has', 'can', 'should'] },
        ],

        // Rhythm: one blank line between statements (imports may stay together)
        '@stylistic/padding-line-between-statements': [
          'error',
          { blankLine: 'always', prev: '*', next: '*' },
          { blankLine: 'any', prev: 'import', next: 'import' },
          { blankLine: 'any', prev: 'directive', next: 'directive' },
        ],
        '@stylistic/brace-style': ['error', '1tbs', { allowSingleLine: false }],
        '@stylistic/operator-linebreak': ['error', 'after', { overrides: { '?': 'before', ':': 'before' } }],
        '@stylistic/lines-between-class-members': ['error', 'always', { exceptAfterSingleLine: false }],
      },
    },
    {
      // Tests: example numbers, long describe blocks and consecutive expects do not hurt reading
      files: TEST_FILES,
      rules: {
        'no-magic-numbers': 'off',
        'max-lines-per-function': 'off',
        'max-lines': 'off',
        '@typescript-eslint/no-unsafe-assignment': 'off',
        '@typescript-eslint/no-unsafe-member-access': 'off',
        '@stylistic/padding-line-between-statements': [
          'error',
          { blankLine: 'always', prev: '*', next: '*' },
          { blankLine: 'any', prev: 'import', next: 'import' },
          { blankLine: 'any', prev: 'expression', next: 'expression' },
        ],
      },
    },
  );
}
