---
name: ship
description: "Commit, push and open a pull request in one go after coding is done, then decide which review the change needs. Use when the user says ship it, or asks to commit, push and open a PR."
---

Automates the delivery loop once the coding is done.

## Arguments

- no argument: generate the commit message from the diff and confirm it before applying
- a quoted message: use it as given
- `--no-review`: skip the review step

## Step 1: check the state

Run `git status` and `git diff HEAD --stat`. If there is nothing to commit, say so in one line and stop.

## Step 2: prepare the commit message

If the user gave a message, use it as is and go to Step 3.

Otherwise:
- Read the full `git diff HEAD`.
- Write a message that follows the project's commit convention (see the `git-conventions` skill): `<type>(<scope>): <description>`, with the scope naming the area that changed.
- Show it as `Commit message: [message]. OK, or edit?` and wait for confirmation. If the user edits it, use their version.

## Step 3: stage and commit

Run `git status --short` to list modified and new files. Stage only the relevant files by name. Do not use `git add -A`, and never stage `.env` files or anything that looks like a secret. Then run `git commit -m "[message]"`.

## Step 4: push

Run `git push origin <current-branch>`. If no upstream is set, run `git push -u origin <current-branch>`. Never push to the default branch directly. Never force-push without the user's approval.

## Step 5: pull request

Run `gh pr list --head <current-branch> --state open --json number,title`.

- A PR exists: say "PR #N is already open, the new commit was added" and go to Step 6.
- No PR: run `gh pr create --fill` and print the PR URL.

## Step 6: review decision

With `--no-review`, say "review skipped" and stop.

Otherwise read the changed file paths and apply this rule of thumb, using the first level that matches:

- **Deep review** if the change touches authentication or sessions, shared libraries, database schema, payments, permission checks, encryption, or merges into the production branch
- **Standard review** if it changes an API contract, finishes a new module, adds an external API or background worker, changes middleware or the error-handling pattern, touches transaction logic, or has 6 to 15 files
- **Skip** if none of that applies and the change is 1 to 5 files

Say which level you chose and why in one line, then run the matching review, for example the built-in `/code-review` command for a standard review. A deep review is a larger multi-agent review that the user starts themselves, so recommend it instead of launching it.
