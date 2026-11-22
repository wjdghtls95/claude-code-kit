---
name: pr-review
description: Review a pull request before merging with four independent reviewers (architecture, backend and AI, frontend, security) running in parallel, then merge their findings into one report with fixes that can be applied right away. Optional mode argument arch, backend, frontend, security or all (default).
argument-hint: "[mode: arch|backend|frontend|security|all]"
---

Four reviewers look at the same change independently and the results are merged. They diagnose current problems and future risks, and every finding comes in a form that can be applied at once: AUTO-FIX, USE-EXISTING, ASK or FUTURE-RISK.

## Step 0: find the changed files and build EXISTING_CODE_MAP

### Changed files

```bash
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||') \
  || BASE=$(git rev-parse --verify origin/main 2>/dev/null && echo main) \
  || BASE=$(git rev-parse --verify origin/master 2>/dev/null && echo master) \
  || BASE="main"
git diff origin/$BASE...HEAD --name-only 2>/dev/null \
  || git diff --name-only HEAD~1 2>/dev/null \
  || git diff --cached --name-only
```

If no changed file is found, ask the user before reviewing the whole codebase.

### EXISTING_CODE_MAP

Follow the imports of the changed files, and scan with Grep and Glob for utilities, helpers, services, constants and hooks that already exist in the project. Summarize them like this and pass the result to **every reviewer** as context:

```
EXISTING_CODE_MAP:
- utils/format.ts: formatDate(), formatCurrency()
- services/api.ts: apiClient, handleApiError()
- constants/errors.ts: error code constants
- hooks/useAuth.ts: useAuth(), usePermission()
(list everything you find)
```

If `REVIEW.md` exists at the repository root, read it and pass it to every reviewer as context. Its DO NOT FLAG and SKIP sections win over the reviewers' own checklists.

Do not start any reviewer before Step 0 is complete.

## Principles for every reviewer

### Search first

Before recommending a change:
1. Check EXISTING_CODE_MAP. If existing code solves it, use [USE-EXISTING].
2. Verify the version: is the recommended pattern best practice for the framework version in use?
3. Prefer built-in solutions over workarounds.
4. Confidence: at 5 or below, add a "needs verification" warning. At 3 or below, drop the finding.

### Iron law: no claim without evidence

Every finding needs file:line evidence. Do not post a finding without it.
- Do not use "should", "probably", "seems to", "likely". Those words mean a guess.
- Before posting: IDENTIFY the code that proves the problem, VERIFY by reading that file:line yourself, CITE it in the finding.
- Exception for the security reviewer: structural problems such as missing rate limiting or no way to revoke tokens may cite a list of related files instead of one file:line.

### Read custom implementations

Before posting a finding, read the source of any custom decorator, middleware or wrapper applied to that code. Judging by name or signature alone is the main cause of false positives.
- If it is already handled inside, drop the finding.
- If it is handled but another way would be better, use [ASK], name the existing way, and never apply it without the user's approval.

### Test quality (when changed files include tests)

- A tested function changed but no test changed: [ASK] whether to write a test
- Only weak assertions (`toBeDefined()`, `toBeTruthy()`, `toBeFalsy()` alone): [ASK]
- Far more mock setup than assertions, nothing real is checked: [FUTURE-RISK]

### Check tools before AUTO-FIX deletions

Propose deleting dead code, unused imports or unused dependencies only for items a tool has confirmed.
- JS or TS files included: run `npx knip --no-exit-code` (if knip is not available, skip and record [FUTURE-RISK])
- Python files included: run `vulture .` on the Python source directory (if vulture is not available, skip and record [FUTURE-RISK])

Never propose deleting what the tool did not confirm.

### AUTO-FIX or ASK

**AUTO-FIX** (present a ready-to-apply fix without asking. The review itself never edits files, applying the fixes is a separate step the user chooses):
- Dead code, unused variables and imports
- N+1 queries (add eager loading)
- Magic numbers turned into constants
- Comments that contradict the code
- A duplicate of a function that EXISTING_CODE_MAP already has

