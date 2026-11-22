"""Frontmatter of every skill and agent in every plugin must be valid YAML.

The Claude Code validator rejects a plain (unquoted) value that contains ": " or " #". A broken
frontmatter makes the file load with empty metadata at runtime, so an agent would lose its tool
restrictions. PyYAML is not available everywhere, so this checks the rules that bite in practice.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLUGINS = os.path.join(ROOT, "plugins")


def frontmatter_files():
    for root, _, files in os.walk(PLUGINS):
        for f in files:
            if f.endswith(".md") and not f.startswith("README"):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                m = re.match(r"---\n(.*?)\n---\n", text, re.S)
                if m:
                    yield os.path.relpath(path, ROOT), m.group(1)


def plain_value_problem(value):
    value = value.strip()
    if not value or value[0] in "\"'[{|>":
        return None
    if ": " in value:
        return "unquoted value contains ': '"
    if " #" in value:
        return "unquoted value contains ' #'"
    if value[0] in "*&!%@`":
        return "unquoted value starts with a YAML indicator"
    return None


class FrontmatterTests(unittest.TestCase):
    def test_found_some_files(self):
        self.assertGreater(len(list(frontmatter_files())), 10)

    def test_plain_values_are_valid_yaml(self):
        for path, fm in frontmatter_files():
            for line in fm.splitlines():
                m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
                if not m:
                    continue
                problem = plain_value_problem(m.group(2))
                self.assertIsNone(problem, f"{path}: {line[:80]!r} {problem}")

    def test_checker_catches_the_known_bad_value(self):
        self.assertIsNotNone(plain_value_problem("Use when reviewing code: auth, caches"))
        self.assertIsNone(plain_value_problem('"Use when reviewing code: auth, caches"'))
        self.assertIsNone(plain_value_problem("Use when reviewing code, auth, caches"))

    def test_every_agent_still_declares_name_description_and_tools(self):
        for path, fm in frontmatter_files():
            if os.sep + "agents" + os.sep in path:
                for key in ("name", "description", "tools"):
                    self.assertRegex(fm, r"(?m)^" + key + r": .+", f"{path} missing {key}")


if __name__ == "__main__":
    unittest.main()
