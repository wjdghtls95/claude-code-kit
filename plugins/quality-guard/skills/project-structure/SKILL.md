---
name: project-structure
description: "A fixed process for deciding folder structure, sensible defaults, and how to make the linter enforce dependency direction. Use before creating a new project, a new top-level folder or a new module, or when someone asks where a file should go."
---

# Project Structure

There is no single right folder structure. Because there is none, **fix the process of deciding**. Do not skip it and leave everything flat, and do not split folders out of habit.

## 1. The order (every time, before a new folder or project)

1. **Look at the team's existing projects first.** If they already have a shape (for example feature folders with `module`, `controller`, `service`, `repository` and `dto/` inside, shared code in `common/`), follow it.
2. **Look at the framework's and tools' conventions.** If the official docs do not define a structure (NestJS explains modules but not folders), say so and follow the team's way. If a tool fixes a location (for example a migrations folder), use that location.
3. **Look at what changes together.** The files you open to change one rule should sit in one folder.
4. **Write down the decision and the reason** (section 3). If you cannot write a reason, it is not decided.

## 2. Defaults (when steps 1 to 3 give no other answer)

- Top level is **feature folders**. Inside a folder, the **end of the file name says the role** (`orders.service.ts`). Do not add `controllers/` and `services/` inside a feature folder: splitting three to eight files further only makes them harder to find.
- Code that several features use goes in `common/`. **Dependencies go one way, feature to common.** Features use each other only where needed, in one direction, with no cycles.
- The database schema (migrations) lives outside the server code, where the tool expects it. The server does not create tables at startup.
- File names are `<feature>.<role>.ts` (`customers.repository.ts`). Types and rules about one item use the singular (`order.types.ts`). No abbreviations.
- Create a folder when four or more files belong to the same feature, or a tool requires one. Not before.

## 3. Record the decisions

Keep a table in the project (in its README or its rules folder):

| Decision | Reason | Level |
|---|---|---|
| `src/{feature}/` feature folders | same as the team's other services | checked (opened that project) |
| one module per feature | framework docs on feature modules | source (the docs do not fix folders) |
| migrations in the tool's folder, server never creates tables | the tool's migration workflow | source |
| API field names kept as they are | shared with other clients, changing one side breaks the other | open (not decided) |

Level: **checked** (you verified it in code), **source** (from documentation), **open** (not decided yet, say so).

## 4. Let the linter keep the direction

Write the dependency direction once and let ESLint refuse imports that break it (`no-restricted-imports` in the project's `eslint.config.js`, next to the `code-standard` config):

```js
const FEATURE_RULES = {
  common: { forbid: ['**/customers/**', '**/orders/**'], message: 'common must not know feature folders' },
  customers: { forbid: ['**/orders/**'], message: 'orders uses customers, not the other way round' },
};

const ROLE_RULES = {
  controller: { files: ['*.controller.ts'], forbid: ['**/*.repository*'], message: 'controllers call services only' },
  repository: { files: ['*.repository.ts'], forbid: ['**/*.service*', '**/*.controller*'], message: 'repositories do SQL only' },
};

const restrict = rules => ({
  'no-restricted-imports': ['error', {
    patterns: rules.flatMap(rule => rule.forbid.map(group => ({ group: [group], message: rule.message }))),
  }],
});

// ESLint does not merge the same rule from two blocks, the last one wins.
// So build one block per (folder, role) pair that holds both rules.
const boundaries = Object.entries(FEATURE_RULES).flatMap(([folder, feature]) => [
  { files: [`**/${folder}/**/*.ts`], rules: restrict([feature]) },
  ...Object.values(ROLE_RULES).map(role => ({
    files: role.files.map(pattern => `**/${folder}/**/${pattern}`),
    rules: restrict([feature, role]),
  })),
]);
```

Then add `...boundaries` after the standard config in `export default`.

The patterns match the import text, not the file on disk. End role patterns with `*` (`**/*.repository*`) so they match `./x.repository`, `./x.repository.js` and `./x.repository.ts` alike. Check the rule once by adding a forbidden import and running the linter.

Write the direction in one picture as well, for people:

```
controller -> service -> repository -> database
                 |
                 v
           pure rules (know nothing about the framework or the database)
features -> common
```
