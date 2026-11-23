---
name: test-fake-timers
description: Do not combine fake timers with TanStack Query hook tests. Control only Date.now instead
metadata:
  type: pattern
  domain: testing
  scope: global
  confidence: low
---

## Situation
A test for a TanStack Query hook needs to control time.

## Previous approach
Call `vi.useFakeTimers()` in the test.

## Trigger (what changed it)
Observed in practice: with `vi.useFakeTimers()` and `useQuery` together, `waitFor` times out. The query's async flow and refetch interval stop progressing while timers are faked.

## New approach
Control only the value of `Date.now` with `vi.spyOn(Date, 'now')` or `vi.setSystemTime()`. Keep real timers so `waitFor` works.

## When to apply
- Testing TanStack Query hooks that depend on the current time

## Alternatives considered
- Faking only timers that the hook does not use: not practical, the hook's own timers are the ones that stall
- Waiting in real time inside the test: slow and flaky

## When not to apply
- Tests that do not involve TanStack Query, where fake timers are fine

## Related patterns
- Keep tests deterministic by controlling inputs (time, randomness) instead of the framework's internals
