---
name: land
description: "Merge a reviewed pull request, delete its branch and return to the default branch. Use when the review is clean and the user asks to merge or land the PR."
---

Run this after the review is clean and the pull request is ready to merge.

## Step 1: check the PR status

Run `gh pr view --json number,title,state,mergeable`.

- No open PR: say so and stop.
- `mergeable` is CONFLICTING: say there are conflicts to resolve first, and stop.

## Step 2: confirm

Show this and wait for the user's confirmation:

```
PR #[N]: [title]
This will squash merge, delete the branch and check out the default branch. Go ahead?
```

If the answer is no, stop.

## Step 3: squash merge

Run `gh pr merge --squash --delete-branch`. Use a different merge method only if the project's convention says so (see the `git-conventions` skill).

## Step 4: return to the default branch

```bash
git checkout <default-branch>
git pull origin <default-branch>
```

Then say the merge is done and the default branch is checked out.
