"""code-review structure tests

Test list (5 axes)
  normal:   every skill and agent has frontmatter whose name matches its file or folder
  error:    agents declare only read-only tools; no skill pre-grants tool permissions
  boundary: expected skills and agents all exist; the REVIEW.md template has all sections
  order:    skills that refer to each other by name only refer to skills that exist; templates they mention exist
  abuse:    no personal paths, no real company names, no Hangul in English files
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN = os.path.join(ROOT, "plugins", "code-review")
SKILLS = ["review-routing", "review-followup", "pr-review", "design-review", "review-checklist"]
AGENTS = ["reviewer-server", "reviewer-front", "reviewer-ai", "reviewer-infra"]
COMPANIES = ["Google", "Amazon", "Meta", "Vercel", "Kakao", "Toss", "Naver", "OpenAI", "Anthropic partner", "Line "]
READ_ONLY = {"Read", "Grep", "Glob"}


def read(*parts):
    with open(os.path.join(PLUGIN, *parts), encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


class StructureTests(unittest.TestCase):
    def test_manifest_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))

    def test_every_skill_exists_with_matching_name(self):
        for name in SKILLS:
            fm = frontmatter(read("skills", name, "SKILL.md"))
            self.assertIsNotNone(fm, name)
            self.assertRegex(fm, r"(?m)^name: " + re.escape(name) + r"$")
            self.assertRegex(fm, r"(?m)^description: .+")

    def test_every_agent_exists_with_matching_name(self):
        for name in AGENTS:
            fm = frontmatter(read("agents", name + ".md"))
            self.assertIsNotNone(fm, name)
            self.assertRegex(fm, r"(?m)^name: " + re.escape(name) + r"$")
            self.assertRegex(fm, r"(?m)^description: .+")

    def test_agents_are_read_only(self):
        for name in AGENTS:
            fm = frontmatter(read("agents", name + ".md"))
            m = re.search(r"(?m)^tools: (.+)$", fm)
            self.assertIsNotNone(m, name + " must declare tools")
            tools = {t.strip() for t in m.group(1).split(",")}
            self.assertTrue(tools <= READ_ONLY, (name, tools))

    def test_skills_do_not_pre_grant_tools(self):
        for name in SKILLS:
            self.assertNotRegex(frontmatter(read("skills", name, "SKILL.md")), r"(?m)^allowed-tools:", name)

    def test_review_template_has_all_sections(self):
        text = read("templates", "REVIEW.template.md")
        for heading in ["IMPORTANT", "NIT", "DO NOT FLAG", "SKIP", "Severity"]:
            self.assertIn(heading, text)

    def test_skill_cross_references_point_to_existing_skills(self):
        for name in SKILLS:
            text = read("skills", name, "SKILL.md")
            for ref in re.findall(r"`([a-z]+(?:-[a-z]+)+)` skill", text):
                self.assertIn(ref, SKILLS, (name, ref))

    def test_every_template_a_skill_points_to_exists(self):
        for name in SKILLS:
            text = read("skills", name, "SKILL.md")
            for ref in re.findall(r"`(?:templates/)?([A-Za-z.]+\.template\.md)`", text):
                self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "templates", ref)), (name, ref))

    def test_pr_review_and_agents_read_review_md_when_present(self):
        self.assertIn("REVIEW.md", read("skills", "pr-review", "SKILL.md"))
        for name in AGENTS:
            self.assertIn("REVIEW.md", read("agents", name + ".md"), name)

    def test_review_md_is_read_from_the_default_branch_so_a_pr_cannot_silence_itself(self):
        text = read("skills", "pr-review", "SKILL.md")
        self.assertIn("git show origin/", text)
        self.assertRegex(text, r"(?i)changes `REVIEW\.md`")
        for name in AGENTS:
            self.assertRegex(read("agents", name + ".md"), r"(?i)default branch", name)

    def test_severity_levels_have_a_mapping(self):
        text = read("skills", "pr-review", "SKILL.md")
        self.assertIn("Severity mapping", text)
        template = read("templates", "REVIEW.template.md")
        self.assertIn("Warning", template)

    def test_progress_template_has_the_review_issue_section(self):
        text = read("templates", "progress.template.md")
        for s in ("## Review Issues", "## Status", "## Next"):
            self.assertIn(s, text)

    def test_auto_fix_is_described_as_a_proposal(self):
        text = read("skills", "pr-review", "SKILL.md")
        self.assertIn("never edits files", text)

    def test_no_personal_paths_companies_or_hangul(self):
        for root, _, files in os.walk(PLUGIN):
            for f in files:
                if f.endswith(".ko.md"):
                    continue
                text = open(os.path.join(root, f), encoding="utf-8").read()
                self.assertNotRegex(text, "/" + "Users/|/home/\\w+", f)
                for c in COMPANIES:
                    self.assertNotIn(c, text, (f, c))
                if f != "README.md":  # the language switch link contains the Korean word
                    self.assertNotRegex(text, "[가-힣]", f)


if __name__ == "__main__":
    unittest.main()
