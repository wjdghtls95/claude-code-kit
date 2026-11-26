---
name: code-standard
description: "A code quality standard for TypeScript projects that a linter checks, plus the review rules a linter cannot check and a safe refactoring procedure. Use when setting up linting in a TypeScript project, writing or reviewing TypeScript code against a shared standard, or refactoring without changing behavior."
---

# Code Standard (TypeScript)

Goal: the next person who opens the code knows **where a change lives and what it affects within a minute**.

Every rule here is either checked by the bundled ESLint config or listed under "Rules people check". A rule that cannot be checked is not written as a rule.

## 1. Set it up in a project (5 minutes)

1. Copy `<base directory>/../../templates/eslint-standard.js` into the project (the base directory of this skill is shown when it loads). Keep it unchanged.
2. Install: `npm i -D eslint @eslint/js typescript-eslint @stylistic/eslint-plugin` (ESLint 9 flat config).
3. In the project's `eslint.config.js`:
   ```js
   import { codeStandard } from './eslint-standard.js';

   export default [...codeStandard({ tsconfigRootDir: import.meta.dirname })];
   ```
4. Put only what differs per project in `eslint.config.js`: folder dependency rules (see the `project-structure` skill) and names that are part of an external contract.
5. Run `npx eslint . --fix` for formatting (blank lines, braces, indentation), then fix the rest by hand.
6. Done means `lint`, `typecheck` and `test` all pass with zero lint violations.

**Evidence level.** The principles come from well-known sources (Clean Code, A Philosophy of Software Design, the Node.js best practices list). The numbers (50-line functions, nesting depth 2, complexity 10, 4 parameters, 300-line files, 120-character lines) are conventions, not proven optima. To change one, edit the constant at the top of `eslint-standard.js`, in one place.

## 2. What the linter enforces (zero violations)

| Area | Rule | Why |
|---|---|---|
| Safety | no `any`, no `!`, no floating promises, exhaustive `switch`, `===` only | you can trust types and async code when you change it |
| Safety | no `console` (use a logger or `process.stdout.write`) | one place decides what gets logged |
| Reading | functions 50 lines, files 300 lines, nesting 2, parameters 4, complexity 10 | fits on one screen and in one head |
| Reading | no nested ternaries, no `else` after `return`, no parameter reassignment, braces on every `if` | the flow reads top to bottom |
| Reading | no magic numbers (except 0, 1, -1, 2), no empty `catch` | numbers have names and errors are not swallowed |
| Names | no single letters, no abbreviations (`tx`, `req`, `res`, `ctx`, `db`, `err`, `msg`...), boolean variables start with `is`, `has`, `can`, `should` | the reader does not have to expand names |
| Rhythm | one blank line between statements (imports may stay together), blank lines between class members | a dense block hides the flow |
| Format | 2-space indent, single quotes, semicolons, trailing commas, 120 characters, one statement per line, braces on their own lines | no format debates and smaller diffs |
| Structure | folder dependency direction (set in the project's `eslint.config.js`) | the linter, not a document, keeps the structure |

Tests are the only exception: example numbers, long `describe` blocks and consecutive `expect` lines are allowed.

The blank line rule separates even consecutive `const` lines. That makes multi-line steps taller, and some teams prefer to group declarations of the same kind. To allow that, add `{ blankLine: 'any', prev: 'const', next: 'const' }` to `padding-line-between-statements`.

## 3. Rules people check (in review)

**Comments say only what the code cannot, in one line.**
- Write: why it is done this way, units and limits, traps, names that a contract forbids changing.
- Do not write: comments that repeat the code, comments that are only an issue number.
- At a module boundary (an exported class or function), one `/** */` line says what it is responsible for.

```ts
// bad: multiply by 5
const windowMs = 5 * 60_000;

// good: a retry counts as the same request for five minutes either side, not within a fixed slot
const RETRY_WINDOW_MS = 300_000;
```

**Separate what changes from what does not.**
- Values that change (limits, time windows, error codes, routes, header names, environment variable names, SQL statements) get a name and live in one place, for example `policy.constants.ts` and `error-codes.ts`. Fixed domain values are an `enum`; shapes are types, interfaces or schemas (for example zod). Call sites do not write the numbers or strings.
- Tests are the exception: request and response examples spell contract strings out (`'order_paid'`, `'/v1/orders'`) instead of importing the constant, so a changed enum value or route fails a test.
- Rules that do not change are pure functions from input to output. They know nothing about the framework, the database or the clock.
- Side effects (database, clock, network) are injected at the edge, so tests can move time and swap the database.
- Make an abstraction when a second implementation is needed. Boundaries such as the clock, the database and HTTP are injected from the start.

**Deep modules.** A small interface that does a lot inside. No thin wrappers that only rename. When the same code appears in a third place, merge it.

**One error shape.** Where errors are thrown and where they are caught is fixed (one error class, for example `ApiError`), and nothing swallows them. Catch `error: unknown` and narrow it with a type guard.

**Type boundaries.** Use `as` only where a driver can return `any` (the database entry point) and say why in a comment. Replace every other `as` with a type guard.

**Function names are verb plus object** (`findUnpaidInvoices`). Not `check`, `handle`, `process`, `data` or `info` alone.

## 4. Refactoring without changing behavior

1. Write down the baseline first: number of tests, type errors, lint violations.
2. Do not change the expected values of existing tests. Change structure only (helpers, names).
3. Run typecheck and tests after every step.
4. **For regular expressions, parsers and other code that tests miss easily, run the old and the new implementation on the same thousands of inputs and compare.** In one project a rewritten parser passed all 29 existing tests and still disagreed on 1,451 of 20,000 real inputs.
5. Keep every difference you find as a regression test, then bring the bug back on purpose and check that the test fails (see "Do the tests really guard the code?" in the `tdd-rule` skill).
6. If you touched locks, transactions or SQL, run a concurrency test against the real database.
7. Report the numbers before and after (lint violations, tests).

## 5. Before saying it is done

Run lint, typecheck and tests (for example `npm run lint && npm run typecheck && npm test`). If one fails, it is not done. Before writing a new rule into a document, check whether the linter can enforce it.
