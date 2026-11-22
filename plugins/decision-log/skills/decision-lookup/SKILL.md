---
name: decision-lookup
description: Answer "why did we decide X" from the decision documents. Use when the user asks why something was chosen or built a certain way.
---

1. Identify the topic from the question.
2. Find the decision document that covers it in the folder named by `decisions_dir` in `.claude-kit.json`, otherwise `docs/decisions`. If the topic is ambiguous or spans several documents, read all of the relevant ones.
3. Find the `→ Why:` block for that topic.
4. Return its bullet points as written, without paraphrasing.

If no `→ Why:` exists for the topic, say so explicitly. Never guess or invent a reason.
