---
name: pr-check
description: "Check open pull requests, leftover branches, CI status and commit convention. Use when the user asks for a git health check or wants to clean up branches."
---

## 1. Open pull requests

- Run `gh pr list --state open` in each repository you are asked about.
- Mark pull requests with failing CI.

## 2. Recently merged pull requests

- Run `gh pr list --state merged --limit 5`.
- Check whether a merged pull request left its remote branch behind (this happens when `gh pr merge --delete-branch` was not used).
- List the branches that were not deleted and ask whether to delete them.

## 3. Clean up local branches

- Run `git fetch --prune`, then `git branch -vv`.
- A branch marked `: gone` has no remote anymore. After a squash merge that means it is done and is a deletion candidate.
- Delete in this order:
  1. If the branch to delete is the current one, run `git checkout <default-branch>` first
  2. `git branch -D <branch>` (a squash-merged branch needs `-D`, not `-d`)
  3. `git status && git branch` to confirm the result

## 4. Commit convention

- Run `git log --oneline -10`.
- Mark commits that break the convention (see the `git-conventions` skill).
- Look for commits pushed to the default branch without a pull request.

## 5. Unpushed commits

- Run `git log origin/<default-branch>..HEAD --oneline` and list commits that were not pushed.

## Result

- Give each item a pass, warning or fail.
- Delete branches only after the user approves.
- If a progress file exists, offer to add one line about this check to it, and add it only if the user agrees. Say in one line what you wrote and where.

## Progress file lookup (shared by every skill that reads or updates project progress)

Several skills in this kit read or update a file that tracks the project's progress. Find it in this order and use the first match:

1. The path in `progress_file` inside `.claude-kit.json` at the project root
2. `docs/progress/current.md`
3. `progress.md` at the project root

If none exists, skip the progress step, say so in one line, and continue with the rest of the skill. Never create the file unless the user asks. A starting template is in `templates/progress.template.md` of this plugin.
