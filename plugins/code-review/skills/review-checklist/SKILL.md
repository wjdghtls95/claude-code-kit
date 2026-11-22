---
name: review-checklist
description: Create or update the REVIEW.md that code reviews read for the project. Use when the user wants project-specific review rules, a REVIEW.md, or a list of intentional decisions the reviewer must not flag.
---

Claude Code's review commands read a `REVIEW.md` at the repository root. A good one tells the reviewer what really matters in this project, what is intentional, and what to ignore. A generic template is in this plugin at `templates/REVIEW.template.md`.

## Steps

1. If `REVIEW.md` exists, read it and update it. Do not overwrite it.
2. If not, copy the template to the project root as `REVIEW.md`.
3. Tailor each section to the project. Read the project's instructions file and a few core modules first. Replace the generic wording with the real attack surface and failure modes of this project (its framework, its queue, its data layer, its external APIs).
4. Fill in the **DO NOT FLAG** section only with decisions the user confirms are intentional. Do not invent them.
5. Keep **IMPORTANT** short and concrete. A rule the reviewer cannot check by reading code does not belong there.
6. Keep the cap on nits in **NIT** so reviews stay readable.

## What goes where

| Section | Put here |
|---------|----------|
| IMPORTANT | Behavior-breaking, security and data-loss problems specific to this project |
| NIT | Low-severity style points, with a cap per review |
| DO NOT FLAG | Intentional decisions, so the reviewer does not repeat them every time |
| SKIP | Paths and files that must not get findings (generated code, lock files, migrations) |
| Severity | One-line meaning of each level |

After updating, say in one line what you changed and ask the user to confirm the DO NOT FLAG entries.
