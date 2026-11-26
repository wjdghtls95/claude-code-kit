"""quality-guard skills point at files that ship with the plugin (nothing outside the plugin)

Test list
  normal:   every `<base directory>/../../<path>` a skill names exists inside the plugin
  boundary: the ESLint template is plain English and exports codeStandard; the README lists every skill
  abuse:    no skill names a path outside the plugin
"""
import os
import re
import unittest

PLUGIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "quality-guard"))
SKILLS = os.path.join(PLUGIN, "skills")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class SkillFileTests(unittest.TestCase):
    def test_referenced_files_exist_inside_the_plugin(self):
        for name in os.listdir(SKILLS):
            text = read(os.path.join(SKILLS, name, "SKILL.md"))
            for rel in re.findall(r"<base directory>/\.\./\.\./([\w./-]+)", text):
                path = os.path.normpath(os.path.join(PLUGIN, rel))
                self.assertTrue(path.startswith(PLUGIN + os.sep), (name, rel))
                self.assertTrue(os.path.isfile(path), (name, rel))

    def test_eslint_template_is_english_and_exports_the_config(self):
        text = read(os.path.join(PLUGIN, "templates", "eslint-standard.js"))
        self.assertIn("export function codeStandard", text)
        self.assertIsNone(re.search("[가-힣]", text))

    def test_readmes_list_every_skill(self):
        for readme in ("README.md", "README.ko.md"):
            text = read(os.path.join(PLUGIN, readme))
            for name in os.listdir(SKILLS):
                self.assertIn(f"/quality-guard:{name}", text, (readme, name))


if __name__ == "__main__":
    unittest.main()
