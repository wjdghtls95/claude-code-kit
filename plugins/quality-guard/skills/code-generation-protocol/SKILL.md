---
name: code-generation-protocol
description: Six-round checklist (intent, adversarial review, reference, simplicity, durability, testability) and confirmation gate to run before generating or changing code. Use for new features, bug fixes and design changes.
---

# Code Generation Protocol

Execution checklist for every code generation. Complements the `coding-behavior-guidelines` skill (principles → this skill = execution).

## Tiers

Declare a tier in your reply before editing source files. A hook blocks source edits that come without a declaration in the same turn.

| Tier | When | Protocol |
|------|------|----------|
| `[A]` | New feature / bug fix / design change | Rounds 1-6 in full + confirmation gate |
| `[B]` | Review fix / assertion change / constant rename | Abbreviated: intent + risk + why the rest is skipped (3 lines) |
| `[C]` | Docs / meta files | One-line reason, no rounds |

Skipping is never silent: say which tier applies and why.

## The six rounds

Before writing any code, complete ALL 6 rounds below in order. Do not skip.

**[Round 1 — Intent]** State in one sentence: what exact problem does this code solve, and why in this location? If you cannot answer clearly → stop and ask the user.

**[Round 2 — Adversarial]** Argue against your own approach. Find at least 2 specific weaknesses or failure scenarios. Address each one. If you can't address them → revise the approach and restart from Round 1.
- Caller check (mandatory): "If this function throws, which layer catches it? If no layer catches it → error contract is broken. Fix: either never throw (expose error state instead) or document the throw contract explicitly in the spec."
- Bug fix check (mandatory when fixing a bug): "Are there workarounds in the codebase that exist because of this bug? Grep for related patterns and remove or replace them alongside the fix."
- Symmetric path check (mandatory when fixing an error path): "What other code paths lead to the same broken state? Grep for them — fix all or explicitly decide to skip each one."
- try-finally side effect check (mandatory when adding early return/redirect inside try): "`finally` ALWAYS runs. List every side effect in the `finally` block — is each one safe to run in this early-exit path? If not, signal the intent (e.g., abort a controller, set a flag) before returning."
- Second implementation check (mandatory when writing behavior that already exists elsewhere): "Does this behavior already have a canonical implementation? If yes — extract and import, do not rewrite. If no — extract now so future locations can reuse it."
- Production impact check (mandatory for any new feature or significant change):
  - Scale: "Does this add unbounded growth to DB, memory, or queue? If yes — cap it or paginate."
  - Latency: "Is this on a hot path (streaming response, login, per-request)? If yes — is blocking I/O added? Can it be async or cached?"
  - Security: "Does user-controlled data flow into a DB query, LLM prompt, or external API call? If yes — validate and sanitize at the boundary."

**[Round 3 — Reference]** Name one well-known open-source project or established pattern that solves this class of problem. Compare your approach: where does it align, where does it deviate, and is the deviation justified? If you can't name one → say so explicitly.
- Gotchas check (mandatory when introducing a new external API): "Have the return value, exceptions, and side effects of this API been verified against your project's known-gotchas notes? If not documented, verify explicitly and add a gotcha entry if needed."
- Structure check (mandatory when adding a file or folder): "Does the location follow the project's structure decisions (team's existing projects, then framework and tool conventions, then what changes together)? Name the evidence." See the `project-structure` skill.
- Contract check (mandatory when changing a shared type, an API request or response shape, or an event payload): "Who else reads this shape: other services, mobile or web clients, stored data? Is the change compatible with each of them?" If not, change both sides in the same plan or keep the old shape working.

**[Round 4 — Simplicity]** Ask: "Can this be written in half the code without losing correctness or clarity?" If yes → rewrite it. If no → explain specifically why not. If the project lints with the `code-standard` config, the change must keep zero violations.

**[Round 5 — Durability]** Ask: "What is the single most likely change request for this code in 3 months?" Does the current design handle it without a rewrite? If not → flag whether the design needs rethinking now.
- Rollback check (mandatory when writing to DB or external state): "If this code writes wrong data, is there a recovery path? Can it be rolled back without manual intervention, or does it require a migration/support ticket?" If no rollback path exists → either add one or document the gap explicitly.

**[Round 6 — Testability]** Can this code be unit tested in isolation with no more than 1 mocked dependency? If not → that is a design smell. Either explain why tight coupling is unavoidable here, or restructure so it can be tested independently.

If after Round 6 you remain uncertain: do NOT generate the code. Say: "I'm not confident about [specific concern] — here's what I'd need to resolve it: [list]"

## Confirmation gate (mandatory before writing any code)

After Round 6 passes, present this 5-line summary and wait for confirmation:

```
Intent:    [one sentence — what this solves]
Risk:      [top concern from Round 2 + how it's addressed]
Impact:    [Scale / Latency / Security — each one word: bounded / cached / validated / N/A]
Rollback:  [yes (how) / no (gap documented)]
Test plan: [N cases — axes covered]
```

Only proceed after the user confirms (for example "yes"). If uncertain → stop.

## TDD execution

After confirmation, follow Test List → Red → Green → Refactor (see the `tdd-rule` skill).

**Step 0 — Test List (mandatory first).** Before writing any test, enumerate all cases using 5 axes:
1. Happy path — what does success look like?
2. Error variants — same situation, different values that should fail?
3. Boundary conditions — off-by-one, empty input, maximum limit?
4. Order and timing — system-level: different call order, concurrent requests, retry after failure?
5. Abnormal input — user-level: empty string, malformed data, rapid repeated action?

Present the list. The list IS the design. Do not proceed to Red until the list is complete.

**Then execute:**
1. **Red** — Write ALL tests from the list. Run them. Confirm every test fails for the right reason.
2. **Green** — Write the minimum implementation to pass all tests. No extras.
3. **Refactor** — Clean up. All tests must still pass.

If a test goes straight to Green without Red, it was written after the implementation — flag it.

If the layer is ❌ (visual / LLM response quality) — skip TDD, use manual verification or an evaluation suite instead.
