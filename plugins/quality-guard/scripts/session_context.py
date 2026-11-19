#!/usr/bin/env python3
"""quality-guard: add the tier rule to the session context (SessionStart hook)."""
import json
import sys

import qg_common as common

CONTEXT = """Quality Guard is active.
Before editing source files, declare a tier in your reply:
[A] new feature / bug fix / design change: run the 6-round code generation protocol, then show the 5-line confirmation summary and wait for the user.
[B] review fixes / assertion or constant changes: abbreviated check (intent, risk, why the rest is skipped), 3 lines.
[C] docs / meta files: one-line reason, no protocol.
A hook blocks edits to source files that come without a declaration in the same turn. After the user confirms an [A] plan, declare the tier again in your next reply.
Detailed rules are available as skills: code-generation-protocol, tdd-rule, coding-behavior-guidelines, code-consistency, code-pitfalls.
Set QUALITY_GUARD=off to disable the hooks."""


def main():
    if common.is_disabled():
        return 0
    payload = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": CONTEXT}}
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(common.guarded(main))
