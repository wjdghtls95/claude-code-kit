---
name: wrap-up
description: "Close out a work session: sync the progress file, summarize what was done, name the first task for next time, and report the git state without changing it. Use when the user says wrap up, end the session, clean up the session, or is about to run /clear or /compact."
---

Run these steps in order. Do only the steps that apply.

## Step 1: sync the progress file (before any summary)

Find what this session produced that the progress file does not show yet, and update the file. Follow the layout the file already has. If it has none, use the layout of `templates/progress.template.md`.

- Finished items: tick them or move them to the completed list with the date
- New problems or review issues found: add them
- A changed priority: reorder or relabel
- A new decision: record it, and remove an open question that is now answered
- Open topics that were saved or confirmed in this session: update their working notes
- Work that is still in progress: record it as in progress with its current state, so the next session can pick it up

Then say in one line what you changed, as a short list:

```
Progress file updated:
- [added / changed / ticked] [item]
```

If nothing needed to change, say "No progress file changes this session". A session that was only discussion still counts: record the decisions and priority changes.

## Step 2: summary

```
This session:
- [what was done, 3 lines at most]

First task next session:
- [the highest-priority unfinished item in the progress file after Step 1]
```

"First task next session" is read from the progress file after Step 1, so it matches what the `next-task-check` skill would answer. If there is no progress file, write "unknown (no progress file)" and name the most likely next step from this conversation instead.

## Step 3: git state, read only

Run `git branch --show-current`, `git status` and `git log @{u}..HEAD --oneline` (commits not pushed yet). Only report:

- the current branch and whether the working tree is clean
- how many commits are not pushed
- the pull request of the branch, from `gh pr list --head <branch> --state all --limit 1 --json number,state`: say "pull request: open #N / merged #N / none". If `gh` is not available or not logged in, say so in one line and skip this item

Do not push, create or merge anything in this skill. If there is something to push or merge, say so and let the user decide.

## Step 4: keep the progress file small

If the progress file has grown very long (about 300 lines or more), ask first whether to move the completed entries older than the last five sessions to an archive file next to it (for example `docs/progress/YYYY-MM.md`). Move them only if the user agrees, and say in one line what you wrote and where.

## Step 5: next steps for the user

- `/context` shows the token usage
- `/clear` resets the session. Tell the user to type it themselves, you cannot run it
- If the user is about to run `/compact`, make sure Step 1 is done first, and keep only the ids of completed and remaining items in the summary

If the project keeps an index of its rules or skills and you created new ones in this session, add them to the index too, and say in one line what you added.

## Progress file lookup (shared by every skill that reads or updates project progress)

Several skills in this kit read or update a file that tracks the project's progress. Find it in this order and use the first match:

1. The path in `progress_file` inside `.claude-kit.json` at the project root
2. `docs/progress/current.md`
3. `progress.md` at the project root

If none exists, skip the progress step, say so in one line, and continue with the rest of the skill. Never create the file unless the user asks. A starting template is in `templates/progress.template.md` of this plugin.
