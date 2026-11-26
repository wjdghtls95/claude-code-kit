"""project_context tests: find the version of a library that the project really uses, and where its source is

Test list (5 axes)
  normal:   npm (package.json range, node_modules exact version, package-lock), Python (pyproject, requirements,
            uv.lock or poetry.lock, site-packages dist-info), Go (go.mod); the changelog and readme shipped
            with the installed package, and its repository, homepage and changelog links
  error:    broken JSON or unreadable files are reported as notes, not crashes; an unknown package says "not found"
  boundary: scoped npm packages (@scope/name), Python names with - and _ and case differences,
            the lockfile wins over the declared range, node_modules wins over the lockfile
  order:    nested folders: the nearest manifest above --root is not required, only --root is searched
  abuse:    huge or binary lockfiles are capped; output never includes file contents beyond the version;
            links keep only http(s) URLs
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "plugins", "lookup", "scripts"))
import project_context as pc  # noqa: E402


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)


class NpmTests(Tmp):
    def test_declared_range_only(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5.1.0"}}))
        r = pc.find(self.root, "bullmq")
        self.assertEqual(r["ecosystem"], "npm")
        self.assertEqual(r["declared"], "^5.1.0")
        self.assertIsNone(r["installed"])

    def test_lockfile_gives_exact_version(self):
        write(self.root, "package.json", json.dumps({"devDependencies": {"bullmq": "^5.1.0"}}))
        write(self.root, "package-lock.json", json.dumps({"packages": {"node_modules/bullmq": {"version": "5.34.2"}}}))
        self.assertEqual(pc.find(self.root, "bullmq")["installed"], "5.34.2")

    def test_node_modules_wins_and_gives_source_path(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5.1.0"}}))
        write(self.root, "package-lock.json", json.dumps({"packages": {"node_modules/bullmq": {"version": "5.30.0"}}}))
        write(self.root, "node_modules/bullmq/package.json", json.dumps({"name": "bullmq", "version": "5.34.2", "types": "dist/index.d.ts"}))
        r = pc.find(self.root, "bullmq")
        self.assertEqual(r["installed"], "5.34.2")
        self.assertTrue(r["source_path"].endswith(os.path.join("node_modules", "bullmq")))
        self.assertEqual(r["types"], "dist/index.d.ts")

    def test_scoped_package(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"@nestjs/bullmq": "^10.0.0"}}))
        write(self.root, "node_modules/@nestjs/bullmq/package.json", json.dumps({"version": "10.2.1"}))
        self.assertEqual(pc.find(self.root, "@nestjs/bullmq")["installed"], "10.2.1")

    def test_pnpm_lock(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5.0.0"}}))
        write(self.root, "pnpm-lock.yaml", "packages:\n\n  bullmq@5.12.0:\n    resolution: {}\n")
        self.assertEqual(pc.find(self.root, "bullmq")["installed"], "5.12.0")

    def test_pnpm_lock_with_quoted_scoped_keys_and_peer_suffix(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"@nestjs/bullmq": "^11.0.4"}}))
        write(self.root, "pnpm-lock.yaml", "packages:\n\n  '@nestjs/bullmq@11.0.4(@nestjs/common@11.1.0)':\n    resolution: {}\n")
        self.assertEqual(pc.find(self.root, "@nestjs/bullmq")["installed"], "11.0.4")

    def test_workspace_node_modules_gives_the_source_path(self):
        write(self.root, "package.json", json.dumps({"private": True}))
        write(self.root, "apps/server/package.json", json.dumps({"dependencies": {"bullmq": "^5"}}))
        write(self.root, "apps/server/node_modules/bullmq/package.json", json.dumps({"version": "5.81.3"}))
        r = pc.find(self.root, "bullmq")
        self.assertEqual(r["installed"], "5.81.3")
        self.assertTrue(r["source_path"].endswith(os.path.join("apps", "server", "node_modules", "bullmq")))

    def test_yarn_lock(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5.0.0"}}))
        write(self.root, "yarn.lock", '"bullmq@^5.0.0":\n  version "5.9.1"\n  resolved "x"\n')
        self.assertEqual(pc.find(self.root, "bullmq")["installed"], "5.9.1")

    def test_monorepo_workspace_package_json_is_found(self):
        write(self.root, "package.json", json.dumps({"private": True}))
        write(self.root, "apps/server/package.json", json.dumps({"dependencies": {"bullmq": "^5.2.0"}}))
        r = pc.find(self.root, "bullmq")
        self.assertEqual(r["declared"], "^5.2.0")
        self.assertIn(os.path.join("apps", "server", "package.json"), r["manifests"])

    def test_broken_package_json_is_a_note_not_a_crash(self):
        write(self.root, "package.json", "{broken")
        r = pc.find(self.root, "bullmq")
        self.assertIn("could not read package.json", " ".join(r["notes"]))


class PythonTests(Tmp):
    def test_pyproject_and_uv_lock(self):
        write(self.root, "pyproject.toml", '[project]\ndependencies = ["fastapi>=0.110", "pydantic-settings~=2.3"]\n')
        write(self.root, "uv.lock", '[[package]]\nname = "fastapi"\nversion = "0.115.2"\n\n[[package]]\nname = "pydantic-settings"\nversion = "2.6.0"\n')
        r = pc.find(self.root, "fastapi")
        self.assertEqual((r["ecosystem"], r["declared"], r["installed"]), ("python", ">=0.110", "0.115.2"))

    def test_name_normalization(self):
        write(self.root, "requirements.txt", "Pydantic_Settings==2.6.0\n")
        r = pc.find(self.root, "pydantic-settings")
        self.assertEqual(r["declared"], "==2.6.0")

    def test_site_packages_dist_info_gives_installed_and_source(self):
        write(self.root, "requirements.txt", "httpx>=0.27\n")
        write(self.root, ".venv/lib/python3.12/site-packages/httpx-0.27.2.dist-info/METADATA", "Name: httpx\nVersion: 0.27.2\n")
        write(self.root, ".venv/lib/python3.12/site-packages/httpx/__init__.py", "")
        r = pc.find(self.root, "httpx")
        self.assertEqual(r["installed"], "0.27.2")
        self.assertTrue(r["source_path"].endswith(os.path.join("site-packages", "httpx")))

    def test_poetry_lock(self):
        write(self.root, "pyproject.toml", '[tool.poetry.dependencies]\nredis = "^5.0"\n')
        write(self.root, "poetry.lock", '[[package]]\nname = "redis"\nversion = "5.2.1"\n')
        r = pc.find(self.root, "redis")
        self.assertEqual((r["declared"], r["installed"]), ("^5.0", "5.2.1"))


class GoTests(Tmp):
    def test_go_mod(self):
        write(self.root, "go.mod", "module x\n\nrequire (\n\tgithub.com/redis/go-redis/v9 v9.5.1\n)\n")
        r = pc.find(self.root, "github.com/redis/go-redis/v9")
        self.assertEqual((r["ecosystem"], r["installed"]), ("go", "v9.5.1"))


class EdgeTests(Tmp):
    def test_unknown_package(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"a": "1"}}))
        r = pc.find(self.root, "nope")
        self.assertIsNone(r["declared"])
        self.assertIsNone(r["installed"])
        self.assertIn("not found", " ".join(r["notes"]))

    def test_huge_lockfile_is_capped(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5"}}))
        write(self.root, "pnpm-lock.yaml", "x" * (pc.MAX_READ_BYTES + 10) + "\n  bullmq@5.1.0:\n")
        r = pc.find(self.root, "bullmq")
        self.assertIsNone(r["installed"])

    def test_node_modules_inside_subfolders_is_not_walked(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"a": "1"}}))
        write(self.root, "node_modules/x/package.json", json.dumps({"dependencies": {"bullmq": "^4"}}))
        self.assertIsNone(pc.find(self.root, "bullmq")["declared"])

    def test_hidden_folders_like_worktree_copies_are_not_walked(self):
        write(self.root, ".claude/worktrees/old/package.json", json.dumps({"dependencies": {"bullmq": "^3"}}))
        write(self.root, "apps/server/package.json", json.dumps({"dependencies": {"bullmq": "^5"}}))
        r = pc.find(self.root, "bullmq")
        self.assertEqual(r["declared"], "^5")
        self.assertNotIn(os.path.join(".claude", "worktrees", "old", "package.json"), r["manifests"])

    def test_poetry_lock_alone_is_enough_for_python(self):
        write(self.root, "poetry.lock", '[[package]]\nname = "redis"\nversion = "5.2.1"\n')
        r = pc.find(self.root, "redis")
        self.assertEqual((r["ecosystem"], r["installed"]), ("python", "5.2.1"))

    def test_venv_alone_is_enough_for_python(self):
        write(self.root, ".venv/lib/python3.12/site-packages/httpx-0.27.2.dist-info/METADATA", "Name: httpx\n")
        self.assertEqual(pc.find(self.root, "httpx")["installed"], "0.27.2")

    def test_other_ecosystems_do_not_leak_into_the_result(self):
        write(self.root, "package.json", "{broken")
        write(self.root, "pyproject.toml", '[project]\ndependencies = ["httpx>=0.27"]\n')
        r = pc.find(self.root, "httpx")
        self.assertEqual((r["ecosystem"], r["manifests"], r["notes"]), ("python", ["pyproject.toml"], []))

    def test_cli_prints_json(self):
        import io
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5"}}))
        out = io.StringIO()
        code = pc.main(["bullmq", "--root", self.root], stdout=out)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["declared"], "^5")


class LinksAndDocsTests(Tmp):
    """docs: changelog and readme files shipped inside the installed package. links: repository, homepage, changelog"""

    def test_npm_installed_package_lists_its_changelog_and_links(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5"}}))
        write(self.root, "node_modules/bullmq/package.json", json.dumps({
            "name": "bullmq", "version": "5.34.2", "homepage": "https://docs.bullmq.io",
            "repository": {"type": "git", "url": "git+https://github.com/taskforcesh/bullmq.git"}}))
        write(self.root, "node_modules/bullmq/CHANGELOG.md", "## 5.34.2")
        write(self.root, "node_modules/bullmq/README.md", "# bullmq")
        r = pc.find(self.root, "bullmq")
        self.assertEqual([os.path.basename(d) for d in r["docs"]], ["CHANGELOG.md", "README.md"])
        self.assertEqual(r["links"], {"repository": "https://github.com/taskforcesh/bullmq", "homepage": "https://docs.bullmq.io"})

    def test_npm_repository_shorthand_and_string(self):
        for repo, want in (("github:colinhacks/zod", "https://github.com/colinhacks/zod"),
                           ("colinhacks/zod", "https://github.com/colinhacks/zod"),
                           ("git@github.com:colinhacks/zod.git", "https://github.com/colinhacks/zod")):
            write(self.root, "package.json", json.dumps({"dependencies": {"zod": "^3"}}))
            write(self.root, "node_modules/zod/package.json", json.dumps({"name": "zod", "version": "3.23.8", "repository": repo}))
            self.assertEqual(pc.find(self.root, "zod")["links"].get("repository"), want, repo)

    def test_python_metadata_project_urls(self):
        write(self.root, "requirements.txt", "httpx\n")
        write(self.root, ".venv/lib/python3.12/site-packages/httpx-0.27.2.dist-info/METADATA",
              "Name: httpx\nVersion: 0.27.2\nHome-page: https://www.python-httpx.org\n"
              "Project-URL: Changelog, https://github.com/encode/httpx/blob/master/CHANGELOG.md\n"
              "Project-URL: Source, https://github.com/encode/httpx\n\nlong description with Project-URL: fake, https://x\n")
        write(self.root, ".venv/lib/python3.12/site-packages/httpx/__init__.py", "")
        r = pc.find(self.root, "httpx")
        self.assertEqual(r["links"], {"homepage": "https://www.python-httpx.org",
                                      "changelog": "https://github.com/encode/httpx/blob/master/CHANGELOG.md",
                                      "repository": "https://github.com/encode/httpx"})

    def test_nothing_installed_gives_empty_docs_and_links(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"bullmq": "^5"}}))
        r = pc.find(self.root, "bullmq")
        self.assertEqual((r["docs"], r["links"]), ([], {}))

    def test_links_ignore_non_web_values(self):
        write(self.root, "package.json", json.dumps({"dependencies": {"x": "1"}}))
        write(self.root, "node_modules/x/package.json", json.dumps({"name": "x", "version": "1.0.0",
                                                                    "homepage": "javascript:alert(1)", "repository": 42}))
        self.assertEqual(pc.find(self.root, "x")["links"], {})


if __name__ == "__main__":
    unittest.main()
