---
name: enhancement-tracking
description: Record features and design choices that were deliberately postponed. Use when the conversation says "out of scope for now", "add it later", "low priority", or asks to put something on the enhancement list.
---

## When to add an entry

Add an entry right away when the conversation clearly decides to postpone a feature or design choice, for example "out of scope for now", "later", "low priority", "put it on the enhancement list".

Do not add:
- Correctness bugs such as race conditions, data corruption or duplicate sends. Fix them now, or file a tracked issue with an owner and a trigger. There is no "later" for bugs.
- Anything still undecided. Mark that as an open topic instead (see the topic-tracking skill).
- Reversals of confirmed decisions. Those go through the concept-update skill.

No need to ask the user first when the decision is clear from the conversation. After adding, say in one line what you added and where.

## Where it goes

The file named by `enhancement_file` in `.claude-kit.json`, otherwise `docs/enhancement-list.md`. If it does not exist, create it with the structure below.

```markdown
# Enhancement List
_Updated: YYYY-MM-DD_

> Contents
> 1. Why this file exists
> 2. How to use it
> 3. [topic] - short description

## Why this file exists
**Date:** YYYY-MM-DD
**Background:** [what discussion led to this file]

Principles:
- Not "do it later" but "do it when the trigger happens". Every entry names its trigger.
- Undecided or still-debated items do not belong here.
- Reversing a confirmed decision does not belong here.

## [topic]

### [item]
- **Current decision**: how it works now
- **Enhancement**: what to do later
- **Trigger**: when to do it
```

## Adding an entry

If the topic section exists, add only the item. If not, create the section and add a line to the contents. Update the contents whenever you add an item or a section. Keep the `_Updated_` date current.
