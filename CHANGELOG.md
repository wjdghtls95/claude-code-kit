# Changelog

## quality-guard 0.1.1

- Fix: the session-start reminder now follows `"disable": ["tier_guard"]` in `.quality-guard.json`, so it no longer says a hook blocks edits when that hook is off
- Docs: `skip_patterns` is a prefix match (stated plainly), `QUALITY_GUARD_TAIL_BYTES` is documented

## decision-log 0.1.1

- Fix: the progress file template now has the `Working Notes` section the skills write to, and the template path is stated as `templates/progress.template.md`
- Fix: example pattern files follow the documented file name (`pattern_<domain>_<name>.md`) and all sections
- Fix: `concept-update` and `decision-lookup` say what to do when the decisions folder is missing
- Fix: the project directory is read from `CLAUDE_PROJECT_DIR` first, as in `quality-guard`

## code-review 0.1.2

- Security: `pr-review` and the reviewer agents read `REVIEW.md` from the default branch, so a pull request cannot silence its own findings by editing it
- Docs: a severity mapping between the finding classes, the summary levels and the agents' headings
- Fix: the progress file template has a `Review Issues` section, the review skills no longer claim they edit nothing while `review-routing` lists small fixes

## git-workflow 0.1.0

- Skills: `ship`, `land`, `pr-check`, `git-rules`, `ship-reminder`, `git-conventions`
- A progress file template, no hooks, nothing to install besides the plugin


## code-review 0.1.1

- Fix: the `description` of the reviewer agents contained `: ` and was not valid YAML, so the agents loaded with empty metadata (no name, description or read-only tool list). The values are now quoted
- Tests: a frontmatter check for every skill and agent of every plugin

## code-review 0.1.0

- Skills: `review-routing`, `review-followup`, `pr-review`, `design-review`, `review-checklist`
- Read-only reviewer agents: `reviewer-server`, `reviewer-front`, `reviewer-ai`, `reviewer-infra`
- Template: `REVIEW.template.md`
- No hooks, nothing to install besides the plugin

## decision-log 0.1.0

- Skills: `topic-tracking`, `enhancement-tracking`, `pattern-capture`, `concept-update`, `decision-lookup`, `decision-index`
- SessionStart reminder when `.claude/memory/pattern_candidates.md` has lines starting with `- [pending]`
- Templates for the pattern buffer, the pattern index and a progress file, plus two example patterns
- Optional shared settings file `.claude-kit.json`, kill switch `DECISION_LOG=off`

## quality-guard 0.1.0

- Tier declaration hook: blocks source edits without `[A]`, `[B]` or `[C]` in the current turn, fails open when the transcript cannot be verified
- Test-first hook: blocks creating a new source file before its test file exists, opt-in through `.quality-guard.json`
- SessionStart reminder of the tier rule
- Skills: `code-generation-protocol`, `tdd-rule`, `coding-behavior-guidelines`, `code-consistency`, `code-pitfalls`
- Kill switch: `QUALITY_GUARD=off`
