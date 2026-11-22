# REVIEW.md

Read by the code review commands. Replace the generic wording below with the facts of this project.

Project summary: [one line: what it is, the stack, who uses it]

## IMPORTANT: flag these as critical (behavior-breaking, security, data loss)

### Transactions and background jobs
- A job is queued inside a database transaction that may roll back, or outside one that should wrap it
- A cancel or delete flow that changes the queue first and the database second, so a failure leaves them out of sync
- Several writes that must be atomic but are not wrapped in one transaction

### Auth and data ownership
- A list, update or delete query without a filter on the owner (one user can reach another user's data)
- An endpoint without an authentication guard that should have one
- A token, secret or key in code, logs, or client-side code
- A permission check done only on the client

### Input that reaches an LLM or another interpreter
- User input inserted directly into a system prompt, a query, a shell command or a template
- A model call without a maximum output size or a timeout

### Contracts between services
- A change to an API request or response shape without the matching change in the other service
- A new environment variable that is not added to the example environment file

### Infrastructure and deployment
- A server bound to localhost only, a health check that is missing, a hard-coded environment value
- A build step that embeds secrets in an image

### Error handling
- An empty catch block, or an error swallowed so the caller cannot know it failed
- A function that can throw with no layer that catches it

### Concurrency
- Check-then-act on shared state without a lock, a transaction or an atomic operation
- A retry that is not idempotent

### Queries
- A paginated query without a stable order
- A query inside a loop (N+1)
- A repeatable job without a deterministic key, so it cannot be removed later

### Web frontend
- Authentication or authorization decided only in the browser
- A missing cleanup in an effect (listener, timer, stream)
- Hard-coded colors or values that the design system already defines

### Streaming
- No handling of a dropped connection or a timeout
- Partial output treated as complete

### Observability
- A failure path with no log or metric
- Sensitive data in a log line

## NIT: low severity, style only. Cap at 5 nits per review.

- Naming that breaks the project's convention
- Deep nesting that a guard clause would flatten
- A duplicated block that appears for the third time
- A comment that repeats the code

## DO NOT FLAG: intentional decisions in this codebase

List decisions the team confirmed on purpose, so they are not flagged again. Example format:

- [pattern]: [why it is intentional]

## SKIP: do not post findings for these

- Generated code and lock files
- Database migrations that are already applied
- Vendored third-party code

## Severity reference

| Level | Meaning |
|-------|---------|
| Critical | Breaks behavior, leaks data, or loses data. Block the merge |
| Important | A real risk or a likely bug. Fix in this change |
| Nit | Style or taste. Mention briefly |
