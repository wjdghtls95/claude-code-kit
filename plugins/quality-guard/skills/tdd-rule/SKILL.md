---
name: tdd-rule
description: Test-driven development rule - test list first, then Red, Green, Refactor. Use when writing new code or fixing a bug, and when deciding which layers need tests.
---

# TDD Rule

Applies to every new code file. Do not skip. Red → Green → Refactor.

## TDD scope

Decide per layer whether TDD applies and which tool to use. Adapt this table to your stack:

| Layer | Apply | Tool |
|-------|-------|------|
| Backend — all new code | ✅ TDD | Your test runner (integration tests preferred, see below) |
| Frontend — hooks / utils / store | ✅ TDD | Your unit test runner |
| Frontend — component behavior (events · state · errors) | ✅ TDD | A component test library with an async user-event API |
| Frontend — visual / animation | ❌ verify manually | — |
| Service layer with mocked external clients | ✅ TDD | Your unit test runner |
| HTTP endpoint routing · validation · errors | ✅ TDD | Your HTTP test client |
| LLM response quality / content | ❌ Eval (LLM-as-judge) | — |

**Rule: TDD applies to new code only. Do NOT retroactively add tests to existing files unless fixing a bug.**

**Exception — Touch It, Test It:** When modifying an existing file that has no tests, write tests for the function(s) you are about to change *before* making the change. This is not retroactive coverage inflation — it is the minimum TDD gate for any modification. Scope: only the functions being touched, not the entire file.

## TDD cycle (Test List → Red → Green → Refactor)

**Step 0 — Test List (mandatory before any Red).** Before writing a single test, enumerate ALL cases using these 5 axes:

| Axis | Question | Example (rate limit feature) |
|------|----------|------------------------------|
| 1. Happy path | What does success look like? | 429 + limit-exceeded code → banner shown |
| 2. Error variants | Same situation, different value? | 429 + other code → generic error |
| 3. Boundary conditions | Off-by-one, empty, max? | last allowed request passes, the next one is blocked |
| 4. Order and timing | Different order of operations? | limit hit → new message → banner resets |
| 5. Abnormal user behavior | Empty input, rapid clicks, unexpected sequence? | empty submit → no request sent |

Write the full list first. This list IS the design — if you can't enumerate it, you don't understand the feature yet.

**Checkpoint rule: the confirmation gate of the `code-generation-protocol` skill is the ONLY stop point.** Once the user confirms, proceed through all steps below WITHOUT asking "Shall I proceed?" between them. Asking again after the Test List is a protocol violation — write the failing tests immediately.

After the list is complete, proceed without pause:

1. **Red** — Write ALL tests from the list. Run them. Confirm every one fails for the right reason (not a compile error).
2. **Green** — Write the **minimum** code to pass all tests. Intentionally ugly is fine — hardcoded values, no abstraction, no cleanup. Goal: passing tests, nothing more.
3. **Refactor** — Make it production-ready. Applies to **all code, including first-time writes**. Check:
   - Magic numbers → constants
   - Duplicate logic → extracted function
   - Nested depth > 2 → guard clause or extraction
   - Function doing more than one thing → split
   - Simplicity check: "Could this be half the code?" (see the `coding-behavior-guidelines` skill)

   Run tests after every refactor step. If tests break, the refactor introduced a bug.

**Why Green must stay ugly:** Trying to write clean code in Green defeats TDD. You end up designing while implementing, skipping the "minimum" constraint. Green = prove it works. Refactor = make it right.

**Anti-pattern to avoid:** Writing tests incrementally during implementation. If a test goes straight to Green without a Red phase, it means you added it after the implementation — the design value of TDD is already lost for that case.

Never write implementation before the test list is complete. If you can't enumerate test cases, that is a design smell — stop and restructure.

## Test file location

Mirror your source layout in the test directory and keep one naming convention per language.

| Language / layer | Example location |
|-----|----------|
| TypeScript (backend) | `test/<domain>/<name>.spec.ts` |
| TypeScript (frontend) | `__tests__/<hooks\|components\|store>/<name>.test.ts` |
| Python | `tests/<domain>/test_<name>.py` |

The plugin can enforce "test before source" for new files: see `tdd.mappings` in `.quality-guard.json` (README).

## Backend — integration test pattern

Backend tests should be **integration tests** against a real database, not mock-based unit tests, whenever practical.

```typescript
// test/<domain>/<name>.spec.ts  (helper names are examples)
describe('SomeService', () => {
  let app: AppFixture;

  beforeAll(async () => {
    app = await AppFixture.get();
  });

  beforeEach(() => DbTransaction.begin());
  afterEach(() => DbTransaction.rollback());

  it('should do something', async () => {
    const service = app.get(SomeService);
    // test against the real database — rolled back after each test
  });
});
```

**Key rules:**
- Use a real database with a dedicated test configuration — no in-memory substitute
- Mock only external dependencies (third-party APIs, push services, queues) in one shared test-app setup file
- When adding a new external dependency, also add its mock to that shared setup
- Roll back each test's transaction automatically — no manual cleanup needed
- Use a generous per-test timeout (for example 30 seconds) — a 5 second default causes flaky tests under a debugger

## Frontend — test level selection

Two levels of tests for the frontend. Choose based on what you're verifying:

| Level | Tool | What it tests | When to use |
|-------|------|---------------|-------------|
| Hook unit | Unit test runner + hook test utilities | Logic, state, async flows | Business logic, error handling, state transitions |
| Component behavior | Component test library + user-event | Click → state change, render conditions, disabled states | User-facing behavior, empty input, button states |

Both levels apply the Test List (5 axes) before Red. The axes generate different tests at each level:

```
Axis 5 (abnormal user behavior) at hook level      → submitting an empty message
Axis 5 (abnormal user behavior) at component level → empty input → submit button disabled / no request sent
```

**Do not skip component behavior tests for user-facing features.** Hook tests alone cannot verify that a disabled state is actually rendered, or that an empty submit is blocked in the UI.

## Frontend — async user-event pattern

If you use `@testing-library/user-event` v14 or later, its API is async — always `await` it.

```typescript
// ✅ v14 — await required
await userEvent.click(button)
await userEvent.type(input, 'hello')

// ❌ v13 style — do not use
userEvent.click(button)
```

Component test pattern:

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

it('should handle click', async () => {
  render(<MyComponent />)
  await userEvent.click(screen.getByRole('button', { name: /submit/i }))
  expect(screen.getByText('success')).toBeInTheDocument()
})
```

## HTTP endpoint fixture

If your endpoints require authentication, override the auth dependency in a shared fixture so each test file does not repeat the setup:

```python
# tests/<domain>/test_router.py
import pytest
from fastapi.testclient import TestClient
from your_app.main import app
from your_app.auth import verify_token  # your auth dependency

@pytest.fixture
def client():
    app.dependency_overrides[verify_token] = lambda: None
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

Service layer tests mock external clients directly — no HTTP client needed:

```python
def test_extract_items(monkeypatch):
    monkeypatch.setattr("your_app.service.get_llm_client", lambda: mock_llm)
    result = await service.extract(payload)
    assert len(result.items) > 0
```

## Watch mode

Run tests in watch mode during development, using your runner's watch command (for example `jest --watch`). For runners without a watch mode, run the single test file directly.
