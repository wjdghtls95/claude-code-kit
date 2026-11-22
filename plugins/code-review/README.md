# code-review

[English](README.md) | [한국어](README.ko.md)

Skills and reviewer agents for code review.

- **Review routing** — recommends the right review level (skip, standard, deep) from the size and nature of a change, and says what to fix at once and what to ask first.
- **Pull request review** — four independent reviewers (architecture, backend and AI, frontend, security) run in parallel and their findings are merged into one report. Every finding is an AUTO-FIX, USE-EXISTING, ASK or FUTURE-RISK. Findings cite file:line evidence and a confidence score. A future risk names its trigger instead.
- **Design review** — checks how a UI change actually looks in the browser, with screenshots at desktop and phone width.
- **Review follow-up** — closes a resolved finding: ticks the progress file, fills in the resolution and result, and checks that the fix improves the code and does not only close the bug.
- **REVIEW.md** — a template and a skill for the file the review commands read, with sections for what is critical, what is a nit, what is intentional and what to skip.
- **Reviewer agents** — read-only server, frontend, AI and infrastructure reviewers with checklists.

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install code-review@claude-code-kit
```

Nothing else is required. The plugin has no hooks and needs no `python3`.

## Skills

Skills are namespaced by the plugin name:

| Skill | Use it for |
|-------|-----------|
| `/code-review:review-routing` | Which review a change needs, and what to do with a finding |
| `/code-review:pr-review` | The four-reviewer pull request review. Optional argument: `arch`, `backend`, `frontend`, `security` or `all` |
| `/code-review:design-review` | Visual quality of a changed screen |
| `/code-review:review-followup` | Closing out a resolved finding |
| `/code-review:review-checklist` | Create or update the project's `REVIEW.md` |

## Agents

`reviewer-server`, `reviewer-front`, `reviewer-ai` and `reviewer-infra`. They are separate role reviewers for a focused review of one area, with Critical, Warning and Suggestion output. The `pr-review` skill has its own four roles. They can only read files (Read, Grep, Glob), so they cannot change your code. Ask Claude to use one, for example "review this with reviewer-server".

## What it runs

The skills only run commands that you can see in them: `git` commands in `pr-review`, `npx knip` and `vulture` for dead-code checks, `npm audit` or `pip check` when asked, and `npx playwright` plus the project's own dev command in `design-review`. `npx` may download a package the first time. The review itself never edits your code.

## Settings

Everything works without settings. Optional keys in `.claude-kit.json` at the project root:

| Key | Meaning | Default |
|-----|---------|---------|
| `progress_file` | The progress file used by `review-followup` | first of `docs/progress/current.md`, `progress.md` |
| `design_system_file` | The design system document used by `design-review` | the first file named `DESIGN_SYSTEM.md` found in the project |

If a file is missing, the skill skips that step and says so in one line.

## Templates

- `templates/REVIEW.template.md` — a generic `REVIEW.md` to copy to your repository root and tailor
- `templates/progress.template.md` — a starting progress file for `review-followup`

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/code-review --strict
```

## License

MIT, see the repository `LICENSE`.
