# Changelog

## quality-guard 0.1.0

- Tier declaration hook: blocks source edits without `[A]`, `[B]` or `[C]` in the current turn, fails open when the transcript cannot be verified
- Test-first hook: blocks creating a new source file before its test file exists, opt-in through `.quality-guard.json`
- SessionStart reminder of the tier rule
- Skills: `code-generation-protocol`, `tdd-rule`, `coding-behavior-guidelines`, `code-consistency`, `code-pitfalls`
- Kill switch: `QUALITY_GUARD=off`
