---
name: git-conventions
description: "Default git conventions: branch structure and names, commit message format and scope, merge strategy, conflict handling, pull request checklist. Use when naming a branch, writing a commit message or deciding how to merge."
---

These are defaults. If the project documents its own conventions, follow those and treat this skill as the fallback.

## Branch structure

Before the first production release:

```
main       default branch, deploys directly
feat/*     work branches
fix/*
chore/*
```

- Create `feat/*` from `main` and merge back into `main`.
- Never push to `main` directly. Use pull requests.
- Even after a pull request is merged, do not commit progress notes straight to `main`. Put them on a new branch and merge them through a pull request, otherwise local and remote `main` diverge.

After production exists:

```
main       production only
develop    deploys to the dev server, becomes the default branch
feat/*     work branches
```

- Create `feat/*` from `develop` and merge into `develop`.
- `develop` to `main` needs a pull request and a deep review before the merge.

## Branch names

| Prefix | Use |
|--------|-----|
| `feat/<desc>` | new feature (with its tests) |
| `fix/<desc>` | bug fix |
| `chore/<desc>` | configuration, dependencies, refactoring |
| `docs/<desc>` | documentation only |
| `ci/<desc>` | CI/CD changes |

`<desc>` is short and in kebab-case. In a repository with several apps, keep one branch per app and merge each on its own. If an API must exist first, merge the server branch before starting the client branch.

## Commit messages

Format: `<type>(<scope>): <description>`

- **scope** is one short lowercase name for the area that changed, for example `auth`, `chat`, `core`, `web`. It is optional. Use one name, not a path. Put finer detail into the description after the colon. If the project already has a list of scopes, use that list.
- **description** is a short imperative sentence in the language the project agreed on, English by default.
- If the body lists two or more changes, separate them with `- ` bullets.

| Type | Use |
|------|-----|
| `feat` | new feature |
| `fix` | bug fix |
| `test` | tests only |
| `docs` | documentation |
| `refactor` | refactoring and performance work |
| `chore` | configuration, dependencies |
| `ci` | CI/CD changes |
| `revert` | reverting a commit |

Do not put internal planning labels in a message ("Part 10", "Scenario A", ticket batches). Describe what was built or changed.

```
Bad:  feat(task): Part 10, scenario A morning briefing
Good: feat(task): add daily briefing setting with a morning cron job
```

Metadata-only commits follow the same rule. Describe the real change, not the checkbox you ticked.

## Merge strategy

- Always squash merge.
- Before production: `feat` into `main` through a pull request (direct pushes to `main` are not allowed).
- After production: `feat` into `develop` through a pull request, `develop` into `main` through a pull request with a deep review first.

## Merge conflicts

Prevention first: keep branches short-lived, within a few days. A long-lived branch drifts from its base.

When a conflict happens:

```bash
git rebase origin/<default-branch>   # replay your commits on top of the latest default branch
# fix the conflicting files by hand
git rebase --continue
```

A conflict means two branches changed the same lines differently. If a rebase seems to have lost commits, run `git reflog` to see every recent move of HEAD and `git checkout <hash>` to go back. Local commits stay in the reflog for at least 30 days.

## Pull request checklist

Before merging:
- [ ] A deep review is done and has no critical findings (for security, database schema or shared infrastructure changes)
- [ ] You tested it locally
- [ ] Any new environment variable is added to the example environment file
