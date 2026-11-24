---
name: next-task-check
description: "Answer what to do next: check pull request states first, read the progress file, and list what only the user can do and what Claude can do next. Use when the user asks what is next, what to work on, or to check the next task."
---

## Step 0: verify pull request state first (before reading the progress file)

Run:

```bash
gh pr list --state all --json number,title,state,mergedAt --limit 20
```

If a pull request is merged, update the progress file **before you report**: add it to the completed list with the date, and remove any "after PR #N is merged" condition from the next items. Say in one line what you changed. If the progress file was out of date, say so: "The progress file was stale, so I updated it."

If `gh` is not available or not logged in, say so in one line and continue without this step.

## Step 1: read the progress file

Read its status, next items, open issues and open questions (the sections it has). If the status lists work in progress, read what it points to as well.

If there is no progress file, say so in one line, base the answer on open pull requests and this conversation, and offer to start one from `templates/progress.template.md`.

## Answer in two sections

```
**Only you can do** (needs a person)
- [item]: [why a person is needed]

**Claude can do next**
- [task]: [dependency, if any]
```

- Only you can do: decisions, approvals, merges, external settings, anything an open question marks as "before starting"
- Claude can do next: the first unchecked item in the next list that has no open dependency. If it has a dependency, name it

Find the progress file the way the `wrap-up` skill describes it: the `progress_file` path in `.claude-kit.json`, then `docs/progress/current.md`, then `progress.md`. If none exists, skip that step and say so in one line.
