"""mutation_check.py tests: break the source on purpose, one change at a time, and see whether the tests notice

Test list (5 axes)
  normal:   a mutation the tests catch is KILLED, one they miss is SURVIVED, the file is byte-identical afterwards
  error:    missing or broken config, a bad timeout, an unknown index or argument -> exit 2 with a message; the find text is absent -> NOT_APPLIED;
            the test command cannot start -> ERROR and the file is restored
  boundary: run only the chosen indexes; an empty list exits 0; a find text that occurs twice changes the first only
  order:    a backup left by an interrupted run -> refuse to start and touch nothing; a slow test command -> TIMEOUT
            and the file is restored; the exit code is 1 when anything survived or did not apply
  abuse:    a file outside the root or an absolute path is rejected; the config cannot run a shell string
"""
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "plugins", "quality-guard", "scripts"))
import mutation_check as mc  # noqa: E402

# the "test suite": passes only while rules.txt still says LIMIT=10
CHECK = [sys.executable, "-c", "import sys; sys.exit(0 if 'LIMIT=10' in open('rules.txt').read() else 1)"]
ALWAYS_PASS = [sys.executable, "-c", "pass"]


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        self.write("rules.txt", "LIMIT=10\nWINDOW=5\nWINDOW=5\n")

    def write(self, rel, text):
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as f:
            return f.read()

    def config(self, mutations, command=None, **extra):
        data = {"test_command": command or CHECK, "mutations": mutations, **extra}
        self.write(".mutations.json", json.dumps(data))

    def run_main(self, *args):
        out = io.StringIO()
        code = mc.main(["--root", self.root, *args], stdout=out)
        return code, out.getvalue()


class StatusTests(Tmp):
    def test_caught_mutation_is_killed_and_the_file_is_restored(self):
        self.config([{"file": "rules.txt", "description": "limit 10 to 20", "find": "LIMIT=10", "replace": "LIMIT=20"}])
        code, out = self.run_main()
        self.assertIn("KILLED", out)
        self.assertEqual(code, 0)
        self.assertEqual(self.read("rules.txt"), "LIMIT=10\nWINDOW=5\nWINDOW=5\n")

    def test_missed_mutation_survived_and_exit_code_is_one(self):
        self.config([{"file": "rules.txt", "description": "window 5 to 9", "find": "WINDOW=5", "replace": "WINDOW=9"}])
        code, out = self.run_main()
        self.assertIn("SURVIVED", out)
        self.assertEqual(code, 1)
        self.assertEqual(self.read("rules.txt"), "LIMIT=10\nWINDOW=5\nWINDOW=5\n")

    def test_missing_find_text_is_not_applied(self):
        self.config([{"file": "rules.txt", "description": "gone", "find": "NOPE", "replace": "X"}])
        code, out = self.run_main()
        self.assertIn("NOT_APPLIED", out)
        self.assertEqual(code, 1)

    def test_command_that_cannot_start_is_an_error_and_restores(self):
        self.config([{"file": "rules.txt", "description": "limit", "find": "LIMIT=10", "replace": "LIMIT=20"}],
                    command=["definitely-not-a-real-command-xyz"])
        code, out = self.run_main()
        self.assertIn("ERROR", out)
        self.assertEqual(code, 1)
        self.assertEqual(self.read("rules.txt"), "LIMIT=10\nWINDOW=5\nWINDOW=5\n")

    def test_slow_command_times_out_and_restores(self):
        slow = [sys.executable, "-c", "import time; time.sleep(5)"]
        self.config([{"file": "rules.txt", "description": "limit", "find": "LIMIT=10", "replace": "LIMIT=20"}],
                    command=slow, timeout_seconds=1)
        code, out = self.run_main()
        self.assertIn("TIMEOUT", out)
        self.assertEqual(self.read("rules.txt"), "LIMIT=10\nWINDOW=5\nWINDOW=5\n")

    def test_only_the_first_occurrence_changes(self):
        seen = os.path.join(self.root, "seen.txt")
        copy = [sys.executable, "-c", f"open({seen!r}, 'w').write(open('rules.txt').read())"]
        self.config([{"file": "rules.txt", "description": "window", "find": "WINDOW=5", "replace": "WINDOW=9"}], command=copy)
        self.run_main()
        self.assertEqual(self.read("seen.txt"), "LIMIT=10\nWINDOW=9\nWINDOW=5\n")


class SelectionAndConfigTests(Tmp):
    def test_only_chosen_indexes_run(self):
        self.config([{"file": "rules.txt", "description": "first", "find": "LIMIT=10", "replace": "LIMIT=20"},
                     {"file": "rules.txt", "description": "second", "find": "WINDOW=5", "replace": "WINDOW=9"}])
        code, out = self.run_main("1")
        self.assertNotIn("first", out)
        self.assertIn("second", out)

    def test_empty_list_exits_zero(self):
        self.config([])
        self.assertEqual(self.run_main()[0], 0)

    def test_missing_config(self):
        code, out = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn(".mutations.json", out)

    def test_broken_config(self):
        self.write(".mutations.json", "{not json")
        self.assertEqual(self.run_main()[0], 2)

    def test_shell_string_command_is_rejected(self):
        self.config([], command="npm test && echo done")
        code, out = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("list", out)

    def test_bad_timeout_is_a_setup_error(self):
        for value in ("abc", None, [1], 0, -5):
            self.config([], timeout_seconds=value)
            self.assertEqual(self.run_main()[0], 2, value)

    def test_unknown_index_or_argument_is_a_setup_error(self):
        self.config([{"file": "rules.txt", "description": "first", "find": "LIMIT=10", "replace": "LIMIT=20"}])
        for args in (("5",), ("--unknown",), ("foo",)):
            code, out = self.run_main(*args)
            self.assertEqual(code, 2, args)
            self.assertNotIn("KILLED", out, args)

    def test_file_outside_root_is_rejected(self):
        for path in ("../outside.txt", os.path.join(self.root, "rules.txt")):
            self.config([{"file": path, "description": "x", "find": "a", "replace": "b"}])
            self.assertEqual(self.run_main()[0], 2, path)


class InterruptedRunTests(Tmp):
    def test_leftover_backup_refuses_to_start(self):
        self.write("rules.txt.mutation-backup", "LIMIT=10\n")
        self.write("rules.txt", "LIMIT=99\n")
        self.config([{"file": "rules.txt", "description": "limit", "find": "LIMIT=99", "replace": "LIMIT=1"}])
        code, out = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("mutation-backup", out)
        self.assertEqual(self.read("rules.txt"), "LIMIT=99\n")

    def test_no_backup_is_left_after_a_run(self):
        self.config([{"file": "rules.txt", "description": "limit", "find": "LIMIT=10", "replace": "LIMIT=20"}], command=ALWAYS_PASS)
        self.run_main()
        self.assertFalse(os.path.exists(os.path.join(self.root, "rules.txt.mutation-backup")))


if __name__ == "__main__":
    unittest.main()
