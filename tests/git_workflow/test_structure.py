"""git-workflow structure and behavior tests

Test list (5 axes)
  normal:   every skill exists with frontmatter whose name matches its folder
  error:    risky git actions are guarded in the text (no add -A, confirm before commit message and merge,
            never force-push without approval, never auto-resolve conflicts)
  boundary: no hard dependency on another plugin of this kit, templates the skills mention exist
  order:    ship pushes only after staging specific files; land confirms before it merges
  abuse:    no personal paths, no project-specific words, no Hangul in English files (README.md is exempt, its language link contains the Korean word)
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN = os.path.join(ROOT, "plugins", "git-workflow")
SKILLS = ["ship", "land", "pr-check", "git-rules", "ship-reminder", "git-conventions"]
OTHER_PLUGINS = ["quality-guard", "decision-log", "code-review", "session-handoff"]
PROJECT_WORDS = ["motionlab", "jarvis", "nestjs", "prisma", "bullmq", "pnpm", "obsidian"]


def skill(name):
    with open(os.path.join(PLUGIN, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class StructureTests(unittest.TestCase):
    def test_manifest_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))

    def test_every_skill_has_matching_frontmatter(self):
        for name in SKILLS:
            m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", skill(name))
            self.assertIsNotNone(m, name)
            self.assertEqual(m.group(1).strip(), name)

    def test_no_pre_granted_tools(self):
        for name in SKILLS:
            self.assertNotRegex(skill(name), r"(?m)^allowed-tools:")

    def test_ship_never_uses_add_all_and_confirms_the_message(self):
        t = skill("ship")
        self.assertIn("git add -A", t)  # mentioned only to forbid it
        self.assertRegex(t, r"(?i)do not use `git add -A`|never use `git add -A`")
        self.assertRegex(t, r"(?i)wait for (the user's )?confirmation")

    def test_ship_stages_before_it_pushes(self):
        t = skill("ship")
        self.assertLess(t.index("Step 3: stage"), t.index("Step 4: push"))

    def test_land_confirms_before_merging(self):
        t = skill("land")
        self.assertLess(t.lower().index("confirm"), t.index("gh pr merge"))

    def test_git_rules_guard_force_push_and_conflicts(self):
        t = skill("git-rules")
        self.assertRegex(t, r"(?i)never force-push without (the user's )?approval")
        self.assertRegex(t, r"(?i)never auto-resolve conflicts")
        self.assertRegex(t, r"(?i)never commit or push directly to the (default|main) branch")

    def test_conventions_decide_the_scope_rule_explicitly(self):
        t = skill("git-conventions")
        self.assertIn("scope", t)
        self.assertRegex(t, r"(?i)one short lowercase name")

    def test_force_push_wording_is_the_same_everywhere(self):
        for path in (os.path.join(PLUGIN, "README.md"), os.path.join(PLUGIN, "skills", "git-rules", "SKILL.md")):
            text = open(path, encoding="utf-8").read()
            self.assertNotIn("never force-push and", text.lower(), path)
            self.assertRegex(text, r"(?i)force-push without (the user's |your )?approval", path)

    def test_squash_merged_branches_are_deleted_with_capital_d(self):
        self.assertIn("git branch -D", skill("git-rules"))
        self.assertNotIn("`git branch -d <branch>`", skill("git-rules"))

    def test_conventions_do_not_hard_code_the_main_branch_in_rebase(self):
        self.assertNotIn("git rebase main", skill("git-conventions"))

    def test_pr_check_only_logs_to_the_progress_file_when_the_user_agrees(self):
        self.assertRegex(skill("pr-check"), r"(?i)offer to add one line")

    def test_template_path_is_unambiguous(self):
        self.assertIn("`templates/progress.template.md`", skill("pr-check"))

    def test_no_dependency_on_other_plugins_or_project_words(self):
        for root, _, files in os.walk(PLUGIN):
            for f in files:
                if f.endswith(".ko.md"):
                    continue
                text = open(os.path.join(root, f), encoding="utf-8").read().lower()
                for w in OTHER_PLUGINS + PROJECT_WORDS:
                    # the built-in /code-review command is not the plugin, so a leading slash is allowed
                    self.assertNotRegex(text, r"(?<![\w/-])" + re.escape(w) + r"(?![\w-])", (f, w))

    def test_no_personal_paths_or_hangul(self):
        for root, _, files in os.walk(PLUGIN):
            for f in files:
                if f.endswith(".ko.md"):
                    continue
                text = open(os.path.join(root, f), encoding="utf-8").read()
                self.assertNotRegex(text, "/" + "Users/|/home/\\w+", f)
                if f != "README.md":
                    self.assertNotRegex(text, "[가-힣]", f)

    def test_every_template_a_skill_points_to_exists(self):
        for name in SKILLS:
            for ref in re.findall(r"`(?:templates/)?([A-Za-z.\-_]+\.(?:template\.md|example\.json))`", skill(name)):
                self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "templates", ref)), (name, ref))


if __name__ == "__main__":
    unittest.main()
