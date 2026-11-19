#!/usr/bin/env python3
"""quality-guard: block source edits that come without a tier declaration.

PreToolUse hook for Edit, Write and MultiEdit.
exit 2 -> block (the message on stderr is shown to Claude)
exit 0 -> allow (also whenever the declaration cannot be verified: the hook fails open)
"""
import os
import sys

import qg_common as common

BLOCK_MESSAGE = """no tier declaration found in this turn for {path}

Declare a tier in your reply before editing source files:
  [A] new feature / bug fix / design change -> full 6-round protocol, then wait for confirmation
  [B] review fixes / assertion or constant changes -> abbreviated check (intent, risk, why the rest is skipped)
  [C] docs / meta files -> one-line reason

Write the tier as plain text in your reply, before the tool call. This hook only reads visible reply text:
a declaration inside your reasoning or inside tool arguments is not seen.

Then retry the edit. To disable this hook set QUALITY_GUARD=off, or add "tier_guard" to "disable" in .quality-guard.json."""

UNVERIFIED_MESSAGE = "could not verify a tier declaration for {path}; allowing the edit."


def check_tier_declaration(transcript_path, env=None):
    """Return 'declared', 'missing' or 'unknown'."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return "unknown"
    try:
        lines, complete = common.read_tail(transcript_path, common.tail_limit(env))
    except OSError:
        return "unknown"
    texts, boundary = common.analyze_current_turn(lines, complete)
    if any(common.TIER_PATTERN.search(text) for text in texts):
        return "declared"
    # Block only on positive evidence: the turn is fully visible and has text, but no declaration.
    # Visible text can be missing from the transcript, so an empty turn is "unknown", never "missing".
    if not boundary or not texts:
        return "unknown"
    return "missing"


def main():
    if common.is_disabled():
        return 0
    hook = common.read_hook_input(sys.stdin)
    if not hook or hook.get("tool_name") not in common.EDIT_TOOLS:
        return 0
    tool_input = hook.get("tool_input")
    path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not path:
        return 0
    directory = common.project_dir(hook)
    config, warning = common.load_config(directory)
    if warning:
        common.warn(warning)
    if common.hook_disabled(config, "tier_guard") or not common.is_source_file(path, directory, config):
        return 0
    shown = common.relative_posix(path, directory)
    verdict = check_tier_declaration(hook.get("transcript_path"))
    if verdict == "missing":
        common.warn(BLOCK_MESSAGE.format(path=shown))
        return 2
    if verdict == "unknown":
        common.warn(UNVERIFIED_MESSAGE.format(path=shown))
    return 0


if __name__ == "__main__":
    sys.exit(common.guarded(main))
