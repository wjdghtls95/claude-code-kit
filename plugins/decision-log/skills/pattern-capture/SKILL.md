---
name: pattern-capture
description: Capture lessons and mistakes as reusable patterns. Use when the user corrects you, says "save this as a pattern" or "remember this", when you notice you changed direction after a failed approach, or when pending pattern candidates exist.
---

## At session start

If `.claude/memory/pattern_candidates.md` has lines tagged `[pending]`, ask before starting work:

```
There are N pending pattern candidates from earlier sessions:
  1. [content] (date)
  2. [content] (date)
Review them? (confirm / reject / later)
```

- confirm: run the promotion flow below
- reject: change the tag to `[rejected]`
- later: leave it as it is

## Using patterns

Before starting a task, check the indexes (`.claude/memory/PATTERN_INDEX.md` and `~/.claude/patterns/PATTERN_INDEX.md`). If a pattern's "when to apply" line matches the task, read that pattern file first and follow it. Skip this when no index exists.

## Automatic detection

Write one line to the buffer immediately, without waiting for confirmation, and mention it in one short line, when:

User signals:
- An explicit correction ("that's wrong", "no", "bug", "failed")
- The user proposes a better approach
- Problem keywords such as race condition, duplicate, missing, overflow

Your own signals, even without a correction:
- You change direction while writing code
- You find an unexpected gotcha while researching
- You tried something, it failed, and you found the right way
- You realize during the discussion that the first approach was wrong
- A decision you made could easily be repeated by mistake later

## Manual trigger

When the user says "save it", "save as pattern" or "remember this", add it to the buffer at once, whether it is code or a discussion process.

## Buffer format

```
- [pending] one-line summary of what was learned (YYYY-MM-DD)
```

## Promotion flow

1. Show the user a draft:

```
Situation: [what code or decision]
Previous approach: [what was done or about to be done]
Trigger: [what changed it, from the actual conversation]
New approach: [what to do now]
Alternatives considered: [other options and why this one]
When to apply: [situations that should bring this pattern up]
When not to apply: [exceptions such as performance cases]
Related patterns: [what to watch when combined]
```

2. After the user confirms, create the file:
   - Global: `~/.claude/patterns/pattern_[domain]_[name].md`
   - Project: `.claude/memory/pattern_[name].md`
3. Update the index:
   - Global: add one line to `~/.claude/patterns/PATTERN_INDEX.md`
   - Project: add one line to `.claude/memory/PATTERN_INDEX.md`
4. Remove the item from `pattern_candidates.md`.

## Global or project

Decide by keywords. If it is unclear, ask the user once.

- Global: names a library, framework or general technique (queues, caches, transactions, retries, timeouts, API design, concurrency)
- Project: names a product feature, an entity or a business rule that only exists in this project
- Process or discussion patterns follow the same rule. "Validate with plain files before adding machine learning" is global. A project's own dedup strategy is project-level.

## Pattern file frontmatter

```markdown
---
name: [kebab-case-slug]
description: [one-line description]
metadata:
  type: pattern
  domain: [e.g. system-design / queues / testing]
  scope: global | project
  confidence: low | high
---
```

Confidence: `high` when the user corrected it directly, `low` when you detected it yourself (raise it after a later check).

Templates for the buffer and the index are in this plugin's `templates` folder.
