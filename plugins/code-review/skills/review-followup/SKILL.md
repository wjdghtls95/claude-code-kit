---
name: review-followup
description: Close out a resolved review finding. Use when a code review issue or an architecture decision has been fixed and the records need updating.
---

## When

Each time one review issue or one design decision has been implemented or resolved. Not before: leave in-progress issues alone and update once, when the work is done.

## Fix the right problem

When you fix a review finding, answer two questions at the same time:

1. Does this fix actually close the bug? (correctness)
2. After this fix, is the code a better starting point for the next change? (extensibility and readability)

A fix that does only the first is a band-aid. Check:

- If the same pattern appears elsewhere later, is it obvious what to do?
- Could someone new to the code understand why it was done this way without extra explanation?
- Does the fix make a future feature harder to add?

Examples: for a log-order bug, do not just move a line, apply "log after success is confirmed" consistently. For a missing validation, do not just add an if, keep validations of the same kind in one place. For a missing type, do not just add a field, make the contract between the two sides explicit.

## Update in this order

1. **Progress file.** Tick the checkbox of the issue (`- [ ]` to `- [x]`) in the review issues section.
2. **The document that describes the issue.** In the same document, fill in two sections:

```markdown
**Resolution**
- What was changed and how
- Why this approach fixes the problem

**Result**
- What behaves differently now
- Confirmation that there is no side effect or follow-up issue
```

   For an architecture decision, write the design decision in Resolution and, if it is only decided but not built yet, write "to be implemented" in Result.
3. **Status label.** Change the issue's `Status: unresolved` line to `Status: resolved`.

## Format

- Use `-` bullets in Resolution and Result, no prose paragraphs
- Say why the code was a problem, what changed, and how the result differs. A code snippet helps.

## Progress file lookup (shared by every skill that reads or updates project progress)

Several skills in this kit read or update a file that tracks the project's progress. Find it in this order and use the first match:

1. The path in `progress_file` inside `.claude-kit.json` at the project root
2. `docs/progress/current.md`
3. `progress.md` at the project root

If none exists, skip the progress step, say so in one line, and continue with the rest of the skill. Never create the file unless the user asks. A starting template is in `progress.template.md`.
