"""session-handoff structure and behavior tests

Test list (5 axes)
  normal:   three skills exist with frontmatter whose name matches the folder
  error:    wrap-up does not push, merge or open pull requests (that belongs to a git workflow),
            resume does not switch branches or pull, next-task-check only edits the progress file
  boundary: skills ask before large changes (archive of a long progress file), and say what they changed
  order:    next-task-check verifies pull request state before it reads the progress file
  abuse:    no project-specific words, no personal paths, no Hangul in English files
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN = os.path.join(ROOT, "plugins", "session-handoff")
SKILLS = ["wrap-up", "resume", "next-task-check"]
PROJECT_WORDS = ["obsidian", "cleanup.md", "fix-next", "agents.md", "agent-plan", "motionlab", "jarvis",
                 "nestjs", "phase file", "concept-update"]


def skill(name):
    with open(os.path.join(PLUGIN, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class StructureTests(unittest.TestCase):
    def test_manifest_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))

    def test_only_the_expected_skills_exist(self):
        base = os.path.join(PLUGIN, "skills")
        self.assertEqual(sorted(os.listdir(base)), sorted(SKILLS))

    def test_every_skill_has_matching_frontmatter(self):
        for name in SKILLS:
            m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", skill(name))
            self.assertIsNotNone(m, name)
            self.assertEqual(m.group(1).strip(), name)

    def test_no_pre_granted_tools(self):
        for name in SKILLS:
            self.assertNotRegex(skill(name), r"(?m)^allowed-tools:")

    def test_wrap_up_does_not_push_merge_or_open_pull_requests(self):
        t = skill("wrap-up")
        for forbidden in ("git push", "gh pr create", "gh pr merge", "git checkout"):
            self.assertNotIn(forbidden, t, forbidden)

    def test_wrap_up_reports_git_state_read_only(self):
        t = skill("wrap-up")
        self.assertIn("git status", t)
        self.assertRegex(t, r"(?i)do not push|does not push|only report")

    def test_wrap_up_says_what_it_changed_and_asks_before_archiving(self):
        t = skill("wrap-up")
        self.assertRegex(t, r"(?i)say in one line what you (changed|wrote)")
        self.assertRegex(t, r"(?i)ask (first|before)")

    def test_wrap_up_tells_the_user_to_type_clear_because_claude_cannot(self):
        self.assertRegex(skill("wrap-up"), r"(?i)tell the user to type it")

    def test_wrap_up_queries_every_pull_request_state_and_handles_missing_gh(self):
        t = skill("wrap-up")
        self.assertIn("--state all", t)
        self.assertRegex(t, r"(?i)if `gh` is not available")

    def test_both_skills_say_what_to_do_without_a_progress_file(self):
        self.assertRegex(skill("wrap-up"), r"(?i)no progress file")
        self.assertRegex(skill("next-task-check"), r"(?i)no progress file")

    def test_resume_age_check_only_when_entries_have_dates(self):
        self.assertRegex(skill("resume"), r"(?i)if the entries have no dates")

    def test_resume_does_not_switch_branches_or_pull(self):
        t = skill("resume")
        for forbidden in ("git checkout", "git pull", "git fetch", "git switch"):
            self.assertNotIn(forbidden, t, forbidden)

    def test_resume_asks_before_continuing(self):
        self.assertRegex(skill("resume"), r"(?i)ask the user whether")

    def test_next_task_check_verifies_pull_requests_before_reading_progress(self):
        t = skill("next-task-check")
        self.assertLess(t.index("gh pr list"), t.index("Step 1"))

    def test_next_task_check_never_merges(self):
        t = skill("next-task-check")
        for forbidden in ("gh pr merge", "git push", "git checkout"):
            self.assertNotIn(forbidden, t, forbidden)

    def test_progress_template_exists_and_is_referenced_by_path(self):
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "templates", "progress.template.md")))
        self.assertIn("`templates/progress.template.md`", skill("wrap-up"))
        for name in ("resume", "next-task-check"):
            self.assertIn("`wrap-up` skill", skill(name), name)  # short pointer instead of a repeated paragraph

    def test_no_project_words_personal_paths_or_hangul(self):
        for root, _, files in os.walk(PLUGIN):
            for f in files:
                if f.endswith(".ko.md"):
                    continue
                text = open(os.path.join(root, f), encoding="utf-8").read()
                self.assertNotRegex(text, "/" + "Users/|/home/\\w+", f)
                for w in PROJECT_WORDS:
                    self.assertNotIn(w, text.lower(), (f, w))
                if f != "README.md":
                    self.assertNotRegex(text, "[가-힣]", f)


if __name__ == "__main__":
    unittest.main()
