# Changelog

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
