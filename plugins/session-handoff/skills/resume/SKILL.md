---
name: resume
description: "Get oriented when coming back to a project: show the latest progress entries and the git state, point out unfinished work, and ask what to do next. Use at the start of a session, after a long break, or when the last progress entry is about five hours old or older."
---

Use this when the user returns to work, or when the last entry in the progress file is about five hours old or older. If the entries have no dates, skip the age check and use this only when the user returns. It only reads. It never changes branches, pulls or edits files.

## Steps

1. Show the five most recent entries of the progress file.
2. Run `git branch --show-current`, `git status` and `git log --oneline -3`.
3. If the last entry is marked as in progress, show a warning: "Unfinished work: [item]". If a local branch looks related to it, name it: "Related branch: [name] (exists locally)".
4. If you are not on the default branch, or the working tree is dirty, say so plainly and do not fix it yourself.
5. Ask the user whether to continue the unfinished work or start something new.
6. Proceed only after the user answers.

Find the progress file the way the `wrap-up` skill describes it: the `progress_file` path in `.claude-kit.json`, then `docs/progress/current.md`, then `progress.md`. If none exists, skip that step and say so in one line.
