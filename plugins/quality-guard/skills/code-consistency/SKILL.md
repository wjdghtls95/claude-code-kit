---
name: code-consistency
description: Flag and discuss code that breaks an existing pattern before generating it, and stop on the third duplication (Rule of Three). Use when a change alters import style, error handling, naming, response shape or guard placement.
---

# Code Consistency Rule

Before generating code that breaks an existing pattern, flag it and discuss it first.

Check targets: import style changes, error handling changes, naming pattern changes, response shape changes, guard/decorator placement changes.

Flag format: "⚠️ Consistency check — was: X / now: Y / reason: Z — proceed?"

Exceptions: a new feature that does not overlap with existing code, or a change already discussed in the same session.

## Rule of Three

The moment the same logic is about to appear a third time → stop generating and flag it.

Flag format: "⚠️ Rule of Three — [pattern] would be duplicated a third time. Extract it?"
