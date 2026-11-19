#!/usr/bin/env python3
"""quality-guard: block creating a new source file when its test file does not exist yet.

PreToolUse hook for Write. It does nothing until .quality-guard.json defines "tdd.mappings".
The first mapping that applies decides: its "source" regex matches the new file and, when it has
a "content_regex", the new file content matches too.

Example .quality-guard.json:
  {"tdd": {"mappings": [
      {"source": "^src/(?P<name>[^/]+)\\\\.py$", "test": "tests/test_{name}.py"}
  ]}}

exit 2 -> block, exit 0 -> allow.
"""
import os
import re
import sys

import qg_common as common

BLOCK_MESSAGE = """test file missing for the new file {source}
  expected: {test}

Write the test first (Red -> Green -> Refactor), then create the source file.
To disable this hook set QUALITY_GUARD=off, or add "tdd_guard" to "disable" in .quality-guard.json."""


def is_test_file(relative, tdd_config):
    patterns = tdd_config.get("test_file_patterns", common.DEFAULT_TEST_FILE_PATTERNS)
    return any(re.search(pattern, relative) for pattern in patterns)


def expected_test(relative, content, mapping, directory):
    """Return the expected test path, or None when the mapping does not apply."""
    match = re.search(mapping["source"], relative)
    if not match:
        return None
    content_regex = mapping.get("content_regex")
    if content_regex and not re.search(content_regex, content, re.MULTILINE):
        return None
    try:
        return os.path.join(directory, mapping["test"].format(**match.groupdict()))
    except (KeyError, IndexError, ValueError, AttributeError) as exc:
        common.warn(f"skipping a tdd mapping whose 'test' template is invalid ({exc.__class__.__name__}).")
        return None


def main():
    if common.is_disabled():
        return 0
    hook = common.read_hook_input(sys.stdin)
    if not hook or hook.get("tool_name") != "Write":
        return 0
    tool_input = hook.get("tool_input")
    path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not path:
        return 0
    directory = common.project_dir(hook)
    config, warning = common.load_config(directory)
    if warning:
        common.warn(warning)
    tdd_config = config.get("tdd", {})
    mappings = tdd_config.get("mappings", [])
    absolute = path if os.path.isabs(path) else os.path.join(directory, path)
    if common.hook_disabled(config, "tdd_guard") or not mappings or os.path.exists(absolute):
        return 0
    relative = common.relative_posix(path, directory)
    if common.is_skipped(relative, config) or is_test_file(relative, tdd_config):
        return 0
    content = tool_input.get("content")
    content = content if isinstance(content, str) else ""
    for mapping in mappings:
        test_path = expected_test(relative, content, mapping, directory)
        if test_path is None:
            continue
        if os.path.isfile(test_path):
            return 0
        common.warn(BLOCK_MESSAGE.format(source=relative, test=common.relative_posix(test_path, directory)))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(common.guarded(main))
