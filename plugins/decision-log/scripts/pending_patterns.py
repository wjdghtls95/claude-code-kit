#!/usr/bin/env python3
"""decision-log: remind about pending pattern candidates when a session starts (SessionStart hook).

Reads .claude/memory/pattern_candidates.md in the project. Prints a short reminder when it has
lines starting with "- [pending]". Never blocks and never fails: any problem means no output and exit 0.
Set DECISION_LOG=off to disable.
"""
import json
import os
import sys

BUFFER = os.path.join(".claude", "memory", "pattern_candidates.md")
OFF_VALUES = {"off", "0", "false", "no", "disable", "disabled"}


def project_dir(hook):
    cwd = hook.get("cwd") if isinstance(hook, dict) else None
    return cwd or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def count_pending(path):
    count = 0
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", errors="replace").lstrip()
            if line.startswith("- [pending]"):
                count += 1
    return count


def main():
    if os.environ.get("DECISION_LOG", "").strip().lower() in OFF_VALUES:
        return 0
    try:
        hook = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except ValueError:
        hook = {}
    path = os.path.join(project_dir(hook), BUFFER)
    if not os.path.isfile(path):
        return 0
    pending = count_pending(path)
    if not pending:
        return 0
    context = (
        f"Decision Log: {pending} pending pattern candidate(s) in {BUFFER}. "
        "Before starting work, ask the user whether to review them (confirm / reject / later). "
        "Use the pattern-capture skill for the promotion flow."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
