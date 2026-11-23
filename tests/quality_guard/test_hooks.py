"""Tests for the quality-guard hooks (standard library only).

Run from the repository root:  python3 -m unittest discover -s tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, "plugins", "quality-guard", "scripts")
sys.path.insert(0, SCRIPTS)


# ---- transcript fixtures (one content block per entry, like Claude Code writes them) ----
def user_prompt(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def user_tool_result():
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}}


def assistant_text(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def assistant_tool_use(name="Write"):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": name, "input": {}}]}}


def user_image_only():
    return {"type": "user", "message": {"role": "user", "content": [{"type": "image", "source": {"type": "base64", "data": "x"}}]}}


def assistant_thinking():
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "..."}]}}


def legacy_assistant(text):
    return {"role": "assistant", "content": text}


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = os.path.join(self.tmp.name, "project")
        os.makedirs(self.project)
        self.addCleanup(self.tmp.cleanup)

    def write_transcript(self, entries, raw_lines=None):
        path = os.path.join(self.tmp.name, "transcript.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
            for line in raw_lines or []:
                f.write(line + "\n")
        return path

    def write_config(self, data, raw=None):
        with open(os.path.join(self.project, ".quality-guard.json"), "w", encoding="utf-8") as f:
            f.write(raw if raw is not None else json.dumps(data))

    def run_hook(self, script, payload, env_extra=None, stdin_text=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("QUALITY_GUARD")}
        env["CLAUDE_PROJECT_DIR"] = self.project
        env.update(env_extra or {})
        stdin = stdin_text if stdin_text is not None else json.dumps(payload, ensure_ascii=False)
        path = os.path.join(SCRIPTS, script)
        self.assertTrue(os.path.isfile(path), "hook script missing: " + script)
        r = subprocess.run([sys.executable, path], input=stdin.encode("utf-8"), capture_output=True, env=env)
        r.stderr = r.stderr.decode("utf-8", errors="replace")
        r.stdout = r.stdout.decode("utf-8", errors="replace")
        if r.returncode == 2:
            self.assertIn("[quality-guard]", r.stderr, "exit 2 must carry a quality-guard message, got: " + r.stderr[:200])
        else:
            self.assertEqual(r.returncode, 0, "unexpected exit code with stderr: " + r.stderr[:200])
        return r.returncode, r.stderr, r.stdout

    def edit_payload(self, transcript, file_path="src/app.py", tool="Edit", content=None):
        full = file_path if os.path.isabs(file_path) else os.path.join(self.project, file_path)
        ti = {"file_path": full}
        if content is not None:
            ti["content"] = content
        return {"tool_name": tool, "tool_input": ti, "transcript_path": transcript, "cwd": self.project}


class TierGuardTests(HookCase):
    # axis 1: normal path
    def test_allows_when_turn_has_tier_a(self):
        t = self.write_transcript([user_prompt("add feature"), assistant_text("[A] new feature, running the rounds"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)

    def test_allows_tier_b_and_c(self):
        for tier in ("[B]", "[C]"):
            t = self.write_transcript([user_prompt("x"), assistant_text(tier + " small change"), assistant_tool_use()])
            self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0, tier)

    def test_allows_non_source_file_without_declaration(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("no tier here"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "README.md"))[0], 0)

    def test_blocks_source_file_without_declaration(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("I will edit it now"), assistant_tool_use()])
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(t, "src/app.ts"))
        self.assertEqual(code, 2)
        self.assertIn("tier", err.lower())
        self.assertIn("QUALITY_GUARD=off", err)

    def test_block_message_says_the_declaration_must_be_visible_text(self):
        # Seen in a live session: Claude declared inside its reasoning and could not tell why it stayed blocked.
        t = self.write_transcript([user_prompt("x"), assistant_text("I will edit it now"), assistant_tool_use()])
        _, err, _ = self.run_hook("tier_guard.py", self.edit_payload(t, "src/app.ts"))
        self.assertIn("plain text", err)
        self.assertIn("reasoning", err)

    # axis 2: error variants (fail open when nothing can be verified)
    def test_fails_open_when_transcript_missing(self):
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(os.path.join(self.tmp.name, "nope.jsonl")))
        self.assertEqual(code, 0)
        self.assertIn("could not verify", err.lower())

    def test_fails_open_when_no_transcript_path(self):
        payload = self.edit_payload("")
        payload.pop("transcript_path")
        self.assertEqual(self.run_hook("tier_guard.py", payload)[0], 0)

    def test_fails_open_when_turn_has_no_assistant_entries(self):
        t = self.write_transcript([user_prompt("x")])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)

    def test_fails_open_when_turn_has_no_visible_text(self):
        # Seen in real transcripts: visible text may not be persisted yet. Never lock the user out.
        t = self.write_transcript([user_prompt("x"), assistant_thinking(), assistant_tool_use()])
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(t))
        self.assertEqual(code, 0)
        self.assertIn("could not verify", err.lower())

    def test_user_message_sent_mid_turn_does_not_start_a_new_turn(self):
        # Claude Code stores a message the user sends while it works next to tool results in one user entry.
        mid_turn = {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t1", "content": "ok"},
            {"type": "text", "text": "The user sent a new message while you were working: keep going"}]}}
        t = self.write_transcript([user_prompt("x"), assistant_text("[A] plan"), assistant_tool_use(), mid_turn,
                                   assistant_thinking(), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)

    def test_ignores_malformed_lines(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("[A] go"), assistant_tool_use()], raw_lines=["{broken json", ""])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)

    def test_supports_legacy_top_level_role_schema(self):
        t = self.write_transcript([{"role": "user", "content": "x"}, legacy_assistant("[A] ok")])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)
        t2 = self.write_transcript([{"role": "user", "content": "x"}, legacy_assistant("no tier")])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t2))[0], 2)

    # axis 3: boundaries
    def test_declaration_from_previous_turn_does_not_count(self):
        t = self.write_transcript([user_prompt("first"), assistant_text("[A] earlier turn"), assistant_tool_use(), user_tool_result(),
                                   user_prompt("second"), assistant_text("no declaration now"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 2)

    def test_declaration_in_user_text_does_not_count(self):
        t = self.write_transcript([user_prompt("please use [A]"), assistant_text("working"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 2)

    def test_lowercase_tier_does_not_count(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("[a] lowercase"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 2)

    def test_skip_patterns_and_extension_case(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("no tier"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "node_modules/pkg/index.js"))[0], 0)
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "src/APP.PY"))[0], 2)

    def test_fails_open_when_turn_start_is_outside_the_read_window(self):
        entries = [user_prompt("x")] + [assistant_tool_use() for _ in range(200)]
        t = self.write_transcript(entries)
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(t), env_extra={"QUALITY_GUARD_TAIL_BYTES": "1500"})
        self.assertEqual(code, 0)
        self.assertIn("could not verify", err.lower())

    # axis 4: order and timing
    def test_declaration_covers_every_edit_in_the_same_turn(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("[A] plan"), assistant_tool_use(), user_tool_result(),
                                   assistant_thinking(), assistant_tool_use(), user_tool_result(), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)

    def test_declaration_after_tool_results_in_same_turn_counts(self):
        t = self.write_transcript([user_prompt("x"), assistant_tool_use("Read"), user_tool_result(), assistant_text("[B] now editing"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0)

    # axis 5: abnormal use
    def test_kill_switch(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("no tier"), assistant_tool_use()])
        for value in ("off", "0", "FALSE"):
            self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t), env_extra={"QUALITY_GUARD": value})[0], 0, value)

    def test_project_config_changes_source_extensions(self):
        self.write_config({"source_extensions": [".lua"]})
        t = self.write_transcript([user_prompt("x"), assistant_text("no tier"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "init.lua"))[0], 2)
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "src/app.py"))[0], 0)

    def test_invalid_config_falls_back_to_defaults_with_notice(self):
        self.write_config(None, raw="{not json")
        t = self.write_transcript([user_prompt("x"), assistant_text("no tier"), assistant_tool_use()])
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(t))
        self.assertEqual(code, 2)
        self.assertIn(".quality-guard.json", err)

    def test_invalid_stdin_and_other_tools_are_ignored(self):
        self.assertEqual(self.run_hook("tier_guard.py", None, stdin_text="not json")[0], 0)
        t = self.write_transcript([user_prompt("x"), assistant_text("no tier"), assistant_tool_use()])
        payload = self.edit_payload(t)
        payload["tool_name"] = "Bash"
        self.assertEqual(self.run_hook("tier_guard.py", payload)[0], 0)


class TddGuardTests(HookCase):
    MAPPING = {"tdd": {"mappings": [{"source": r"^src/(?P<name>[^/]+)\.py$", "test": "tests/test_{name}.py"}]}}

    def write_payload(self, rel, content="x = 1\n"):
        return self.edit_payload("", rel, tool="Write", content=content)

    def test_noop_without_config(self):
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("src/new.py"))[0], 0)

    def test_blocks_new_source_file_without_test(self):
        self.write_config(self.MAPPING)
        code, err, _ = self.run_hook("tdd_guard.py", self.write_payload("src/new.py"))
        self.assertEqual(code, 2)
        self.assertIn("tests/test_new.py", err)

    def test_allows_when_test_exists(self):
        self.write_config(self.MAPPING)
        os.makedirs(os.path.join(self.project, "tests"))
        open(os.path.join(self.project, "tests", "test_new.py"), "w").close()
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("src/new.py"))[0], 0)

    def test_allows_modifying_an_existing_file(self):
        self.write_config(self.MAPPING)
        os.makedirs(os.path.join(self.project, "src"))
        open(os.path.join(self.project, "src", "old.py"), "w").close()
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("src/old.py"))[0], 0)

    def test_allows_test_files_and_unmatched_files(self):
        self.write_config(self.MAPPING)
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("tests/test_x.py"))[0], 0)
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("scripts/other.py"))[0], 0)

    def test_content_regex_limits_enforcement(self):
        cfg = {"tdd": {"mappings": [{"source": r"^src/(?P<name>[^/]+)\.py$", "test": "tests/test_{name}.py", "content_regex": r"^def "}]}}
        self.write_config(cfg)
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("src/consts.py", "A = 1\n"))[0], 0)
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("src/logic.py", "def f():\n    pass\n"))[0], 2)

    def test_only_write_tool_is_checked(self):
        self.write_config(self.MAPPING)
        payload = self.write_payload("src/new.py")
        payload["tool_name"] = "Edit"
        self.assertEqual(self.run_hook("tdd_guard.py", payload)[0], 0)

    def test_kill_switch_and_invalid_config(self):
        self.write_config(self.MAPPING)
        self.assertEqual(self.run_hook("tdd_guard.py", self.write_payload("src/new.py"), env_extra={"QUALITY_GUARD": "off"})[0], 0)
        self.write_config(None, raw="{broken")
        code, err, _ = self.run_hook("tdd_guard.py", self.write_payload("src/new.py"))
        self.assertEqual(code, 0)
        self.assertIn(".quality-guard.json", err)

    def test_invalid_stdin_is_ignored(self):
        self.assertEqual(self.run_hook("tdd_guard.py", None, stdin_text="")[0], 0)


class RobustnessTests(HookCase):
    """Cases found by reviewing the code: bad config values, odd transcript entries, platform quirks."""
    MAP_ALL = {"tdd": {"mappings": [{"source": r"(?P<name>[^/]+)\.py$", "test": "tests/test_{name}.py"}]}}

    def undeclared(self):
        return self.write_transcript([user_prompt("x"), assistant_text("no tier"), assistant_tool_use()])

    def test_wrong_value_types_in_config_fall_back_to_defaults_with_notice(self):
        self.write_config({"source_extensions": None, "skip_patterns": 5, "disable": "tier_guard",
                           "tdd": {"mappings": 123, "test_file_patterns": None}})
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(self.undeclared()))
        self.assertEqual(code, 2)
        self.assertIn(".quality-guard.json", err)
        code, err, _ = self.run_hook("tdd_guard.py", self.edit_payload("", "src/new.py", tool="Write", content="x"))
        self.assertEqual(code, 0)
        self.assertIn(".quality-guard.json", err)

    def test_invalid_regex_in_config_is_skipped_with_notice(self):
        self.write_config({"tdd": {"test_file_patterns": ["("], "mappings": [
            {"source": "(", "test": "x"}, {"source": r"^src/(?P<name>[^/]+)\.py$", "test": "tests/test_{name}.py"}]}})
        code, err, _ = self.run_hook("tdd_guard.py", self.edit_payload("", "src/new.py", tool="Write", content="x"))
        self.assertEqual(code, 2)
        self.assertIn(".quality-guard.json", err)

    def test_unexpected_hook_input_never_crashes(self):
        payload = self.edit_payload(self.undeclared())
        payload["tool_input"] = 5
        code, err, _ = self.run_hook("tier_guard.py", payload)
        self.assertEqual(code, 0)

    def test_null_text_block_in_transcript_does_not_crash(self):
        t = self.write_transcript([user_prompt("x"), {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": None}]}},
                                   assistant_text("no tier"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 2)

    def test_tier_token_must_stand_alone(self):
        for text in ("see arr[A] here", "read [B](http://example.com)"):
            t = self.write_transcript([user_prompt("x"), assistant_text(text), assistant_tool_use()])
            self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 2, text)
        for text in ("Tier [A]: plan", "[C] docs only", "(tier [B])"):
            t = self.write_transcript([user_prompt("x"), assistant_text(text), assistant_tool_use()])
            self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 0, text)

    def test_skip_patterns_match_whole_path_segments(self):
        t = self.undeclared()
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "src/redist/app.py"))[0], 2)
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "my_dist/app.py"))[0], 2)
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "dist/app.py"))[0], 0)
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "pkg/dist/app.py"))[0], 0)

    def test_image_only_user_message_starts_a_new_turn(self):
        t = self.write_transcript([user_prompt("old"), assistant_text("[A] old turn"), assistant_tool_use(), user_tool_result(),
                                   user_image_only(), assistant_text("no tier now"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t))[0], 2)

    def test_non_ascii_paths_survive_stdin(self):
        t = self.write_transcript([user_prompt("x"), assistant_text("[A] ok"), assistant_tool_use()])
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(t, "src/한글.py"))[0], 0)
        t2 = self.undeclared()
        code, err, _ = self.run_hook("tier_guard.py", self.edit_payload(t2, "src/한글.py"))
        self.assertEqual(code, 2)
        self.assertIn("한글.py", err)

    def test_tail_limit_ignores_odd_values(self):
        import qg_common
        for value in ("\u00b2", " 5 ", "-3", "abc", ""):
            self.assertGreater(qg_common.tail_limit({"QUALITY_GUARD_TAIL_BYTES": value}), 0, value)
        self.assertEqual(qg_common.tail_limit({"QUALITY_GUARD_TAIL_BYTES": "\u00b2"}), qg_common.DEFAULT_TAIL_BYTES)

    def test_disable_key_turns_off_a_single_hook(self):
        self.write_config({"disable": ["tier_guard"]})
        self.assertEqual(self.run_hook("tier_guard.py", self.edit_payload(self.undeclared()))[0], 0)
        self.write_config({**self.MAP_ALL, "disable": ["tdd_guard"]})
        self.assertEqual(self.run_hook("tdd_guard.py", self.edit_payload("", "src/new.py", tool="Write", content="x"))[0], 0)

    def test_tdd_respects_skip_patterns(self):
        self.write_config({**self.MAP_ALL, "skip_patterns": ["vendor/"]})
        self.assertEqual(self.run_hook("tdd_guard.py", self.edit_payload("", "vendor/lib.py", tool="Write", content="x"))[0], 0)
        self.assertEqual(self.run_hook("tdd_guard.py", self.edit_payload("", "src/lib.py", tool="Write", content="x"))[0], 2)

    def test_a_directory_is_not_a_test_file(self):
        self.write_config(self.MAP_ALL)
        os.makedirs(os.path.join(self.project, "tests", "test_new.py"))
        self.assertEqual(self.run_hook("tdd_guard.py", self.edit_payload("", "src/new.py", tool="Write", content="x"))[0], 2)

    def test_null_content_is_treated_as_empty(self):
        self.write_config({"tdd": {"mappings": [{"source": r"(?P<name>[^/]+)\.py$", "test": "tests/test_{name}.py", "content_regex": "None"}]}})
        payload = self.edit_payload("", "src/new.py", tool="Write")
        payload["tool_input"]["content"] = None
        self.assertEqual(self.run_hook("tdd_guard.py", payload)[0], 0)

    def test_first_matching_mapping_decides(self):
        self.write_config({"tdd": {"mappings": [
            {"source": r"^src/(?P<name>[^/]+)\.py$", "test": "tests/test_{name}.py"},
            {"source": r"^src/(?P<name>[^/]+)\.py$", "test": "tests/other_{name}.py"}]}})
        os.makedirs(os.path.join(self.project, "tests"))
        open(os.path.join(self.project, "tests", "other_new.py"), "w").close()
        self.assertEqual(self.run_hook("tdd_guard.py", self.edit_payload("", "src/new.py", tool="Write", content="x"))[0], 2)


class SessionContextTests(HookCase):
    def test_outputs_additional_context_json(self):
        code, _, out = self.run_hook("session_context.py", {"hook_event_name": "SessionStart"})
        self.assertEqual(code, 0)
        data = json.loads(out)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "SessionStart")
        for token in ("[A]", "[B]", "[C]", "QUALITY_GUARD=off"):
            self.assertIn(token, ctx)

    def test_silent_when_disabled(self):
        code, _, out = self.run_hook("session_context.py", {}, env_extra={"QUALITY_GUARD": "off"})
        self.assertEqual((code, out.strip()), (0, ""))

    def test_silent_when_tier_guard_is_disabled_in_config(self):
        self.write_config({"disable": ["tier_guard"]})
        code, _, out = self.run_hook("session_context.py", {"hook_event_name": "SessionStart", "cwd": self.project})
        self.assertEqual((code, out.strip()), (0, ""))

    def test_still_outputs_when_only_tdd_guard_is_disabled(self):
        self.write_config({"disable": ["tdd_guard"]})
        code, _, out = self.run_hook("session_context.py", {"hook_event_name": "SessionStart", "cwd": self.project})
        self.assertEqual(code, 0)
        self.assertIn("additionalContext", out)

    def test_still_outputs_when_config_is_broken(self):
        self.write_config(None, raw="{not json")
        code, _, out = self.run_hook("session_context.py", {"hook_event_name": "SessionStart", "cwd": self.project})
        self.assertEqual(code, 0)
        self.assertIn("additionalContext", out)


if __name__ == "__main__":
    unittest.main()
