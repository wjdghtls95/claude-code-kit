---
name: review-routing
description: Recommend which kind of code review a change needs. Use right before committing or opening a pull request, or when the user asks which review to run.
---

Look at the size and the nature of the change, then recommend a review level. Use the first level whose condition matches.

## Recommendation format

Right before a commit or a pull request:

```
This change is [small | medium | large]: N files, [one line on what it is].
-> [skip | standard review | deep review] recommended.
```

## Levels

**Deep review** if any of these is touched:

- [ ] Authentication, tokens, sessions, refresh flows
- [ ] Shared libraries that many modules import
- [ ] Database schema or migrations
- [ ] Payments or billing
- [ ] Data deletion logic (bulk deletes, cascades)
- [ ] Guards, roles, permission checks
- [ ] Encryption or hashing
- [ ] A merge into the production branch

**Standard review** if any of these is touched:

- [ ] API contract changes (request or response shapes)
- [ ] The first complete version of a new domain module
- [ ] A new integration with an external API
- [ ] Background workers or queue jobs
- [ ] Global middleware, interceptors, filters
- [ ] Changes that cross a domain boundary (one domain now calls another)
- [ ] Transaction logic
- [ ] A change of the error-handling pattern
- [ ] 6 to 15 files

**Skip** if none of the above applies and the change is 1 to 5 files.

Adjust the lists to your project. If the project keeps a `REVIEW.md`, mention that the review will read it (see the `review-checklist` skill).

## How to run them

- Standard: the built-in `/code-review` command, or the `pr-review` skill from this plugin
- Deep: the `pr-review` skill with all reviewers, and `/ultrareview` if it is available to you (a multi-agent cloud review that you start yourself)
- If the change touches UI components or pages, also run the `design-review` skill after the code review

## What to do with a finding

**Fix right away, without asking, and say in one line what you changed:**
- Refactoring inside one file: removing duplication, renaming, extracting a constant
- About 10 lines or fewer, no API contract change, no database schema change
- A simple bug fix of one or two lines
- The effect reaches only that file and its direct callers

**Say it first, fix after the user agrees:**
- A new module or layer
- An API contract change (request or response shape)
- An error-handling strategy that spans several files
- An effect across repositories or services
- A database schema change
- More than 3 files or more than 20 lines

## Order of work after the review

```
1. Commit, push, open the pull request, review
2. If there are fixes, add commits to the same pull request
3. Merge
```

Reviewing on the pull request keeps inline comments next to the diff and keeps the fix commits in its history. A local review before pushing is also fine, especially for anything security sensitive.
