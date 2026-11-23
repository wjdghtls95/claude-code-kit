---
name: ship-reminder
description: "Remind the user to run the ship skill when a piece of coding work is finished. Use at the end of a reply in which source files were created or modified and the work is complete."
---

## When

In this reply you created or modified source files (code or configuration that ships with the project) and the work is finished.

## What to do

Add one line at the very end of the reply:

```
Work complete. Run the ship skill to commit, push and open a pull request in one go.
```

## When not to add it

- The work is still in progress (a test fails, more edits are needed)
- Only meta files changed (project instructions, progress or planning notes, tool settings)
- The reply is analysis, research or a question with no code change
- A ship or land run is already in progress in this session
- The reply is a git operation that changed no files (commit, push, merge)
