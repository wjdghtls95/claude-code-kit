---
name: concept-update
description: Change an already-confirmed decision in a decision document. Use when the user suggests reversing or changing something that was decided and recorded earlier.
---

Decision documents live in the folder named by `decisions_dir` in `.claude-kit.json`, otherwise `docs/decisions`. A confirmed decision is an entry marked as confirmed (for example a status table row with a check mark) and has `→ Why:` bullets.

If the decisions folder or the document does not exist, say so in one line and stop.

## When this applies

1. Read the decision document that covers the topic.
2. If the topic matches a confirmed entry, this skill applies.
3. If the topic is still open, use the topic-tracking skill instead.

Do not trigger on exploratory language such as "what if", "how about", "I am thinking about" or "what do you think". Wait until the user actually wants the change.

## Flow

1. Identify what changed and which document it belongs to.
2. Show a preview before writing:
   ```
   I will update [document]:
   - [section]: [change]
   OK?
   ```
3. After the user confirms, update the document.
4. Write the reasons as `→ Why:` followed by bullet points, never as one long sentence.
5. If it is a new section, add it under the right heading.
