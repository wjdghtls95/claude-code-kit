"""lookup structure tests: the skill keeps the rules that make search trustworthy"""
import os
import re
import unittest

PLUGIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "lookup"))


def skill():
    with open(os.path.join(PLUGIN, "skills", "find", "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class SkillTests(unittest.TestCase):
    def test_frontmatter(self):
        m = re.match(r'---\nname: find\ndescription: "(.+)"\n---\n', skill())
        self.assertIsNotNone(m)

    def test_script_the_skill_points_to_exists(self):
        self.assertIn("scripts/project_context.py", skill())
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "scripts", "project_context.py")))

    def test_project_first_and_installed_version_rules(self):
        t = skill()
        self.assertLess(t.index("Look in the project first"), t.index("Then the web"))
        self.assertIn("installed major version", t)

    def test_information_rules(self):
        t = skill().lower()
        for phrase in ("primary sources", "check the date", "two independent sources", "not confirmed"):
            self.assertIn(phrase, t)

    def test_open_the_primary_page_and_stay_on_topic(self):
        t = skill()
        self.assertIn("open the primary page itself", t)
        self.assertIn("A search result snippet is a lead, not a source", t)
        self.assertIn("stay on the question", t)

    def test_never_invent_and_safe_checks(self):
        t = skill()
        self.assertIn("Never invent", t)
        self.assertRegex(t, r"no side effects")
        self.assertIn("not run", t)

    def test_no_pre_granted_tools_and_no_hangul(self):
        t = skill()
        self.assertNotRegex(t, r"(?m)^allowed-tools:")
        self.assertNotRegex(t, "[가-힣]")


if __name__ == "__main__":
    unittest.main()
