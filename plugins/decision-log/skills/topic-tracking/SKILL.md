---
name: topic-tracking
description: Track undecided topics during a discussion. Use when a new open question or an undecided direction comes up, or when the user asks to save, confirm or move on from a topic.
---

## Marking open topics

When a topic is being discussed and nothing is decided yet, treat it as open. Before you finish a reply, check: if this reply introduced or touched an open topic, add this at the very end, after all other content. If there is none, add nothing.

```
📍 Open topics
- [topic] (direction: [current direction] / reason: [key reason])
```

A topic is confirmed only when the user explicitly says so ("confirmed", "let's go with this", "decided"). Research finished, discussion finished, or "this looks likely" is not a decision. Until the user confirms, keep it open and never write "confirmed" anywhere.

## Saving working notes

When the user asks to save or to move on ("save", "next"), write the topic to the `## Working Notes` section of the project's progress file, then stop marking it as open. If you are unsure where it should go, ask once.

```markdown
### [topic] - [date]
- **Status**: likely / under discussion / on hold
- **Options considered**: every option discussed
  - [option]: [pros and cons]
- **Current direction**: [option and why]
- **Key reasons**: every reason
- **Trade-offs**: [what gets worse, in which situation, one-off or ongoing]
- **Conclusion**: [option A] vs [option B] - chose [X] because [what gets better]
- **Still open**: [what must be checked before confirming, or "none"]
```

## Lifecycle

```
discussion starts -> mark as open
end of each reply -> add the open-topics block if any
user asks to save -> write working notes, stop marking it
user confirms     -> move it to the decision document, delete the working notes
```

## Progress file lookup (shared by every skill that reads or updates project progress)

Several skills in this kit read or update a file that tracks the project's progress. Find it in this order and use the first match:

1. The path in `progress_file` inside `.claude-kit.json` at the project root
2. `docs/progress/current.md`
3. `progress.md` at the project root

If none exists, skip the progress step, say so in one line, and continue with the rest of the skill. Never create the file unless the user asks. A starting template is in `progress.template.md`.
