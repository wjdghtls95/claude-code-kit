#!/usr/bin/env python3
"""quality-guard: do the tests really guard the code? Break the source on purpose, one change at a time.

  mutation_check.py [--root DIR] [--config FILE] [INDEX ...]

Reads .mutations.json in the project root:

  {
    "test_command": ["npm", "test"],
    "timeout_seconds": 300,
    "mutations": [
      {"file": "src/rules.ts", "description": "retry window 5 min to 1 min",
       "find": "RETRY_WINDOW_MS = 300_000", "replace": "RETRY_WINDOW_MS = 60_000"}
    ]
  }

For each mutation it replaces the first occurrence of "find", runs the test command (a list, never a shell
string), and restores the file. KILLED means a test failed (good). SURVIVED means every test still passed: no
test guards that rule. NOT_APPLIED means the find text is gone, so the list is out of date.

The source files change while it runs, so do nothing else in the project meanwhile. A copy is kept next to the
file (<file>.mutation-backup) until it is restored. Ctrl+C and a normal kill (SIGTERM) restore the file. A hard
kill (SIGKILL) or a power cut cannot, so the next run refuses to start until you restore the file from that copy
and delete it. Exit code: 0 all killed, 1 something survived or failed, 2 setup.
"""
import json
import os
import signal
import subprocess
import sys

CONFIG_NAME = ".mutations.json"
BACKUP_SUFFIX = ".mutation-backup"
DEFAULT_TIMEOUT_SECONDS = 300


class SetupError(Exception):
    pass


def load_config(root, path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SetupError(f"no {CONFIG_NAME} at {path}. Create one with test_command and mutations (see --help)")
    except ValueError as error:
        raise SetupError(f"{path} is not valid JSON: {error}")
    command = data.get("test_command")
    if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
        raise SetupError("test_command must be a list of strings, for example [\"npm\", \"test\"] (no shell string)")
    mutations = data.get("mutations", [])
    if not isinstance(mutations, list):
        raise SetupError("mutations must be a list")
    for index, mutation in enumerate(mutations):
        check_mutation(root, index, mutation)
    timeout = data.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise SetupError("timeout_seconds must be a positive number")
    return command, timeout, mutations


def check_mutation(root, index, mutation):
    keys = ("file", "description", "find", "replace")
    if not isinstance(mutation, dict) or not all(isinstance(mutation.get(key), str) for key in keys):
        raise SetupError(f"mutation {index} needs file, description, find and replace as strings")
    target = os.path.realpath(os.path.join(root, mutation["file"]))
    if os.path.isabs(mutation["file"]) or not target.startswith(os.path.realpath(root) + os.sep):
        raise SetupError(f"mutation {index}: file must be a path inside the project root: {mutation['file']}")


def leftover_backups(root, mutations):
    paths = {os.path.join(root, mutation["file"]) + BACKUP_SUFFIX for mutation in mutations}
    return sorted(path for path in paths if os.path.exists(path))


def run_tests(root, command, timeout):
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except OSError as error:
        return f"ERROR ({error.strerror or error})"
    return "KILLED" if result.returncode != 0 else "SURVIVED"


def try_mutation(root, command, timeout, mutation):
    path = os.path.join(root, mutation["file"])
    try:
        with open(path, encoding="utf-8") as f:
            original = f.read()
    except (OSError, UnicodeDecodeError):
        return "NOT_APPLIED (cannot read the file)"
    if mutation["find"] not in original:
        return "NOT_APPLIED"
    backup = path + BACKUP_SUFFIX
    with open(backup, "w", encoding="utf-8") as f:
        f.write(original)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original.replace(mutation["find"], mutation["replace"], 1))
        return run_tests(root, command, timeout)
    finally:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original)
        os.remove(backup)


def main(argv, stdout=None):
    out = stdout or sys.stdout
    args = list(argv)
    if "-h" in args or "--help" in args:
        out.write(__doc__)
        return 0
    root = os.path.abspath(option(args, "--root") or ".")
    config = option(args, "--config") or os.path.join(root, CONFIG_NAME)
    try:
        command, timeout, mutations = load_config(root, config)
    except SetupError as error:
        out.write(f"setup: {error}\n")
        return 2
    leftovers = leftover_backups(root, mutations)
    if leftovers:
        out.write("setup: a previous run was interrupted. Restore each file from its copy, delete the copy, then run again:\n")
        out.write("".join(f"  {path}\n" for path in leftovers))
        return 2
    unknown = [arg for arg in args if not arg.isdigit()]
    if unknown:
        out.write(f"setup: unknown argument {unknown[0]} (expected --root, --config or mutation indexes)\n")
        return 2
    chosen = {int(arg) for arg in args}
    missing = sorted(index for index in chosen if index >= len(mutations))
    if missing:
        out.write(f"setup: no mutation with index {missing[0]} (there are {len(mutations)}, counting from 0)\n")
        return 2
    results = [(index, mutation, try_mutation(root, command, timeout, mutation))
               for index, mutation in enumerate(mutations) if not chosen or index in chosen]
    for index, mutation, status in results:
        out.write(f"{index}\t{status}\t{mutation['file']}\t{mutation['description']}\n")
    weak = [status for _, _, status in results if status != "KILLED"]
    out.write(f"\n{len(results) - len(weak)} of {len(results)} killed\n")
    return 1 if weak else 0


def option(args, name):
    if name not in args:
        return None
    index = args.index(name)
    value = args[index + 1] if index + 1 < len(args) else None
    del args[index:index + 2]
    return value


if __name__ == "__main__":
    # a plain kill would skip the finally that puts the original file back
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
    sys.exit(main(sys.argv[1:]))
