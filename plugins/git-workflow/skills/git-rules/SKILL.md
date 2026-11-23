---
name: git-rules
description: "Rules for working with git branches safely: sync the default branch, one branch per task, rebase instead of merge, no force-push without approval. Use at the start of a session and before creating a branch, committing or pushing."
---

Follow the project's own git conventions for names and message formats (see the `git-conventions` skill). These rules are about how to work with git day to day.

## Sync the default branch

- When you switch to the default branch, run `git fetch origin && git pull origin <default-branch>` before anything else.
- Before creating a branch, make sure the default branch is up to date:
  1. `git checkout <default-branch>`
  2. `git fetch origin`
  3. `git pull origin <default-branch>`
  4. `git checkout -b <new-branch>`
- If the pull fails because of local changes, stash first: `git stash`, pull, `git stash pop`.

## Session start

At the start of a session, return to the default branch first:
1. Check the current branch with `git branch --show-current`.
2. If you are not on the default branch and the working tree is clean, check it out and pull.
3. If you are not on the default branch and the working tree is dirty, stop and ask the user what to do with the uncommitted changes.

## One task, one branch

- One branch is one task is one pull request. Do not mix tasks.
- Create every feature or fix branch from the latest default branch, never from another feature branch.
- Before creating a branch, run `git status` and `git branch`. The working tree must be clean.
- Create a branch before you change any source code. Show the branch name and wait for the user's approval.
- Never commit or push directly to the default branch. Everything goes through a pull request, and CI must pass before merging.
- Never start a new branch while another one has uncommitted work.
- If a task depends on an unmerged branch, do not start it. Merge the dependency first, or stop and ask the user.
- Keep branches short-lived and merge within the same session when possible.

## Before you commit and push

- Run the tests of the packages you changed, using the project's own test command.
- Before pushing, check for dependency conflicts with other open branches.
- Show a short commit body with `- ` bullets when a commit contains two or more changes.

## Conflicts

- Before pushing, rebase onto the latest default branch: `git fetch origin`, then `git rebase origin/<default-branch>`, then run the tests again.
- Never merge the default branch into a feature branch. Rebase instead. Never run `git merge` between feature branches.
- If a rebase conflicts, stop at once and show the conflicting files to the user. Never auto-resolve conflicts.
- Never force-push without the user's approval, and after a rebase run the full validation (tests and build) before asking.
- If dependent branches have already mixed commits from different tasks, do not try to split them. Continue and note it in the pull request description.

## Pull request workflow

- After the push, create the pull request with `gh pr create --title "..." --body "..."`.
- Merge with squash: `gh pr merge --squash --delete-branch`, unless the project's convention says otherwise.
- After the merge, clean up in exactly this order:
  1. `git checkout <default-branch>`
  2. `git fetch origin`
  3. `git pull origin <default-branch>`
  4. `git branch -D <branch>` if the local branch remains (a squash-merged branch is not seen as merged, so `-d` refuses)
  5. `git status && git branch` to verify
- When you wrap up a session, report the pull request status: created, merged or not needed.
- Do not leave stale feature branches locally or remotely.
- For anything these rules and the project's conventions do not cover, ask the user before you proceed.