**ASK** (needs the user's judgment, give options A and B):
- Every security-related fix, even a small one
- Race conditions
- A fix of 20 lines or more
- A fix that changes what the user sees
- A fix that needs a design decision

## Modes

No argument means `all`.

| Mode | Reviewers |
|------|-----------|
| `arch` | Reviewer 1 only |
| `backend` | Reviewer 2 only |
| `frontend` | Reviewer 3 only |
| `security` | Reviewer 4 only |
| `all` | All four in parallel |

After Step 0, start the reviewers **at the same time** with the Agent tool, give each the EXISTING_CODE_MAP, and merge the results when all have finished. The reviewer agents of this plugin (`reviewer-server`, `reviewer-front`, `reviewer-ai`, `reviewer-infra`) are separate role reviewers with their own Critical, Warning and Suggestion output. This skill uses its own four roles. If you want a focused review of one area, ask Claude to run the matching agent directly. Read the project's instructions file first to learn its stack.

## Reviewer 1: Staff engineer (architecture)

The role: a staff engineer who asks whether the code survives three situations.

**A new teammate arrives**
- Can you tell what a function or class does from its name?
- Do you have to follow dependencies more than three levels deep after opening one file?
- Does the code show why the business logic is as it is, without comments?
- Following the data from the entry point, can you understand the whole structure?

**A feature is added**
- Does one feature touch three or more files?
- Does a new case need one change (config or enum), or an if or switch hunt in many places?
- Can it be extended without copy-paste?
- Does EXISTING_CODE_MAP already solve part of it? Use [USE-EXISTING].

**Something breaks in production**
- Can you find the file and function from the error log alone?
- Do logs carry a request id or similar trace context?

**Future risks**
- A feature touching three or more files means more conflicts as the team grows
- Direct dependence on implementations means no replacing or testing later
- Core business logic without tests means regressions go unnoticed

**Integration points** (when changed files cross a package boundary): API URL, HTTP method, request body shape, response type, header names, camelCase versus snake_case, date format. A mismatch is [ASK] with confidence. A match: move on.

**Output:** classify every finding as [AUTO-FIX], [USE-EXISTING], [ASK] or [FUTURE-RISK], with a confidence score.

## Reviewer 2: Senior backend and AI engineer

The role: a principal engineer who asks whether the server survives 3 a.m. and whether the AI pipeline fails quietly on edge cases. Learn the backend and AI stack from the project's instructions file first.

**Current problems, API server**
- Needless serialization of awaits (parallel work run one by one)
- ORM N+1 queries: found and fixable with eager loading is [AUTO-FIX], needs a structure change of 20 lines or more is [ASK] with options, not found: move on
- Where clauses without an index
- Missing input validation, response type mismatch
- Missing transactions where several writes must be atomic
- Inconsistent error code scheme (follow the project's rule)
- try-catch that swallows errors instead of propagating

**AI and ML server**
- Wrong sync or async use (CPU-bound as async, IO-bound as sync)
- Heavy computation blocking the event loop
- No retry or fallback when an external API fails
- Temporary files and resources not cleaned up
- Missing input model validation

**Queues**
- Missing retry settings after a job fails
- No dead letter queue handling
- No guarantee that completed or failed jobs update their state

**Future risks**
- Queue concurrency limits when traffic grows
- APIs without pagination time out as data grows
- No fallback when an external API changes its policy
- Model updates may change results (no version pinning)
- A new domain may miss a hard-coded branch

**Boundary tracing** (for changed API endpoints): follow the data from the input entry to final storage. At each step check type conversion, null checks and exception handling. A gap is [ASK] with file:line.

**Output:** same four classes, with confidence.

## Reviewer 3: Senior frontend engineer

The role: an engineer who finds everything users feel as slow and every UI that breaks when data changes a little. Learn the frontend stack from the project's instructions file first.

**Current problems**

Rendering and performance:
- Client components that could be server-rendered
- Heavy components without lazy loading
- Missing image optimization
- Needless re-renders (missing or overused memoization)

Data and state:
- Missing cache settings in the server-state library, or too much polling
- Global state and server state storing the same data
- Silent failure on API errors (no error UI)
- Flow breaks after the auth token expires

UX and safety:
- Missing empty (zero items) or loading states
- Broken layout in a phone viewport
- z-index conflicts between fixed elements
- XSS risk (inserting unverified HTML)

**Future risks**
- Parsing code that breaks silently when the API response shape changes
- A new domain or feature missing a hard-coded branch
- State management complexity when polling targets grow
- Code that is risky on a framework upgrade
- Untreated touch and viewport areas as mobile use grows

**State enumeration** (for changed components or pages): check the UI in loading, success, error, empty, unauthorized and not-found. A missing state is [ASK].

**Output:** same four classes, with confidence.

## Reviewer 4: Security engineer

The role: a security engineer who looks first at whether the code **cannot be abused**.

**Current problems**
- Authentication and authorization: endpoints without an auth guard, paths that bypass token verification
- Input: data going straight into the database without validation, injection
- Secrets: hard-coded keys, passwords, tokens, sensitive data in logs
- CORS and headers: CORS that is too open, missing security headers
- File upload: MIME type check, size limit, path traversal
- Dependencies: packages with known vulnerabilities (`npm audit`, `pip check`)

**Hostile user scenarios:** submit an empty form, double click, call the API after the token expired, edit the URL by hand. A hole found is [ASK].

**Future risks**
- Endpoints without rate limiting once users grow
- No way to revoke a stolen token
- The current role model cannot separate permissions when an admin area is added
- Neglected dependencies accumulating CVEs

Every security finding is [ASK] or [FUTURE-RISK]. Never AUTO-FIX a security finding, no exceptions.

## Merge the results

### Finding format

```
[AUTO-FIX] (confidence: N/10)
file:line - problem
-> the fix to apply

[USE-EXISTING] (confidence: N/10)
file:line - problem
-> use {function} from {file} in EXISTING_CODE_MAP (X lines to 1)

[ASK] (confidence: N/10)
file:line - problem
Option A: ...
Option B: ...

[FUTURE-RISK]
trigger condition - the risk
```

### Final summary

```
## PR Review Result

### Critical (must fix before merge)

### Important (recommended in this PR)

### Future risks

### Suggestion (next time)

### What went well

### Verdict
- Do not merge: N Critical findings
- Conditional merge: only Important findings, the team decides
- Can merge: no Critical findings
```
