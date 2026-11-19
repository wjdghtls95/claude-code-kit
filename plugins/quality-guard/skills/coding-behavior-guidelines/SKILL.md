---
name: coding-behavior-guidelines
description: Behavior guidelines for coding with an LLM - think before coding, simplicity first, surgical changes, goal-driven execution. Use at the start of any coding task and when scope or complexity starts to grow.
---

# Coding Behavior Guidelines

_Derived from Andrej Karpathy's observations on LLM coding pitfalls._

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Function length: flag at 30 lines, mandatory split at 50 lines.
- Function name with "and/or" → split signal (`validateAndSave` → `validate` + `save`).

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 2a. System & Pipeline Design

**"Minimum code" means minimum scope — not minimum quality.**

"MVP" or "simple project" defines *what* to build, not *how well* to build it.
Shortcuts that require a future rewrite are not simpler — they are deferred complexity.

When building a **code-layer system** (pipeline, transaction management, queue, cache strategy, algorithm):
- Actively evaluate tech stack combinations — don't default to the first option
- Consider performance, readability, and extensibility at design time
- Scalability scenarios (10×, 100× traffic) must be stated and reasoned about, not dismissed as "out of scope"

**Code layer vs infrastructure layer:**

| Code layer | Infrastructure layer |
|---|---|
| Transaction pipelines, queue processors | Deployment (hosting platform, containers) |
| Caching strategy, Redis patterns | CI/CD configuration |
| Algorithm and data structure choices | Environment variable management |
| Module architecture, DI wiring | Monitoring, alerting setup |

- Code layer: quality standards apply from day one regardless of project stage
- Infrastructure layer: startup-stage simplicity is acceptable until scaling signals appear
  (this is the ONLY place "early stage" is a valid reason to defer — it does NOT apply to code correctness)

**Verify before adding (wrapper / decorator / abstraction):**
1. Check library source — does it already handle this?
2. "Necessary" must be proven with code evidence, not assumption.
3. If removing it doesn't change behavior → don't add it.

**Code review findings on framework behavior:** open the library source and verify before acting. A wrong diagnosis leads to unnecessary changes.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### 2b. Consistency & Deduplication

Before writing code that changes an existing pattern (import style, error handling, naming, response shape, guard/decorator placement), flag it first:

"⚠️ Consistency — was: X / now: Y / reason: Z — proceed?"

Exception: new features that don't overlap with existing code, or patterns already discussed this session.

When the same logic appears a 3rd time, stop and flag:

"⚠️ Rule of Three — [pattern] appears 3 times. Extract?"

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
