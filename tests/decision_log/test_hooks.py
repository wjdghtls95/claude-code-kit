"""decision-log hook tests

Test list (5 axes)
  normal:   pending candidates in the buffer -> a reminder with the count
  error:    broken stdin / unreadable buffer -> exit 0 and no output
  boundary: empty buffer, only rejected items, no buffer file -> no output
  order:    hook input without cwd falls back to the project directory env var
  abuse:    kill switch env var, 10000 pending lines, binary garbage in the buffer
Plugin structure checks: every skill has frontmatter matching its folder, no personal paths
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN = os.path.join(ROOT, "plugins", "decision-log")
HOOK = os.path.join(PLUGIN, "scripts", "pending_patterns.py")


def run(stdin, env_extra=None, cwd=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("DECISION_LOG", "CLAUDE_PROJECT_DIR"))}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, HOOK], input=stdin.encode("utf-8"), capture_output=True, env=env, cwd=cwd)


class Project:
    def __init__(self, buffer_text=None, raw=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        if buffer_text is not None or raw is not None:
            d = os.path.join(self.dir, ".claude", "memory")
            os.makedirs(d)
            with open(os.path.join(d, "pattern_candidates.md"), "wb") as f:
                f.write(raw if raw is not None else buffer_text.encode("utf-8"))

    def hook_input(self):
        return json.dumps({"hook_event_name": "SessionStart", "cwd": self.dir})


class HookTests(unittest.TestCase):
    def project(self, **kw):
        p = Project(**kw)
        self.addCleanup(p.tmp.cleanup)
        return p

    def context(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        if not result.stdout.strip():
            return ""
        return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_script_exists(self):
        self.assertTrue(os.path.isfile(HOOK))

    def test_pending_items_produce_reminder_with_count(self):
        p = self.project(buffer_text="- [pending] a lesson (2026-01-01)\n- [pending] another (2026-01-02)\n- [rejected] old (2026-01-03)\n")
        ctx = self.context(run(p.hook_input()))
        self.assertIn("2 pending pattern candidate", ctx)

    def test_no_buffer_file_is_silent(self):
        p = self.project()
        self.assertEqual(self.context(run(p.hook_input())), "")

    def test_empty_buffer_is_silent(self):
        p = self.project(buffer_text="")
        self.assertEqual(self.context(run(p.hook_input())), "")

    def test_only_rejected_is_silent(self):
        p = self.project(buffer_text="- [rejected] old (2026-01-03)\n")
        self.assertEqual(self.context(run(p.hook_input())), "")

    def test_broken_stdin_is_silent_and_exit_zero(self):
        r = run("not json at all")
        self.assertEqual(r.returncode, 0)

    def test_unreadable_buffer_is_silent_and_exit_zero(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root can read any file")
        p = self.project(buffer_text="- [pending] x (2026-01-01)\n")
        path = os.path.join(p.dir, ".claude", "memory", "pattern_candidates.md")
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o644)
        r = run(p.hook_input())
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), b"")

    def test_empty_stdin_exit_zero(self):
        self.assertEqual(run("").returncode, 0)

    def test_binary_garbage_in_buffer_does_not_crash(self):
        p = self.project(raw=b"\xff\xfe\x00- [pending] x\n\xff")
        self.assertEqual(run(p.hook_input()).returncode, 0)

    def test_falls_back_to_project_dir_env(self):
        p = self.project(buffer_text="- [pending] one (2026-01-01)\n")
        ctx = self.context(run("{}", {"CLAUDE_PROJECT_DIR": p.dir}))
        self.assertIn("1 pending pattern candidate", ctx)

    def test_project_dir_env_wins_over_hook_cwd(self):
        with_pending = self.project(buffer_text="- [pending] one (2026-01-01)\n")
        without = self.project()
        r = run(without.hook_input(), {"CLAUDE_PROJECT_DIR": with_pending.dir})
        self.assertIn("1 pending pattern candidate", self.context(r))

    def test_kill_switch(self):
        p = self.project(buffer_text="- [pending] one (2026-01-01)\n")
        self.assertEqual(self.context(run(p.hook_input(), {"DECISION_LOG": "off"})), "")

    def test_many_pending_lines_report_count_without_listing_all(self):
        p = self.project(buffer_text="".join(f"- [pending] item {i} (2026-01-01)\n" for i in range(10000)))
        ctx = self.context(run(p.hook_input()))
        self.assertIn("10000 pending pattern candidate", ctx)
        self.assertLess(len(ctx), 2000)


class ContentTests(unittest.TestCase):
    def test_examples_follow_the_documented_file_name_and_sections(self):
        sections = ["## Situation", "## Previous approach", "## Trigger", "## New approach",
                    "## Alternatives considered", "## When to apply", "## When not to apply", "## Related patterns"]
        base = os.path.join(PLUGIN, "examples")
        names = sorted(os.listdir(base))
        self.assertEqual(len(names), 2)
        for n in names:
            text = open(os.path.join(base, n), encoding="utf-8").read()
            domain = re.search(r"(?m)^  domain: (.+)$", text).group(1).strip()
            self.assertTrue(n.startswith(f"pattern_{domain}_"), n)
            for s in sections:
                self.assertIn(s, text, (n, s))

    def test_lookup_and_update_skills_say_what_to_do_when_the_folder_is_missing(self):
        for name in ("concept-update", "decision-lookup"):
            text = open(os.path.join(PLUGIN, "skills", name, "SKILL.md"), encoding="utf-8").read()
            self.assertRegex(text, r"(?i)does not exist.*say so", name)

    def test_progress_template_has_the_sections_the_skills_write_to(self):
        text = open(os.path.join(PLUGIN, "templates", "progress.template.md"), encoding="utf-8").read()
        for s in ("## Working Notes", "## Status", "## Completed", "## Next"):
            self.assertIn(s, text)

    def test_template_path_is_unambiguous(self):
        text = open(os.path.join(PLUGIN, "skills", "topic-tracking", "SKILL.md"), encoding="utf-8").read()
        self.assertIn("`templates/progress.template.md`", text)


class StructureTests(unittest.TestCase):
    def skills(self):
        base = os.path.join(PLUGIN, "skills")
        return [d for d in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, d))] if os.path.isdir(base) else []

    def test_every_skill_has_matching_frontmatter(self):
        names = self.skills()
        self.assertGreaterEqual(len(names), 6)
        for name in names:
            text = open(os.path.join(PLUGIN, "skills", name, "SKILL.md"), encoding="utf-8").read()
            m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
            self.assertIsNotNone(m, name)
            self.assertEqual(m.group(1).strip(), name)

    def test_hooks_json_points_to_existing_scripts(self):
        data = json.load(open(os.path.join(PLUGIN, "hooks", "hooks.json"), encoding="utf-8"))
        cmds = [h["command"] for g in data["hooks"].values() for e in g for h in e["hooks"]]
        self.assertTrue(cmds)
        for c in cmds:
            script = re.search(r'\$\{CLAUDE_PLUGIN_ROOT\}/([^"\s]+)', c).group(1)
            self.assertTrue(os.path.isfile(os.path.join(PLUGIN, script)), script)

    def test_no_personal_paths_or_non_ascii_in_plugin_files(self):
        for root, _, files in os.walk(PLUGIN):
            for f in files:
                if f.endswith(".ko.md"):
                    continue
                text = open(os.path.join(root, f), encoding="utf-8").read()
                self.assertNotRegex(text, "/" + "Users/|/home/\\w+", f)
                if f != "README.md":  # the language switch link contains the Korean word
                    self.assertNotRegex(text, "[\uac00-\ud7a3]", f)


if __name__ == "__main__":
    unittest.main()
